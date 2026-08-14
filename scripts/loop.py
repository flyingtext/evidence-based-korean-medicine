#!/usr/bin/env python3
"""opencode로 RUN.md 워크플로우를 무한 반복 실행하는 스크립트.

터미널에서 opencode를 호출해 RUN.md에 정의된 위키 작성·보강·검증 작업을
끝날 때마다 반복 실행한다. Ctrl+C로 중단한다.

사용법:
    python3 scripts/loop.py                 # 무한 반복
    python3 scripts/loop.py --max 10         # 10회만 실행
    python3 scripts/loop.py --interval 5     # 실행 사이 5초 대기
"""
import argparse
import subprocess
import sys
import time

PROMPT = "RUN.md 실행"


def run_once(opencode_cmd: list, interval: float, count: int) -> int:
    print(f"\n=== [{count}] opencode 실행: {PROMPT!r} ===")
    try:
        rc = subprocess.call(opencode_cmd)
    except KeyboardInterrupt:
        print("\n중단됨.")
        return -1
    print(f"=== [{count}] 종료 코드: {rc} ===")
    if interval > 0:
        print(f"{interval}초 대기...")
        try:
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\n중단됨.")
            return -1
    return rc


def main() -> int:
    p = argparse.ArgumentParser(description="opencode로 RUN.md 워크플로우 무한 반복")
    p.add_argument("--max", type=int, default=0, help="실행 횟수 (0 = 무한)")
    p.add_argument("--interval", type=float, default=0, help="실행 사이 대기(초)")
    p.add_argument("--opencode", default="opencode", help="opencode 실행 파일")
    args = p.parse_args()

    cmd = [args.opencode, PROMPT]
    count = 0
    while args.max == 0 or count < args.max:
        count += 1
        rc = run_once(cmd, args.interval, count)
        if rc == -1:
            return 0
        if rc != 0:
            print(f"opencode 종료 코드 {rc} — 계속 진행합니다.")
    print(f"완료: {count}회 실행.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
