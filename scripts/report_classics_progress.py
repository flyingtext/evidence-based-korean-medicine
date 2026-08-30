#!/usr/bin/env python3
"""전체 고전 교감·표점·정본 승격 진행 현황을 Markdown으로 집계한다."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGING = ROOT / "docs" / "원문" / "_가져오기"
REVIEW = ROOT / "data" / "classics_review_status.json"
ONLINE = ROOT / "data" / "classics_online_catalog.json"
OUTPUT = STAGING / "교감현황.md"


def main() -> int:
    manifest = json.loads((STAGING / "manifest.json").read_text(encoding="utf-8"))
    review = json.loads(REVIEW.read_text(encoding="utf-8")).get("books", {})
    online = json.loads(ONLINE.read_text(encoding="utf-8"))
    by_source = {book["source_path"]: book for book in manifest["books"]}
    complete = [source for source, item in review.items() if item.get("collation_status") == "complete"]
    first_pass = [source for source, item in review.items() if item.get("collation_status") == "first_pass"]
    punctuated = sorted(STAGING.rglob("punctuation-report.json"))
    promoted = sorted(
        path for path in (ROOT / "docs" / "원문").iterdir()
        if path.is_dir() and (path / "finalized.json").is_file()
    )
    lines = [
        "# 고전 원문 교감 현황",
        "",
        f"- 전체 원자료: {manifest['count']}권",
        f"- jicheng.tw 본문 자동 대응: {online['summary']['with_data_sec']}권",
        f"- 결자 전수 판정 완료: {len(complete)}권",
        f"- 결자 1차 대조 진행: {len(first_pass)}권",
        f"- 검증된 표점본: {len(punctuated)}권",
        f"- 정본 폴더 승격: {len(promoted)}권",
        "",
        "## 개별 진행 문헌",
        "",
        "| 원자료 | 서명 | 결자 교감 | 미해결 | 표점 | 정본 승격 |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for source in sorted(review):
        item = review[source]
        book = by_source.get(source, {})
        metadata = book.get("metadata", {})
        title = metadata.get("書名") or metadata.get("篇名") or source
        directory = book.get("output_directory", "")
        has_punctuation = bool(directory and (STAGING / directory / "punctuation-report.json").is_file())
        punctuation_label = (
            "완료"
            if has_punctuation
            else "원자료 표점" if item.get("punctuation_status") == "source_present" else "대기"
        )
        is_promoted = bool(directory and (ROOT / "docs" / "원문" / directory / "finalized.json").is_file())
        lines.append(
            f"| `{source}` | {title} | {item.get('collation_status', 'pending')} | "
            f"{item.get('unresolved_candidates', '미집계')} | {punctuation_label} | "
            f"{'완료' if is_promoted else '대기'} |"
        )
    lines.extend([
        "",
        "완료 판정은 전각 공백 전수 분류, 확정 교정 적용, 표점 필요 여부 및 문자 보존 검증을 모두 통과한 경우에만 부여한다.",
        "",
    ])
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"현황 생성: {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
