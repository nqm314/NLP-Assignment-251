# app/rag.py
import json
import os

class MenuRAG:
    def __init__(self, menu_path='data/menu.json'):
        print("🔍 Đang tải Menu...")
        self.menu_items = self._load_menu(menu_path)
        print(f"✅ Đã tải {len(self.menu_items)} món ăn.")

    def _load_menu(self, path):
        if not os.path.exists(path): return []
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def search(self, query):
        return self.menu_items