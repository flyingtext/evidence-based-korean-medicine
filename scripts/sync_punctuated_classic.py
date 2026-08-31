#!/usr/bin/env python3
"""기존 표점을 보존하면서 표점본의 본문 문자를 최신 교정 원문과 맞춘다."""

from __future__ import annotations

import argparse
import difflib
import json
import re
import unicodedata
from pathlib import Path

from convert_classics import DEFAULT_CORRECTIONS, DEFAULT_SOURCE, apply_corrections, load_book, load_corrections


ROOT = Path(__file__).resolve().parents[1]
STAGING = ROOT / "docs" / "원문" / "_가져오기"
HEADING_TAG_RE = re.compile(r"\[h([1-6])\](.*?)\[/h\1\]", re.DOTALL | re.IGNORECASE)
INLINE_FORMAT_TAG_RE = re.compile(r"</?(?:ins|u)>|\[/?u\]", re.IGNORECASE)


def significant(char: str) -> bool:
    return not char.isspace() and not unicodedata.category(char).startswith("P")


def significant_positions(text: str) -> list[int]:
    ignored: set[int] = set()
    for match in INLINE_FORMAT_TAG_RE.finditer(text):
        ignored.update(range(match.start(), match.end()))
    return [
        index
        for index, char in enumerate(text)
        if index not in ignored and significant(char)
    ]


def signature(text: str) -> str:
    return "".join(text[index] for index in significant_positions(text))


def punctuation_signature(text: str) -> str:
    ignored: set[int] = set()
    for match in INLINE_FORMAT_TAG_RE.finditer(text):
        ignored.update(range(match.start(), match.end()))
    return "".join(
        char
        for index, char in enumerate(text)
        if index not in ignored and unicodedata.category(char).startswith("P")
    )


def split_title(text: str) -> tuple[str, str]:
    match = re.match(r"(\A# [^\n]*\n)", text)
    return (match.group(1), text[match.end() :]) if match else ("", text)


def sync_body(rendered: str, desired: str) -> tuple[str, dict[str, int]]:
    positions = significant_positions(rendered)
    old = "".join(rendered[index] for index in positions)
    new = signature(desired)
    # 결자 교감의 가장 흔한 형태는 두 글자 표지(HT/KT)를 한 글자로
    # 복원하는 것이다. 이 경우에는 전체 LCS를 구할 필요 없이 한 번의
    # 선형 순회로 정확한 편집 위치를 얻을 수 있다.
    marker_edits: list[tuple[int, int, str]] = []
    i = j = 0
    while i < len(old) and j < len(new):
        if old[i] == new[j]:
            i += 1
            j += 1
            continue
        if old[i : i + 2] in {"HT", "KT"}:
            run_start = i
            marker_count = 0
            while old[i : i + 2] in {"HT", "KT"}:
                marker_count += 1
                i += 2
            next_markers = [position for position in (old.find("HT", i), old.find("KT", i)) if position >= 0]
            anchor_end = min(i + 24, min(next_markers)) if next_markers else i + 24
            anchor = old[i:anchor_end]
            search_end = min(len(new), j + max(32, marker_count * 8) + len(anchor))
            anchor_at = new.find(anchor, j + marker_count, search_end) if anchor else len(new)
            if anchor_at < 0:
                marker_edits = []
                break
            replacement = new[j:anchor_at]
            if len(replacement) < marker_count:
                marker_edits = []
                break
            offset = 0
            for marker_index in range(marker_count):
                take = 1 if marker_index + 1 < marker_count else len(replacement) - offset
                source_index = run_start + marker_index * 2
                marker_edits.append(
                    (
                        positions[source_index],
                        positions[source_index + 1] + 1,
                        replacement[offset : offset + take],
                    )
                )
                offset += take
            j = anchor_at
            continue
        marker_edits = []
        break
    if marker_edits and i == len(old) and j == len(new):
        punctuation_before = punctuation_signature(rendered)
        for start, end, replacement in reversed(marker_edits):
            rendered = rendered[:start] + replacement + rendered[end:]
        if signature(rendered) != new:
            raise RuntimeError("동기화 후 비표점 문자 배열이 교정 원문과 일치하지 않음")
        if punctuation_signature(rendered) != punctuation_before:
            raise RuntimeError("동기화 과정에서 기존 표점 순서열이 변경됨")
        return rendered, {"replace": len(marker_edits) * 2, "delete": 0, "insert": 0}

    # 대형 고전은 같은 한자가 수천 번 반복된다. autojunk를 끄면
    # SequenceMatcher가 반복 문자마다 후보 좌표를 모두 훑어 수 분 이상
    # 걸릴 수 있다. 여기서는 결과를 아래의 완전한 서명 비교로 다시
    # 검증하므로, 빈출 문자를 앵커에서 제외해도 안전하다.
    matcher = difflib.SequenceMatcher(a=old, b=new, autojunk=True)
    edits: list[tuple[int, int, str]] = []
    punctuation_before = punctuation_signature(rendered)
    counts = {"replace": 0, "delete": 0, "insert": 0}
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        replacement = new[j1:j2]
        old_positions = positions[i1:i2]
        if tag == "insert":
            counts["insert"] += len(replacement)
        elif tag == "delete":
            counts["delete"] += i2 - i1
        else:
            counts["replace"] += max(i2 - i1, len(replacement))
        common = min(len(old_positions), len(replacement))
        for offset in range(common):
            position = old_positions[offset]
            edits.append((position, position + 1, replacement[offset]))
        for position in old_positions[common:]:
            edits.append((position, position + 1, ""))
        if len(replacement) > common:
            position = (
                old_positions[-1] + 1
                if old_positions
                else positions[i1] if i1 < len(positions) else len(rendered)
            )
            edits.append((position, position, replacement[common:]))
    for start, end, replacement in reversed(edits):
        rendered = rendered[:start] + replacement + rendered[end:]
    if signature(rendered) != new:
        raise RuntimeError("동기화 후 비표점 문자 배열이 교정 원문과 일치하지 않음")
    if punctuation_signature(rendered) != punctuation_before:
        raise RuntimeError("동기화 과정에서 기존 표점 순서열이 변경됨")
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
    corrections = load_corrections(DEFAULT_CORRECTIONS)
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
