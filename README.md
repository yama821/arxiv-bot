# arXiv-bot

## 概要
* arXiv に投稿された論文を日本語で要約して discord などに送信
* 動作の仕組み
  * pdf をダウンロード / tex ファイルをダウンロード
    * Mistral OCR でテキスト化
  * GPT-5-mini で主定理の取り出し
  * Notion に要約ページの作成
  * 一言要約 + Notion ページリンクを discord に送信

## 使い方
### 1. 各種 API Key を設定
`arxiv-bot/.env.sample` をコピーして `arxiv-bot/.env` を作成し、

- OpenAI API key
- Mistral API key
- Notion API key
- Notion DB id
- Discord webhook url

を入力してください。

### 2. 実行
`uv sync` の後に、以下のように実行してください。

__(a) PDF URL を指定する場合__
```sh
uv run python arxiv-bot/app.py --url (ここに pdf の url を入力)
```

例：
```sh
uv run python arxiv-bot/app.py --url https://arxiv.org/abs/2309.01119
```

__(b) primary category を指定__
arXiv の primary category を指定し、そのカテゴリーで当日投稿された論文に対して実行します。
```sh
uv run python arxiv-bot/app.py --cat (スペース区切りで対象のカテゴリー入力) --top-k (件数を指定する場合はここに数字を入力)
```

例：
```sh
uv run python arxiv-bot/app.py --cat math.CO cs.DS --top-k 5
```
