#!/usr/bin/env python3
"""자동 변환된 고전 원문 staging 영역을 검증한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT.parent / "source"
DEFAULT_OUTPUT = ROOT / "docs" / "원문" / "_가져오기"
SOURCE_ID_RE = re.compile(r"<!-- source-id: ([^ ]+) -->")
RAW_TAG_RE = re.compile(r"\[/?(?:book|h[1-6]|b|i|u|s|p|br)(?:=[^\]]*)?\]", re.IGNORECASE)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    manifest_path = output / "manifest.json"
    errors: list[str] = []
    warnings: list[str] = []
    if not manifest_path.exists():
        print(f"오류: manifest 없음: {manifest_path}")
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    seen_ids: set[str] = set()
    for book in manifest.get("books", []):
        source_path = source / book["source_path"]
        if not source_path.exists():
            errors.append(f"원본 없음: {book['source_path']}")
            continue
        digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
        if digest != book["sha256"]:
            errors.append(f"원본 변경됨: {book['source_path']}")
        if "output_directory" not in book:
            continue
        book_dir = output / book["output_directory"]
        punctuated_exists = (book_dir / "표점본.md").is_file()
        report_exists = (book_dir / "punctuation-report.json").is_file()
        if punctuated_exists != report_exists:
            errors.append(f"표점본·보고서 짝 불일치: {book['output_directory']}")
        if bool(book.get("punctuated")) != punctuated_exists:
            errors.append(f"표점 상태 불일치: {book['output_directory']}")
        task_path = book_dir / "translation-tasks.jsonl"
        if not task_path.exists():
            errors.append(f"번역 작업 파일 없음: {task_path.relative_to(output)}")
        task_ids: set[str] = set()
        if task_path.exists():
            for line_no, line in enumerate(task_path.read_text(encoding="utf-8").splitlines(), 1):
                try:
                    task = json.loads(line)
                    task_ids.add(task.get("parent_source_id", task["source_id"]))
                    if not task.get("text", "").strip():
                        warnings.append(f"빈 번역 단위: {task_path.relative_to(output)}:{line_no}")
                    if len(task.get("text", "")) > 6000:
                        errors.append(f"번역 단위 6,000자 초과: {task_path.relative_to(output)}:{line_no}")
                except (json.JSONDecodeError, KeyError) as exc:
                    errors.append(f"잘못된 JSONL: {task_path.relative_to(output)}:{line_no} ({exc})")
        file_ids: set[str] = set()
        management_files = {"README.md", "교감기록.md", "표점본.md"}
        md_files = [p for p in book_dir.glob("*.md") if p.name not in management_files]
        if len(md_files) != book.get("markdown_files"):
            errors.append(f"Markdown 수 불일치: {book['output_directory']}")
        for path in md_files:
            content = path.read_text(encoding="utf-8")
            raw_tags = RAW_TAG_RE.findall(content)
            if raw_tags:
                errors.append(f"원시 태그 잔류: {path.relative_to(output)} ({len(raw_tags)}개)")
            for source_id in SOURCE_ID_RE.findall(content):
                if source_id in seen_ids:
                    errors.append(f"중복 source-id: {source_id}")
                seen_ids.add(source_id)
                file_ids.add(source_id)
        missing = sorted(task_ids - file_ids)
        if missing:
            errors.append(f"Markdown에 없는 번역 ID: {book['output_directory']} ({len(missing)}개)")
    print(f"검증: {len(manifest.get('books', []))}권, 오류 {len(errors)}건, 경고 {len(warnings)}건")
    for item in errors:
        print(f"ERROR {item}")
    for item in warnings[:50]:
        print(f"WARN  {item}")
    if len(warnings) > 50:
        print(f"WARN  외 {len(warnings) - 50}건")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
