# marketing.py
from __future__ import annotations
import json
import os
import random
from typing import Dict, Any, List, Optional, Iterable

class Marketing:
    """
    Bộ công cụ marketing cho dự án A:
      - CTA chuẩn
      - Quick-reply theo từ khoá
      - Load/format danh sách airdrop (có filter status/network)
      - Chọn airdrop ngẫu nhiên (FOMO)
      - Build nội dung chiến dịch dạng bullet
    """

    def __init__(self, lp_url: str, keywords: Dict[str, str]):
        self.lp_url = lp_url
        self.keywords = keywords

    # ====== CTA ======
    def cta(self) -> str:
        return f"👉 Xem chi tiết: {self.lp_url}"

    # ====== Quick reply theo từ khoá ======
    def quick_reply(self, text: str) -> Optional[str]:
        t = (text or "").lower().strip()
        for k, v in self.keywords.items():
            if k in t:
                return f"{v}\n{self.cta()}"
        return None

    # ====== Airdrops ======
    def load_airdrops(self, path: str = "airdrops.json") -> List[Dict[str, Any]]:
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return []
        except Exception as e:
            print(f"[marketing] Lỗi load {path}: {e}")
            return []

    @staticmethod
    def _filter(items: Iterable[Dict[str, Any]], status: Optional[str], network: Optional[str]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for it in items:
            ok = True
            if status:
                ok = ok and (it.get("status", "").lower() == status.lower())
            if network:
                ok = ok and (it.get("network", "").lower() == network.lower())
            if ok:
                out.append(it)
        return out

    def format_airdrops(
        self,
        items: List[Dict[str, Any]],
        status: Optional[str] = "open",
        network: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> str:
        """
        Hiển thị danh sách airdrop:
          - status: lọc theo 'open'/'closed'/'upcoming' (mặc định 'open')
          - network: 'ton' / 'bsc' / 'eth' ... (nếu có)
          - limit: giới hạn số dòng hiển thị
        """
        if not items:
            return "Hiện chưa có airdrop nào."

        items = self._filter(items, status=status, network=network)
        if not items:
            return "Không có airdrop phù hợp bộ lọc."

        if limit:
            items = items[:limit]

        lines = ["🔥 Danh sách Airdrop HOT:"]
        for i, it in enumerate(items, 1):
            name    = it.get("name", "?")
            desc    = it.get("desc", "")
            link    = it.get("link", "")
            reward  = it.get("reward", "N/A")
            net     = it.get("network", "N/A")
            stat    = it.get("status", "unknown")
            tags    = ", ".join(it.get("tags", []))

            lines.append(
                f"{i}. <b>{name}</b> – {desc}\n"
                f"🎁 Phần thưởng: {reward}\n"
                f"🌐 Network: {net}\n"
                f"📌 Trạng thái: {stat}\n"
                f"🏷 Tags: {tags}\n"
                f"🔗 {link}\n"
            )
        lines.append(self.cta())
        return "\n".join(lines)

    def random_airdrop(
        self,
        items: List[Dict[str, Any]],
        status: Optional[str] = "open",
        network: Optional[str] = None,
    ) -> str:
        if not items:
            return "Không có airdrop nào."
        filtered = self._filter(items, status=status, network=network) or items
        it = random.choice(filtered)
        name    = it.get("name", "?")
        desc    = it.get("desc", "")
        link    = it.get("link", "")
        reward  = it.get("reward", "N/A")
        net     = it.get("network", "N/A")
        stat    = it.get("status", "unknown")
        tags    = ", ".join(it.get("tags", []))

        return (
            f"🚀 <b>{name}</b>\n"
            f"{desc}\n"
            f"🎁 {reward} | 🌐 {net} | 📌 {stat}\n"
            f"🏷 {tags}\n"
            f"🔗 {link}\n\n{self.cta()}"
        )

    # ====== Builder chiến dịch ======
    def build_campaign(self, title: str, bullet_points: List[str]) -> str:
        bullets = "\n".join([f"• {x}" for x in bullet_points])
        return f"📢 <b>{title}</b>\n{bullets}\n\n{self.cta()}"
