import requests
import os
from enum import Enum
import datetime

class Color(Enum):
    RED     = 0xFF0000  # 赤
    GREEN   = 0x00FF00  # 緑
    BLUE    = 0x0000FF  # 青
    YELLOW  = 0xFFFF00  # 黄色
    ORANGE  = 0xFFA500  # オレンジ
    PURPLE  = 0x800080  # 紫
    BLACK   = 0x000000  # 黒
    WHITE   = 0xFFFFFF  # 白
    CYAN    = 0x00FFFF  # シアン
    MAGENTA = 0xFF00FF  # マゼンタ

class DiscordWebhookSender:
    def __init__(self, webhook_url: str):
        """
        初期化。Webhook の URL を設定します。
        """
        self.webhook_url = webhook_url

    def send_embed(
        self,
        title: str,
        description: str,
        color: Color = Color.WHITE,
        fields: list = None,
        footer: str = None,
        author: str = None
    ) -> requests.Response:
        """
        embed 形式のメッセージを送信します。

        Parameters:
          title (str): embed のタイトル
          description (str): embed の本文
          color (int): embed のカラー（デフォルト: 0x000000）
          fields (list): 辞書のリスト。各辞書は { "name": str, "value": str, "inline": bool } の形式
          footer (str): フッターテキスト
          author (str): 作者名

        Returns:
          requests.Response: POST リクエストのレスポンス
        """
        embed = {
            "title": title,
            "description": description,
            "color": color.value
        }
        if fields:
            embed["fields"] = fields
        if footer:
            embed["footer"] = {"text": footer}
        if author:
            embed["author"] = {"name": author}

        payload = {"embeds": [embed]}

        response = requests.post(self.webhook_url, json=payload)
        return response

if __name__ == "__main__":
    # あらかじめ Discord で作成した Webhook の URL に置き換えてください
    webhook_url = os.environ["DISCORD_WEBHOOK_URL"]
    webhook = DiscordWebhookSender(webhook_url)

    # embed を送信
    response = webhook.send_embed(
        author=f"論文紹介 {datetime.datetime.today().date()}",
        title="This is a sample paper",
        description="Author: hoge\nAbstruct: fuga\n[Link](https://arxiv.com)",
        color=Color.BLUE,
    )

    if response.status_code == 204:
        print("Embed メッセージの送信に成功しました。")
    else:
        print(f"送信に失敗しました: {response.status_code} {response.text}")
