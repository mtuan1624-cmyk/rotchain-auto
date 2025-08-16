import json
import os
import random
from typing import Dict, Any, List, Optional

class Marketing:
    def __init__(self, lp_url: str, keywords: Dict[str, str]):
        self.lp_url = lp_url
        self.keywords = keywords

    def cta(self) -> str:
        return f"👉 Xem chi tiết tại đây: {self.lp_url}"

    def quick_reply(self, text: str) -> Optional[str]:
        t = (text or "").lower().strip()
        for k, v in self.keywords.items():
            if k in t:
                return f"{v}\n{self.cta()}"
        return None

    def load_airdrops(self, path="airdrops.json") -> List[Dict[str, Any]]:
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Lỗi load {path}: {e}")
            return []

    def format_airdrops(self, items: List[Dict[str, Any]]) -> str:
        if not items:
            return "Hiện chưa có airdrop nào đang hot."
        lines = ["🔥 Danh sách Airdrop HOT:"]
        for i, it in enumerate(items, 1):
            lines.append(
                f"{i}. <b>{it.get('name','?')}</b> – {it.get('desc','')}\n🔗 {it.get('link','')}"
            )
        lines.append("\n" + self.cta())
        return "\n".join(lines)

    def random_airdrop(self, items: List[Dict[str, Any]]) -> str:
        if not items:
            return "Không có airdrop nào."
        it = random.choice(items)
        return f"🚀 <b>{it.get('name')}</b>\n{it.get('desc')}\n🔗 {it.get('link')}\n\n{self.cta()}"

    def build_campaign(self, title: str, bullet_points: List[str]) -> str:
        bullets = "\n".join([f"• {x}" for x in bullet_points])
        return f"📢 <b>{title}</b>\n{bullets}\n\n{self.cta()}"
