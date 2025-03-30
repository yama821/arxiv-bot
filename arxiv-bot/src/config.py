import json
import os
from pathlib import Path


def load_config():
    config_path = Path(__file__).resolve().parent / "config.json"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"設定ファイルの読み込みに失敗しました: {e}")
        exit(1)


CONFIG = load_config()
GUILD_IDS = CONFIG.get("guild_ids")
