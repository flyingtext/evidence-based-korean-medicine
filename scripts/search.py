#!/usr/bin/env python3
"""근거기반 한의학 위키 — 논문 검색 API 자동화 스크립트.

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
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--out", help="출력 파일 (없으면 stdout)")
    args = p.parse_args()

    params = {"q": args.q, "per_page": args.per_page, "page": args.page}
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

    data = fetch(params)
    items = data.get("items", [])

    lines = [
        f"# 근거 표: {args.q}",
        "",
        f"> 검색어: `{args.q}` · 총 {data.get('total', 0)}건 · 페이지 {data.get('page')}/{data.get('total_pages')}",
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
