#!/usr/bin/env python3
"""근거 기반 한의학 위키 — 논문 검색 API 자동화 스크립트.

med.symbolicinfo.com /search API로 논문을 수집해 마크다운 근거 표를 생성한다.
사용법:
    python3 scripts/search.py "요통" --cat clinical_trial,meta_analysis --km --human --analyzed
    python3 scripts/search.py "합곡" --per-page 50 --out /tmp/evidence.md
"""
import argparse
import json
import sys
import urllib.parse
import urllib.request

BASE = "https://med.symbolicinfo.com"

CATEGORY_LABEL = {
    "clinical_trial": "임상시험",
    "systematic_review": "체계적 고찰",
    "meta_analysis": "메타분석",
    "observational_study": "관찰연구",
    "case_report": "증례",
    "experimental_study": "실험연구",
    "review": "문헌고찰",
    "guideline": "가이드라인",
    "other": "기타",
}


def fetch(params: dict) -> dict:
    url = BASE + "/search?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.load(resp)


def fetch_all(q: str, base_params: dict, per_page: int, target: int = 0) -> list:
    """여러 페이지를 순회하며 최대한 많은 논문을 수집한다.

    - `target`이 양수면 그 수량만큼 확보할 때까지 순회한다(최대 1000건).
    - 같은 DOI의 논문은 하나로 병합(중복 제거)한다.
    """
    items = []
    seen = set()
    page = 1
    while target <= 0 or len(items) < target:
        params = dict(base_params)
        params.update({"q": q, "per_page": per_page, "page": page})
        data = fetch(params)
        batch = data.get("items", [])
        if not batch:
            break
        for it in batch:
            key = it.get("doi") or it.get("pmid") or it.get("url")
            if key and key in seen:
                continue
            if key:
                seen.add(key)
            items.append(it)
        if page >= data.get("total_pages", page):
            break
        page += 1
        if len(items) >= 1000:
            break
    return items


def evidence_row(item: dict) -> str:
    doi = item.get("doi") or "-"
    pmid = item.get("pmid") or "-"
    cat = item.get("research_category") or ""
    label = CATEGORY_LABEL.get(cat, cat)
    patients = item.get("patient_count")
    patients = patients if patients else "-"
    summary = (item.get("clinical_summary") or "").replace("|", "\\|").replace("\n", " ")
    return f"| {item.get('title','')} | {label} | {patients} | {label} | {doi} / {pmid} | {summary} |"


def main() -> int:
    p = argparse.ArgumentParser(description="논문 검색 API로 근거 표 생성")
    p.add_argument("q", help="검색어")
    p.add_argument("--cat", help="연구 유형 (콤마 구분)")
    p.add_argument("--km", action="store_true", help="한의학만")
    p.add_argument("--human", action="store_true", help="인체 연구만")
    p.add_argument("--lit", action="store_true", help="문헌 고찰만")
    p.add_argument("--analyzed", action="store_true", help="분석 완료만")
    p.add_argument("--per-page", type=int, default=20, help="페이지당 개수 (1~100)")
    p.add_argument("--target", type=int, default=0,
                   help="수집 목표 논문 수 (0 = 전부 순회, 최대 1000)")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--out", help="출력 파일 (없으면 stdout)")
    args = p.parse_args()

    params = {"per_page": args.per_page}
    if args.cat:
        params["cat"] = args.cat
    if args.km:
        params["km"] = 1
    if args.human:
        params["human"] = 1
    if args.lit:
        params["lit"] = 1
    if args.analyzed:
        params["analyzed"] = 1

    items = fetch_all(args.q, params, args.per_page, args.target)
    first = fetch(dict(params, q=args.q, per_page=args.per_page, page=1))
    total = first.get("total", len(items))

    lines = [
        f"# 근거 표: {args.q}",
        "",
        f"> 검색어: `{args.q}` · 총 {total}건 · 확보 {len(items)}건 (DOI 중복 제거 후)",
        "",
        "| 논문 제목 | 연구 유형 | 환자 수 | 근거 수준 | DOI/PMID | AI 임상 요약 |",
        "|---|---|---|---|---|---|",
    ]
    lines += [evidence_row(it) for it in items]

    out = "\n".join(lines) + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"작성 완료: {args.out} ({len(items)}건)")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
