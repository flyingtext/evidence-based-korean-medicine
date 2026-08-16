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

    # RUN.md 파일 내용을 프롬프트로 사용
    try:
        with open(os.path.join(ROOT, "RUN.md"), "r", encoding="utf-8") as f:
            run_md_content = f.read()
        full_prompt = (
            f"다음은 위키 작성·보강을 위한 RUN.md의 전체 지침이다. 이 지침과 AGENTS.md의 규칙을 엄격히 따라 위키를 증식·보강하라.\n\n"
            f"--- RUN.md START ---\n{run_md_content}\n--- RUN.md END ---\n"
        )
    except Exception as e:
        log(f"RUN.md 파일을 읽는 중 오류 발생: {e}")
        sys.exit(1)

    cmd = [args.opencode, "run"]
    count = 0
    consecutive_failures = 0
    while args.max == 0 or count < args.max:
        count += 1
        rc = run_once(cmd, full_prompt, args.interval, count, args.timeout)
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
