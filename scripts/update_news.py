#!/usr/bin/env python3
"""
自動運転・ロボタクシー ニュース 自動更新スクリプト
GitHub Actions から毎日実行される
"""

import anthropic
import os
import re
import sys
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))
today = datetime.now(JST).strftime("%Y-%m-%d")

PROMPT = f"""あなたは自動運転・ロボタクシーのニュースキュレーターです。今日の日付は {today} です。

以下の検索キーワードでWebを検索し、最新ニュースを収集してHTMLページを生成してください。

## 検索キーワード（必ず全て検索すること）
1. waymo robotaxi news today {today[:4]}
2. tesla cybercab autonomous driving news
3. China Baidu Apollo autonomous vehicle news {today[:4]}
4. autonomous driving regulation policy news {today[:4]}
5. 自動運転 ロボタクシー ニュース 最新 日本
6. トヨタ ホンダ 日産 自動運転 {today[:4]}
7. 自動運転 規制 国土交通省 警察庁 {today[:4]}

## 記事の分類
**海外（左カラム）:**
- 🇺🇸 Waymo / 米国（3件以上）
- ⚡ Tesla / EV各社（2件以上）
- 🌏 中国・欧州・その他（3件以上）
- 📋 規制・政策（海外）（2件以上）

**国内（右カラム）:**
- 🚕 実証実験・サービス（4件以上）
- 🏭 メーカー・技術（3件以上）
- 📋 規制・政策（日本）（2件以上）

## 重要な要件
- 合計15件以上の記事を掲載すること
- 各記事を日本語で2〜3文に要約すること
- 全記事に実際のURLを設定すること（# は絶対に使わない）
- 該当ニュースがないカテゴリは丸ごと省略すること

## 出力形式
以下のHTMLテンプレートを使って、完全なHTMLを出力してください。省略せず最初から最後まで出力すること。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>自動運転・ロボタクシー ニュース</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Hiragino Sans', sans-serif; background: #f0f2f5; color: #1a202c; min-height: 100vh; }}
    header {{ background: linear-gradient(135deg, #ffffff 0%, #e8ecf0 100%); border-bottom: 1px solid #cbd5e0; padding: 20px; text-align: center; position: sticky; top: 0; z-index: 100; backdrop-filter: blur(10px); }}
    header h1 {{ font-size: 1.5rem; font-weight: 700; background: linear-gradient(135deg, #2b6cb0, #2c7a7b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }}
    header .subtitle {{ color: #718096; font-size: 0.82rem; margin-top: 3px; }}
    .update-info {{ display: inline-flex; align-items: center; gap: 6px; background: #e6f4ea; border: 1px solid #c6e6ce; border-radius: 20px; padding: 3px 12px; font-size: 0.75rem; color: #276749; margin-top: 8px; }}
    .update-info::before {{ content: ''; width: 6px; height: 6px; background: #38a169; border-radius: 50%; animation: pulse 2s infinite; }}
    @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} }}
    .two-col-layout {{ max-width: 1300px; margin: 0 auto; padding: 20px 16px; display: grid; grid-template-columns: 1fr 1fr; gap: 20px; align-items: start; }}
    .col-header {{ font-size: 0.7rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #4a5568; padding: 8px 12px; background: #e2e8f0; border-radius: 8px; margin-bottom: 14px; display: flex; align-items: center; gap: 8px; }}
    .col-header span {{ font-size: 1rem; }}
    .category-section {{ margin-bottom: 24px; }}
    .category-title {{ font-size: 0.68rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: #718096; padding: 0 0 8px 0; border-bottom: 1px solid #cbd5e0; margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }}
    .news-grid {{ display: grid; gap: 10px; }}
    .news-card {{ background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 16px; transition: border-color 0.2s, background 0.2s; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }}
    .news-card:hover {{ border-color: #4299e1; background: #f7faff; box-shadow: 0 2px 8px rgba(66,153,225,0.15); }}
    .news-card-meta {{ display: flex; align-items: center; gap: 8px; margin-bottom: 6px; flex-wrap: wrap; }}
    .source-tag {{ font-size: 0.68rem; font-weight: 600; background: #ebf4ff; color: #2b6cb0; padding: 1px 7px; border-radius: 4px; white-space: nowrap; }}
    .news-date {{ font-size: 0.68rem; color: #a0aec0; }}
    .news-title {{ font-size: 0.9rem; font-weight: 600; color: #1a202c; line-height: 1.45; margin-bottom: 6px; }}
    .news-summary {{ font-size: 0.82rem; color: #4a5568; line-height: 1.65; }}
    .news-link {{ display: inline-flex; align-items: center; gap: 3px; font-size: 0.73rem; color: #3182ce; margin-top: 8px; text-decoration: none; }}
    .news-link:hover {{ color: #2b6cb0; text-decoration: underline; }}
    footer {{ text-align: center; padding: 20px; color: #718096; font-size: 0.75rem; border-top: 1px solid #e2e8f0; margin-top: 10px; }}
    @media (max-width: 768px) {{ .two-col-layout {{ grid-template-columns: 1fr; }} header h1 {{ font-size: 1.2rem; }} }}
  </style>
</head>
<body>
<header>
  <h1>🚗 自動運転・ロボタクシー ニュース</h1>
  <p class="subtitle">World Autonomous Driving News — AI Daily Digest</p>
  <div class="update-info">最終更新: {today} 07:00 JST</div>
</header>
<div class="two-col-layout">
  <div class="col-left">
    <div class="col-header"><span>🌍</span> 海外ニュース</div>
    [ここに海外カテゴリのHTMLを挿入]
  </div>
  <div class="col-right">
    <div class="col-header"><span>🇯🇵</span> 国内ニュース</div>
    [ここに国内カテゴリのHTMLを挿入]
  </div>
</div>
<footer>
  <p>このサイトはClaude AIが毎日自動的にニュースを収集・要約して更新しています。</p>
  <p style="margin-top:4px;">Powered by Claude + GitHub Actions</p>
</footer>
</body>
</html>
```

各カテゴリのHTMLは以下の構造で作成してください：
```html
<div class="category-section">
  <h2 class="category-title"><span>[絵文字]</span> [カテゴリ名]</h2>
  <div class="news-grid">
    <div class="news-card">
      <div class="news-card-meta">
        <span class="source-tag">[情報源]</span>
        <span class="news-date">[YYYY-MM-DD]</span>
      </div>
      <div class="news-title">[日本語タイトル]</div>
      <div class="news-summary">[日本語要約 2〜3文]</div>
      <a href="[実際のURL]" class="news-link" target="_blank" rel="noopener">元記事を読む →</a>
    </div>
  </div>
</div>
```

必ず完全なHTMLを最初から最後まで出力してください。途中で省略しないこと。"""


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable is not set")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    print(f"Generating news for {today}...")

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=16000,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 10,
        }],
        messages=[{"role": "user", "content": PROMPT}],
    )

    # レスポンスからHTMLを抽出
    full_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            full_text += block.text

    # HTMLブロックを抽出
    match = re.search(r"<!DOCTYPE html>.*?</html>", full_text, re.DOTALL | re.IGNORECASE)
    if not match:
        # コードブロック内のHTMLも試みる
        match = re.search(r"```html\s*(<!DOCTYPE html>.*?</html>)\s*```", full_text, re.DOTALL | re.IGNORECASE)
        if match:
            html_content = match.group(1)
        else:
            print("ERROR: Could not extract HTML from response")
            print("Response preview:", full_text[:500])
            sys.exit(1)
    else:
        html_content = match.group(0)

    # index.html に書き込み
    output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Successfully updated index.html ({len(html_content)} chars)")
    print(f"Date: {today}")


if __name__ == "__main__":
    main()
