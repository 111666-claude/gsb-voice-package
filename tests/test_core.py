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
