import unittest

from voice.core import Packs


def packs():
    return Packs(chain=["en"], budget_kb=1000)


class BasicTest(unittest.TestCase):
    def test_empty_packs_missing(self):
        self.assertIsNone(packs().resolve("hello", "en"))

    def test_hit_returns_pack(self):
        world = packs()
        world.add("base", "en", 100, ["hello"])
        self.assertEqual(world.resolve("hello", "en")[0], "base")

    def test_chain_is_stored(self):
        self.assertEqual(packs().chain, ["en"])

    def test_used_starts_at_zero(self):
        self.assertEqual(packs().used_kb, 0)

    def test_scanned_starts_at_zero(self):
        self.assertEqual(packs().scanned_count(), 0)


class FallbackChainTest(unittest.TestCase):
    def test_falls_back_to_chain_language(self):
        world = Packs(chain=["en", "de"], budget_kb=1000)
        world.add("de-pack", "de", 100, [])
        world.add("base-en", "en", 100, ["hello"])
        self.assertEqual(world.resolve("hello", "de")[0], "base-en")

    def test_target_language_preferred(self):
        world = Packs(chain=["en", "de"], budget_kb=1000)
        world.add("de-pack", "de", 100, ["hello"])
        world.add("base-en", "en", 100, ["hello"])
        self.assertEqual(world.resolve("hello", "de")[0], "de-pack")

    def test_chain_order_respected(self):
        world = Packs(chain=["en", "de", "fr"], budget_kb=1000)
        world.add("fr-pack", "fr", 100, ["hello"])
        world.add("de-pack", "de", 100, ["hello"])
        self.assertEqual(world.resolve("hello", "ja")[0], "de-pack")

    def test_chain_head_is_ultimate_fallback(self):
        world = Packs(chain=["en", "de"], budget_kb=1000)
        world.add("base-en", "en", 100, ["hello"])
        self.assertEqual(world.resolve("hello", "fr")[0], "base-en")


class BudgetTest(unittest.TestCase):
    def test_over_budget_pack_not_loaded(self):
        world = Packs(chain=["en"], budget_kb=50)
        world.add("big", "en", 200, ["hello"])
        self.assertIsNone(world.resolve("hello", "en"))
        self.assertEqual(world.used_kb, 0)

    def test_over_budget_falls_to_next_candidate(self):
        world = Packs(chain=["en", "de"], budget_kb=150)
        world.add("big-de", "de", 200, ["hello"])
        world.add("small-en", "en", 100, ["hello"])
        hit = world.resolve("hello", "de")
        self.assertEqual(hit[0], "small-en")
        self.assertEqual(world.used_kb, 100)

    def test_budget_is_cumulative(self):
        world = Packs(chain=["en"], budget_kb=150)
        world.add("a", "en", 100, ["hello"])
        world.add("b", "en", 100, ["world"])
        self.assertEqual(world.resolve("hello", "en")[0], "a")
        self.assertIsNone(world.resolve("world", "en"))
        self.assertEqual(world.used_kb, 100)

    def test_pack_not_billed_twice(self):
        world = Packs(chain=["en"], budget_kb=1000)
        world.add("base", "en", 100, ["hello"])
        world.resolve("hello", "en")
        world.resolve("hello", "en")
        self.assertEqual(world.used_kb, 100)

    def test_repeat_resolve_same_result(self):
        world = Packs(chain=["en", "de"], budget_kb=1000)
        world.add("de-pack", "de", 100, [])
        world.add("base-en", "en", 100, ["hello"])
        first = world.resolve("hello", "de")
        second = world.resolve("hello", "de")
        self.assertEqual(first, second)


class MissingEntryTest(unittest.TestCase):
    def test_missing_key_falls_through_to_next_candidate(self):
        world = Packs(chain=["en", "de"], budget_kb=1000)
        world.add("de-pack", "de", 100, ["other"])
        world.add("base-en", "en", 100, ["hello"])
        self.assertEqual(world.resolve("hello", "de")[0], "base-en")

    def test_missing_counted_when_no_candidate_has_key(self):
        world = Packs(chain=["en"], budget_kb=1000)
        world.add("base-en", "en", 100, ["hello"])
        self.assertIsNone(world.resolve("goodbye", "en"))
        self.assertEqual(world.missing, 1)

    def test_missing_not_counted_on_hit(self):
        world = Packs(chain=["en"], budget_kb=1000)
        world.add("base-en", "en", 100, ["hello"])
        world.resolve("hello", "en")
        self.assertEqual(world.missing, 0)


class ScannedTest(unittest.TestCase):
    def test_scanned_does_not_grow_with_pack_count(self):
        world = Packs(chain=["en"], budget_kb=10 ** 9)
        world.add("base-en", "en", 100, ["hello"])
        for i in range(1000):
            world.add("pack-%d" % i, "lang-%d" % i, 100, ["hello"])
        world.resolve("hello", "en")
        self.assertEqual(world.scanned_count(), 1)

    def test_many_packs_many_resolves_stay_cheap(self):
        world = Packs(chain=["en"], budget_kb=10 ** 9)
        for i in range(10000):
            world.add("pack-%d" % i, "lang-%d" % i, 1, ["k"])
        world.add("base-en", "en", 1, ["k"])
        for _ in range(1000):
            self.assertEqual(world.resolve("k", "en")[0], "base-en")
        self.assertEqual(world.scanned_count(), 1000)


class CliSampleTest(unittest.TestCase):
    def run_sample(self, sample):
        import io
        from contextlib import redirect_stdout

        from voice.cli import main

        buf = io.StringIO()
        with redirect_stdout(buf):
            main(["--sample", sample])
        return buf.getvalue().strip()

    def test_fallback_sample(self):
        self.assertEqual(self.run_sample("fallback"), "pack=base-en")

    def test_budget_sample(self):
        self.assertEqual(self.run_sample("budget"), "pack=none used=0")

    def test_missing_sample(self):
        self.assertEqual(self.run_sample("missing"), "missing=1 pack=none")


if __name__ == "__main__":
    unittest.main()
