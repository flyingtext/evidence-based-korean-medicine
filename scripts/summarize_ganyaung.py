#!/usr/bin/env python3
"""논문 목록에서 각주 정의 생성용 요약 출력."""
import json

with open("/var/folders/wk/rr41_hvx11n61txygwhc3xvh0000gn/T/opencode/ganyaung_relevant.json", encoding="utf-8") as f:
    papers = json.load(f)

CAT_LABEL = {
    "meta_analysis": "메타분석",
    "systematic_review": "체계적 고찰",
    "clinical_trial": "임상시험",
    "observational_study": "관찰연구",
    "case_report": "증례 보고",
    "experimental_study": "실험연구",
    "review": "문헌 고찰",
    "guideline": "임상진료지침",
    "other": "기타",
}

# 전체 논문 목록을 각주 정의 형식으로 출력 (번호 부여)
lines = []
for i, p in enumerate(papers):
    title = (p.get("title","") or "").rstrip(".")
    journal = (p.get("journal","") or "")
    pub = (p.get("pub_date","") or "")[:10]
    cat = p.get("research_category","")
    label = CAT_LABEL.get(cat, cat)
    doi = p.get("doi","")
    pmid = p.get("pmid","")
    km = "KM" if p.get("is_korean_medicine") else ""
    human = "H" if p.get("is_human_study") else ""
    n_pat = p.get("patient_count","") or ""
    
    links = ""
    if doi:
        links += f"[DOI {doi}](https://doi.org/{doi}) "
    if pmid:
        links += f"[PMID {pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)"
    links = links.strip()
    
    # 간단 요약용 answer/clinical_summary 일부
    ans = (p.get("answer","") or "")[:200]
    cs = (p.get("clinical_summary","") or "")[:200]
    pico_i = (p.get("pico_i","") or "")[:150]
    herbs = p.get("method_specific_herbal","") or ""
    formula = p.get("method_specific_herbal_formula","") or ""
    acup = p.get("method_specific_acupoint","") or ""
    
    lines.append(f"--- [{i+1}] {label} | {km} {human} | n={n_pat} ---")
    lines.append(f"  T: {title}")
    lines.append(f"  J: {journal} | {pub}")
    lines.append(f"  L: {links}")
    if herbs: lines.append(f"  HERB: {herbs[:120]}")
    if formula: lines.append(f"  FORM: {formula[:120]}")
    if acup: lines.append(f"  ACUP: {acup[:120]}")
    if ans: lines.append(f"  ANS: {ans}")
    if cs: lines.append(f"  CS: {cs}")

out = "ganyaung_summary.txt"
with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"저장: {out} ({len(papers)}건)")