#!/usr/bin/env python3
"""근거 기반 한의학 위키 — RUN.md 워크플로우 자동 실행 스크립트.

RUN.md에 정의된 검증·링크 점검 단계를 순서대로 실행한다.
작업이 끝날 때마다 이 스크립트를 호출해 품질을 확인한다.

사용법:
    python3 scripts/run.py            # 검증 + 링크 점검
    python3 scripts/run.py --health   # API 헬스 체크 포함
    python3 scripts/run.py --watch    # 30초마다 반복 실행 (Ctrl+C로 종료)
    python3 scripts/run.py --watch --interval 10  # 10초 간격 반복
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
    print("\n=== [3/3] 교차 참조(상대 링크) 점검 ===")
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


def step_recent() -> int:
    """git log 기준으로 wiki/최근업데이트.md를 자동 재생성한다."""
    print("\n=== [2/3] 최근 업데이트 문서 자동 재생성 ===")
    out = subprocess.run(
        ["git", "log", "--format=%ad", "--date=format:%Y-%m-%d %H:%M:%S", "--name-only", "-z", "--", "wiki/"],
        cwd=ROOT, capture_output=True, text=True,
    )
    if out.returncode != 0:
        print(f"git log 오류: {out.stderr}")
        return 1

    # (날짜, 파일경로) 목록 수집
    entries = []
    date = None
    for token in out.stdout.split("\0"):
        token = token.strip()
        if not token:
            continue
        if re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", token):
            date = token
        elif token.startswith("wiki/") and token.endswith(".md"):
            rel = token[len("wiki/"):]
            if rel in ("README.md", "최근업데이트.md", "추천순위.md", "_template.md"):
                continue
            if rel.startswith("assets/"):
                continue
            if os.path.basename(rel) == "README.md":
                continue
            # 현재 존재하는 실제 문서만 포함 (삭제된 옛 구조 제외)
            if not os.path.exists(os.path.join(WIKI_DIR, rel)):
                continue
            entries.append((date, rel))

    # 최신순 정렬, 중복(같은 파일)은 최신 날짜만 유지
    seen = {}
    for date, rel in entries:
        if rel not in seen or date > seen[rel]:
            seen[rel] = date
    items = sorted(seen.items(), key=lambda kv: kv[1], reverse=True)

    if not items:
        print("최근 업데이트할 문서가 없습니다.")
        return 0

    # 분류(중분류 폴더명) 추출
    def category(rel: str) -> str:
        parts = rel.split("/")
        return parts[1] if len(parts) > 2 else parts[0]

    lines = [
        "# 최근 업데이트 문서",
        "",
        "근거 기반 한의학 위키에서 가장 최근에 작성·갱신된 문서 목록입니다.",
        "(git 커밋 시각 기준, 최신순)",
        "",
        "## 최근 문서",
        "",
        "| 문서 | 분류 | 업데이트 |",
        "|---|---|---|",
    ]
    for rel, date in items:
        title = os.path.splitext(os.path.basename(rel))[0]
        lines.append(f"| {title} | {category(rel)} | {date} |")
    lines.append("")

    target = os.path.join(WIKI_DIR, "최근업데이트.md")
    with open(target, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"최근업데이트.md 재생성 완료 ({len(items)}개 문서).")
    return 0


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


def run_once(args) -> int:
    steps = [step_validate, step_recent, step_links]
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


def main() -> int:
    p = argparse.ArgumentParser(description="RUN.md 워크플로우 자동 실행")
    p.add_argument("--health", action="store_true", help="API 헬스 체크 포함")
    p.add_argument("--watch", action="store_true", help="워크플로우를 반복 실행 (기본 30초 간격)")
    p.add_argument("--interval", type=int, default=30, help="--watch 반복 간격(초), 기본 30")
    args = p.parse_args()

    if args.interval <= 0:
        p.error("--interval 은 1 이상이어야 합니다.")

    if not args.watch:
        return run_once(args)

    import time

    print(f"워치 모드 시작 — {args.interval}초 간격 반복 실행 (종료: Ctrl+C)")
    try:
        while True:
            print("\n" + "=" * 60)
            print(time.strftime("[%Y-%m-%d %H:%M:%S] 워크플로우 실행"))
            run_once(args)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n워치 모드 종료.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
