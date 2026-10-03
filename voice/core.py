"""语音包回退：语言回退链、条目缺失回退、体积预算与缺失统计。"""


class Packs:
    """语音包台账。"""

    def __init__(self, chain, budget_kb):
        self.chain = list(chain)
        self.budget_kb = budget_kb
        self.packs = {}
        self._by_lang = {}
        self._loaded = set()
        self.used_kb = 0
        self.missing = 0
        self.scanned = 0

    def add(self, pack, lang, kb, keys):
        self.packs[pack] = {"lang": lang, "kb": kb, "keys": set(keys)}
        self._by_lang.setdefault(lang, []).append(pack)

    def _candidate_langs(self, lang):
        """目标语言优先，再按 chain 顺序，最后兜底链首语言。"""
        seen = set()
        order = [lang] + self.chain
        if self.chain:
            order.append(self.chain[0])
        for item in order:
            if item not in seen:
                seen.add(item)
                yield item

    def resolve(self, key, lang):
        """找一条能播 key 的语音，返回 (包名, 条目) 或 None。"""
        found = False
        for cand_lang in self._candidate_langs(lang):
            for pack in self._by_lang.get(cand_lang, ()):
                self.scanned += 1
                data = self.packs[pack]
                if key not in data["keys"]:
                    continue
                found = True
                if pack in self._loaded:
                    return pack, key
                if self.used_kb + data["kb"] > self.budget_kb:
                    continue
                self._loaded.add(pack)
                self.used_kb += data["kb"]
                return pack, key
        if not found:
            self.missing += 1
        return None

    def scanned_count(self):
        return self.scanned
