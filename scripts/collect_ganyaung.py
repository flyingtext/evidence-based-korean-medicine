#!/usr/bin/env python3
"""간양상항 관련 논문 전수 수집 — 빠른 버전."""
import json, urllib.parse, urllib.request, sys, time

BASE = "https://med.symbolicinfo.com"

def fetch(params, retries=3):
    url = BASE + "/search?" + urllib.parse.urlencode(params)
    for i in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=15) as resp:
                return json.load(resp)
        except Exception as e:
            if i < retries - 1:
                time.sleep(1)
            else:
                return None

def fetch_all(q, base_params, per_page=100, max_pages=3):
    items = []
    seen = set()
    for page in range(1, max_pages+1):
        params = dict(base_params)
        params.update({"q": q, "per_page": per_page, "page": page})
        data = fetch(params)
        if not data:
            break
        batch = data.get("items", [])
        if not batch:
            break
        for it in batch:
            key = it.get("doi") or it.get("pmid") or it.get("url") or it.get("title")
            if key and key in seen:
                continue
            if key:
                seen.add(key)
            items.append(it)
        if page >= data.get("total_pages", page):
            break
    return items

QUERIES = [
    "간양상항",
    "천마구등음",
    "진간식풍탕",
    "Tianma Gouteng",
    "Zhen Gan Xi Feng",
    "liver yang",
    "간양화풍",
    "평간잠양",
    "간신음허",
    "hyperactivity liver yang",
    "간양 고혈압",
    "liver yang hypertension",
    "천마 고혈압",
    "Gastrodia hypertension",
    "구등 고혈압",
    "Uncaria hypertension",
    "현훈 간양",
    "vertigo liver",
    "편두통 간양",
    "migraine liver yang",
    "갱년기 간양",
    "이명 간양",
    "tinnitus liver",
]

all_items = {}

for q in QUERIES:
    for params in [{"analyzed": 1}, {"analyzed": 1, "km": 1}]:
        items = fetch_all(q, params)
        for it in items:
            key = it.get("doi") or it.get("pmid") or it.get("url") or it.get("title")
            if key:
                all_items[key] = it
        if items:
            print(f"  {q} [{list(params.values())[1] if len(params)>1 else 'all'}]: +{len(items)} -> 누적 {len(all_items)}건", flush=True)

print(f"\n=== 전체 병합 후: {len(all_items)}건 ===", flush=True)

cat_dist = {}
human_count = 0
km_count = 0
for it in all_items.values():
    cat = it.get("research_category") or "other"
    cat_dist[cat] = cat_dist.get(cat, 0) + 1
    if it.get("is_human_study"):
        human_count += 1
    if it.get("is_korean_medicine"):
        km_count += 1

print("\n=== 연구유형 분포 ===")
for cat, n in sorted(cat_dist.items(), key=lambda x: -x[1]):
    print(f"  {cat}: {n}")
print(f"\n인체연구: {human_count}, 한의학: {km_count}")

out = "/var/folders/wk/rr41_hvx11n61txygwhc3xvh0000gn/T/opencode/ganyaung_papers.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(list(all_items.values()), f, ensure_ascii=False, indent=2)
print(f"\n저장: {out}", flush=True)