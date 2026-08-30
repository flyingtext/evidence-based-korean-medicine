#!/usr/bin/env python3
"""승인된 jicheng.tw 대응 판본에서 원서별 보존형 표점본을 생성한다."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT.parent / "source"
DEFAULT_OUTPUT = ROOT / "docs" / "원문" / "_가져오기"
DEFAULT_CONFIG = ROOT / "data" / "classics_punctuation_sources.json"
HAN_RE = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")
PUNCTUATION_RE = re.compile(r"[.,!?;:]")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--include", action="append", default=[])
    parser.add_argument("--min-punctuation-density", type=float, default=0.005)
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    manifest = json.loads((args.output / "manifest.json").read_text(encoding="utf-8"))
    by_source = {book["source_path"]: book for book in manifest["books"]}
    generated = 0
    for item in config["books"]:
        source_path = item["source_path"]
        if item.get("status") != "alignment_approved":
            continue
        if args.include and not any(pattern in source_path for pattern in args.include):
            continue
        book = by_source[source_path]
        book_dir = args.output / book["output_directory"]
        command = [
            sys.executable,
            str(ROOT / "scripts" / "extract_jicheng_punctuated.py"),
            "--url", item["url"],
            "--title", item["title"] + " 표점본",
            "--source", str(args.source / source_path),
            "--output", str(book_dir / "표점본.md"),
            "--stats-output", str(book_dir / "punctuation-report.json"),
        ]
        completed = subprocess.run(command, text=True, capture_output=True)
        if completed.returncode:
            print(f"실패 {source_path}: {completed.stderr.strip()}", file=sys.stderr)
            return completed.returncode
        report_path = book_dir / "punctuation-report.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        report["source_path"] = source_path
        report["approval"] = {
            "status": "approved",
            "basis": "CJK 7자 표본 일치율 0.92 이상",
            "sampled_7gram_match_ratio": item["sampled_7gram_match_ratio"],
        }
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        punctuated_path = book_dir / "표점본.md"
        punctuated = punctuated_path.read_text(encoding="utf-8")
        han_count = len(HAN_RE.findall(punctuated))
        density = len(PUNCTUATION_RE.findall(punctuated)) / max(han_count, 1)
        report["validation"]["punctuation_density"] = round(density, 6)
        if density < args.min_punctuation_density:
            punctuated_path.unlink()
            report_path.unlink()
            print(f"유보 {source_path}: 온라인 판본 표점 밀도 {density:.6f}")
            continue
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        readme_path = book_dir / "README.md"
        readme = readme_path.read_text(encoding="utf-8").rstrip()
        marker = "\n\n## 표점본\n"
        if marker in readme:
            readme = readme.split(marker, 1)[0].rstrip()
        readme += (
            "\n\n## 표점본\n\n"
            "- [표점본](표점본.md) — jicheng.tw 대응 판본의 표점을 이식하고 문자 일치도를 검증한 파생본\n"
            "- 검증 근거: `punctuation-report.json`\n"
        )
        readme_path.write_text(readme, encoding="utf-8")
        generated += 1
        print(f"생성 {source_path} → {book_dir.name}/표점본.md")
    print(f"표점본 생성 완료: {generated}권")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
