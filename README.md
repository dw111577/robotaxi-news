# 自動運転・ロボタクシー ニュース

毎日自動更新される自動運転ニュースサイトです。Claude AIがWebからニュースを収集・日本語要約しています。

## GitHub Pages で公開する手順

### 1. GitHubリポジトリを作成

1. https://github.com/new にアクセス
2. Repository name: `robotaxi-news`
3. **Public** を選択
4. 「Create repository」をクリック

### 2. ローカルでgitを初期化してプッシュ

```bash
cd ~/Claude/robotaxi-news
git init
git add -A
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<あなたのユーザー名>/robotaxi-news.git
git push -u origin main
```

### 3. GitHub Pages を有効化

1. GitHubのリポジトリページを開く
2. Settings → Pages
3. Source: **Deploy from a branch**
4. Branch: **main** / **(root)**
5. 「Save」をクリック

数分後、以下のURLで公開されます:
```
https://<あなたのユーザー名>.github.io/robotaxi-news/
```

## 自動更新の仕組み

Claude Codeのスケジュールタスクが毎日AM9:00に起動し:
1. WebSearchで最新の自動運転ニュースを収集
2. Claude AIが日本語で要約・分類
3. `index.html` を更新
4. GitHubに自動プッシュ → GitHub Pagesに自動デプロイ

## ディレクトリ構成

```
robotaxi-news/
├── index.html    ← 毎日生成・更新されるメインページ
└── README.md     ← このファイル
```
