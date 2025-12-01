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
