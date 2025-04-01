import re
import json

class MarkdownToNotionConverter:
    def __init__(self, markdown_text=None):
        self.markdown_text = markdown_text
        self.results = []          # トップレベルのブロックリスト
        self.bullet_stack = []     # (indent, block) タプルで箇条書き階層を管理
        self.paragraph_lines = []  # 段落行のバッファ
        self.in_math_block = False # ディスプレイ数式ブロック内か否かのフラグ
        self.math_lines = []       # ディスプレイ数式ブロックの内容を蓄積

    def parse_inline_text(self, text):
        """
        テキスト中のインライン数式 ($...$) を検出し、Notion API 用の rich_text リストに変換する。
        空文字の場合はトークンとして追加しない。
        """
        parts = re.split(r'(\$[^$]+\$)', text)
        rich_text = []
        for part in parts:
            part_stripped = part.strip()
            if not part_stripped:
                continue
            if part_stripped.startswith('$') and part_stripped.endswith('$'):
                expr = part_stripped[1:-1].strip()
                if expr:
                    rich_text.append({
                        "type": "equation",
                        "equation": {"expression": expr}
                    })
            else:
                rich_text.append({
                    "type": "text",
                    "text": {"content": part}
                })
        return rich_text

    def flush_paragraph(self):
        """段落バッファの内容を paragraph ブロックとして追加する。"""
        if self.paragraph_lines:
            content = " ".join(self.paragraph_lines).strip()
            if content:
                self.results.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": self.parse_inline_text(content)
                    }
                })
            self.paragraph_lines.clear()

    def flush_math_block(self):
        """ディスプレイ数式ブロックの内容を equation ブロックとして追加する。"""
        if self.math_lines:
            expr = "\n".join(self.math_lines).strip()
            if expr:
                self.results.append({
                    "object": "block",
                    "type": "equation",
                    "equation": {"expression": expr}
                })
            self.math_lines.clear()

    def add_bullet_block(self, indent, content):
        """
        箇条書き行のブロックを生成し、インデントに応じた階層構造に追加する。
        同じインデントの場合は同じ階層（兄弟）として扱う。
        """
        block = {
            "object": "block",
            "type": "bulleted_list_item",
            "has_children": False,
            "bulleted_list_item": {
                "rich_text": self.parse_inline_text(content)
            }
        }
        if not self.bullet_stack:
            self.results.append(block)
            self.bullet_stack.append((indent, block))
        else:
            last_indent, _ = self.bullet_stack[-1]
            if indent > last_indent:
                # 深いインデント → 子ブロック
                parent_block = self.bullet_stack[-1][1]
                parent_block["has_children"] = True
                if "children" not in parent_block:
                    parent_block["children"] = []
                parent_block["children"].append(block)
                self.bullet_stack.append((indent, block))
            else:
                # 同じまたは浅いインデント → 同階層
                while self.bullet_stack and self.bullet_stack[-1][0] >= indent:
                    self.bullet_stack.pop()
                if self.bullet_stack:
                    parent_block = self.bullet_stack[-1][1]
                    parent_block["has_children"] = True
                    if "children" not in parent_block:
                        parent_block["children"] = []
                    parent_block["children"].append(block)
                else:
                    self.results.append(block)
                self.bullet_stack.append((indent, block))

    def parse(self, markdown_text) -> dict:
        """
        Markdown テキストを解析し、Notion API 用の JSON（{"results": [...]}）形式に変換する。
        インライン数式とディスプレイ数式ブロック、見出し、箇条書き、段落に対応。
        """
        if markdown_text is None:
            return {"results": []}
        
        lines = markdown_text.splitlines()
        self.results = []
        self.bullet_stack = []
        self.paragraph_lines = []
        self.in_math_block = False
        self.math_lines = []
        
        for line in lines:
            stripped = line.strip()
            # ディスプレイ数式ブロックの判定
            if stripped == "$$":
                if not self.in_math_block:
                    # 数式ブロック開始前に段落をフラッシュ
                    self.flush_paragraph()
                    self.bullet_stack.clear()
                    self.in_math_block = True
                    self.math_lines = []
                else:
                    # 数式ブロック終了 → flush math block
                    self.flush_math_block()
                    self.in_math_block = False
                continue

            if self.in_math_block:
                # 数式ブロック内はそのまま蓄積
                self.math_lines.append(line)
                continue

            # 空行の場合は段落フラッシュおよび箇条書き階層のリセット
            if not stripped:
                self.flush_paragraph()
                self.bullet_stack.clear()
                continue

            # 見出しの判定 (例: "## 論文情報")
            m_heading = re.match(r'^(#{1,6})\s+(.*)$', line)
            if m_heading:
                self.flush_paragraph()
                self.bullet_stack.clear()
                level = len(m_heading.group(1))
                content = m_heading.group(2).strip()
                block_type = f"heading_{level}" if level <= 3 else "heading_3"
                self.results.append({
                    "object": "block",
                    "type": block_type,
                    block_type: {
                        "rich_text": self.parse_inline_text(content)
                    }
                })
                continue

            # 箇条書き行の判定 (例: "* タイトル：..." または "- キーワード：...")
            m_bullet = re.match(r'^(\s*)([*-])\s+(.*)$', line)
            if m_bullet:
                self.flush_paragraph()
                indent = len(m_bullet.group(1))
                content = m_bullet.group(3).strip()
                self.add_bullet_block(indent, content)
                continue

            # それ以外の行は段落行として蓄積
            self.paragraph_lines.append(line.strip())

        # 最後に残っている段落と数式ブロックをフラッシュ
        if self.in_math_block:
            self.flush_math_block()
            self.in_math_block = False
        self.flush_paragraph()
        return {"results": self.results}

# 使用例: "../data/summay.md" を読み込む
if __name__ == "__main__":
    converter = MarkdownToNotionConverter()
    with open('../data/summary.md') as f:
        markdown_text = f.read()
    output_json = converter.parse(markdown_text)
    print(json.dumps(output_json, indent=4, ensure_ascii=False))
