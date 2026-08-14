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

PROMPT = (
    "RUN.md와 AGENTS.md의 규칙을 따라 위키를 증식·보강하라. "
    "1) 각 폴더의 README.md 목차(동음이의 분류 포함)를 확인해 아직 작성되지 않은 문서를 하나 골라라. "
    "2) 해당 주제로 med.symbolicinfo.com /search API(analyzed=1, km=1, human=1)에서 논문을 수집하고, "
    "근거 표(제목·연구유형·환자수·근거수준·DOI/PMID·AI 임상요약)를 포함한 위키 문서를 작성하라. "
    "3) 질환 문서는 KCD-8 코드를 개요 첫 문단에 명시하고, 임상한의학 각 과 밑에는 교과서적 편제로 질환을 서술하라. "
    "4) 기존 문서는 최신 논문(analyzed_at/fetched_at)과 대조해 틀린 내용·오래된 근거·누락된 근거수준 라벨을 수정·갱신하라. "
    "   AI 요약(answer/clinical_summary)은 원문과 대조해 정확성을 확인하고, 근거가 없는 주장은 '근거 미확인'으로 명시하라. "
    "5) 작성·수정 후 python3 scripts/run.py로 검증·링크·빌드를 통과시키고 커밋하라. "
    "새 문서도 없고 수정할 내용도 없으면 그 사실을 알리고 종료하라."
)


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
