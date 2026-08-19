#!/usr/bin/env python3
"""수집된 논문 중 인간 대상 연구만 추출·분석."""
import json

with open("/var/folders/wk/rr41_hvx11n61txygwhc3xvh0000gn/T/opencode/ganyaung_papers.json", encoding="utf-8") as f:
    papers = json.load(f)

# 동물실험 배제: experimental_study 중 is_human_study가 True가 아닌 것 제외
human_papers = []
animal_excluded = 0
for p in papers:
    cat = p.get("research_category") or ""
    is_human = p.get("is_human_study")
    if cat == "experimental_study" and not is_human:
        animal_excluded += 1
        continue
    human_papers.append(p)

print(f"전체: {len(papers)}건")
print(f"동물실험 배제: {animal_excluded}건")
print(f"인간 대상/비동물실험: {len(human_papers)}건")

# 연구유형별 분포
cat_dist = {}
for p in human_papers:
    cat = p.get("research_category") or "other"
    cat_dist[cat] = cat_dist.get(cat, 0) + 1
print("\n=== 연구유형 분포 (동물실험 배제 후) ===")
for cat, n in sorted(cat_dist.items(), key=lambda x: -x[1]):
    print(f"  {cat}: {n}")

km = sum(1 for p in human_papers if p.get("is_korean_medicine"))
human = sum(1 for p in human_papers if p.get("is_human_study"))
print(f"\n한의학: {km}, 인체연구 명시: {human}")

# 메타분석/체계적고찰/임상시험/관찰연구/증례 우선 정렬
PRIORITY = {"meta_analysis": 0, "systematic_review": 1, "guideline": 2, "clinical_trial": 3, "observational_study": 4, "case_report": 5, "review": 6, "experimental_study": 7, "other": 8}
human_papers.sort(key=lambda p: (PRIORITY.get(p.get("research_category","other"), 9), p.get("pub_date","") or "", ))

# 저장
out = "/var/folders/wk/rr41_hvx11n61txygwhc3xvh0000gn/T/opencode/ganyaung_human.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(human_papers, f, ensure_ascii=False, indent=2)
print(f"\n저장: {out}")

# 상위 30개 미리보기
print("\n=== 상위 30개 (높은 연구유형 우선) ===")
for i, p in enumerate(human_papers[:30]):
    title = (p.get("title","") or "")[:80]
    cat = p.get("research_category","")
    doi = p.get("doi","")
    pmid = p.get("pmid","")
    km = "KM" if p.get("is_korean_medicine") else ""
    human = "H" if p.get("is_human_study") else ""
    print(f"  [{i+1}] {cat} | {km} {human} | {title} | DOI:{doi} PMID:{pmid}")