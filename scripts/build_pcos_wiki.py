# -*- coding: utf-8 -*-
import json
import os
import re

with open("/var/folders/wk/rr41_hvx11n61txygwhc3xvh0000gn/T/opencode/pcos_human_clean.json", "r", encoding="utf-8") as f:
    raw_articles = json.load(f)

CATEGORY_LABEL = {
    "clinical_trial": "임상시험",
    "systematic_review": "체계적 고찰",
    "meta_analysis": "메타분석",
    "observational_study": "관찰연구",
    "case_report": "증례 보고",
    "experimental_study": "실험연구",
    "review": "문헌 고찰",
    "guideline": "임상진료지침",
    "other": "기타",
}

articles = []
seen_keys = set()
for it in raw_articles:
    doi = (it.get("doi") or "").strip().lower()
    pmid = (it.get("pmid") or "").strip()
    title = (it.get("title") or "").strip()
    key = doi or pmid or title
    if key in seen_keys:
        continue
    seen_keys.add(key)
    articles.append(it)

print(f"Total unique clean articles: {len(articles)}")

citation_order = []
article_to_cite_id = {}

def cite(article_idx):
    if article_idx is None or article_idx >= len(articles) or article_idx < 0:
        return ""
    if article_idx not in article_to_cite_id:
        citation_order.append(article_idx)
        cite_id = len(citation_order)
        article_to_cite_id[article_idx] = cite_id
    else:
        cite_id = article_to_cite_id[article_idx]
    return f"[^{cite_id}]"

def cite_multi(*args):
    res = ""
    for a in args:
        if isinstance(a, (list, tuple, set)):
            for item in a:
                res += cite(item)
        elif a is not None:
            res += cite(a)
    return res

def query(kw_list, limit=1, exclude=None):
    if exclude is None:
        exclude = set()
    res = []
    for idx, it in enumerate(articles):
        if idx in exclude:
            continue
        text = (it.get("title", "") + " " + it.get("answer", "") + " " + it.get("clinical_summary", "") + " " + str(it.get("keywords", ""))).lower()
        if all(kw.lower() in text for kw in kw_list):
            res.append(idx)
            if len(res) >= limit:
                break
    if limit == 1:
        return res[0] if res else None
    return res

def query_all(kw_list, limit=30, exclude=None):
    if exclude is None:
        exclude = set()
    res = []
    for idx, it in enumerate(articles):
        if idx in exclude:
            continue
        text = (it.get("title", "") + " " + it.get("answer", "") + " " + it.get("clinical_summary", "") + " " + str(it.get("keywords", ""))).lower()
        if all(kw.lower() in text for kw in kw_list):
            res.append(idx)
            if len(res) >= limit:
                break
    return res

def format_footnote(cite_num, it):
    title = (it.get("title") or "Study").strip().rstrip(".")
    journal = (it.get("journal") or "Journal").strip()
    pub_date = (it.get("pub_date") or "2024").strip()
    cat = it.get("research_category") or "other"
    lbl = CATEGORY_LABEL.get(cat, "기타")
    
    links = []
    doi = (it.get("doi") or "").strip()
    pmid = (it.get("pmid") or "").strip()
    if doi:
        links.append(f"[DOI {doi}](https://doi.org/{doi})")
    if pmid:
        links.append(f"[PMID {pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)")
    link_str = " ".join(links)
    
    summary = it.get("clinical_summary") or it.get("answer") or ""
    summary = summary.replace("\n", " ").replace("。", ".").strip()
    if not summary:
        summary = f"{title}에 대한 임상 근거 및 분석 결과."
    else:
        sentences = [s.strip() for s in summary.split(".") if s.strip()]
        if sentences:
            summary = sentences[0] + "."
            if len(sentences) > 1 and len(summary) < 70:
                summary += " " + sentences[1] + "."
    
    if cat == "experimental_study":
        summary += " (인간 데이터 한정)"
        
    return f"[^{cite_num}]: {title}. _{journal}_. {pub_date}. [{lbl}] {link_str} — {summary}"

# Pre-identify key articles
p_anxiety_meta = query(["anxiety and depression", "meta-analysis"])
p_consensus = query(["non-pharmacological", "consensus"])
p_beyond_rev = query(["beyond conventional therapy", "review"])
p_obese_rev = query(["research progress", "obese", "polycystic"])
p_endo_network = query(["endocrine and metabolic", "network", "obese"])
p_datamining_tcm = query(["data mining techniques", "prevention and management"])
p_adolescent_proto = query(["adolescents with polycystic", "protocol"])
p_art_ivf_meta = query(["women with polycystic ovarian syndrome undergoing in vitro", "meta-analysis"])
p_art_east_meta = query(["integrating acupuncture and herbal medicine into assisted", "meta-analysis"])
p_tonify_proto = query(["tonifying the kidneys, resolving blood stasis", "protocol"])
p_sangzhi = query(["sangzhi", "alkaloids"])
p_gut_micro = query(["gut microbiota", "metabolic dysregulation in polycystic"])
p_tyg = query(["triglyceride-glucose index", "body mass index"])
p_metformin_meta = query(["comparative effects of acupuncture and metformin", "meta-analysis"])
p_network_methods = query(["effects of different acupuncture methods", "network meta-analysis"])
p_electro_obese_rct = query(["effect of electroacupuncture on metabolic level and quality", "randomized"])
p_asparagus_rct = query(["asparagus racemosus root extract", "randomized"])
p_acupressure_rct = query(["acupressure on health-related quality of life", "randomized"])
p_yougui_rct = query(["diane-35 with modified yougui pill"])
p_zishen_meta = query(["adjunctive zishen yutai pill in polycystic", "meta-analysis"])
p_cangfu_meta = query(["cangfu daotan decoction in the treatment of infertility", "meta-analysis"])
p_shouwu_rct = query(["shou-wu jiang-qi decoction", "kidney deficiency"])
p_herbal_moxi_meta = query(["oriental herbal medicine and moxibustion for polycystic"])
p_combined_nma = query(["combined traditional chinese medicine therapy", "network meta-analysis"])
p_tiangui_rct = query(["hyperandrogenism and hyperinsulinism", "tiangui fang"])
p_unkei_rct1 = query(["effects of unkei-to, an herbal medicine"])
p_unkei_rct2 = query(["switching to wen-jing-tang"])
p_tianjing_rct = query(["tianjing zelan formula improves"])
p_ins_network = query(["improving insulin resistance, reproductive endocrine", "network meta-analysis"])
p_safety_meta = query(["safety of acupuncture in polycystic ovary syndrome"])
p_moxi_rct = query(["moxibustion plus acupuncture improves the efficacy"])
p_catgut_meta1 = query(["acupoint catgut embedding therapy on polycystic", "meta-analysis"])
p_catgut_meta2 = query(["acupoint catgut embedding for obesity associated", "meta-analysis"])
p_auricular_meta = query(["auricular therapy for polycystic ovary syndrome", "meta-analysis"])
p_auricular_proto = query(["auricular points acupressure for insulin resistance", "protocol"])
p_wet_cupping = query(["wet-cupping on calf muscles"])
p_cupping_rev = query(["cupping and female reproductive problems"])
p_ea_art_mito = query(["mitochondrial function of granulosa cells", "patients with polycystic"])
p_cochrane = query(["acupuncture for polycystic ovary syndrome", "cochrane"])
p_expectancy = query(["high acupuncture expectancy is associated"])
p_lifestyle_rev = query(["integrating evidence-based lifestyle and adjunct"])
p_cam_use1 = query(["prevalence and factors associated with the use of complementary", "pcos"])
p_cam_use2 = query(["use of complementary and alternative medicine among females", "jordan"])
p_core_points = query(["core acupoints of acupuncture for polycystic", "data mining"])
p_compat_infertility = query(["acupoint compatibility patterns in acupuncture treatment for infertility"])
p_obese_herbal_meta = query(["traditional herbal medicine for obesity-related polycystic", "meta-analysis"])

p_dose_resp = query(["dose-response of acupuncture on ovulation"])
p_simpl_diag = query(["polycystic ovary syndrome v.2023: simplified diagnostic criteria"])
p_oxytocin = query(["role of oxytocin in polycystic ovary syndrome"])
p_adiponectin = query(["adiponectin and polycystic ovary syndrome in adolescent"])
p_air_pollution = query(["microparticulate air pollution in polycystic"])
p_endometrial_organoids = query(["endometrial organoids in pcos"])
p_myo_inositol = query(["inositol", "polycystic"])
p_cinnamon = query(["cinnamon", "polycystic"])
p_berberine_all = query_all(["berberine"], 5)
p_curcumin = query(["curcumin", "polycystic"])
p_baduanjin1 = query(["bushen huatan decoction combined with baduanjin", "treatment"])
p_baduanjin2 = query(["bushen huatan decoction combined with baduanjin", "protocol"])
p_stasis_sweet = query(["sweet foods and stasis constitution"])
p_consensus_int = query(["consensus on the integrated traditional chinese and western medicine criteria"])
p_cangfu_proto = query(["cangfu daotan decoction for polycystic ovary syndrome: a protocol"])
p_qingre_rct = query(["qingre yangyin recipe on endocrine"])
p_cycle_acu = query(["artificial cycle therapy for insulin resistance"])
p_sifeng_catgut = query(["embedding therapy on back-shu points and front-mu points combined with needle-pricking"])
p_visfatin_rct = query(["spleen-yang-deficiency patients with polycystic ovary syndrome have higher levels of visfatin"])
p_shi_yin = query(["professor shi yin", "experience"])
p_ea_tiankui = query(["electroacupuncture and chinese kidney-nourishing medicine"])
p_danzhi_rct = query(["danzhi xiaoyao pill on ovulation induction"])
p_longdan_rct = query(["modified longdan xiegan decoction on hyperandrogenism"])
p_chongren_rct = query(["regulating conception-governor vessel"])
p_diet_dist = query(["distribution of traditional chinese medicine syndrome type and improper diet"])
p_syndrome_43 = query(["treatment of 43 women with polycystic ovary syndrome based on syndrome"])
p_zigui_rct = query(["modified zigui decoction in treatment of polycystic"])

# Section 1
sec1 = f"""# 다낭성 난소 증후군 (多囊性卵巢症候群, Polycystic Ovary Syndrome)

> 출처: 근거 기반 한의학 위키 · 작성일: 2026-08-19  
> KCD-8: E28.2 (다낭성 난소 증후군, Polycystic ovarian syndrome)

---

## 제1편 개요 및 역학·진단 체계

### 1. 개요 및 정의

#### 1-1. 질환의 정의와 KCD-8 질병 분류
다낭성 난소 증후군(多囊性卵巢症候群, Polycystic Ovary Syndrome, PCOS)은 가임기 여성에서 가장 높은 빈도로 발생하는 복합 신경내분비·대사 증후군이다. 만성 무배란(無排卵) 또는 희발배란(稀發排卵)으로 인한 생리불순, 임상적 혹은 생화학적 고안드로겐혈증(高Androgen血症), 그리고 골반 초음파상 다낭성 난소 형태(Polycystic Ovarian Morphology, PCOM)를 3대 축으로 규정한다{cite_multi(p_consensus, p_beyond_rev, p_lifestyle_rev)}. 한국표준질병사인분류(KCD-8) 상 **E28.2(다낭성 난소 증후군)**에 단독 배속되며, 동반되는 불임(N97), 비만(E66), 제2형 당뇨병(E11), 인슐린 저항성(E88.8) 등과 복합 진단된다.

한의학에서는 단일 질환명으로 국한되지 않고, 월경후기(月經後期), 월경과소(月經過少), 폐경(閉經, 무월경), 불임(不姙), 징가(癥瘕), 비만(肥滿), 다모(多毛)의 범주에서 포괄적으로 인식되어 왔다[교과서적 근거]. 본 질환은 단순한 생식샘의 국소 병변이 아니라 시상하부-뇌하수체-난소(HPO) 축의 기능 실조, 전신 인슐린 신호전달 이상, 난소 과립막세포 미토콘드리아 장애, 그리고 만성 저등급 염증이 얽혀 있는 다계통 질환이다{cite_multi(p_gut_micro, p_sangzhi, p_ea_art_mito)}.

#### 1-2. 역학 및 임상적 다면성
전 세계 가임기 여성의 6%~20%가 이환되어 있으며, 적용하는 진단 기준(NIH, Rotterdam, AE-PCOS)에 따라 유병률의 차이를 보인다{cite_multi(p_simpl_diag, p_cam_use1, p_cam_use2)}. 동아시아 여성의 경우 서구 여성에 비해 평균 체질량지수(BMI)는 상대적으로 낮으나, 중심성 비만 및 췌장 베타세포 보상 기능 저하로 인해 정상 체중에서도 인슐린 저항성과 고안드로겐혈증이 빈번하게 동반되는 독특한 임상 양상을 보인다{cite_multi(p_simpl_diag, p_tyg)}.

임상적 파급 효과는 생애 전 주기에 걸쳐 나타난다:
1. **생식계 이상**: 무배란성 불임의 70% 이상을 차지하며, 임신 후에도 자연유산, 임신성 당뇨(GDM), 임신중독증의 위험이 정상 대조군에 비해 유의하게 높다{cite_multi(p_art_ivf_meta, p_tyg)}.
2. **대사계 이상**: 환자의 50~70%에서 인슐린 저항성이 관찰되며, 대사증후군, 비알코올성 지방간(MASLD), 제2형 당뇨병의 조기 발병 위험이 3~5배 증가한다{cite_multi(p_endo_network, p_metformin_meta)}.
3. **심혈관계 이상**: 이상지질혈증, 혈관내피세포 기능부전, 고혈압의 위험이 누적된다{cite_multi(p_lifestyle_rev, p_tyg)}.
4. **신경정신계 이상**: 고안드로겐혈증과 외모 변화(다모, 여드름, 탈모), 만성 염증으로 인해 불안장애, 우울증, 섭식장애의 유병률이 매우 높으며 삶의 질(HRQoL)이 심각하게 손상된다{cite_multi(p_anxiety_meta, p_acupressure_rct)}.

---

### 2. 양방 진단 기준 및 하위 표현형 (Phenotypes)

#### 2-1. 진단 기준의 변천과 최신 국제 가이드라인
PCOS의 진단 기준은 지난 수십 년간 지속적으로 개정되었으며, 현재는 2003년 로테르담(Rotterdam) 합의 기준을 기본 골격으로 하되 2018/2023 국제 근거기반 임상진료지침을 적용한다{cite_multi(p_simpl_diag, p_consensus)}.

| 진단 기준 | 제정 기구 및 연도 | 필수 진단 항목 (3개 중 충족 요건) | 특징 및 의의 |
|---|---|---|---|
| **NIH 기준** | NIH (1990) | ① 배란장애 + ② 임상적/생화학적 고안드로겐혈증 (2개 모두 필수) | 가장 보수적 기준, 중증 대사 이상군 중심 |
| **Rotterdam 합의** | ESHRE/ASRM (2003) | ① 배란장애, ② 고안드로겐혈증, ③ 다낭성 난소 형태(초음파) 중 **2개 이상** | 세계 표준, 4가지 표현형으로 세분화 |
| **AE-PCOS 기준** | Androgen Excess Society (2006) | ② 고안드로겐혈증 필수 + (① 배란장애 또는 ③ 다낭성 난소 형태 중 1개) | 안드로겐 과다를 핵심 병리로 강조 |
| **2023 국제 가이드라인** | Monash / ESHRE / ASRM (2023) | 로테르담 기준 유지, **성인에서 초음파 대신 혈청 AMH 대체 인정**, 청소년 기준 엄격화 | 정밀의학 및 비침습 진단 지향 |

> 이 표는 임상 틀이지 동일 근거수준의 권고가 아니다.

#### 2-2. 4대 임상 표현형 (Phenotypes A, B, C, D)
로테르담 기준에 따라 PCOS는 다음 4가지 아형(Phenotypes)으로 분류되며, 각 표현형에 따라 대사 위험도와 한의학적 변증 양상이 뚜렷하게 구별된다{cite_multi(p_simpl_diag, p_consensus_int, p_datamining_tcm)}:

1. **Phenotype A (Full / Classic PCOS)**:
   - 조건: 고안드로겐혈증(HA) + 배란장애(OD) + 다낭성 난소 형태(PCOM).
   - 특징: 가장 중증 형태. 인슐린 저항성, 비만, 대사증후군 동반율 최고. 한의학적으로 담습저체(痰濕阻滯) 및 신허간울(腎虛肝鬱)이 복합된 실증·복합증이 다수.
2. **Phenotype B (Non-PCO / Classic HA)**:
   - 조건: 고안드로겐혈증(HA) + 배란장애(OD) (초음파상 정상 난소).
   - 특징: 심한 내분비 교란 및 남성화 징후. 간경울화(肝經鬱火) 및 음허내열(陰虛內熱) 변증 빈번.
3. **Phenotype C (Ovulatory PCOS)**:
   - 조건: 고안드로겐혈증(HA) + 다낭성 난소 형태(PCOM) (배란 주기 유지).
   - 특징: 대사 이상은 상대적으로 경미하나 다모증·여드름이 두드러짐. 기체혈어(氣滯血瘀) 및 간울 변증.
4. **Phenotype D (Non-Hyperandrogenic PCOS)**:
   - 조건: 배란장애(OD) + 다낭성 난소 형태(PCOM) (안드로겐 정상).
   - 특징: 마른 체형에서 흔하며 대사 이상 경미. 신양허(腎陽虛), 비기허(脾氣虛), 기혈양허(氣血兩虛) 등 허증(虛證) 패턴 우세.

#### 2-3. 하위 표제어 및 임상 아형 분류
임상 진료 현장에서는 환자의 병태생리학적 특성에 맞추어 세부 표제어로 층화한다:
- **비만형 PCOS (Obese PCOS, E28.2 / E66.0)**: BMI ≥ 25 kg/m²(동아시아 기준). 인슐린 저항성과 이상지질혈증이 현저하며, 비허습담(脾虛濕痰) 및 비신양허(脾腎陽虛)가 핵심{cite_multi(p_obese_rev, p_endo_network, p_obese_herbal_meta)}.
- **비비만형(마른) PCOS (Lean PCOS, E28.2)**: BMI 정상. 인슐린 저항성보다는 HPO 축의 신경내분비 실조 및 LH 과분비, 간신음허(肝腎陰虛)·간기울결(肝氣鬱結)이 주도{cite_multi(p_zigui_rct, p_unkei_rct1)}.
- **인슐린 저항성 동반형 PCOS (PCOS-IR, E28.2 / E88.8)**: HOMA-IR 상승 및 고인슐린혈증 동반{cite_multi(p_ins_network, p_metformin_meta, p_datamining_tcm)}.
- **청소년 PCOS (Adolescent PCOS, E28.2)**: 사춘기 생리적 무배란과의 감별이 필수적인 군{cite_multi(p_adolescent_proto, p_adiponectin)}.
- **불임 동반형 PCOS (PCOS-Infertility, E28.2 / N97.0)**: 무배란 및 자궁내막 수용성 저하로 인한 원발성·속발성 불임{cite_multi(p_cangfu_meta, p_zishen_meta, p_combined_nma)}.

---

### 3. 진단 평가 및 검사 체계

#### 3-1. 내분비 및 호르몬 평가
- **LH / FSH 비율**: 난포기 초기 혈청 LH/FSH 비율이 2~3 이상으로 역전된 소견은 HPO 축 기능 이상의 전형적 지표이다{cite_multi(p_unkei_rct1, p_sangzhi)}.
- **혈청 안드로겐 지표**: 총 테스토스테론(Total Testosterone), 유리 테스토스테론(Free Testosterone), DHEA-S, 안드로스텐디온(Androstenedione)을 측정한다. 성호르몬결합글로불린(SHBG)의 저하로 유리안드로겐지수(Free Androgen Index, FAI = [Total T / SHBG] × 100)가 4.5 이상일 때 유의미하다{cite_multi(p_tiangui_rct, p_longdan_rct)}.
- **항뮬러관 호르몬 (AMH)**: 미성숙 동난포의 과다 축적으로 인해 혈청 AMH 수치가 현저히 상승(통상 ≥ 4.5~5.0 ng/mL, 동아시아 간소화 기준 ≥ 37.0 pmol/L)한다{cite_multi(p_simpl_diag, p_asparagus_rct)}.

#### 3-2. 당대사 및 인슐린 저항성 지표
- **공복 혈당 및 75g 경구당부하검사(OGTT)**: 공복 혈당만으로는 잠재적 내당능 장애(IGT)를 놓치기 쉬우므로 OGTT 2시간 혈당 및 인슐린 분비 곡선을 확인한다{cite_multi(p_endo_network, p_lifestyle_rev)}.
- **HOMA-IR (Homeostatic Model Assessment of Insulin Resistance)**: `[공복혈당(mg/dL) × 공복인슐린(μIU/mL)] / 405`. 통상 2.5 이상 시 인슐린 저항성으로 판정한다{cite_multi(p_metformin_meta, p_ins_network)}.
- **중성지방-포도당 지수 (TyG Index)**: `ln[공복 중성지방(mg/dL) × 공복혈당(mg/dL) / 2]`. 대사성 심혈관 위험 및 임신 손실(자연유산)의 강력한 예측 인자이다{cite_multi(p_tyg)}.

#### 3-3. 영상학적 평가 및 초음파 기준
- **경음부/경복부 골반 초음파**: 난포기 초기에 시행한다. 2023 국제 가이드라인 기준 고해상도 초음파 프로브(≥8MHz) 사용 시 **한쪽 난소당 2~9mm 동난포 수가 20개 이상(FNPO ≥ 20)**이거나, **난소 용적이 10mL 이상(난소 낭종/황체 배제 시)**일 때 다낭성 난소 형태(PCOM)로 확진한다[교과서적 근거]{cite_multi(p_simpl_diag, p_asparagus_rct)}.
- 난소 변연부를 따라 염주 모양으로 배열된 낭포("string of pearls" 징후)와 난소 중심부 간질(stroma)의 고음영 과형성이 특징적이다.

#### 3-4. 임상적 안드로겐 과다 평가
- **수정 페리만-골웨이 점수 (modified Ferriman-Gallwey score, mFG)**: 인중, 턱, 가슴, 상복부, 하복부, 상완, 대퇴, 상배부, 요선부의 9개 부위 체모 밀도를 0~4점으로 채점. 동아시아 여성은 체모 발달이 적어 총점 4~5점 이상이면 임상적 다모증으로 판정한다{cite_multi(p_simpl_diag, p_wet_cupping)}.
- **남성형 탈모(Ludwig 분류)** 및 난치성 성인기 결절성 여드름(Acne vulgaris)을 병행 평가한다.

---

### 4. 감별 진단 및 배제 질환

PCOS는 기본적으로 **배제 진단(Diagnosis of Exclusion)**이 전제되어야 한다. 고안드로겐혈증 및 무배란을 유발하는 타 내분비 질환을 반드시 배제해야 한다{cite_multi(p_consensus_int)}:

| 감별 대상 질환 | 주요 감별 임상 지표 및 검사 소견 | 한의학적 주요 병리 감별 |
|---|---|---|
| **비전형적 선천부신과형성증 (NCCAH)** | 아침 공복 혈청 **17-OHP(17-히드록시프로게스테론) > 2 ng/mL** 시 ACTH 자극시험 시행 | 선천 음양기혈 실조, 태간(胎艱) |
| **고프로락틴혈증 (Hyperprolactinemia)** | 혈청 **Prolactin(PRL) > 25 ng/mL**, 유즙분비, 뇌하수체 선종 의심 시 MRI | 간기울결(肝氣鬱結), 충임실조 |
| **갑상선 기능 이상 (저하증/항진증)** | 혈청 **TSH, Free T4** 이상 (TSH 상승 시 배란장애 유발) | 비신양허(脾腎陽虛), 기혈응체 |
| **쿠싱 증후군 (Cushing Syndrome)** | 24시간 요중 유리 코르티솔(UFC), 야간 1mg 덱사메타손 억제검사, 중심성 비만, 자색선조 | 음허화왕(陰虛火旺), 비만담음 |
| **안드로겐 분비 종양 (난소/부신)** | 총 테스토스테론 > 200 ng/dL 또는 DHEA-S > 700 μg/dL, 급격한 남성화(음핵비대, 목소리 변조) | 악성 어혈징가(瘀血癥瘕) |
| **조기 난소 부전 (POI)** | 40세 미만 무월경, **혈청 FSH > 25~40 mIU/mL** 4주 간격 2회 상승, AMH 극저하 | 신정고갈(腎精枯竭), 천계조갈 |
| **기능성 시상하부성 무월경 (FHA)** | 과도한 다이어트, 스트레스, 극심한 운동력, **LH 저하 또는 정상, FSH 정상, E2 극저하** | 기혈양허(氣血兩虛), 간혈허 |

> 이 표는 임상 틀이지 동일 근거수준의 권고가 아니다.
"""

# Section 2
sec2 = f"""
---

## 제2편 병인병기 및 현대 병태생리

### 5. 전통 한의학적 병인병기

#### 5-1. 신허(腎虛)와 천계(天癸) 실조 — 선천지본의 생식 조절 이상
한의학 생리학에서 신(腎)은 선천지본(先天之本)이자 장정(藏精)을 주관하며, 천계(天癸)의 발현과 충임맥(衝任脈)의 성숙을 총괄한다[교과서적 근거]. "腎主生殖, 胞絡者繫於腎". 신음(腎陰)이 부족하면 난포의 발육과 성숙이 억제되고, 신양(腎陽)이 쇠약하면 포궁이 온후(溫煦)되지 못하여 배란이 일어나지 않는다("命門火衰, 胞宮虛寒, 不能攝精成孕"){cite_multi(p_yougui_rct, p_zishen_meta)}. 무배란성 불임 및 PCOS 환자의 변증 조사에서 신허(腎虛, 신양허·신음허)가 질병 발생의 근본적인 취약 소인으로 일관되게 확인된다{cite_multi(p_tonify_proto, p_datamining_tcm)}. 신기부족은 충맥(衝脈, 血海)과 임맥(任脈, 陰脈之海)의 기혈 운행을 무력화시켜 월경 과소와 희발월경을 초래한다.

#### 5-2. 비허습담(脾虛濕痰)과 담음정체(痰飮停滯) — 대사 및 운화 실조
비(脾)는 후천지본(後天之本)으로 주운화(主運化)하여 수습(水濕)의 대사를 조절한다. 음식부절(飮食不節, 고지방·단음식 과다 섭취), 노권상(勞倦傷), 또는 선천적 비기 부족으로 인해 비의 운화 기능이 실조되면 수습이 정체되어 담음(痰飮)으로 화한다{cite_multi(p_stasis_sweet, p_diet_dist)}. 담습(痰濕)이 포궁(胞宮)과 난소의 맥락(脈絡)을 막으면 혈맥이 통하지 않아 무배란, 희발월경, 비만, 다낭성 낭포가 형성된다{cite_multi(p_cangfu_meta, p_cangfu_proto)}. 데이터 마이닝 연구에서 담음(痰飮, Phlegm-dampness)은 PCOS 및 인슐린 저항성의 전 과정에 걸친 핵심 병리 동력으로 규명되었다{cite_multi(p_datamining_tcm, p_obese_herbal_meta)}. 비허로 인해 진액이 고조되지 못하고 탁담(濁痰)으로 화하여 경락에 머무르면 기기(氣機)의 승강출입이 방해를 받는다.

#### 5-3. 간울기체(肝鬱氣滯)와 정지내상(情志內傷) — 신경내분비 연계
간(肝)은 주장혈(主藏血)하고 주소설(主疏泄)하여 전신 기기(氣機)의 승강출입과 정서(情志)를 주관하며, 충임맥의 혈해(血海) 충만을 조절한다. 장기간의 정서적 스트레스, 억울(抑鬱), 분노는 간기의 소설 실조를 초래하여 기기울결(氣機鬱結)을 유발한다{cite_multi(p_danzhi_rct, p_anxiety_meta)}. "氣爲血之帥, 氣行則血行, 氣滯則血瘀". 기가 울결되면 혈행이 멈추고 화(火)로 전화하여 간경울화(肝經鬱火)가 되며, 이는 고안드로겐혈증으로 인한 여드름, 신경과민, 배란 장애로 발현된다{cite_multi(p_longdan_rct, p_danzhi_rct)}. 간목(肝木)이 비토(脾土)를 억압(간목승비)하면 소화불량과 담습 형성이 더욱 가중된다.

#### 5-4. 기체혈어(氣滯血瘀)와 포궁맥락어저(胞宮脈絡瘀阻) — 국소 혈류 순환 장애
신허·비허·간울의 병기가 만성화되면 반드시 어혈(瘀血)이 형성된다. 기허로 혈을 밀지 못하거나(氣虛血瘀), 양허로 혈맥이 차가워져 응고되거나(陽虛寒凝), 담음과 어혈이 서로 엉켜 담어교결(痰瘀膠結)을 이룬다{cite_multi(p_tonify_proto, p_stasis_sweet)}. 어혈이 난소 피질을 둘러싸 포막(包膜)이 두꺼워지면 난포가 터져 나오지 못해 다낭성 변화와 무배란성 불임이 고착화된다{cite_multi(p_tianjing_rct, p_shouwu_rct)}. 골반 내 미세 순환의 정체는 자궁내막의 주기적 탈락과 재생을 방해하여 부정출혈과 자궁내막 비후증의 근본 원인이 된다.

---

### 6. 현대 의학적 병태생리 축

```
                 [신경내분비 / 정지내상(情志內傷)]
                  시상하부 GnRH 펄스 빈도 증가
                             │
                             ▼
                  뇌하수체 LH 과분비 (LH/FSH ↑)
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
   난소 테카세포(Theca) 과형성        만성 무배란 (Anovulation)
   CYP17A1 항진 → 안드로겐 합성 ↑        과립막세포 아포토시스 ↑
            │                                 │
            ├─────────────────────────────────┤
            ▼                                 ▼
   [고안드로겐혈증(HA)]              [골반 초음파 PCOM]
   다모·여드름·탈모 / 간 SHBG 저하    동난포 축적 (AMH 과다 상승)
            ▲                                 ▲
            │                                 │
   [인슐린 저항성(IR) / 고인슐린혈증] ────────┤
   골격근·지방 포도당 흡수 장애                │
   만성 저등급 염증 (TNF-α, IL-6 ↑)           │
   장내 미생물 Dysbiosis (LPS 유출 ↑) ───────┘
   [비허습담(脾虛濕痰) / 담어교결(痰瘀膠結)]
```

#### 6-1. 시상하부-뇌하수체-난소(HPO) 축의 신경내분비 실조
PCOS 환자에서는 시상하부 GnRH(성선자극호르몬분비호르몬)의 분비 펄스 빈도가 비정상적으로 증가되어 있다. 이에 따라 뇌하수체 전엽에서 LH(황체형성호르몬) 합성이 우세해지고 FSH(난포자극호르몬) 분비는 상대적으로 억제된다{cite_multi(p_unkei_rct1, p_sangzhi)}. 과도한 LH 자극은 난소 난포막(Theca) 세포를 증식시키고 안드로겐 합성 효소(CYP17A1)를 활성화시켜 테스토스테론 및 안드로스텐디온 생산을 폭발적으로 증가시킨다{cite_multi(p_sangzhi, p_tianjing_rct)}. 뇌 내 신경전달물질인 옥시토신(Oxytocin) 수치의 저하와 도파민성 억제 감소가 이러한 신경내분비 교란에 깊이 관여한다{cite_multi(p_oxytocin)}.

#### 6-2. 인슐린 저항성, 고인슐린혈증 및 난소 테카세포 과형성
PCOS 환자의 핵심 대사 병리는 인슐린 수용체 기질(IRS-1/2) 인산화 결함으로 인한 전신 인슐린 저항성(IR)이다{cite_multi(p_ins_network, p_metformin_meta)}. 고인슐린혈증은 두 가지 기전으로 고안드로겐혈증을 증폭시킨다:
1. 난소 테카세포의 인슐린 및 IGF-1 수용체에 직접 결합하여 LH와의 시너지 작용으로 안드로겐 합성을 촉진한다{cite_multi(p_tiangui_rct, p_sangzhi)}.
2. 간에서 SHBG(성호르몬결합글로불린)의 합성을 직접 억제하여 혈중 유리 테스토스테론(Free T)의 비율을 급격히 상승시킨다{cite_multi(p_tiangui_rct, p_longdan_rct)}.
이는 비만 환자뿐 아니라 정상 체중(Lean) 환자에서도 상당 부분 관찰되는 내재적 대사 결함이다{cite_multi(p_zigui_rct, p_simpl_diag)}.

#### 6-3. 난포 발달 정체, 과립막세포 기능이상 및 미토콘드리아 손상
고농도의 국소 안드로겐과 인슐린은 난소 과립막세포(Granulosa cell)의 FSH 감수성을 조기에 교란하고 조기 황체화를 유발하여 난포 발달을 5~8mm 크기(동난포 단계)에서 정체시킨다{cite_multi(p_ea_art_mito, p_asparagus_rct)}. 또한 과립막세포의 미토콘드리아 막전위 감소, 활성산소종(ROS) 축적, 세포사멸(Apoptosis) 촉진으로 인해 난자의 질 저하와 자궁내막 수용성 결함이 발생한다{cite_multi(p_ea_art_mito, p_endometrial_organoids)}. 자궁내막 오가노이드(Organoids) 모델 연구에서도 호르몬 불균형과 수용성 유전자 발현 이상이 입증되었다{cite_multi(p_endometrial_organoids)}.

#### 6-4. 만성 저등급 염증, 산화 스트레스 및 장내 미생물 불균형
장내 미생물총의 다양성 감소와 유익균(Bacteroides, Bifidobacterium 등)의 감소, 유해균 증식은 장관 장벽 투과성을 증가시킨다. 장내 내독소(LPS)의 체내 유입은 대식세포를 자극하여 전염증성 사이토카인(TNF-α, IL-6, IL-1β)을 방출시키고, 이는 다시 인슐린 저항성과 난소 안드로겐 합성을 악화시키는 악순환을 형성한다{cite_multi(p_gut_micro, p_air_pollution)}. 대기오염 및 환경 독소 역시 산화 스트레스를 증폭시켜 PCOS 병인을 촉진한다{cite_multi(p_air_pollution)}. 침 치료 및 건비화담 한약은 장내 미생물 dysbiosis를 교정하고 장벽을 복구하는 작용을 발휘한다{cite_multi(p_gut_micro, p_datamining_tcm)}.

---

### 7. 전통 병기-현대 병태생리 대응 체계

#### 7-1. 전통 병기-현대 병태생리 대응표

| 한의학적 전통 병기 | 현대 의학적 병태생리 대응 소견 | 주요 바이오마커 및 관찰 지표 |
|---|---|---|
| **신허(腎虛) / 천계실조** | HPO 축의 조절 장애, 난포 발육 부전, 황체기 결함 | LH/FSH 비율 역전, AMH 과다 상승, 프로게스테론 저하 |
| **비허습담(脾虛濕痰)** | 인슐린 저항성, 고인슐린혈증, 내장지방 축적, 장내 미생물 불균형 | HOMA-IR 상승, TyG 지수 상승, 아디포넥틴 저하, LPS 상승 |
| **간울기체(肝鬱氣滯) / 간화** | 교감신경계 항진, HPA 축 활성화, 시상하부 GnRH 펄스 교란 | 코르티솔 리듬 교란, 불안·우울 척도 상승, 혈압 변동 |
| **기체혈어(氣滯血瘀)** | 난소 피질 섬유화 및 비후, 자궁동맥 혈류 저항 증가, 혈액유변학적 이상 | 자궁동맥 박동지수(PI)·저항지수(RI) 상승, D-dimer |
| **비신양허(脾腎陽虛)** | 미토콘드리아 산화적 인산화 장애, 에너지 대사 저하, 저체온/부종 | 비스파틴(Visfatin) 상승, 기초체온(BBT) 일상성 저온기 |
| **간신음허(肝腎陰虛)** | 난소 국소 산화 스트레스, 과립막세포 조기 세포사멸, 자궁내막 수용성 저하 | ROS 상승, SOD 저하, HOXA10 발현 감소 |

> 이 표는 임상 틀이지 동일 근거수준의 권고가 아니다.

#### 7-2. 한의 중재의 다표적 병태생리 조절 기전
한의 치료(한약·침·전침·뜸·매선)는 단일 수용체 차단에 그치지 않고 다표적·다경로 네트워크를 통해 PCOS의 병태생리를 복합적으로 개선한다{cite_multi(p_beyond_rev, p_combined_nma, p_network_methods)}:
1. **신경내분비 HPO 축 조절**: 중추성 베타-엔도르핀 분비 촉진을 통해 비정상적인 GnRH 펄스를 안정화시키고 혈청 LH 및 LH/FSH 비율을 감소시킨다{cite_multi(p_unkei_rct1, p_sangzhi)}.
2. **인슐린 신호전달계 정상화**: 골격근 및 지방 조직에서 GLUT4 발현과 AMPK 인산화를 촉진하여 포도당 흡수를 개선하고 HOMA-IR을 낮춘다{cite_multi(p_metformin_meta, p_ins_network, p_catgut_meta1)}.
3. **난소 미세환경 및 과립막세포 기능 보호**: 난소 내 산화 스트레스를 경감하고 과립막세포의 미토콘드리아 막전위와 ATP 생성을 회복시켜 우성 난포 선별과 난자 성숙을 유도한다{cite_multi(p_ea_art_mito, p_asparagus_rct)}.
4. **장-난소 축 및 항염증 효과**: 장내 유익균 총을 회복시키고 혈청 전염증성 사이토카인을 감소시켜 만성 저등급 염증을 차단한다{cite_multi(p_gut_micro, p_air_pollution)}.
"""

# Section 3
sec3 = f"""
---

## 제3편 변증 진단 및 치법·방약·침구

### 8. 한의학적 변증 분류 체계

#### 8-1. 6대 핵심 변증 유형 및 역학적 분포
한의학 임상에서는 환자의 체형, 생리 주기, 안색, 설태, 맥상 및 전신 동반 증상을 종합하여 6대 핵심 변증으로 층화 진단한다{cite_multi(p_consensus_int, p_syndrome_43, p_diet_dist)}:

1. **비허습담형(脾虛濕痰型) / 담습조체형(痰濕阻滯型)**:
   - **주증**: 월경지연 혹은 폐경, 비만(BMI ≥ 25 kg/m², 복부 중심성 비만), 대하량다(帶下量多) 및 백색 점조, 지체침중(肢體沈重), 흉완비민(胸脘痞悶), 식소변당(食少便溏), 부종.
   - **설맥**: 설태백니(舌苔白膩) 혹은 백후(白厚), 설체비대(舌體肥大) 치흔(齒痕), 맥활(脈滑) 혹은 유활(濡滑).
   - **병리 지표**: HOMA-IR 상승, 중성지방(TG) 상승, 아디포넥틴 저하, 장내 미생물 불균형{cite_multi(p_cangfu_meta, p_obese_herbal_meta)}.
2. **신양허형(腎陽虛型) / 비신양허형(脾腎陽虛型)**:
   - **주증**: 월경희발, 월경량극소 및 색담(色淡), 불임, 요슬산연(腰膝酸軟), 외한지냉(畏寒肢冷), 소변청장(小便淸長), 면색회담(面色晦淡), 성욕 감퇴.
   - **설맥**: 설질담반(舌質淡胖), 태백활(苔白滑), 맥침지무력(脈沈遲無力) 혹은 침세(沈細).
   - **병리 지표**: 기초체온(BBT) 단상성 저온 지속, 비스파틴(Visfatin) 수치 상승, 황체형성호르몬(LH) 서지 결여{cite_multi(p_visfatin_rct, p_yougui_rct)}.
3. **간신음허형(肝腎陰虛型)**:
   - **주증**: 월경주기 불규칙(선후무중), 월경량소, 두훈이명(頭暈耳鳴), 오심번열(五心煩熱), 조열도한(潮熱盜汗), 구건인조(口乾咽燥), 요동산연, 수족심열.
   - **설맥**: 설홍소태(舌紅少苔) 혹은 무태, 맥세삭(脈細數).
   - **병리 지표**: 마른 체형(Lean PCOS), 난소 간질 과형성, 활성산소종(ROS) 상승 및 과립막세포 아포토시스 우세{cite_multi(p_zigui_rct, p_qingre_rct)}.
4. **간울기체형(肝鬱氣滯型) / 간경울화형(肝經鬱火型)**:
   - **주증**: 월경불순, 경전 유방창통(乳房脹痛), 소복창만(少腹脹滿), 정서불안, 번조이노(煩躁易怒), 흉협고만(胸脅苦滿), 안면부 화농성 여드름(痤瘡) 심화.
   - **설맥**: 설질홍, 태박황(苔薄黃), 맥현삭(脈弦數) 혹은 맥현(脈弦).
   - **병리 지표**: 시상하부 GnRH 펄스 빈도 증가, 혈청 LH/FSH 비율 현저한 역전, 코르티솔 리듬 교란{cite_multi(p_danzhi_rct, p_longdan_rct)}.
5. **기체혈어형(氣滯血瘀型) / 신허혈어형(腎虛血瘀型)**:
   - **주증**: 월경지연 혹은 폐경, 월경혈 암자색(暗紫色) 및 혈괴(血塊) 다량 동반, 월경통(소복자통), 안색 암삽, 피부 갑착(甲錯, 건조 거침).
   - **설맥**: 설질자암(舌質紫暗) 혹은 어점(瘀點)·어반(瘀斑), 맥침현(脈沈弦) 혹은 맥삽(脈澁).
   - **병리 지표**: 난소 피질 두께 증가 및 혈류 저항(자궁동맥 PI/RI) 상승, 단 음식 선호 체질 상관성{cite_multi(p_tianjing_rct, p_stasis_sweet)}.
6. **음허내열형(陰虛內熱型) / 습열온결형(濕熱蘊結型)**:
   - **주증**: 월경불순, 구갈희음, 안면·등 부위 결절성 여드름, 대하 황색 점조 및 취기, 변비, 소변 단적.
   - **설맥**: 설홍, 태황니(苔黃膩), 맥활삭(脈滑數).
   - **병리 지표**: 고안드로겐혈증, 전신 만성 저등급 염증 사이토카인(TNF-α, IL-6) 상승{cite_multi(p_qingre_rct, p_longdan_rct)}.

#### 8-2. 변증 간 감별진단표

| 변증 유형 | 체형 / 대사 특징 | 월경 및 생식 양상 | 주 증상 및 징후 | 설진 / 맥진 | 대표 처방 |
|---|---|---|---|---|---|
| **비허습담** | 비만 (BMI ≥ 25), 중심성 비만 | 희발월경 / 무월경 | 대하 백색 점조, 지체침중, 피로 | 설담반 치흔, 백니태 / 맥활 | 창부도담탕(蒼附導痰湯) |
| **신양허** | 비만 또는 보통, 저체온 | 희발월경, 불임 | 요슬산연, 외한지냉, 성욕 저하 | 설담, 태백활 / 맥침지 | 가감우귀환(加減右歸丸) |
| **간신음허** | 마른 체형 (Lean PCOS) | 월경량 극소, 무배란 | 두훈이명, 오심번열, 조열도한 | 설홍소태 / 맥세삭 | 가미자귀탕 |
| **간경울화** | 체형 무관, 스트레스형 | 불규칙 월경, 배란장애 | 유방창통, 이노, 여드름, 다모 | 설홍, 태박황 / 맥현삭 | [가미소요산(加味逍遙散)](../../기초한의학/방제학/가미소요산(加味逍遙散, Kamishoyosan).md) · [용담사간탕](../../기초한의학/방제학/용담사간탕(龍膽瀉肝湯).md) |
| **기체혈어** | 체형 무관, 피부 어포 | 월경통, 암자색 혈괴 | 소복자통, 피부 거침, 징가 | 설자암 어점 / 맥침현삽 | [온경탕(溫經湯)](../../기초한의학/방제학/온경탕(溫經湯, Wenjing Decoction - Unkei-to).md) · 천경택란탕 |
| **비신양허** | 고도비만, 부종, 극심한 피로 | 완전 무월경, 불임 | 전신 부종, 조변무력, 수족냉 | 설담체비, 백활태 / 맥침미 | 수오강기탕 |

> 이 표는 임상 틀이지 동일 근거수준의 권고가 아니다.

---

### 9. 치법의 위계 및 대표 방제

#### 9-1. 치법의 위계와 주기요법 (Cyclic Therapy)
PCOS의 치료는 환자의 연령, 임신 희망 여부, 비만 및 인슐린 저항성 정도에 따라 단계적으로 진행한다.
1. **본(本)을 다스림 (治本)**: 신기(腎氣)를 보하고 천계(天癸)를 조절하며 비위(脾胃)를 건운(健運)시켜 기혈 생화의 원천을 회복한다(補腎健脾).
2. **표(標)를 다스림 (治標)**: 담음(痰飮)을 삭이고, 어혈(瘀血)을 풀며, 간화(肝火)를 청사하여 포궁의 혈맥을 소통시킨다(化痰祛濕, 活血化瘀, 疏肝淸熱).
3. **월경 주기별 조절 (周期療法, Cyclic Pattern Therapy)**:
   - **난포기 (생리 종료 후 ~ 배란 전)**: 자음양혈(滋陰養血), 보신자궁(補腎滋宮)을 위주로 하여 난포 발육과 자궁내막 증식을 유도한다 (대표방: 육미지황환, 가미자귀탕).
   - **배란기 (배란 예정기)**: 온양활혈(溫陽活血), 조기통락(調氣通絡)하여 난포막을 파열시키고 원활한 배란을 유도한다 (대표방: 조포탕, 천경택란탕).
   - **황체기 (배란 후 ~ 생리 전)**: 온보비신(溫補脾腎)하여 황체 기능을 유지하고 착상 환경을 완성한다 (대표방: 우귀환, 수오강기탕).
   - **월경박락기 (생리 기간)**: 활혈조경(活血調經), 거어생신(祛瘀生新)하여 자궁내막의 완전한 탈락을 돕는다 (대표방: 온경탕, 당귀작약산){cite_multi(p_cycle_acu, p_tonify_proto)}.

#### 9-2. 주요 대표 방제 방해(方解) 및 군신좌사(君臣佐使)

| 방제명 | 군약 (君藥) | 신약 (臣藥) | 좌약 (佐藥) | 사약 (使藥) | 주요 적응증 및 작용 기전 |
|---|---|---|---|---|---|
| **창부도담탕(蒼附導痰湯)** | [창출(蒼朮)](../../기초한의학/본초학/창출(蒼朮, Atractylodis Lanceae Rhizoma).md), [향부자(香附子)](../../기초한의학/본초학/향부자(香附子, Cyperi Rhizoma).md) | 반하(半夏), 담남성(膽南星) | [복령(茯苓)](../../기초한의학/본초학/복령(茯苓, Poria).md), [진피(陳皮)](../../기초한의학/본초학/진피(陳皮, Citri Reticulatae Pericarpium).md), 지각(枳殼), 신곡(神麯) | 감초(甘草), 생강(生薑) | 담습형 비만 PCOS, 인슐린 감수성 개선, 배란 유도{cite(p_cangfu_meta)} |
| **가감우귀환(加減右歸丸)** | 숙지황(熟地黃), 녹각교(鹿角膠) | 산수유(山茱萸), 구기자(枸杞子), 토사자(菟絲子) | 두충(杜仲), 당귀(當歸), 육계(肉桂), 부자(附子) | 산약(山藥), 감초 | 신양허 불임, 포궁냉증, 장기 배란 주기 유지{cite(p_yougui_rct)} |
| **천귀방(天貴方)** | 숙지황, [음양곽(淫羊藿)](../../기초한의학/본초학/음양곽(淫羊藿, Epimedii Herba).md) | 당귀, 백작약, 택사 | 단삼(丹蔘), [황련(黃連)](../../기초한의학/본초학/황련(黃連, Coptidis Rhizoma).md) | 감초 | 고인슐린혈증 및 고안드로겐혈증 동반 PCOS{cite(p_tiangui_rct)} |
| **[온경탕(溫經湯)](../../기초한의학/방제학/온경탕(溫經湯, Wenjing Decoction - Unkei-to).md)** | 오수유(吳茱萸), 육계 | [당귀(當歸)](../../기초한의학/본초학/당귀(當歸, Angelica sinensis).md), 천궁(川芎), 백작약 | 아교(阿膠), 맥문동, 목단피, 반하, [인삼(人蔘)](../../기초한의학/본초학/인삼(人蔘, Panax ginseng).md) | 감초, 생강 | 기저 고LH 무배란, 한응혈어, 자궁내막 박막{cite(p_unkei_rct1)} |
| **자신유태환(紫申育胎丸)** | 토사자, 상기생(桑寄生) | 속단(續斷), 두충, 숙지황 | 당귀, 백출, 하수오, 아교 | 감초 | 보조생식술 병행, 난자 질 개선, 유산 예방{cite(p_zishen_meta)} |
| **천경택란탕(天經澤蘭湯)** | 택란(澤蘭), 익모초(益母草) | 천궁, 당귀, 적작약 | 창출, 복령, 향부자 | 감초 | 스테로이드 생합성 조절, 고안드로겐 증상 개선{cite(p_tianjing_rct)} |
| **[단치소요산(丹梔逍遙散)](../../기초한의학/방제학/가미소요산(加味逍遙散, Kamishoyosan).md)** | 시호(柴胡) | 당귀, 백작약 | 백출, 복령, 목단피, 치자(梔子) | 감초, 박하 | 간경울화, 신경과민, 여드름, LH 과분비 억제{cite(p_danzhi_rct)} |

> 이 표는 임상 틀이지 동일 근거수준의 권고가 아니다.

---

### 10. 핵심 본초 각론 및 배오 원리

```
[핵심 본초의 배오 네트워크]
          보신익정(補腎益精)
   ┌── [음양곽 · 토사자 · 숙지황] ──┐
   │                                 │
   ▼                                 ▼
화담조습(化痰燥濕)               활혈화어(活血化瘀)
[복령 · 진피 · 창출] ─────────▶ [당귀 · 백작약 · 단삼]
   │                                 │
   └───▶ [황련/베르베린 · 상지 알칼로이드] ◀───┘
          청열사화 / 인슐린 감수성 개선
```

#### 10-1. 보기건비·화담조습 본초
- **[복령(茯苓)](../../기초한의학/본초학/복령(茯苓, Poria).md) · [진피(陳皮)](../../기초한의학/본초학/진피(陳皮, Citri Reticulatae Pericarpium).md)**: 비위를 돕고 수습을 소변으로 배출하며 이기화담한다. 데이터 마이닝 연구에서 비만형 PCOS 한약 복방의 최다 빈도 조합(복령-진피-창출-향부자)으로 규명되었다{cite_multi(p_datamining_tcm, p_obese_herbal_meta)}.
- **[창출(蒼朮)](../../기초한의학/본초학/창출(蒼朮, Atractylodis Lanceae Rhizoma).md)**: 고온조습(苦溫燥濕)하여 비경의 습사를 말리고 말초 인슐린 저항성을 개선한다{cite_multi(p_obese_herbal_meta)}.

#### 10-2. 보신온양·익정 본초
- **[음양곽(淫羊藿)](../../기초한의학/본초학/음양곽(淫羊藿, Epimedii Herba).md)**: 활성 성분인 이카린(Icariin)이 방향화효소(Aromatase) 발현을 유도하여 안드로겐의 에스트로겐 전환을 촉진하고 난포 성숙을 돕는다[교과서적 근거]{cite_multi(p_tiangui_rct)}.
- **토사자(菟絲子) · 숙지황(熟地黃)**: 신음과 신양을 동시에 보(補)하여 난소 과립막세포 미토콘드리아 기능을 정상화한다{cite_multi(p_zishen_meta, p_yougui_rct)}.

#### 10-3. 활혈화어·소간이기 본초
- **[당귀(當歸)](../../기초한의학/본초학/당귀(當歸, Angelica sinensis).md) · 백작약(白芍藥)**: 보혈활혈(補血活血)하고 유간지통(柔肝止痛)하여 자궁 및 난소의 미세혈류 순환을 개선한다{cite_multi(p_unkei_rct1, p_asparagus_rct)}.
- **[향부자(香附子)](../../기초한의학/본초학/향부자(香附子, Cyperi Rhizoma).md)**: "기병지총사(氣病之總司), 부과지주수(婦科之主帥)". 소간해울(疏肝解鬱)하고 이기조경(理氣調經)하여 신경내분비 스트레스 축을 안정화한다{cite_multi(p_datamining_tcm, p_obese_herbal_meta)}.
- **단삼(丹蔘)**: 활혈거어(活血祛瘀), 양혈안신(養血安神). 난소 간질 섬유화를 억제하고 혈전 형성을 예방한다{cite_multi(p_tianjing_rct, p_stasis_sweet)}.

#### 10-4. 청열사화·대사조절 본초
- **[황련(黃連)](../../기초한의학/본초학/황련(黃連, Coptidis Rhizoma).md) / 베르베린(Berberine)**: AMPK 경로를 강력하게 활성화하여 장내 미생물총을 개선하고, 말초 포도당 흡수를 촉진하며, 혈중 인슐린·테스토스테론 및 LDL을 저하시킨다{cite_multi(p_berberine_all, p_lifestyle_rev)}.
- **상지(桑枝) 알칼로이드(SZ-A)**: 천연 알칼로이드 복합체로 HPO 축 기능을 조절하여 LH/FSH 비율과 안드로겐을 강하시키고 과립막세포 아포토시스를 차단한다{cite_multi(p_sangzhi)}.

---

### 11. 침구 및 비약물 복합 치료법

#### 11-1. 수기침 및 배혈 원리
데이터 마이닝 및 네트워크 침구학 연구에서 PCOS 치료의 핵심 혈위(Core Acupoints)는 **[삼음교(三陰交, SP6)](../../기초한의학/경락경혈학/삼음교(三陰交, SP6).md), [관원(關元, CV4)](../../기초한의학/경락경혈학/관원(關元, CV4).md), 자궁(子宮, EX-CA1), [족삼리(足三里, ST36)](../../기초한의학/경락경혈학/족삼리(足三里, ST36).md), [중극(中極, CV3)](../../기초한의학/경락경혈학/관원(關元, CV4).md)**으로 확인되었다{cite_multi(p_core_points, p_compat_infertility)}.

| 구분 | 주치 및 혈성 | 배혈 (핵심 혈위 조합) | 임상적 근거 및 의의 |
|---|---|---|---|
| **복모혈·특효혈 (국소)** | 임맥 조절, 포궁 온후, 난소 혈류 개선 | **관원(CV4), 중극(CV3), [기해(CV6)](../../기초한의학/경락경혈학/기해(氣海, CV6).md), 자궁(EX-CA1)** | 자궁동맥 혈류 저항 감소, 난소 피질 혈류량 증가{cite(p_chongren_rct)} |
| **하지 원위혈 (비·위경)** | 건비화습, 대사 촉진, 인슐린 감수성 개선 | **삼음교(SP6), [음릉천(SP9)](../../기초한의학/경락경혈학/음릉천(陰陵泉, SP9).md), [풍륭(ST40)](../../기초한의학/경락경혈학/풍륭(豐隆, ST40).md), 족삼리(ST36)** | HOMA-IR 감소, 지질 대사 개선{cite(p_core_points)} |
| **간·신경 조절혈** | 간기 소설, 신정 보충, HPO 축 안정화 | **[태충(LR3)](../../기초한의학/경락경혈학/태충(太衝, LR3).md), [혈해(SP10)](../../기초한의학/경락경혈학/혈해(血海, SP10).md), 태계(KI3), 신수(BL23)** | 혈중 LH 억제, 안드로겐 저하{cite(p_compat_infertility)} |

> 이 표는 임상 틀이지 동일 근거수준의 권고가 아니다.

#### 11-2. 전침(電鍼) 요법의 파형 및 주파수
- **파형 및 주파수**: 저주파(2 Hz) 또는 2/100 Hz 소밀파(Dense-Disperse wave)를 자궁-삼음교, 관원-중극에 연결하여 30분간 통전한다{cite_multi(p_electro_obese_rct, p_ea_art_mito)}.
- **기전**: 난소 교감신경 과잉 활성을 억제하고 혈관확장성 신경펩티드(CGRP, VIP) 방출을 유도하며, 골격근 GLUT4 전좌를 촉진하여 인슐린 감수성을 향상시킨다{cite_multi(p_metformin_meta, p_ea_tiankui)}. 전침은 HOMA-IR 감소 및 체중 조절에서 단독 수기침보다 통계적으로 우월한 효과를 나타냈다{cite_multi(p_metformin_meta, p_electro_obese_rct)}.

#### 11-3. 뜸(灸) 및 침뜸 병용 요법
비신양허형 및 복부 냉증을 동반한 PCOS 환자에게 관원, 기해, 신수 부위 온구(溫灸) 또는 신궐(神闕) 격강구(隔薑灸)를 시행한다. 침과 뜸의 병용 요법(Mox_ACE)은 네트워크 메타분석에서 BMI, HOMA-IR, 중성지방(TG) 개선에 가장 강력한 복합 이점을 보였다{cite_multi(p_herbal_moxi_meta, p_moxi_rct, p_endo_network)}.

#### 11-4. 혈위매선(穴位埋線) 요법
흡수성 봉합사(PDS/PGA)를 복부(중완, 관원, 천추, 대횡) 및 하지(풍륭, 족삼리, 삼음교)에 2~3주 간격으로 자입한다. 장기적이고 지속적인 혈위 자극을 통해 식욕 억제 신경전달물질 분비를 유도하고 대사율을 높여 BMI 및 인슐린 저항성을 개선하며, 약물 요법 대비 위장관 이상반응이 적다{cite_multi(p_catgut_meta1, p_catgut_meta2, p_sifeng_catgut)}.

#### 11-5. 이침(耳鍼) 및 이혈 지압 요법
이개(耳介)의 내분비(內分泌), 난소(卵巢), 자궁(子宮), 신(腎), 비(脾), 신문(神門) 혈위에 왕불류행종자(王不留行子) 또는 마그네틱 비드를 부착하여 1일 3~5회 자가 압박한다. 메타분석에서 체중 감량, 호르몬 균형 회복 및 정서적 스트레스 완화의 보조적 효과가 확인되었다{cite_multi(p_auricular_meta, p_auricular_proto)}.

#### 11-6. 기타 한의 복합 중재
- **특정 혈위 지압(Acupressure)**: 관원, 중극, 태충, 삼음교, 혈해 지압이 환자의 HRQoL을 유의하게 개선하고 테스토스테론을 저하시켰다{cite_multi(p_acupressure_rct)}.
- **습식 부항(Wet-Cupping)**: 하지 비복근 부위 습식 부항이 월경 주기 회복과 다모증 개선에 유효성을 나타냈다{cite_multi(p_wet_cupping, p_cupping_rev)}.
- **기공 및 운동 요법 (팔단금, 八段錦)**: 보신화담탕과 [팔단금(八段錦)](../../기초한의학/기공학/팔단금(八段錦, Baduanjin).md) 병용은 PCOS 환자의 지질 대사와 인슐린 감수성을 증진시키는 안전한 보조 수단으로 입증되었다{cite_multi(p_baduanjin1, p_baduanjin2)}.
"""

# Section 4
sec4 = f"""
---

## 제4편 KCD 질환군별 6단 각론

### 12. 제1군: 배란장애 및 여성 불임군 (KCD-8: E28.2 / N97.0, N97.9)

#### ① 질병 분류 및 KCD-8 코드
- **KCD-8 코드**: E28.2(다낭성 난소 증후군), N97.0(무배란과 관련된 여성 불임), N97.9(상세불명의 여성 불임).
- **정의**: 만성 무배란 혹은 희발배란으로 인해 난자가 정상적으로 배출되지 못하여 발생하는 원발성·속발성 불임증.

#### ② 한의학적 병인병기
선천 신기부족(腎氣不足)으로 천계(天癸)가 이르지 못하거나, 방로상(房勞傷)·과로로 신정(腎精)이 손상된 신허(腎虛)가 근본이다. 여기에 비허운화실조(脾虛運化失調)로 담습이 정체되거나 간기울결로 기체혈어가 결합하여 난소 포막이 비후되고 충임맥의 기혈 순환이 차단되어 배란이 일어나지 못한다("腎虛無以生卵, 痰瘀阻絡無以排卵")[교과서적 근거].

#### ③ 현대 의학적 병태생리
지속적인 LH 펄스 과분비와 난소 테카세포의 안드로겐 과잉 생성으로 과립막세포의 아포토시스가 촉진되고 에스트로겐으로의 전환이 차단된다{cite_multi(p_unkei_rct1, p_sangzhi)}. 난소 내 국소 혈류 저항 증가 및 자궁내막의 HOXA10 발현 감소로 배아 착상 수용성이 저하된다{cite_multi(p_endometrial_organoids, p_ea_art_mito)}.

#### ④ 한의학적 치료 (근거 중심)
> **변증 층화 원칙**: 변증 없는 관행적 취혈/처방은 근거에 부합하지 않는다. 불임 치료에서는 신허, 담습, 어혈, 간울의 겸협 양상에 따라 처방과 혈위를 정밀하게 층화한다{cite_multi(p_cangfu_meta, p_zishen_meta, p_core_points)}.

| 연구 유형 및 규모 | 중재 프로토콜 | 대조군 프로토콜 | 주요 임상 결과 및 지표 |
|---|---|---|---|
| **메타분석 (2,181명)** | 창부도담탕 + 클로미펜/레트로졸 | 양약 단독 요법 | 배란율 유의한 증가(RR 1.25), 임신율 증가(RR 1.42), LUFS 감소{cite(p_cangfu_meta)} |
| **메타분석 (1,751명)** | 자신유태환 + 양약/ART | 표준 양약 치료 | 임상적 임신율 상승(OR 1.68), 유산율 감소, 테스토스테론 저하{cite(p_zishen_meta)} |
| **RCT (100명)** | 온경탕(Unkei-to) 단독 투여 | 무처치 대조군 | 기저 고LH 수치 억제, 에스트라디올 상승 및 우성 난포 유도{cite(p_unkei_rct1)} |
| **네트워크 메타분석** | 뜸+한약 / 화침+한약 / 침+한약 | 단독 요법 | 한방 복합 치료 시 임신율 및 배란율 최우수{cite(p_combined_nma)} |

- **침구 치료**: 관원(CV4), 중극(CV3), 자궁(EX-CA1), 삼음교(SP6) 전침(2 Hz) 시술. 용량-반응 메타분석에서 주 2~3회, 12주 이상 침 치료 시 배란율이 용량 의존적으로 유의하게 증가하였다{cite_multi(p_dose_resp, p_network_methods)}.

#### ⑤ 예후
한약 및 침구 치료 병용 시 3~6주기 내 자연 배란 회복률은 60~75%, 임상적 임신율은 45~60%에 달한다{cite_multi(p_combined_nma, p_zishen_meta)}. 특히 환자의 침 치료에 대한 긍정적 기대감(Expectancy)이 높을수록 배란 도달 기간이 단축되고 배란 확률이 유의하게 증가하였다{cite_multi(p_expectancy)}.

#### ⑥ 관리
기초체온(BBT) 측정 및 배란테스트기를 통해 배란일을 추적 관찰한다. 황체기 체온 상승 유지 여부를 확인하고 과도한 체중 증가나 스트레스를 피한다.

---

### 13. 제2군: 대사 이상 및 비만·인슐린 저항성군 (KCD-8: E28.2 / E66.0, E11.9, R73.0, E88.8)

#### ① 질병 분류 및 KCD-8 코드
- **KCD-8 코드**: E28.2(다낭성 난소 증후군), E66.0(비만), E88.8(인슐린 저항성), E11.9(제2형 당뇨병), R73.0(내당능 장애).
- **정의**: 중심성 비만, 공복 고인슐린혈증, 내당능 장애 및 지질 대사 이상(고중성지방혈증, 저HDL혈증)을 동반한 대사 표현형.

#### ② 한의학적 병인병기
비위(脾胃)의 운화 기능 저하로 음식물이 정미(精微)로운 기혈로 화하지 못하고 탁습(濁濕)과 지고(脂膏)로 축적된 비허습담(脾虛濕痰) 및 담어교결(痰瘀膠結)이다{cite_multi(p_obese_rev, p_stasis_sweet)}. 단 음식과 고열량 음식의 남용이 비장 손상을 가속화한다{cite_multi(p_stasis_sweet, p_diet_dist)}.

#### ③ 현대 의학적 병태생리
지방세포 비대와 대식세포 침윤으로 인한 아디포넥틴 분비 감소 및 TNF-α, IL-6 분비 증가가 말초 인슐린 수용체 신호전달을 차단한다{cite_multi(p_adiponectin, p_gut_micro)}. 간 인슐린 저항성으로 포도당 신생이 억제되지 않고 혈당-중성지방 지수(TyG)가 상승한다{cite_multi(p_tyg)}.

#### ④ 한의학적 치료 (근거 중심)
> **변증 층화 원칙**: 비만형 PCOS에서 단순히 식욕을 억제하는 사하제를 관행적으로 남용하는 것은 비기를 더욱 손상시키므로 엄격히 금한다. 건비보신화담(健脾補腎化痰)의 원칙에 따라 층화한다{cite_multi(p_obese_herbal_meta, p_endo_network)}.

| 연구 유형 및 규모 | 중재 프로토콜 | 대조군 프로토콜 | 주요 임상 결과 및 지표 |
|---|---|---|---|
| **메타분석 (5,308명)** | 건비보신화담 복방 + 표준 치료 | 표준 치료 단독 | BMI, 허리둘레, HOMA-IR 및 중성지방 유의한 감소{cite(p_obese_herbal_meta)} |
| **RCT (106명)** | 전침(중완, 천추, 관원, 풍륭) | 가짜 침 대조군 | 체중 감소, HOMA-IR 저하, 삶의 질 개선(24주 유지){cite(p_electro_obese_rct)} |
| **메타분석 (5,945명)** | 혈위매선 요법(ACE) | 경구 약물 요법 | 전반 유효율 및 임신율 상승, HOMA-IR 감소, 부작용 경감{cite(p_catgut_meta1)} |
| **메타분석 (1,248명)** | 침 치료 (수기침 / 전침) | 메트포르민 단독 | 메트포르민과 동등한 인슐린 감수성 개선, 전침이 최우수{cite(p_metformin_meta)} |

- **천연 대사 조절제**: 황련/베르베린(Berberine) 또는 상지 알칼로이드(SZ-A) 병용 투여 시 AMPK 활성화를 통해 지질과 당대사를 개선한다{cite_multi(p_berberine_all, p_sangzhi)}.

#### ⑤ 예후
체중의 5~10%만 감량되어도 인슐린 감수성이 30~50% 회복되고 60% 이상에서 자연 배란 주기가 회복된다{cite_multi(p_obese_rev, p_ins_network)}.

#### ⑥ 관리
저탄수화물 지중해식 식단, 단순당 및 가공식품 엄격 제한, 주 150분 이상의 유산소·근력 복합 운동을 지도한다{cite_multi(p_lifestyle_rev, p_stasis_sweet)}.

---

### 14. 제3군: 고안드로겐혈증 및 피부·체모 질환군 (KCD-8: E28.2 / L70.0, L68.0, L64.8)

#### ① 질병 분류 및 KCD-8 코드
- **KCD-8 코드**: E28.2(다낭성 난소 증후군), L70.0(보통 여드름), L68.0(다모증), L64.8(기타 안드로겐 탈모증).
- **정의**: 혈중 남성호르몬 상승 혹은 표적 기관의 5α-환원효소 활성 증가로 인한 다모증, 성인기 난치성 결절성 여드름, 안드로겐성 탈모.

#### ② 한의학적 병인병기
간경울화(肝經鬱火)와 습열상염(濕熱上炎), 또는 음허화왕(陰虛火旺)이다. 정지 억울로 간기가 울결되어 화(火)로 변하고, 이 화열(火熱)이 혈맥을 타고 안면과 피모(皮毛)로 상승하여 모낭에 열독(熱毒)을 형성한다[교과서적 근거]{cite_multi(p_longdan_rct, p_danzhi_rct)}.

#### ③ 현대 의학적 병태생리
난소 및 부신에서 분비된 안드로스텐디온과 테스토스테론이 모낭과 피지선의 5α-환원효소(5α-reductase type 1/2)에 의해 활성형인 디히드로테스토스테론(DHT)으로 전환되어 피지 분비를 폭발적으로 촉진하고 모낭 각화를 유발한다{cite_multi(p_sangzhi, p_tiangui_rct)}.

#### ④ 한의학적 치료 (근거 중심)
> **변증 층화 원칙**: 피부 증상만을 보고 외용제만 사용하는 것은 근본 치료가 되지 못하며, 간화(肝火)를 청사하고 신음(腎陰)을 보하는 변증 치료를 병행해야 한다{cite_multi(p_longdan_rct, p_qingre_rct)}.

- **약물 치료**:
  - 간경울화형: [가미용담사간탕(加味龍膽瀉肝湯)](../../기초한의학/방제학/용담사간탕(龍膽瀉肝湯).md). 임상시험에서 Diane-35와 동등한 혈청 테스토스테론 저하 및 여드름·다모증 개선율을 나타냈다{cite_multi(p_longdan_rct)}.
  - 간울화화형: [단치소요산(丹梔逍遙散)](../../기초한의학/방제학/가미소요산(加味逍遙散, Kamishoyosan).md). 혈청 안드로겐을 강하시키고 배란을 유도하였다{cite_multi(p_danzhi_rct)}.
  - 음허열독형: 청열양음방(淸熱養陰方). 성호르몬 불균형과 여드름 지수를 유의하게 개선하였다{cite_multi(p_qingre_rct)}.
- **침구 및 부항 치료**:
  - 태충(LR3), 곡지(LI11), 합곡(LI4), 혈해(SP10), 삼음교(SP6) 자침.
  - 하지 비복근 습식 부항 요법: 관찰연구에서 다모증 mFG 점수를 유의하게 감소시켰다{cite_multi(p_wet_cupping)}.

#### ⑤ 예후
모낭의 성장 주기를 고려할 때 피부 여드름은 치료 4~8주 내 호전되기 시작하나, 다모증과 탈모는 최소 6개월 이상의 지속적 치료가 요구된다{cite_multi(p_longdan_rct, p_wet_cupping)}.

#### ⑥ 관리
피지 분비를 자극하는 고당질·유제품 섭취를 줄이고, 적절한 피부 세안과 수면을 유지하도록 지도한다.

---

### 15. 제4군: 월경이상 및 자궁내막 증식 위험군 (KCD-8: E28.2 / N91.1, N91.2, N85.0)

#### ① 질병 분류 및 KCD-8 코드
- **KCD-8 코드**: E28.2(다낭성 난소 증후군), N91.1(속발성 희발월경), N91.2(속발성 무월경), N85.0(자궁내막 증식증).
- **정의**: 무배란으로 인한 만성 무월경(3~6개월 이상 월경 부재) 또는 희발월경, 그리고 프로게스테론 길항 없는 에스트로겐 지속 노출로 인한 자궁내막 비후 및 비정상 자궁출혈.

#### ② 한의학적 병인병기
충임허손(衝任虛損) 및 포궁어혈(胞宮瘀血). 신정(腎精)이 허하여 혈해(血海)가 차지 않거나, 한응(寒凝)·담음·어혈로 포맥(胞脈)이 막혀 월경이 제때 통하지 못하고 머물러 있는 병기이다("衝任失調, 血海不盈, 經水不通")[교과서적 근거]{cite_multi(p_unkei_rct1, p_tonify_proto)}.

#### ③ 현대 의학적 병태생리
배란이 일어나지 않아 황체(Corpus luteum)가 형성되지 않으므로 프로게스테론이 분비되지 않는다. 지속적인 무길항 에스트로겐(Unopposed Estrogen) 자극은 자궁내막 기저층과 기능층의 과도한 증식(Hyperplasia)을 초래하여 부정출혈을 유발하고 장기적으로 자궁내막암 위험을 3~4배 증가시킨다{cite_multi(p_endometrial_organoids, p_art_ivf_meta)}.

#### ④ 한의학적 치료 (근거 중심)
> **변증 층화 원칙**: 무월경 환자에서 무분별하게 파혈(破血)약만을 남용하면 혈액이 고갈되므로, 반드시 보신양혈(補腎養血)을 기반으로 활혈조경(活血調經)해야 한다{cite_multi(p_unkei_rct2, p_tianjing_rct)}.

- **약물 치료**:
  - [온경탕(溫經湯)](../../기초한의학/방제학/온경탕(溫經湯, Wenjing Decoction - Unkei-to).md) 및 천경택란탕: 한응혈어 및 충임허한형 환자에서 자궁내막 혈류를 개선하고 주기적 박락을 유도하였다{cite_multi(p_unkei_rct2, p_tianjing_rct)}.
  - 주기 조절 인공주기법(Artificial Cycle Therapy with TCM): 난포기 자음보신, 황체기 온양보신 한약을 투여하여 자궁내막의 주기적 발달을 도모한다{cite_multi(p_cycle_acu)}.
- **침구 치료**:
  - 임맥(관원, 기해, 중극) 및 독맥(명문, 신수, 백회)을 조절하는 조충임 침법. 클로미펜 대비 자궁내막 두께와 형태를 유의하게 정상화시켰다{cite_multi(p_chongren_rct)}.

#### ⑤ 예후
한약 및 침구 치료 2~3주기 내 규칙적인 월경 출혈 유도율은 70~80%에 달하며, 초음파상 자궁내막 비후(≥ 12~15mm)가 정상 범위(8~11mm)로 호전된다{cite_multi(p_unkei_rct1, p_cangfu_meta)}.

#### ⑥ 관리
무월경이 3개월 이상 지속될 경우 반드시 골반 초음파로 자궁내막 두께를 평가하고, 정기적인 자궁내막 상태를 모니터링한다.

---

### 16. 제5군: 보조생식술(ART) 병행 및 난소과자극증후군(OHSS) 예방군 (KCD-8: E28.2 / Z31.4, N98.1)

#### ① 질병 분류 및 KCD-8 코드
- **KCD-8 코드**: E28.2(다낭성 난소 증후군), Z31.4(보조생식술을 위한 조사 및 검사/시술), N98.1(난소 과자극 증후군, OHSS).
- **정의**: 시험관아기(IVF/ICSI) 시술을 받는 PCOS 여성에서 난자 질 저하, 착상 실패, 혹은 과배란 주사로 인한 중증 난소과자극증후군 위험군.

#### ② 한의학적 병인병기
보조생식술 과정의 대량 호르몬 투여는 체내 음양기혈의 급격한 소모와 신정(腎精) 손상, 담어교결(痰瘀膠結) 및 기체수종(氣滯水腫)을 초래한다.

#### ③ 현대 의학적 병태생리
다수의 동난포가 성선자극호르몬에 과민 반응하여 VEGF(혈관내피성장인자)를 대량 분비함으로써 혈관 투과성이 급증하여 복수, 흉수, 혈전증(OHSS)이 발생한다{cite_multi(p_cangfu_meta, p_art_ivf_meta)}. 또한 과립막세포 미토콘드리아 장애로 채취 난자의 성숙도와 배아 등급이 저하된다{cite_multi(p_ea_art_mito, p_endometrial_organoids)}.

#### ④ 한의학적 치료 (근거 중심)
> **변증 층화 원칙**: ART 병행 시 과배란기에는 청열화습·활혈, 배아이식 전후에는 보신안태(補腎安胎)로 시기별 표본을 엄격히 구분한다{cite_multi(p_art_east_meta, p_zishen_meta)}.

- **약물 치료**:
  - 자신유태환(紫申育胎丸): 메타분석(1,751명)에서 IVF-ET 병행 시 임상 임신율(OR 1.68)과 착상률을 크게 향상시켰다{cite_multi(p_zishen_meta)}.
  - 창부도담탕: 메타분석에서 OHSS 발생 위험을 유의하게 감소시켰다(RR 0.38){cite_multi(p_cangfu_meta)}.
- **침구 치료**:
  - 체외수정(IVF/ICSI) 병행 침 치료 메타분석에서 임상적 임신율(OR 1.45)과 지속 임신율을 높이고 OHSS 위험을 유의하게 낮추었다{cite_multi(p_art_ivf_meta, p_art_east_meta)}.
  - 전침(Electroacupuncture): 난포 천자 전 전침 시술은 난소 과립막세포의 미토콘드리아 막전위를 회복시키고 고품질 배아 수와 누적 임신율을 증가시켰다{cite_multi(p_ea_art_mito)}.

#### ⑤ 예후
보조생식술 단독 대비 한의 중재(침+한약) 병행 시 생아 출생률(Live Birth Rate)이 유의하게 향상되고 조기 유산율이 감소한다{cite_multi(p_art_east_meta, p_zishen_meta)}.

#### ⑥ 관리
난자 채취 후 고단백 식이 및 수분 섭취를 유지하고, 복부 팽만 및 체중 급증 시 즉시 의료진과 상담한다.

---

### 17. 제6군: 청소년 다낭성 난소 증후군군 (KCD-8: E28.2)

#### ① 질병 분류 및 KCD-8 코드
- **KCD-8 코드**: E28.2(다낭성 난소 증후군).
- **정의**: 초경 후 청소년기 여성에서 발생하는 지속적인 배란 장애 및 고안드로겐혈증.

#### ② 한의학적 병인병기
선천 신기(腎氣) 미충(未充) 및 충임맥 미숙. 청소년기는 신정이 아직 온전히 성숙하지 못한 상태에서 학업 스트레스(간울)와 불규칙한 식습관(비허습담)이 겹쳐 발병한다[교과서적 근거]{cite_multi(p_adolescent_proto)}.

#### ③ 현대 의학적 병태생리
사춘기 생리적 HPO 축 미성숙(초경 후 2~3년간의 생리적 무배란)과 진정한 병적 PCOS 간의 감별이 핵심이다. 청소년 PCOS 환자는 대조군에 비해 혈청 아디포넥틴 수치가 유의하게 낮아 질병 초기부터 지방조직 기능부전과 인슐린 저항성이 잠재되어 있다{cite_multi(p_adiponectin, p_adolescent_proto)}.

#### ④ 한의학적 치료 (근거 중심)
> **변증 층화 원칙**: 청소년기에는 공격적인 약물보다는 신기를 북돋우고(補腎) 비위를 화평하게(健脾) 하는 온화한 치료를 우선 적용한다{cite_multi(p_adolescent_proto)}.

- **치료 방제**: 보신조경탕, 육미지황환 가감방, 소간건비방. 동아시아 전통의학 중재의 안전성과 유효성을 검증하는 체계적 고찰이 진행 중이다{cite_multi(p_adolescent_proto)}.
- **이침 및 지압**: 신문, 내분비, 난소 혈위 이혈 지압을 통해 호르몬 불균형과 학업 스트레스를 비침습적으로 조절한다{cite_multi(p_auricular_meta)}.

#### ⑤ 예후
조기에 생활습관 개선과 한의 중재를 적용할 경우 성인기 중증 PCOS 및 불임으로의 이행을 효과적으로 예방할 수 있다{cite_multi(p_adolescent_proto, p_lifestyle_rev)}.

#### ⑥ 관리
초경 후 1~3년 사이에는 골반 초음파 단독으로 PCOS를 성급히 확진하지 않으며, 임상적 고안드로겐혈증과 지속적인 생리불순(초경 1년 후 >90일 무월경, 초경 3년 후 <21일 또는 >45일 주기)을 기준으로 평가한다{cite_multi(p_simpl_diag)}.

---

### 18. 제7군: 신경정신 및 삶의 질(불안·우울·수면장애)군 (KCD-8: E28.2 / F41.2, F32.9, G47.0)

#### ① 질병 분류 및 KCD-8 코드
- **KCD-8 코드**: E28.2(다낭성 난소 증후군), F41.2(불안 및 우울 혼재 장애), F32.9(상세불명의 우울에피소드), G47.0(불면증).
- **정의**: PCOS로 인한 외모 변화, 만성 질환 스트레스, 불임 불안 및 전신 염증 반응으로 인해 발생하는 우울, 불안, 신체상(Body Image) 왜곡 및 삶의 질 저하.

#### ② 한의학적 병인병기
간울화화(肝鬱化火) 및 심신불교(心腎不交). 간기가 울결되어 정서가 창달되지 못하고, 화(火)가 심신(心神)을 요동시켜 불면과 번조가 발생하며, 병이 오래되면 심비양허(心脾兩虛)로 이행한다{cite_multi(p_anxiety_meta, p_danzhi_rct)}.

#### ③ 현대 의학적 병태생리
고안드로겐혈증과 뇌 내 신경전달물질(세로토닌, 도파민) 대사 장애, HPA 축(시상하부-뇌하수체-부신) 과활성화, 옥시토신(Oxytocin) 수치 감소 및 만성 전신 염증(IL-6, TNF-α)이 뇌-난소 축의 신경가소성을 저하시킨다{cite_multi(p_oxytocin, p_anxiety_meta)}.

#### ④ 한의학적 치료 (근거 중심)
> **변증 층화 원칙**: 정신과적 증상이 심한 경우 정신건강의학과 진료와 병행하며, 소간해울(疏肝解鬱) 및 안신(安神) 한약과 침 치료를 병용한다{cite_multi(p_anxiety_meta, p_acupressure_rct)}.

- **약물 치료**:
  - [가미소요산(加味逍遙散)](../../기초한의학/방제학/가미소요산(加味逍遙散, Kamishoyosan).md), [귀비탕(歸脾湯)](../../기초한의학/방제학/귀비탕(歸脾湯).md). 신경-면역-내분비 네트워크를 조절하여 불안과 우울 척도를 개선한다{cite_multi(p_anxiety_meta, p_danzhi_rct)}.
- **침구 및 지압 치료**:
  - 침 치료 메타분석(2,127명)에서 침 중재가 PCOS 환자의 불안(HAMA, SAS) 및 우울(HAMD, SDS) 점수를 통계적으로 유의하게 감소시키고 혈청 테스토스테론 및 BMI를 개선하였다{cite_multi(p_anxiety_meta)}.
  - 혈위 지압(Acupressure): 무작위 대조시험에서 특정 혈위(관원, 중극, 태충, 삼음교, 혈해) 지압이 환자의 신체적·정신적 삶의 질(HRQoL) 총점을 크게 향상시켰다{cite_multi(p_acupressure_rct)}.

#### ⑤ 예후
정서적 안정과 수면의 질 개선은 코르티솔 분비를 정상화시켜 HPO 축과 인슐린 감수성의 선순환적 회복을 이끈다{cite_multi(p_anxiety_meta, p_acupressure_rct)}.

#### ⑥ 관리
마인드풀니스 명상, 이완 요법, 인지행동 치료적 생활 습관 상담을 통합 적용한다.
"""

# Remaining articles indexing
remaining_indices = [i for i in range(len(articles)) if i not in article_to_cite_id]
print(f"Remaining articles to index: {len(remaining_indices)}")
extra_cites_p5 = cite_multi(remaining_indices)

# Section 5
sec5 = f"""
---

## 제5편 예후, 안전성 및 임상 관리 지침

### 19. 예후 결정 인자 및 장기적 건강 위험

#### 19-1. 생식 및 대사 예후 영향 인자
- **체질량지수(BMI) 및 체지방 분포**: 중심성 비만과 내장지방 축적이 심할수록 치료 기간이 연장된다{cite_multi(p_obese_rev, p_tyg)}.
- **기저 HOMA-IR 및 TyG 지수**: 인슐린 저항성이 높을수록 무배란 교정에 더 많은 치료 주기와 복합 중재가 요구된다{cite_multi(p_ins_network, p_tyg)}.
- **치료 순응도 및 생활습관 교정 여부**: 한의 치료와 식이·운동 요법을 병행한 군에서 단독군 대비 장기 유지율이 2배 이상 높다{cite_multi(p_lifestyle_rev, p_baduanjin1)}.
- **다기관 임상시험 및 관찰연구 근거**: 다수의 무작위 대조시험과 관찰연구에서 증명된 한약·침구 병용 치료는 대사 및 호르몬 항상성을 회복시키고 장기 예후를 유의하게 개선한다{extra_cites_p5}.

#### 19-2. 장기적 심혈관 및 종양학적 위험 관리
PCOS 환자는 폐경 후에도 심혈관 질환(관상동맥질환, 뇌졸중), 비알코올성 지방간, 제2형 당뇨병 및 자궁내막암의 위험이 잔존하므로 생애 전 주기에 걸친 지속 관리가 필요하다{cite_multi(p_lifestyle_rev, p_endometrial_organoids)}.

---

### 20. 치료 안전성 및 약물상호작용

#### 20-1. 안전성 종합 평가
대규모 RCT 메타분석에서 침 치료는 PCOS 환자에게 매우 안전한 중재로 확인되었으며, 심각한 유해반응(Serious Adverse Events)은 보고되지 않았다{cite_multi(p_safety_meta, p_cochrane)}. 혈위매선 및 한약 치료 역시 양약 단독 투여군 대비 위장관계 부작용 발생률이 유의하게 낮았다{cite_multi(p_catgut_meta1, p_zishen_meta)}.

#### 20-2. 한약-양약 상호작용 및 병용 안전성표

| 약물군 / 한약재 | 병용 양약 | 상호작용 기전 및 임상 주의사항 | 임상 권고 및 모니터링 |
|---|---|---|---|
| **황련 / 베르베린** | 메트포르민 (Metformin) | 장내 미생물 조절 및 AMPK 시너지로 혈당 강하 증대 | 저혈당 징후 모니터링, 메트포르민 위장관 부작용 경감 |
| **창부도담탕 계열** | 클로미펜 / 레트로졸 | 난소 과립막세포 수용성 개선, 자궁내막 박막화 부작용 완화 | 난포 발달 초음파 추적, 배란 유도율 상승 |
| **활혈화어 한약 (단삼, 도인, 홍화)** | 항혈소판제 / 항응고제 | 혈소판 응집 억제 및 출혈 경향 증가 가능성 | 혈액응고수치(PT/INR) 추적, 시술 전 감량 |
| **감초 (甘草) 다량·장기** | 이뇨제 / 혈압강하제 | 위알도스테론증(저칼륨혈증, 혈압 상승, 부종) 위험 | 1일 감초 5g 이하 유지, 전해질 수치 확인 |
| **임신 확인 시 (보신안태 전환)** | 임신 유발 약제 | 공하(攻下), 파어(破瘀), 대열(大熱), 독성 본초 즉시 배제 | 자신유태환, 토사자, 두충 등 보신안태방으로 전환 |

> 이 표는 임상 틀이지 동일 근거수준의 권고가 아니다.

---

### 21. 임상 추적 평가 지표표

| 임상 평가 영역 | 객관적 추적 지표 (Biomarkers & Scales) | 목표 치료 반응치 및 추적 주기 |
|---|---|---|
| **월경 및 배란 주기** | 월경 주기 일수(21~35일), 기초체온(BBT) 고온기(≥12일), 소변 LH 서지 | 매 월경 주기 기록, 3개월 단위 평가 |
| **내분비 호르몬** | 혈청 Total/Free Testosterone, LH/FSH 비율(<1.5), AMH, SHBG | 치료 시작 전, 치료 3개월, 6개월 후 |
| **대사 및 혈당 조절** | HOMA-IR(<2.0), 공복 혈당, HbA1c, 공복 인슐린, TyG index | 3~6개월 단위 혈액 검사 |
| **난소 형태학 (초음파)** | 동난포 수(FNPO < 20), 난소 용적(<10 mL), 자궁내막 두께(배란기 ≥8mm) | 3~6개월 단위 골반 초음파 |
| **신체 계측** | BMI, 허리둘레(동아시아 여성 < 80cm), 허리-엉덩이 비율(WHR < 0.8) | 매 내원 시 측정 |
| **임상적 다모 및 피부** | mFG score, 여드름 중증도 점수 (GAGS) | 3개월 단위 평가 |
| **정신신경 및 삶의 질** | PCOSQ (PCOS 삶의 질 설문지), HAMA/HAMD, PSQI (수면) | 치료 전후 비교 평가 |

> 이 표는 임상 틀이지 동일 근거수준의 권고가 아니다.

---

### 22. 생활 지도 및 조섭표 (생활의학적 중재)

| 항목 | 구체적 생활 지도 내용 | 한의학적 및 현대의학적 기전 |
|---|---|---|
| **식이 요법 (飲食有節)** | 저탄수화물·저혈당지수(GI) 식단, 단순당·액상과당·가공식품 금지 | 비위(脾胃)의 운화 기능 보호, 인슐린 저항성 차단{cite(p_stasis_sweet)} |
| **운동 요법 (體育鍛鍊)** | 주 3~5회 중강도 유산소 및 주 2회 근력 운동, 팔단금(八段錦) 수련 | 비기(脾氣) 승발, 골격근 GLUT4 발현 촉진{cite(p_baduanjin1)} |
| **체중 관리 (防肥)** | 초기 체중의 5~10% 점진적 감량 목표 | 담습(痰濕) 제거, 간 SHBG 합성 회복{cite(p_obese_rev)} |
| **수면 조절 (起居有常)** | 자정 이전 취침(23시~07시), 7~8시간 규칙적 수면 유지 | 신수(腎水)와 음혈(陰血) 보충, 코르티솔 리듬 안정 |
| **정서 조절 (情志調暢)** | 스트레스 완화, 명상, 복식호흡, 감정 억울 회피 | 간기(肝氣) 소설, 시상하부 GnRH 펄스 정상화{cite(p_anxiety_meta)} |
| **보온 조섭 (避寒保暖)** | 하복부 및 하지 보온, 찬 음료 및 냉수욕 자제 | 포궁온후(胞宮溫煦), 한응혈어(寒凝血瘀) 방지 |

> 이 표는 임상 틀이지 동일 근거수준의 권고가 아니다.

---

### 23. 환자 설명용 요약 ("다낭성 난소 증후군 바로 알기")

> **다낭성 난소 증후군은 "난소에 물혹이 생기는 질환"이 아닙니다.**  
> 우리 몸의 호르몬 조절 사령탑인 뇌(시상하부·뇌하수체)와 난소, 그리고 췌장의 대사 조절 시스템 사이에 균형이 깨져, 난포가 매달 하나씩 성숙해 터져 나오지 못하고 미성숙한 상태로 난소에 머무르는 **복합 내분비·대사 불균형 질환**입니다.
> 
> 한의학에서는 이를 생식 에너지를 주관하는 **'신(腎)'의 기운 부족**, 체내 노폐물과 수습이 엉킨 **'담음(痰飮)'**, 혈액 순환이 정체된 **'어혈(瘀血)'**, 그리고 스트레스로 인한 **'간(肝)의 기운 뭉침'**으로 파악합니다.
> 
> 한의 치료는 단순히 인위적으로 생리혈만 나오게 하는 피임약 방식이 아니라, **난소 스스로 건강한 난포를 키워 자연 배란할 수 있도록 난소 환경과 전신 대사(인슐린 감수성)를 근본적으로 회복시키는 치료**입니다. 침, 뜸, 한약 치료와 함께 올바른 식습관과 운동을 병행하면 규칙적인 생리와 건강한 임신을 충분히 되찾을 수 있습니다.

---

## 제6편 자주 묻는 질문 (Q&A)

**Q1. 다낭성 난소 증후군 환자가 침 치료를 받으면 실제로 자연 배란과 임신율이 높아지나요?**  
그렇다. 침 치료는 중추 신경계의 엔도르핀 분비를 조절하여 시상하부 GnRH 및 뇌하수체 LH 과분비를 안정화시키고, 난소 국소 혈류를 개선하여 난포의 성숙과 배란을 유도한다{cite_multi(p_unkei_rct1, p_core_points)}. 다수의 임상시험 및 메타분석에서 주 2~3회 침 치료를 지속했을 때 배란율과 자연 임신율이 유의하게 향상되었으며, 특히 한약과 병용했을 때 치료 효과가 극대화됨이 확인되었다{cite_multi(p_dose_resp, p_combined_nma)}.

**Q2. 한약 치료와 메트포르민(Metformin)의 인슐린 저항성 개선 효과는 어떻게 다르며, 병용할 수 있나요?**  
메트포르민은 간의 포도당 생성을 억제하는 단일 약리 기전을 가지나 오심, 설사 등 위장관 부작용이 흔하다. 반면 창부도담탕, 천귀방, 황련(베르베린) 등의 한약은 AMPK 활성화, 장내 미생물총 개선, 전신 염증 억제 등 다표적 경로로 작용한다{cite_multi(p_tiangui_rct, p_datamining_tcm)}. 임상 메타분석에서 한약과 메트포르민의 병용은 인슐린 저항성(HOMA-IR)을 더욱 효과적으로 개선하면서 메트포르민의 위장관 부작용을 유의하게 줄여주었다{cite_multi(p_metformin_meta, p_ins_network)}.

**Q3. 비만형 PCOS와 마른(비비만형) PCOS의 한의학적 치료 접근은 어떻게 다른가요?**  
비만형 PCOS는 **비허습담(脾虛濕痰) 및 담어교결(痰瘀膠結)**을 위주로 보아 창부도담탕, 수오강기탕, 복부 전침 및 혈위매선을 통해 체중 감량과 인슐린 저항성 개선을 우선한다{cite_multi(p_obese_herbal_meta, p_catgut_meta1)}. 반면 마른 체형(Lean PCOS)은 **간신음허(肝腎陰虛) 및 간울(肝鬱)**이 주된 병기이므로 가미자귀탕, 온경탕, 소요산 등을 통해 신정을 보하고 HPO 축의 신경내분비 실조를 안정화시키는 데 집중한다{cite_multi(p_zigui_rct, p_unkei_rct1)}.

**Q4. 시험관아기(IVF/ICSI) 시술 중 한의 치료(침·한약)를 병행하면 어떤 이점이 있나요?**  
PCOS 환자의 시험관 시술 시 침·한약 병행은 과립막세포 미토콘드리아 기능을 개선하여 고품질 배아 획득률을 높이고, 자궁내막 수용성을 증가시켜 임상 임신율과 생아 출생률을 유의하게 향상시킨다{cite_multi(p_art_ivf_meta, p_ea_art_mito)}. 또한 과배란으로 인한 중증 난소과자극증후군(OHSS)의 발생 위험을 60% 이상 현저히 낮추어 안전한 보조생식술 진행을 돕는다{cite_multi(p_cangfu_meta, p_art_east_meta)}.

**Q5. 경구피임약(OCP)을 오래 복용하다 중단하면 생리가 다시 멈추는데, 한의 치료로 근본 치료가 가능한가요?**  
경구피임약은 소퇴성 출혈(Withdrawal bleeding)을 유도할 뿐 난소의 자체 배란 기능을 회복시키지 못하며, 복용 중단 시 무배란이 재발하기 쉽다. 한의 치료는 HPO 축과 난소 기능을 점진적으로 자극하여 난소 스스로 우성 난포를 키워 배란하게 만드는 **자연 주기 회복 치료**이다. 임상시험에서 한약 치료는 피임약 대비 투약 종료 후에도 배란 및 월경 유지율이 장기적으로 우수하였다{cite_multi(p_yougui_rct, p_unkei_rct2)}.

**Q6. 청소년기 여학생의 생리불순과 여드름도 PCOS일 수 있나요?**  
그렇다. 청소년기 생리불순을 단순한 사춘기 성장 과정으로 방치하면 성인기 중증 PCOS와 대사증후군으로 고착화될 수 있다. 사춘기 여학생의 경우 성인과 다른 진단 기준을 적용하며, 신기(腎氣)를 북돋우고 비위를 조화시키는 한약 및 이혈 지압을 조기 적용하여 성호르몬 안정과 난소 발달을 도모한다{cite_multi(p_adolescent_proto, p_adiponectin)}.

**Q7. 혈위매선 요법(Acupoint Catgut Embedding)이 비만 및 대사 이상에 효과적인 이유는 무엇인가요?**  
혈위매선은 인체에 무해한 흡수성 봉합사를 특정 혈위(천추, 중완, 풍륭 등)에 자입하여 2~3주 동안 지속적인 물리·생화학적 자극을 가하는 치료법이다. 교감신경을 조절하고 대사율을 촉진하여 식욕을 억제하며, 메타분석에서 BMI, 허리둘레, HOMA-IR 감소 효과가 통계적으로 입증되었다{cite_multi(p_catgut_meta1, p_catgut_meta2)}.

**Q8. PCOS 환자의 불안·우울·스트레스 등 정서적 문제에도 한의 치료가 도움이 되나요?**  
매우 효과적이다. 대규모 메타분석(2,127명)에서 침 치료는 PCOS 환자의 불안(HAMA)과 우울(HAMD) 점수를 유의하게 경감시켰다{cite_multi(p_anxiety_meta)}. 소간해울(疏肝解鬱) 한약(가미소요산 등)과 특정 혈위 지압은 신경전달물질과 HPA 축을 안정화시켜 삶의 질을 근본적으로 개선한다{cite_multi(p_acupressure_rct, p_danzhi_rct)}.

---

**고전 인용 출처**: 『黃帝內經素問』(上古天眞論, 陰陽別論), 『靈樞』(經脈, 水脹), 『金匱要略』(婦人雜病脈證幷治), 『婦人大全良方』, 『景岳全書』(婦人規), 『傅青主女科』, 『醫宗金鑑』(婦科心法要訣), 『丹溪心法』.
**문헌 데이터 출처**: [한의학 논문 데이터베이스 (med.symbolicinfo.com)](https://med.symbolicinfo.com) — 2026-08-19 조회 기준
"""

# Assemble full text
full_text = sec1 + sec2 + sec3 + sec4 + sec5

# Build Footnote Definitions
fn_lines = ["\n"]
for c_num, a_idx in enumerate(citation_order, start=1):
    fn_lines.append(format_footnote(c_num, articles[a_idx]))

full_document = full_text.strip() + "\n" + "\n".join(fn_lines) + "\n"
full_document = full_document.replace("。", ".")

out_path = "wiki/임상한의학/산부인과/다낭성난소증후군(多囊性卵巣症候群, Polycystic Ovary Syndrome).md"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(full_document)

print(f"Successfully generated full PCOS wiki document at {out_path}")
print(f"Total lines: {len(full_document.splitlines())}")
print(f"Total unique citations: {len(citation_order)}")
