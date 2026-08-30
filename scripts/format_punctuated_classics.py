#!/usr/bin/env python3
"""표점본의 ASCII 쉼표·마침표 뒤에 읽기용 공백을 일관되게 넣는다."""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = ROOT / "docs" / "원문"
def format_spacing(text: str) -> tuple[str, int]:
    """소수점은 보존하고, 나머지 쉼표·마침표 뒤의 붙은 본문을 띄운다."""
    pieces: list[str] = []
    changes = 0
    for index, char in enumerate(text):
        pieces.append(char)
        if char not in {",", "."} or index + 1 >= len(text):
            continue
        following = text[index + 1]
        if following.isspace() or following in ",.!?;:)]}\"'":
            continue
        preceding = text[index - 1] if index else ""
        if char == "." and preceding.isdigit() and following.isdigit():
            continue
        pieces.append(" ")
        changes += 1
    return "".join(pieces), changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check", action="store_true", help="수정하지 않고 누락 공백이 있으면 실패")
    args = parser.parse_args()
    paths = sorted(args.root.resolve().rglob("표점본.md"))
    changed_files = 0
    total = 0
    for path in paths:
        original = path.read_text(encoding="utf-8")
        formatted, changes = format_spacing(original)
        if not changes:
            continue
        changed_files += 1
        total += changes
        if not args.check:
            path.write_text(formatted, encoding="utf-8")
        print(f"{path.relative_to(args.root.resolve())}: {changes}곳")
    action = "누락" if args.check else "수정"
    print(f"표점 공백 {action}: {changed_files}/{len(paths)}파일, {total}곳")
    return 1 if args.check and total else 0


if __name__ == "__main__":
    raise SystemExit(main())
