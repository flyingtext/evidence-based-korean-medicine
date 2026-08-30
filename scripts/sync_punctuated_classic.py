#!/usr/bin/env python3
"""기존 표점을 보존하면서 표점본의 본문 문자를 최신 교정 원문과 맞춘다."""

from __future__ import annotations

import argparse
import difflib
import json
import re
import unicodedata
from pathlib import Path

from convert_classics import DEFAULT_CORRECTIONS, DEFAULT_SOURCE, apply_corrections, load_book


ROOT = Path(__file__).resolve().parents[1]
STAGING = ROOT / "docs" / "원문" / "_가져오기"
HEADING_TAG_RE = re.compile(r"\[h([1-6])\](.*?)\[/h\1\]", re.DOTALL | re.IGNORECASE)


def significant(char: str) -> bool:
    return not char.isspace() and not unicodedata.category(char).startswith("P")


def signature(text: str) -> str:
    return "".join(char for char in text if significant(char))


def split_title(text: str) -> tuple[str, str]:
    match = re.match(r"(\A# [^\n]*\n)", text)
    return (match.group(1), text[match.end() :]) if match else ("", text)


def sync_body(rendered: str, desired: str) -> tuple[str, dict[str, int]]:
    positions = [index for index, char in enumerate(rendered) if significant(char)]
    old = "".join(rendered[index] for index in positions)
    new = signature(desired)
    matcher = difflib.SequenceMatcher(a=old, b=new, autojunk=False)
    edits: list[tuple[int, int, str]] = []
    counts = {"replace": 0, "delete": 0, "insert": 0}
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        replacement = new[j1:j2]
        start = positions[i1] if i1 < len(positions) else len(rendered)
        end = positions[i2 - 1] + 1 if i2 > i1 else start
        if tag == "insert":
            counts["insert"] += len(replacement)
        elif tag == "delete":
            counts["delete"] += i2 - i1
        else:
            counts["replace"] += max(i2 - i1, len(replacement))
        # 바뀐 비표점 문자 사이의 옛 표점은 교정 전 문맥에 속하므로 함께 걷어낸다.
        edits.append((start, end, replacement))
    for start, end, replacement in reversed(edits):
        rendered = rendered[:start] + replacement + rendered[end:]
    if signature(rendered) != new:
        raise RuntimeError("동기화 후 비표점 문자 배열이 교정 원문과 일치하지 않음")
    return rendered, counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_path", help="원자료 상대경로(예: A/A000a.txt)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    manifest = json.loads((STAGING / "manifest.json").read_text(encoding="utf-8"))
    matches = [item for item in manifest["books"] if item["source_path"] == args.source_path]
    if len(matches) != 1:
        raise SystemExit(f"manifest에서 원서를 하나로 찾을 수 없음: {args.source_path}")
    directory = STAGING / matches[0]["output_directory"]
    punctuated_path = directory / "표점본.md"
    report_path = directory / "punctuation-report.json"
    if not punctuated_path.is_file() or not report_path.is_file():
        raise SystemExit(f"표점본 또는 보고서가 없음: {directory}")

    source_path = DEFAULT_SOURCE / args.source_path
    book = load_book(source_path, DEFAULT_SOURCE)
    corrections = json.loads(DEFAULT_CORRECTIONS.read_text(encoding="utf-8"))
    apply_corrections(book, corrections)
    if book.warnings:
        raise SystemExit(f"교정 적용 경고 {len(book.warnings)}건: {book.warnings[:3]}")
    desired = HEADING_TAG_RE.sub(lambda match: match.group(2), book.body)

    title, rendered = split_title(punctuated_path.read_text(encoding="utf-8"))
    # Markdown 헤딩 표식은 구두점으로 취급되어 문자 서명에는 영향을 주지 않는다.
    synced, counts = sync_body(rendered, desired)
    if args.dry_run:
        print(json.dumps(counts, ensure_ascii=False))
        return 0
    punctuated_path.write_text(title + synced, encoding="utf-8")

    report = json.loads(report_path.read_text(encoding="utf-8"))
    preservation = report.setdefault("character_preservation", {})
    preservation["input_non_punctuation_characters"] = len(signature(desired))
    preservation["output_non_punctuation_characters"] = len(signature(synced))
    preservation["verified"] = True
    report["correction_overlay_synchronized"] = True
    report["synchronization_edits"] = counts
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"동기화 완료: {args.source_path} {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
