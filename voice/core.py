"""语音包回退：语言回退链、条目缺失回退、体积预算与缺失统计。"""


class Packs:
    """语音包台账。"""

    def __init__(self, chain, budget_kb):
        self.chain = list(chain)
        self.budget_kb = budget_kb
        self.packs = {}
        self.used_kb = 0
        self.missing = 0
        self.scanned = 0
        self._by_lang = {}
        self._loaded = set()

    def add(self, pack, lang, kb, keys):
        self.packs[pack] = {"lang": lang, "kb": kb, "keys": set(keys)}
        langs = self._by_lang.setdefault(lang, [])
        if pack not in langs:
            langs.append(pack)

    def _candidate_langs(self, lang):
        seen = set()
        for cand in [lang] + self.chain:
            if cand not in seen:
                seen.add(cand)
                yield cand

    def resolve(self, key, lang):
        """找一条能播 key 的语音，返回 (包名, 条目) 或 None。"""
        for cand_lang in self._candidate_langs(lang):
            for pack in self._by_lang.get(cand_lang, ()):
                self.scanned += 1
                data = self.packs[pack]
                if pack not in self._loaded:
                    if self.used_kb + data["kb"] > self.budget_kb:
                        continue
                    self._loaded.add(pack)
                    self.used_kb += data["kb"]
                if key in data["keys"]:
                    return pack, key
        self.missing += 1
        return None

    def scanned_count(self):
        return self.scanned
