#!/usr/bin/env python3
"""간양상항 관련성 필터링 — title/keywords/answer/clinical_summary에서 관련 키워드 확인."""
import json

with open("/var/folders/wk/rr41_hvx11n61txygwhc3xvh0000gn/T/opencode/ganyaung_human.json", encoding="utf-8") as f:
    papers = json.load(f)

# 관련성 키워드 (간양상항/평간잠양/간풍/고혈압 한의학/현훈/편두통 한의학/이명 한의학/천마구등음/진간식풍탕/갱년기 한의학 등)
RELEVANT = [
    "간양", "간신음허", "평간", "잠양", "간풍", "허풍", "화풍", "간화", "간울", "간기울",
    "liver yang", "liver wind", "Gan Yang", "Gan wind", "hyperactivity liver",
    "천마", "天麻", "구등", "鉤藤", "Gastrodia", "Uncaria", "Tianma", "Gouteng",
    "진간", "鎮肝", "Zhen Gan", "Xi Feng",
    "고혈압", "hypertension", "blood pressure", "혈압",
    "현훈", "어지럼", "vertigo", "dizziness", "眩暈",
    "편두통", "migraine",
    "이명", "tinnitus",
    "두통", "headache",
    "갱년기", "menopause", "폐경", "climacteric",
    "뇌졸중", "stroke", "뇌경색", "뇌출혈",
    "파킨슨", "Parkinson",
    "불면", "insomnia",
    "불안", "anxiety",
    "진전", "tremor",
    "경련", "convulsion", "seizure", "epilep",
    "양각", "yang ascen",
    "소간", "疏肝", "간담", "liver gallbladder",
    "acupuncture hypertension", "침 고혈압", "침 혈압",
    "moxibustion hypertension", "뜸 고혈압",
    "Chinese medicine hypertension", "traditional Chinese medicine hypertension",
    "TCM hypertension", "traditional medicine blood pressure",
    "한약 고혈압", "한의학 고혈압",
    "폐간음허", "간음허",
    "liver deficiency", "liver yin deficiency",
    "yin deficiency hypertension",
    "wind stroke", "중풍",
    "hyperactivity yang",
    "stagnation liver",
    "서풍", "祛風", "식풍", "熄風",
]

# 명확히 관련 없는 키워드
EXCLUDE = [
    "hepatectomy", "liver resection", "liver transplant", "liver surgery",
    "Cesarean", "cesarean", "yoga delivery", "prenatal yoga",
    "hepatectomy", "laparoscopic liver",
    " associating liver partition",
]

def is_relevant(p):
    text = " ".join([
        p.get("title","") or "",
        p.get("question","") or "",
        p.get("answer","") or "",
        p.get("clinical_summary","") or "",
        " ".join(p.get("keywords",[]) or []),
        p.get("pico_p","") or "",
        p.get("pico_i","") or "",
    ]).lower()
    
    # 제외 키워드
    for ex in EXCLUDE:
        if ex.lower() in text:
            return False
    
    # 관련 키워드
    for kw in RELEVANT:
        if kw.lower() in text:
            return True
    return False

relevant = [p for p in papers if is_relevant(p)]
excluded = [p for p in papers if not is_relevant(p)]

print(f"전체: {len(papers)}")
print(f"관련: {len(relevant)}")
print(f"제외: {len(excluded)}")

# 연구유형별 분포
cat_dist = {}
for p in relevant:
    cat = p.get("research_category") or "other"
    cat_dist[cat] = cat_dist.get(cat, 0) + 1
print("\n=== 연구유형 분포 (관련성 필터 후) ===")
for cat, n in sorted(cat_dist.items(), key=lambda x: -x[1]):
    print(f"  {cat}: {n}")

km = sum(1 for p in relevant if p.get("is_korean_medicine"))
human = sum(1 for p in relevant if p.get("is_human_study"))
print(f"\n한의학: {km}, 인체연구: {human}")

# 우선순위 정렬
PRIORITY = {"meta_analysis": 0, "systematic_review": 1, "guideline": 2, "clinical_trial": 3, "observational_study": 4, "case_report": 5, "review": 6, "experimental_study": 7, "other": 8}
relevant.sort(key=lambda p: (PRIORITY.get(p.get("research_category","other"), 9), p.get("pub_date","") or ""))

out = "ganyaung_relevant.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(relevant, f, ensure_ascii=False, indent=2)
print(f"\n저장: {out}")

# 제외된 논문 일부 확인
print("\n=== 제외된 논문 샘플 20 ===")
for p in excluded[:20]:
    print(f"  {p.get('research_category','')} | {(p.get('title','') or '')[:70]}")