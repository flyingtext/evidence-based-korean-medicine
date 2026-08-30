#!/usr/bin/env python3
"""승격된 정본의 원자료 해시와 staging 산출물 동일성을 검증한다."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "source"
FINAL_ROOT = ROOT / "docs" / "원문"
STAGING = FINAL_ROOT / "_가져오기"
REVIEW = ROOT / "data" / "classics_review_status.json"
PLACEHOLDER_RE = re.compile(r"HT|KT|\[/?c\]|�|□")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_files(root: Path) -> dict[str, Path]:
    return {
        path.relative_to(root).as_posix(): path
        for path in root.rglob("*")
        if (
            path.is_file()
            and path.name != "finalized.json"
            # 번역 산출물은 정본 원문의 staging 동일성 검사 대상이 아니다.
            and "_번역" not in path.relative_to(root).parts
        )
    }


def main() -> int:
    review = json.loads(REVIEW.read_text(encoding="utf-8")).get("books", {})
    finalized_dirs = sorted(
        path for path in FINAL_ROOT.iterdir()
        if path.is_dir() and path.name != STAGING.name and (path / "finalized.json").is_file()
    )
    errors: list[str] = []
    for directory in finalized_dirs:
        label = directory.name
        try:
            finalized = json.loads((directory / "finalized.json").read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f"{label}: finalized.json 읽기 실패 ({exc})")
            continue
        source_rel = finalized.get("source_path")
        source_path = SOURCE / source_rel if isinstance(source_rel, str) else None
        if source_path is None or not source_path.is_file():
            errors.append(f"{label}: 원자료 없음 ({source_rel})")
        elif file_hash(source_path) != finalized.get("source_sha256"):
            errors.append(f"{label}: 원자료 SHA-256 불일치")
        status = review.get(source_rel, {}) if isinstance(source_rel, str) else {}
        if status.get("collation_status") != "complete" or status.get("unresolved_candidates") != 0:
            errors.append(f"{label}: review 완료 게이트 불일치")
        placeholder_count = 0
        for markdown in directory.glob("*.md"):
            if markdown.name == "교감기록.md":
                continue
            placeholder_count += len(PLACEHOLDER_RE.findall(markdown.read_text(encoding="utf-8")))
        if placeholder_count:
            errors.append(f"{label}: 깨진 토큰·미복원 결자 {placeholder_count}건")
        staging_dir = STAGING / label
        if not staging_dir.is_dir():
            errors.append(f"{label}: 대응 staging 폴더 없음")
            continue
        final_files = tree_files(directory)
        staging_files = tree_files(staging_dir)
        if final_files.keys() != staging_files.keys():
            missing = sorted(staging_files.keys() - final_files.keys())
            extra = sorted(final_files.keys() - staging_files.keys())
            errors.append(f"{label}: 파일 목록 불일치 (누락 {missing}, 추가 {extra})")
            continue
        for relative in final_files:
            if file_hash(final_files[relative]) != file_hash(staging_files[relative]):
                errors.append(f"{label}/{relative}: staging과 내용 불일치")
    print(f"정본 검증: {len(finalized_dirs)}권, 오류 {len(errors)}건")
    for error in errors:
        print(f"ERROR {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
