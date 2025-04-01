import os
import json
import requests

class NotionClient:
    def __init__(self):
        self.NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
        self.DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")

        # 共通ヘッダー
        self.headers = {
            "Authorization": f"Bearer {self.NOTION_TOKEN}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }

    def create_child(self, child_data, parent_id):
        children_data = child_data.pop('children', None)

        url = f"https://api.notion.com/v1/blocks/{parent_id}/children"
        child_data = {"children": [child_data]}
        # print(json.dumps(child_data, ensure_ascii=False, indent=4))
        response = requests.patch(url, headers=self.headers, data=json.dumps(child_data))

        if response.status_code == 200:
            block_id = response.json()['results'][0]['id']
            if children_data is not None:
                self.create_children(children_data, block_id)
        else:
            print(f"child作成失敗: {response.status_code}\n{response.text}")
            raise Exception("child作成に失敗")

    def create_children(self, children_data: list[dict], parent_id):
        for child_data in children_data:
            self.create_child(child_data, parent_id)

    def create_page(self, title):
        page_data = {
            "parent": {"database_id": self.DATABASE_ID},
            "properties": {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": title,
                            }
                        }
                    ]
                }
            }
        }

        url = "https://api.notion.com/v1/pages"
        response = requests.post(url, headers=self.headers, data=json.dumps(page_data))
        
        if response.status_code == 200:
            # print(json.dumps(response.json(), indent=4, ensure_ascii=False))
            return response.json()['id']
            
        else:
            print(f"ページ作成に失敗: {response.status_code}\n{response.text}")
            raise Exception("ページ作成失敗")
        

if __name__ == "__main__":

    with open('parsed_data.json') as f:
        json_data = json.load(f)

    client = NotionClient()
    page_id = client.create_page('論文要約テスト')
    client.create_children(json_data['results'], page_id)
