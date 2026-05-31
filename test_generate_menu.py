#!/usr/bin/env python3
"""Stress-test generate_menu.py across every non-empty subset of twist combos.

Bypasses the interactive checkbox UI by calling generate() directly. Outputs
land in test_output/ named with the same short_code scheme as the real run.
"""

import argparse
import sys
import time
from itertools import combinations
from pathlib import Path

from generate_menu import (
    COMBOS_FILE,
    generate,
    parse_combos,
    short_code,
    single_flavors,
)

TEST_OUT = Path(__file__).parent / "test_output"


def all_subsets(combos, min_size, max_size):
    for r in range(min_size, max_size + 1):
        for subset in combinations(combos, r):
            yield list(subset)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--min", type=int, default=1, help="min subset size (default 1)")
    ap.add_argument("--max", type=int, default=None, help="max subset size (default = all combos)")
    ap.add_argument("--limit", type=int, default=None, help="stop after N renders")
    ap.add_argument("--dry-run", action="store_true", help="print plan, don't render")
    args = ap.parse_args()

    combos = parse_combos(COMBOS_FILE)
    max_size = args.max if args.max is not None else len(combos)

    TEST_OUT.mkdir(exist_ok=True)

    plan = list(all_subsets(combos, args.min, max_size))
    if args.limit:
        plan = plan[: args.limit]

    print(f"Combos available: {len(combos)}")
    print(f"Subsets to render: {len(plan)}  (sizes {args.min}..{max_size})")
    print(f"Output dir: {TEST_OUT}")
    print()

    if args.dry_run:
        for i, subset in enumerate(plan, 1):
            code = "".join(short_code(c) for c in subset)
            print(f"[{i:3d}/{len(plan)}] {code}  singles={len(single_flavors(subset))}  "
                  f"twists={len(subset)}")
        return

    failures = []
    t0 = time.time()
    for i, subset in enumerate(plan, 1):
        code = "".join(short_code(c) for c in subset)
        out = TEST_OUT / f"DE.RM.{code}2025.jpg"
        n_singles = len(single_flavors(subset))
        label = f"[{i:3d}/{len(plan)}] twists={len(subset)} singles={n_singles} {code}"
        try:
            t = time.time()
            generate(subset, out)
            print(f"{label}  ok  ({time.time() - t:.1f}s)")
        except Exception as e:
            print(f"{label}  FAIL  {type(e).__name__}: {e}")
            failures.append((code, e))

    dt = time.time() - t0
    print()
    print(f"Done in {dt:.1f}s. {len(plan) - len(failures)}/{len(plan)} succeeded.")
    if failures:
        print("Failures:")
        for code, e in failures:
            print(f"  {code}: {type(e).__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
