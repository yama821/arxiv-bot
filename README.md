# arXiv-bot

## 概要
* arXiv に投稿された論文を日本語で要約して discord などに送信
* 操作手順
  * pdf をダウンロード / tex ファイルをダウンロード
    * Mistral OCR でテキスト化
  * GPT-5-mini で主定理の取り出し
  * discord に送信
