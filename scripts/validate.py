#!/usr/bin/env python3
"""근거 기반 한의학 위키 — 문서 품질 검증 스크립트.

wiki/ 아래 마크다운 문서의 링크·근거·표기·기준문서 수준 규칙을 점검한다.
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

# 기준 문서 대비 필수 구조 요소 (RUN.md §0-1, §3-5)
GOLD_STANDARD_CHECKS = {
    "다편_구조": {
        "pattern": r"^## 제\d+편",
        "min_count": 5,
        "desc": "다편(多篇) 구조 (5편 이상)",
    },
    "Q&A": {
        "pattern": r"^##+ .*\bQ&A\b|^Q\d+\.",
        "min_count": 1,
        "desc": "Q&A 섹션",
    },
    "각주_정의": {
        "pattern": r"^\[\^\d+\]:|\[PMID \d+\]|\[DOI [^\]]+\]",
        "min_count": 15,
        "desc": "각주 정의/인용 (최소 15개, [^n]: 또는 [PMID/DOI] 형식)",
    },
    "근거_한계_명시": {
        "pattern": r"임상 틀|동일 근거수준의 권고|근거 수준에 맞",
        "min_count": 1,
        "desc": "근거 한계 명시 문구",
    },
    "변증_층화_강조": {
        "pattern": r"변증 없는 관행적|변증 없이|변증 층화",
        "min_count": 1,
        "desc": "변증 층화 강조 문구",
    },
    "환자_설명용_요약": {
        "pattern": r"환자 설명|환자에게.*설명|일반인.*설명",
        "min_count": 1,
        "desc": "환자 설명용 요약",
    },
    "고전_인용_출처": {
        "pattern": r"고전 인용 출처|黃帝內經|內經|傷寒論|金匱",
        "min_count": 1,
        "desc": "고전 인용 출처",
    },
    "추적_지표표": {
        "pattern": r"추적 지표|평가 지표|추적표",
        "min_count": 1,
        "desc": "추적 지표표",
    },
    "안전성_표": {
        "pattern": r"약물상호작용|안전성|부작용|이상반응",
        "min_count": 1,
        "desc": "안전성 항목",
    },
}

# 표제어 유형별 최소 인용 수 (RUN.md §1-2)
MIN_CITATIONS_BY_TYPE = {
    "한방병리학": 100,  # 증후·병리
    "임상한의학": 100,  # 질환
    "방제학": 50,       # 처방
    "본초학": 50,       # 본초
    "경락경혈학": 50,   # 경혈
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


def check_punctuation(path, content, errors):
    """중국어 모점 `。` 잔류 검사."""
    rel = os.path.relpath(path, WIKI_DIR)
    if rel.endswith("README.md"):
        return
    count = content.count("。")
    if count > 0:
        errors.append(f"[표점] {rel} — 중국어 모점 `。` {count}개 잔류 (`.`로 변환 필요)")


def check_gold_standard(path, content, errors, warnings):
    """기준 문서 대비 필수 구조 요소 점검 (RUN.md §0-1, §3-5)."""
    rel = os.path.relpath(path, WIKI_DIR)
    if rel.endswith("README.md"):
        return

    # README.md 가 아닌 문서에 대해 검사
    line_count = content.count("\n") + 1

    for key, spec in GOLD_STANDARD_CHECKS.items():
        matches = re.findall(spec["pattern"], content, re.MULTILINE)
        if len(matches) < spec["min_count"]:
            # 증후·질환 문서만 강제, 본초·경혈은 경고
            if "한방병리학" in rel or "임상한의학" in rel:
                errors.append(f"[기준] {rel} — {spec['desc']} 부족 ({len(matches)}/{spec['min_count']})")
            else:
                warnings.append(f"[기준] {rel} — {spec['desc']} 부족 ({len(matches)}/{spec['min_count']})")

    # 규모 검사
    if "한방병리학" in rel or "임상한의학" in rel:
        if line_count < 500:
            warnings.append(f"[기준] {rel} — 규모 {line_count}줄 (기준 1,000줄 이상 권장)")
    elif line_count < 200:
        warnings.append(f"[기준] {rel} — 규모 {line_count}줄 (기준 500줄 이상 권장)")


def check_citation_count(path, content, errors, warnings):
    """표제어 유형별 최소 인용 수 검사."""
    rel = os.path.relpath(path, WIKI_DIR)
    if rel.endswith("README.md"):
        return

    # 각주 정의 수 카운트 — [^n]: 형식(간기울결 방식) 또는 [PMID ...]/[DOI ...] 인라인 참조(간혈허 방식)
    footnote_defs = set(re.findall(r"^\[\^(\d+)\]:", content, re.MULTILINE))
    pmid_refs = set(re.findall(r"\[PMID (\d+)\]", content))
    doi_refs = set(re.findall(r"\[DOI ([^\]]+)\]", content))
    citation_count = len(footnote_defs) + len(pmid_refs) + len(doi_refs)

    # 표제어 유형 식별
    subject_type = None
    for folder, min_count in MIN_CITATIONS_BY_TYPE.items():
        if folder in rel:
            subject_type = folder
            min_required = min_count
            break

    if subject_type is None:
        return  # 기타 폴더는 검사 제외

    if citation_count < min_required:
        if citation_count < min_required // 2:
            errors.append(f"[인용] {rel} — 인용 {citation_count}편 (기준 {min_required}편, 절반 미만)")
        else:
            warnings.append(f"[인용] {rel} — 인용 {citation_count}편 (기준 {min_required}편)")


def main() -> int:
    ap = argparse.ArgumentParser(description="위키 문서 품질 검증")
    ap.add_argument("--fix", action="store_true", help="수정 가능한 항목 자동 수정")
    args = ap.parse_args()

    errors = []
    warnings = []
    for path in walk_md():
        with open(path, encoding="utf-8") as f:
            content = f.read()
        check_links(path, content, errors)
        check_kcd(path, content, errors)
        check_standard_terms(path, content, errors)
        check_punctuation(path, content, errors)
        check_gold_standard(path, content, errors, warnings)
        check_citation_count(path, content, errors, warnings)

    if warnings:
        print(f"경고 {len(warnings)}건:")
        for w in warnings:
            print("  ⚠", w)
        print()

    if errors:
        print(f"오류 {len(errors)}건:")
        for e in errors:
            print("  ✗", e)
        return 1

    if warnings:
        print("검증 통과 (경고 있음)")
    else:
        print("검증 통과: 문제 없음")
    return 0


if __name__ == "__main__":
    sys.exit(main())
