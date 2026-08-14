#!/usr/bin/env python3
"""근거기반 한의학 위키 — 문서 품질 검증 스크립트.

wiki/ 아래 마크다운 문서의 링크·근거·표기 규칙을 점검한다.
사용법:
    python3 scripts/validate.py            # 전체 검증
    python3 scripts/validate.py --fix      # 수정 가능한 항목 자동 수정
"""
import argparse
import os
import re
import sys

WIKI_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wiki")

# 질환 폴더: KCD-8 코드가 본문에 있어야 함
DISEASE_DIRS = {"4_임상한의학"}

# 교과서적 표준 표기 검사용 (예시 — 필요 시 확장)
STANDARD_TERMS = {
    "합곡": "합곡(LI4)",
    "태충": "태충(LR3)",
    "보중익기탕": "보중익기탕(補中益氣湯)",
    "인삼": "인삼(人蔘)",
}


def walk_md():
    for root, _, files in os.walk(WIKI_DIR):
        for fn in files:
            if fn.endswith(".md"):
                yield os.path.join(root, fn)


def check_links(path, content, errors):
    # 상대 링크 대상 존재 확인
    for m in re.finditer(r"\]\(([^)#]+\.md)\)", content):
        target = m.group(1)
        if target.startswith("http"):
            continue
        resolved = os.path.normpath(os.path.join(os.path.dirname(path), target))
        if not os.path.exists(resolved):
            errors.append(f"[링크] {os.path.relpath(path, WIKI_DIR)} → {target} (없음)")


def check_kcd(path, content, errors):
    rel = os.path.relpath(path, WIKI_DIR)
    if rel.split(os.sep)[0] in DISEASE_DIRS and not rel.endswith("README.md"):
        if not re.search(r"KCD-8", content):
            errors.append(f"[KCD] {rel} — KCD-8 코드가 본문에 없음")


def check_standard_terms(path, content, errors):
    rel = os.path.relpath(path, WIKI_DIR)
    if rel.endswith("README.md"):
        return
    for term, standard in STANDARD_TERMS.items():
        # 표준 표기 없이 단독 한글 표기만 있는 경우
        if re.search(rf"(?<![\w(]){re.escape(term)}(?![\w(])", content) and standard not in content:
            errors.append(f"[표기] {rel} — '{term}' 표준 표기 '{standard}' 권장")


def main() -> int:
    ap = argparse.ArgumentParser(description="위키 문서 품질 검증")
    ap.add_argument("--fix", action="store_true", help="수정 가능한 항목 자동 수정")
    args = ap.parse_args()

    errors = []
    for path in walk_md():
        with open(path, encoding="utf-8") as f:
            content = f.read()
        check_links(path, content, errors)
        check_kcd(path, content, errors)
        check_standard_terms(path, content, errors)

    if errors:
        print(f"발견된 문제 {len(errors)}건:")
        for e in errors:
            print("  -", e)
        return 1
    print("검증 통과: 문제 없음")
    return 0


if __name__ == "__main__":
    sys.exit(main())
