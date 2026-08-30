#!/usr/bin/env python3
"""고전 원자료에서 결자·깨진 문자 후보를 찾아 인터넷 대조 대기열을 만든다."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT.parent / "source"
DEFAULT_OUTPUT = ROOT / "docs" / "원문" / "_가져오기" / "correction-candidates"
CJK = r"\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF"
# 전각 공백은 판면 정렬에도 널리 쓰이므로 모두 후보로 잡지 않는다. 문장부호에
# 바로 붙어 어휘가 끊긴 형태만 1차 후보로 삼아 오탐을 제한한다.
SUSPICIOUS_SPACE = re.compile(rf"(?:[{CJK}]　[。！？；，、]|[，、；：]　[{CJK}])")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--chunk-lines", type=int, default=10_000)
    args = parser.parse_args()
    source = args.source.resolve()
    candidates: list[dict] = []
    for path in sorted(source.rglob("*.txt")):
        text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
        rel = path.relative_to(source).as_posix()
        for line_no, line in enumerate(text.splitlines(), 1):
            for match in SUSPICIOUS_SPACE.finditer(line):
                start = max(0, match.start() - 35)
                end = min(len(line), match.end() + 35)
                context = line[start:end]
                candidates.append({
                    "source_path": rel,
                    "line": line_no,
                    "kind": "fullwidth-space-between-text",
                    "context": context,
                    "search_query": f'"{context[:70]}"',
                    "status": "internet-check-required",
                })
    args.output.mkdir(parents=True, exist_ok=True)
    for old_part in args.output.glob("part-*.jsonl"):
        old_part.unlink()
    parts = []
    for offset in range(0, len(candidates), args.chunk_lines):
        part = args.output / f"part-{offset // args.chunk_lines + 1:04d}.jsonl"
        with part.open("w", encoding="utf-8") as handle:
            for item in candidates[offset : offset + args.chunk_lines]:
                handle.write(json.dumps(item, ensure_ascii=False) + "\n")
        parts.append(part)
    index = [
        "# 인터넷 교감 후보",
        "",
        f"총 {len(candidates)}건을 {len(parts)}개 파일로 나눴다. 각 항목은 인터넷 대조 전 후보이며 자동 교정 근거가 아니다.",
        "",
    ]
    index.extend(f"- `{part.name}`" for part in parts)
    (args.output / "README.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    legacy = args.output.parent / "correction-candidates.jsonl"
    if legacy.exists():
        legacy.unlink()
    print(f"교감 후보: {len(candidates)}건, {len(parts)}개 조각 → {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
