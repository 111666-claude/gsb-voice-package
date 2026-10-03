"""命令行入口：跑语音包样例。"""

import argparse

from .core import Packs


def build_parser():
    parser = argparse.ArgumentParser(prog="voice-package", description="语音包回退")
    parser.add_argument("--sample", default="fallback", help="fallback / budget / missing")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.sample == "fallback":
        packs = Packs(chain=["en", "de"], budget_kb=1000)
        packs.add("de-pack", "de", 100, [])
        packs.add("base-en", "en", 100, ["hello"])
        hit = packs.resolve("hello", "de")
        print("pack=%s" % (hit[0] if hit else "none"))
    elif args.sample == "budget":
        packs = Packs(chain=["en"], budget_kb=50)
        packs.add("big", "en", 200, ["hello"])
        hit = packs.resolve("hello", "en")
        print("pack=%s used=%d" % (hit[0] if hit else "none", packs.used_kb))
    elif args.sample == "missing":
        packs = Packs(chain=["en"], budget_kb=1000)
        packs.add("base-en", "en", 100, ["hello"])
        hit = packs.resolve("goodbye", "en")
        print("missing=%d pack=%s" % (packs.missing, hit[0] if hit else "none"))
    else:
        raise SystemExit("需要 --sample fallback|budget|missing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
