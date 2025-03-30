from mistralai import Mistral
from mistralai import OCRResponse
import os
import json

class MistralOCR:
    def __init__(self):
        api_key = os.environ["MISTRAL_API_KEY"]
        self.client = Mistral(api_key=api_key)

    def ocr_from_url(self, url) -> OCRResponse:
        return self.client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": url,
            },
            include_image_base64=True
        )
    
    def render_md(self, url):
        ocr_response = self.ocr_from_url(url)
        md_ret = ""
        for page in ocr_response.pages:
            md_ret += page.markdown
        return md_ret

if __name__ == "__main__":
    ocr_client = MistralOCR()

    url = "https://arxiv.org/pdf/2503.21077"
    ret = ocr_client.render_md(url)
    print(ret)
    # with open('tmp.json', 'w') as f:
    #     json.dump(ret, f, indent=4)
