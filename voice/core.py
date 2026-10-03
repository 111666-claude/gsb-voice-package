"""语音包回退：语言回退链、条目缺失回退、体积预算与缺失统计。

缺陷：不回退到链上的下一个语言、不检查条目是否存在、
不看体积预算、缺失不计数、每次解析扫描全部语音包。
"""


class Packs:
    """语音包台账。"""

    def __init__(self, chain, budget_kb):
        self.chain = list(chain)
        self.budget_kb = budget_kb
        self.packs = {}
        self.used_kb = 0
        self.missing = 0
        self.scanned = 0

    def add(self, pack, lang, kb, keys):
        self.packs[pack] = {"lang": lang, "kb": kb, "keys": set(keys)}

    def resolve(self, key, lang):
        """找一条能播 key 的语音，返回 (包名, 条目) 或 None。"""
        self.scanned += len(self.packs)
        for pack, data in self.packs.items():
            return pack, key
        return None

    def scanned_count(self):
        return self.scanned
