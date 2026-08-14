#!/usr/bin/env python3
"""근거기반 한의학 위키 — RUN.md 워크플로우 자동 실행 스크립트.

RUN.md에 정의된 검증·링크 점검·빌드 단계를 순서대로 실행한다.
작업이 끝날 때마다 이 스크립트를 호출해 품질을 확인한다.

사용법:
    python3 scripts/run.py            # 검증 + 링크 점검 + 빌드
    python3 scripts/run.py --skip-build
    python3 scripts/run.py --health   # API 헬스 체크 포함
"""
import argparse
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI_DIR = os.path.join(ROOT, "wiki")
BASE = "https://med.symbolicinfo.com"


def sh(cmd: list, cwd: str = ROOT) -> int:
    print(f"\n$ {' '.join(cmd)}")
    return subprocess.call(cmd, cwd=cwd)


def step_validate() -> int:
    print("\n=== [1/3] 문서 품질 검증 (validate.py) ===")
    return sh([sys.executable, os.path.join(ROOT, "scripts", "validate.py")])


def step_links() -> int:
    print("\n=== [2/3] 교차 참조(상대 링크) 점검 ===")
    broken = []
    for root, _, files in os.walk(WIKI_DIR):
        for fn in files:
            if not fn.endswith(".md"):
                continue
            path = os.path.join(root, fn)
            with open(path, encoding="utf-8") as f:
                content = f.read()
            for m in re.finditer(r"\]\(([^)#]+\.md)\)", content):
                target = m.group(1)
                if target.startswith("http"):
                    continue
                resolved = os.path.normpath(os.path.join(os.path.dirname(path), target))
                if not os.path.exists(resolved):
                    broken.append(f"{os.path.relpath(path, ROOT)} -> {target}")
    if broken:
        print("끊어진 링크 발견:")
        for b in broken:
            print(f"  - {b}")
        return 1
    print("끊어진 링크 없음.")
    return 0


def step_build() -> int:
    print("\n=== [3/3] 정적 사이트 빌드 (mkdocs) ===")
    return sh([sys.executable, "-m", "mkdocs", "build"])


def step_health() -> int:
    print("\n=== [추가] API 헬스 체크 ===")
    import json
    import urllib.request

    try:
        with urllib.request.urlopen(BASE + "/health", timeout=15) as resp:
            data = json.load(resp)
        print(f"API 정상: {data}")
        return 0
    except Exception as e:  # noqa: BLE001
        print(f"API 오류: {e}")
        return 1


def main() -> int:
    p = argparse.ArgumentParser(description="RUN.md 워크플로우 자동 실행")
    p.add_argument("--skip-build", action="store_true", help="빌드 단계 생략")
    p.add_argument("--health", action="store_true", help="API 헬스 체크 포함")
    args = p.parse_args()

    steps = [step_validate, step_links]
    if not args.skip_build:
        steps.append(step_build)
    if args.health:
        steps.append(step_health)

    failed = 0
    for step in steps:
        if step() != 0:
            failed += 1

    if failed:
        print(f"\n실패한 단계: {failed}개 — RUN.md 유의사항을 확인하세요.")
        return 1
    print("\n모든 단계 통과.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
