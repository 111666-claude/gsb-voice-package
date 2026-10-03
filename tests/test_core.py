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


if __name__ == "__main__":
    unittest.main()


class FallbackChainTest(unittest.TestCase):
    def test_target_lang_first(self):
        world = Packs(chain=["en", "de"], budget_kb=1000)
        world.add("de-pack", "de", 100, ["hello"])
        world.add("base-en", "en", 100, ["hello"])
        self.assertEqual(world.resolve("hello", "de")[0], "de-pack")

    def test_falls_back_along_chain(self):
        world = Packs(chain=["en", "de"], budget_kb=1000)
        world.add("de-pack", "de", 100, [])
        world.add("base-en", "en", 100, ["hello"])
        self.assertEqual(world.resolve("hello", "de")[0], "base-en")

    def test_falls_back_to_chain_head(self):
        world = Packs(chain=["en", "de"], budget_kb=1000)
        world.add("base-en", "en", 100, ["hello"])
        self.assertEqual(world.resolve("hello", "fr")[0], "base-en")

    def test_missing_key_skips_to_next_candidate(self):
        world = Packs(chain=["en", "de"], budget_kb=1000)
        world.add("de-pack", "de", 100, ["other"])
        world.add("base-en", "en", 100, ["hello"])
        self.assertEqual(world.resolve("hello", "de")[0], "base-en")


class BudgetTest(unittest.TestCase):
    def test_over_budget_pack_not_loaded(self):
        world = Packs(chain=["en"], budget_kb=50)
        world.add("big", "en", 200, ["hello"])
        self.assertIsNone(world.resolve("hello", "en"))
        self.assertEqual(world.used_kb, 0)

    def test_over_budget_tries_next_candidate(self):
        world = Packs(chain=["en", "de"], budget_kb=150)
        world.add("de-big", "de", 200, ["hello"])
        world.add("en-small", "en", 100, ["hello"])
        self.assertEqual(world.resolve("hello", "de")[0], "en-small")
        self.assertEqual(world.used_kb, 100)

    def test_cumulative_budget(self):
        world = Packs(chain=["en"], budget_kb=150)
        world.add("a", "en", 100, ["hello"])
        world.add("b", "en", 100, ["bye"])
        self.assertEqual(world.resolve("hello", "en")[0], "a")
        self.assertIsNone(world.resolve("bye", "en"))
        self.assertEqual(world.used_kb, 100)

    def test_loaded_pack_not_charged_twice(self):
        world = Packs(chain=["en"], budget_kb=100)
        world.add("a", "en", 100, ["hello", "bye"])
        world.resolve("hello", "en")
        self.assertEqual(world.resolve("bye", "en")[0], "a")
        self.assertEqual(world.used_kb, 100)

    def test_repeat_resolve_same_result(self):
        world = Packs(chain=["en"], budget_kb=100)
        world.add("a", "en", 100, ["hello"])
        first = world.resolve("hello", "en")
        second = world.resolve("hello", "en")
        self.assertEqual(first, second)
        self.assertEqual(world.used_kb, 100)


class MissingTest(unittest.TestCase):
    def test_missing_counts_when_no_candidate_has_key(self):
        world = Packs(chain=["en"], budget_kb=1000)
        world.add("base-en", "en", 100, ["hello"])
        self.assertIsNone(world.resolve("goodbye", "en"))
        self.assertEqual(world.missing, 1)

    def test_missing_not_counted_when_key_exists_but_over_budget(self):
        world = Packs(chain=["en"], budget_kb=50)
        world.add("big", "en", 200, ["hello"])
        self.assertIsNone(world.resolve("hello", "en"))
        self.assertEqual(world.missing, 0)

    def test_missing_accumulates(self):
        world = Packs(chain=["en"], budget_kb=1000)
        world.resolve("x", "en")
        world.resolve("y", "en")
        self.assertEqual(world.missing, 2)


class ScannedTest(unittest.TestCase):
    def test_scanned_does_not_grow_with_pack_count(self):
        small = Packs(chain=["en"], budget_kb=1000)
        small.add("base", "en", 100, ["hello"])
        small.resolve("hello", "en")
        big = Packs(chain=["en"], budget_kb=1000)
        big.add("base", "en", 100, ["hello"])
        for i in range(1000):
            big.add("other-%d" % i, "zz", 100, ["hello"])
        big.resolve("hello", "en")
        self.assertEqual(big.scanned_count(), small.scanned_count())
