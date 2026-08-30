#!/usr/bin/env python3
"""검증 게이트를 모두 통과한 원서를 _가져오기에서 정본 위치로 승격한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "source"
STAGING = ROOT / "docs" / "원문" / "_가져오기"
FINAL_ROOT = ROOT / "docs" / "원문"
REVIEW_STATUS = ROOT / "data" / "classics_review_status.json"
PUNCTUATION_RE = re.compile(r"[。！？；，、：,.!?;:]")
CJK_RE = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")

# 같은 디렉터리의 독립 검증기를 승격 게이트에서도 재사용한다.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_punctuated_classics import validate_report  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_path", help="원자료 상대경로(예: N/N000.txt)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    manifest = json.loads((STAGING / "manifest.json").read_text(encoding="utf-8"))
    matches = [book for book in manifest["books"] if book["source_path"] == args.source_path]
    if len(matches) != 1:
        raise SystemExit(f"manifest에서 원서를 하나로 찾을 수 없음: {args.source_path}")
    book = matches[0]
    review_data = json.loads(REVIEW_STATUS.read_text(encoding="utf-8"))
    review = review_data.get("books", {}).get(args.source_path, {})
    staging_dir = STAGING / book["output_directory"]
    source_path = SOURCE / args.source_path

    failures: list[str] = []
    if review.get("collation_status") != "complete":
        failures.append("전면 교감 상태가 complete가 아님")
    if review.get("unresolved_candidates") != 0:
        failures.append("미해결 결자 후보가 0으로 확인되지 않음")
    if book.get("warnings"):
        failures.append(f"변환 경고 {len(book['warnings'])}건")
    source_sha = hashlib.sha256(source_path.read_bytes()).hexdigest()
    if source_sha != book["sha256"]:
        failures.append("원자료 SHA-256 불일치")

    source_text = source_path.read_text(encoding="utf-8-sig")
    cjk_count = len(CJK_RE.findall(source_text))
    source_density = len(PUNCTUATION_RE.findall(source_text)) / max(cjk_count, 1)
    punctuation_required = source_density < 0.005
    if punctuation_required:
        if not (staging_dir / "표점본.md").is_file():
            failures.append("무표점·저표점 원서인데 표점본이 없음")
        if not (staging_dir / "punctuation-report.json").is_file():
            failures.append("무표점·저표점 원서인데 표점 검증 보고서가 없음")
        if review.get("punctuation_status") not in {"codex_verified", "jicheng_verified"}:
            failures.append("표점 검수 상태가 verified가 아님")
        report_path = staging_dir / "punctuation-report.json"
        if report_path.is_file():
            punctuation_errors = validate_report(report_path, STAGING, 0.85, 0.80, 0.005)
            failures.extend(f"표점 엄격 검증: {error}" for error in punctuation_errors)

    if failures:
        print(f"승격 불가: {args.source_path}")
        for failure in failures:
            print(f"- {failure}")
        return 1

    destination = FINAL_ROOT / book["output_directory"]
    if destination.exists():
        raise SystemExit(f"정본 대상 폴더가 이미 존재함: {destination}")
    if args.dry_run:
        print(f"승격 가능: {staging_dir} → {destination}")
        return 0

    shutil.copytree(staging_dir, destination)
    finalized = {
        "source_path": args.source_path,
        "source_sha256": source_sha,
        "promoted_at": datetime.now(timezone.utc).isoformat(),
        "gates": {
            "collation_status": review["collation_status"],
            "unresolved_candidates": review["unresolved_candidates"],
            "punctuation_required": punctuation_required,
            "punctuation_status": review.get("punctuation_status", "source_present"),
        },
    }
    (destination / "finalized.json").write_text(
        json.dumps(finalized, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    index_path = FINAL_ROOT / "README.md"
    index = index_path.read_text(encoding="utf-8").rstrip()
    marker = "\n\n## 교감 완료 정본\n"
    if marker in index:
        index = index.split(marker, 1)[0].rstrip()
    finalized_dirs = sorted(
        path for path in FINAL_ROOT.iterdir()
        if path.is_dir() and path.name != "_가져오기" and (path / "finalized.json").is_file()
    )
    index += "\n\n## 교감 완료 정본\n\n"
    index += "\n".join(f"- [{path.name}]({path.name}/README.md)" for path in finalized_dirs)
    index += "\n"
    index_path.write_text(index, encoding="utf-8")
    print(f"승격 완료: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
