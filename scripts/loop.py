#!/usr/bin/env python3
"""opencode로 RUN.md 워크플로우를 무한 반복 실행하는 스크립트.

터미널에서 opencode를 호출해 RUN.md에 정의된 위키 작성·보강·검증 작업을
끝날 때마다 반복 실행한다. Ctrl+C로 중단한다.

사용법:
    python3 scripts/loop.py                 # 무한 반복
    python3 scripts/loop.py --max 10         # 10회만 실행
    python3 scripts/loop.py --interval 5     # 실행 사이 5초 대기
    python3 scripts/loop.py --reset          # 체크포인트 초기화
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKPOINT = os.path.join(ROOT, "scripts", ".progress.json")
LOG_FILE = os.path.join(ROOT, "scripts", "loop.log")

# 연속 실패 시 중단할 횟수
MAX_CONSECUTIVE_FAILURES = 3
# 세션당 API 검색 상한 (프롬프트에 명시, 제한 없음)
SESSION_SEARCH_LIMIT = None

PROMPT = (
    "RUN.md와 AGENTS.md의 규칙을 따라 위키를 증식·보강하라. "
    "1) scripts/.progress.json 체크포인트를 읽어 이미 처리한 주제를 건너뛰고, "
    "   새로 작성할 표제어(본초·경혈·처방·질환·용어 등)를 직접 선정하라. "
    "   기존 위키 문서 본문에서 자주 언급되지만 아직 문서가 없는 개념을 우선 고르고, "
    "   없으면 위키 분류 체계에 맞는 새 주제를 골라라. "
    "2) 해당 주제로 med.symbolicinfo.com /search API(analyzed=1, km=1, human=1)에서 논문을 수집하되, "
    "   검색 횟수에 제한이 없다. 포괄적 검색어 확장(RUN.md)에 따라 충분히 검색하라. "
    "   **각 문서의 각주 정의에 반드시 최소 15편(가능하면 20편 이상)의 서로 다른 DOI/PMID 논문을 수록하라.** "
    "   (참고문헌 섹션·근거 표는 두지 않고 출처는 각주 정의로만 표기한다.) "
    "   per_page=100을 쓰고 필요시 여러 페이지를 순회해 후보를 전수 수집하되 DOI로 중복을 제거하고, "
    "   임상시험·체계적 고찰·메타분석·관찰연구·증례 등 다양한 연구 유형을 고르게 포함해라. "
    "   각 논문은 본문 문장별 각주로 연결하고, 문서 끝에 별도의 헤더 없이 각주 정의(제목·연구유형·환자수·DOI/PMID 링크)를 나열하라. "
    "3) 질환 문서는 KCD-8 코드를 개요 첫 문단에 명시하고, 임상한의학 각 과 밑에는 교과서적 편제로 질환을 서술하라. "
    "4) 기존 문서는 최신 논문(analyzed_at/fetched_at)과 대조해 틀린 내용·오래된 근거·누락된 연구 유형 라벨을 수정·갱신하라. "
    "   AI 요약(answer/clinical_summary)은 원문과 대조해 정확성을 확인하고, 근거가 없는 주장은 '근거 미확인'으로 명시하라. "
    "5) 근거 무결성 확인: 모든 임상 주장에 DOI/PMID가 있는지, 비한의학 논문이 섞였는지(is_korean_medicine) 확인하라. "
    "6) 작성·수정 후 python3 scripts/run.py로 검증·링크·빌드를 통과시키고 커밋하라. "
    "   커밋 전 git status로 의도한 파일만 스테이징하고, 처리한 주제를 scripts/.progress.json에 기록하라. "
    "새 문서도 없고 수정할 내용도 없으면 그 사실을 알리고 종료하라."
)


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_checkpoint() -> dict:
    cp = {"processed": [], "last_run": None}
    if os.path.exists(CHECKPOINT):
        try:
            with open(CHECKPOINT, encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                cp.update(loaded)
                cp.setdefault("processed", [])
                cp.setdefault("last_run", None)
                return cp
        except (json.JSONDecodeError, OSError):
            pass
    return cp


def save_checkpoint(cp: dict) -> None:
    cp["last_run"] = datetime.now(timezone.utc).isoformat()
    with open(CHECKPOINT, "w", encoding="utf-8") as f:
        json.dump(cp, f, ensure_ascii=False, indent=2)


def run_once(opencode_cmd: list, prompt: str, interval: float, count: int,
             timeout: float = 0) -> int:
    log(f"=== [{count}] opencode 실행 시작 ===")
    try:
        kw = {"input": prompt, "text": True, "encoding": "utf-8"}
        if timeout > 0:
            kw["timeout"] = timeout
        rc = subprocess.run(opencode_cmd, **kw).returncode
    except subprocess.TimeoutExpired:
        log(f"=== [{count}] {timeout}초 경과 — 타임아웃으로 강제 종료 ===")
        return 1
    except KeyboardInterrupt:
        log("중단됨.")
        return -1
    log(f"=== [{count}] 종료 코드: {rc} ===")
    if interval > 0:
        log(f"{interval}초 대기...")
        try:
            time.sleep(interval)
        except KeyboardInterrupt:
            log("중단됨.")
            return -1
    return rc


def main() -> int:
    p = argparse.ArgumentParser(description="opencode로 RUN.md 워크플로우 무한 반복")
    p.add_argument("--max", type=int, default=0, help="실행 횟수 (0 = 무한)")
    p.add_argument("--interval", type=float, default=2, help="실행 사이 대기(초)")
    p.add_argument("--opencode", default="opencode", help="opencode 실행 파일")
    p.add_argument("--timeout", type=float, default=600,
                   help="opencode 응답 없음 시 강제 종료할 시간(초), 0 = 제한 없음")
    p.add_argument("--reset", action="store_true", help="체크포인트 초기화")
    args = p.parse_args()

    if args.reset:
        save_checkpoint({"processed": [], "last_run": None})
        log("체크포인트 초기화 완료.")

    cp = load_checkpoint()
    log(f"체크포인트: 처리 {len(cp['processed'])}건, 마지막 실행 {cp['last_run']}")

    cmd = [args.opencode, "run"]
    count = 0
    consecutive_failures = 0
    while args.max == 0 or count < args.max:
        count += 1
        rc = run_once(cmd, PROMPT, args.interval, count, args.timeout)
        if rc == -1:
            return 0
        if rc != 0:
            consecutive_failures += 1
            log(f"실패 ({consecutive_failures}/{MAX_CONSECUTIVE_FAILURES})")
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                log(f"연속 {MAX_CONSECUTIVE_FAILURES}회 실패 — 중단합니다.")
                return 1
        else:
            consecutive_failures = 0
    log(f"완료: {count}회 실행.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
