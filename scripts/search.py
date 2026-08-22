#!/usr/bin/env python3
"""근거 기반 한의학 위키 — 논문 검색 API 자동화 스크립트.

med.symbolicinfo.com /search API로 논문을 수집해 마크다운 각주 정의(각주 정의)를 생성한다.

사용법:
    python3 scripts/search.py "요통" --km --human --analyzed
    python3 scripts/search.py "요통" --cat clinical_trial,meta_analysis --km --human --analyzed --verbose
    python3 scripts/search.py "합곡" --per-page 50 --out /tmp/evidence.md --json /tmp/evidence.json
    python3 scripts/search.py "요통" --per-page 100 --target 200 --verbose --stats

전수 인용 원칙:
    - per_page=100 + 다중 페이지 순회로 전수 수집, 동일 DOI/PMID 병합
    - experimental_study 중 is_human_study==0 (동물실험)은 본문 인용에서 제외하되 목록에는 남기고 제외 사유를 로깅
    - --include-animal 로 포함 가능 (기본: 제외)

로깅:
    - stderr 로 진행 로그 출력 (INFO: 페이지별, DEBUG: 개별 논문, WARNING: 재시도/누락)
    - --verbose / -v : DEBUG 레벨, --log-level 로 세밀 조정
    - --stats : 수집 후 연구유형/저널/연도 분포 요약 추가 출력
"""
from __future__ import annotations

import argparse
import collections
import json
import logging
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://med.symbolicinfo.com"

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

# 로거는 모듈 레벨에서 생성, setup_logging()에서 핸들러 부착
logger = logging.getLogger("search")


def setup_logging(level: str, verbose: bool) -> None:
    if verbose and level == "INFO":
        level = "DEBUG"
    numeric = getattr(logging, level.upper(), logging.INFO)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    ))
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(numeric)
    # urllib 디버그 노이즈 억제
    logging.getLogger("urllib").setLevel(logging.WARNING)


def build_url(params: dict) -> str:
    return BASE + "/search?" + urllib.parse.urlencode(params)


def fetch(params: dict, retries: int = 3, timeout: int = 30, delay: float = 0.0) -> dict:
    """단일 페이지 fetch — 재시도 + 지수 백오프."""
    url = build_url(params)
    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            if delay and attempt == 1:
                time.sleep(delay)
            logger.debug("GET %s (attempt %d/%d)", url, attempt, retries)
            req = urllib.request.Request(url, headers={"User-Agent": "EvidenceWiki-search.py/1.1"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.load(resp)
                logger.debug("  -> total=%s page=%s/%s items=%d",
                             data.get("total"), data.get("page"), data.get("total_pages"), len(data.get("items", [])))
                return data
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            last_exc = e
            status = getattr(e, "code", "?")
            logger.warning("fetch 실패 (attempt %d/%d) status=%s err=%s url=%s", attempt, retries, status, e, url)
            if attempt < retries:
                backoff = min(2 ** attempt, 8)
                logger.info("  %ds 후 재시도...", backoff)
                time.sleep(backoff)
            else:
                logger.error("fetch 최종 실패: %s", url)
    raise RuntimeError(f"fetch 실패 after {retries} retries: {last_exc}") from last_exc


def is_animal_experimental(item: dict) -> bool:
    return item.get("research_category") == "experimental_study" and not item.get("is_human_study")


def normalize_key(item: dict) -> str | None:
    doi = (item.get("doi") or "").strip().lower()
    if doi:
        # doi 정규화: 공백·대소문자 제거, url prefix 제거
        doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "").strip()
        return f"doi:{doi}"
    pmid = (item.get("pmid") or "").strip()
    if pmid:
        return f"pmid:{pmid}"
    url = (item.get("url") or "").strip()
    if url:
        return f"url:{url}"
    return None


def fetch_all(
    q: str,
    base_params: dict,
    per_page: int,
    target: int = 0,
    start_page: int = 1,
    max_pages: int = 0,
    retries: int = 3,
    delay: float = 0.4,
    exclude_animal: bool = True,
) -> tuple[list[dict], dict]:
    """여러 페이지를 순회하며 최대한 많은 논문을 수집한다.

    Returns:
        (items, stats)  stats: 수집 과정 요약 딕셔너리
    """
    items: list[dict] = []
    seen: set[str] = set()
    stats: dict = collections.Counter()
    stats["excluded_animal"] = 0
    stats["dedup"] = 0
    stats["fetched_pages"] = 0
    stats["total_reported"] = 0
    stats["total_pages_reported"] = 0

    page = start_page
    total: int | None = None
    total_pages: int | None = None

    # target==0 이면 전수(최대 1000건 or total_pages까지)
    hard_cap = 5000  # AGENTS 원칙상 전수 — 1000 제한 완화, 필요 시 더 순회
    if target <= 0:
        target = hard_cap

    logger.info("검색 시작: q=%r params=%s per_page=%d target=%s start_page=%d exclude_animal=%s",
                q, base_params, per_page, "전수" if target == hard_cap else target, start_page, exclude_animal)

    while len(items) < target:
        if max_pages and stats["fetched_pages"] >= max_pages:
            logger.info("max_pages=%d 도달 — 중단", max_pages)
            break
        params = dict(base_params)
        params.update({"q": q, "per_page": per_page, "page": page})
        try:
            data = fetch(params, retries=retries, delay=delay if page > start_page else 0.0)
        except RuntimeError as e:
            logger.error("page %d 수집 중단: %s", page, e)
            stats["fetch_error"] = stats.get("fetch_error", 0) + 1
            break

        batch = data.get("items", [])
        if total is None:
            total = data.get("total", 0)
            total_pages = data.get("total_pages", 0)
            stats["total_reported"] = total
            stats["total_pages_reported"] = total_pages
            logger.info("API 보고: total=%d total_pages=%d per_page=%d", total, total_pages, per_page)
            if total == 0:
                logger.warning("검색 결과 0건: q=%r params=%s", q, base_params)

        stats["fetched_pages"] += 1

        if not batch:
            logger.info("page %d/%s 빈 배치 — 종료", page, total_pages)
            break

        added = 0
        dedup_in_page = 0
        animal_in_page = 0
        for it in batch:
            if exclude_animal and is_animal_experimental(it):
                animal_in_page += 1
                stats["excluded_animal"] += 1
                logger.debug("  동물실험 제외: %s | %s", it.get("doi") or it.get("pmid"), (it.get("title") or "")[:60])
                continue
            key = normalize_key(it)
            if key and key in seen:
                dedup_in_page += 1
                stats["dedup"] += 1
                logger.debug("  중복 제거: %s | %s", key, (it.get("title") or "")[:50])
                continue
            if key:
                seen.add(key)
            items.append(it)
            added += 1

        logger.info("page %d/%s: batch=%d added=%d dedup=%d animal_excluded=%d cumulative=%d/%s",
                    page, total_pages, len(batch), added, dedup_in_page, animal_in_page, len(items), total)

        # 다음 페이지 여부
        if page >= (total_pages or page):
            logger.info("마지막 페이지 도달 (page %d >= total_pages %s) — 종료", page, total_pages)
            break
        page += 1
        if len(items) >= target:
            logger.info("target %d 도달 — 종료", target)
            break
        if len(items) >= hard_cap:
            logger.warning("hard_cap %d 도달 — 종료 (더 필요하면 --target 조정)", hard_cap)
            break
        # 페이지 간 딜레이 (API 과호출 방지)
        if delay:
            time.sleep(delay)

    # 카테고리 분포
    cat_counter = collections.Counter(it.get("research_category") or "other" for it in items)
    stats["by_category"] = dict(cat_counter)
    stats["unique_collected"] = len(items)
    logger.info("수집 완료: unique=%d dedup=%d animal_excluded=%d pages=%d total_reported=%d",
                len(items), stats["dedup"], stats["excluded_animal"], stats["fetched_pages"], stats["total_reported"])
    logger.info("  연구유형 분포: %s", ", ".join(f"{CATEGORY_LABEL.get(k,k)}={v}" for k, v in sorted(cat_counter.items())))
    if logger.isEnabledFor(logging.DEBUG):
        # 상위 저널/연도 분포 (DEBUG 시)
        journal_counter = collections.Counter((it.get("journal") or "미상") for it in items)
        logger.debug("  상위 저널 5: %s", ", ".join(f"{j}({c})" for j, c in journal_counter.most_common(5)))

    return items, dict(stats)


def footnote_def(idx: int, item: dict) -> str:
    """RUN.md §1-4-2-1 고정 포맷.

    [^n]: <제목>. _<저널>_. <YYYY-MM-DD>. [<라벨>] <DOI/PMID 링크> — <부연 한 줄>.
    부연은 clinical_summary/answer가 있으면 1문장 요약, 없으면 생략 가능하되 자리표시는 유지.
    """
    title = (item.get("title") or "제목 미상").strip()
    # 마침표 통일: 중국어 모점 제거
    title = title.replace("。", ".")
    journal = (item.get("journal") or "").strip().replace("。", ".")
    pub_date = (item.get("pub_date") or item.get("fetched_at") or "")[:10]
    cat = item.get("research_category") or "other"
    label = CATEGORY_LABEL.get(cat, cat)
    doi = (item.get("doi") or "").strip()
    pmid = (item.get("pmid") or "").strip()
    patient_count = item.get("patient_count")
    # 링크
    links: list[str] = []
    if doi:
        # doi 정규화: prefix 제거
        doi_clean = doi.replace("https://doi.org/", "").replace("http://doi.org/", "").strip()
        links.append(f"[DOI {doi_clean}](https://doi.org/{doi_clean})")
    if pmid:
        links.append(f"[PMID {pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)")
    link_str = " ".join(links)
    # 환자수 표기
    patient_str = f", {patient_count}명" if isinstance(patient_count, int) and patient_count > 0 else ""
    # 저널/날짜 부분
    journal_part = f" _{journal}_." if journal else ""
    date_part = f" {pub_date}." if pub_date else ""
    # 부연 해석 — clinical_summary 우선, 없으면 answer, 없으면 키워드 기반 1줄
    summary = (item.get("clinical_summary") or item.get("answer") or "").strip().replace("。", ".")
    if summary:
        # 첫 문장만 사용 (너무 길면 자름)
        first_sentence = summary.split(".")[0].strip()
        if first_sentence and not first_sentence.endswith("."):
            first_sentence += "."
        # 120자 넘으면 자름
        if len(first_sentence) > 160:
            first_sentence = first_sentence[:157] + "..."
        annotation = f" — {first_sentence}"
    else:
        annotation = ""
    # 최종 조합
    # 예: [^1]: Title. _Journal_. 2024-09-30. [메타분석, 123명] [DOI ...] [PMID ...] — 부연.
    count_label = f"{label}{patient_str}" if patient_str else label
    if link_str:
        return f"[^{idx}]: {title}.{journal_part}{date_part} [{count_label}] {link_str}{annotation}"
    else:
        return f"[^{idx}]: {title}.{journal_part}{date_part} [{count_label}]{annotation}"


def main() -> int:
    p = argparse.ArgumentParser(description="논문 검색 API로 각주 정의 생성 (전수 수집 + 상세 로깅)")
    p.add_argument("q", help="검색어")
    p.add_argument("--cat", help="연구 유형 필터 (콤마 구분: clinical_trial,meta_analysis 등)")
    p.add_argument("--km", action="store_true", help="한의학만 (km=1)")
    p.add_argument("--human", action="store_true", help="인체 연구만 (human=1)")
    p.add_argument("--lit", action="store_true", help="문헌 고찰만 (lit=1)")
    p.add_argument("--analyzed", action="store_true", help="분석 완료만 (analyzed=1)")
    p.add_argument("--per-page", type=int, default=20, help="페이지당 개수 (1~100, 기본 20, 전수 시 100 권장)")
    p.add_argument("--target", type=int, default=0,
                   help="수집 목표 논문 수 (0=전수, 최대 5000, 기본 전수)")
    p.add_argument("--page", type=int, default=1, help="시작 페이지 (기본 1)")
    p.add_argument("--max-pages", type=int, default=0, help="최대 순회 페이지 수 (0=제한 없음)")
    p.add_argument("--out", help="마크다운 출력 파일 (없으면 stdout)")
    p.add_argument("--json", dest="json_out", help="원시 JSON 덤프 파일 (items 배열)")
    p.add_argument("--stats", action="store_true", help="수집 후 통계 요약 출력")
    p.add_argument("--verbose", "-v", action="store_true", help="DEBUG 로깅 (페이지/개별 논문 상세)")
    p.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                   help="로그 레벨 (기본 INFO, -v는 DEBUG)")
    p.add_argument("--delay", type=float, default=0.4, help="페이지 간 딜레이 초 (기본 0.4, 과호출 방지)")
    p.add_argument("--retries", type=int, default=3, help="페이지 fetch 재시도 횟수 (기본 3)")
    p.add_argument("--timeout", type=int, default=30, help="HTTP 타임아웃 초 (기본 30)")
    p.add_argument("--include-animal", action="store_true", dest="include_animal",
                   help="동물실험 experimental_study도 포함 (기본: 제외하고 제외 수 로깅)")
    p.add_argument("--kw", help="키워드 필터 (콤마 구분, AND 조건)")
    p.add_argument("--source", choices=["pubmed", "crossref", "both", "all"], help="소스 필터")
    args = p.parse_args()

    setup_logging(args.log_level, args.verbose)

    if not 1 <= args.per_page <= 100:
        logger.error("--per-page는 1~100 범위여야 함 (입력: %d)", args.per_page)
        return 2

    params: dict = {"per_page": args.per_page}
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
    if args.kw:
        params["kw"] = args.kw
    if args.source:
        params["source"] = args.source

    exclude_animal = not args.include_animal

    try:
        items, stats = fetch_all(
            args.q, params, args.per_page,
            target=args.target,
            start_page=args.page,
            max_pages=args.max_pages or 0,
            retries=args.retries,
            delay=args.delay,
            exclude_animal=exclude_animal,
        )
    except RuntimeError as e:
        logger.error("수집 실패: %s", e)
        return 1

    total = stats.get("total_reported", len(items))

    # 마크다운 생성
    lines = [
        f"> 검색어: `{args.q}` · 총 {total}건 · 확보 {len(items)}건 (DOI 중복 제거 후, 동물실험 {stats.get('excluded_animal',0)}건 제외)",
        f"> 파라미터: km={params.get('km','-')} human={params.get('human','-')} analyzed={params.get('analyzed','-')} cat={params.get('cat','-')} per_page={args.per_page}",
        f"> 수집: {stats.get('fetched_pages',0)}페이지 순회 · 중복 {stats.get('dedup',0)}건 제거 · 최종 {len(items)}건",
        "",
        "각주 마커는 본문의 문장별 인용 순서에 맞게 재배정한다. 문서 끝에 별도의 헤더 없이 각주 정의로 나열한다.",
        "",
    ]
    lines += [footnote_def(i + 1, it) for i, it in enumerate(items)]

    out = "\n".join(lines) + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(out)
        logger.info("마크다운 작성 완료: %s (%d건)", args.out, len(items))
    else:
        # stdout은 마크다운만, 로그는 stderr로 분리되어 있음
        print(out, end="")

    if args.json_out:
        # 원시 items 덤프 (재사용·검증용)
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        logger.info("JSON 덤프 완료: %s (%d건)", args.json_out, len(items))

    if args.stats or args.verbose:
        # 통계 요약은 stderr(로그)로
        cat_dist = stats.get("by_category", {})
        logger.info("=== 통계 요약 ===")
        logger.info("  검색어: %r  total=%d  unique=%d  dedup=%d  animal_excluded=%d  pages=%d",
                    args.q, total, len(items), stats.get("dedup", 0), stats.get("excluded_animal", 0), stats.get("fetched_pages", 0))
        for cat, cnt in sorted(cat_dist.items(), key=lambda x: -x[1]):
            logger.info("    %-20s %4d  (%s)", cat, cnt, CATEGORY_LABEL.get(cat, cat))
        # 저널 상위 10
        j_counter = collections.Counter((it.get("journal") or "미상") for it in items)
        logger.info("  상위 저널 10:")
        for j, c in j_counter.most_common(10):
            logger.info("    %4d  %s", c, j[:60])

    # 전수 원칙 경고: total 대비 확보율이 낮으면 알림
    if total and len(items) < total * 0.9 and args.target == 0:
        # target==0인데도 90% 미만이면 페이지 누락 가능성
        logger.warning("확보율 %.1f%% — total %d 중 %d건만 확보 (per_page 100·재시도 확인 권장)",
                       len(items) / total * 100 if total else 0, total, len(items))

    return 0


if __name__ == "__main__":
    sys.exit(main())
