#!/usr/bin/env python3
"""로컬 전각 공백을 jicheng.tw 문맥과 대조해 결자 교정안을 만든다."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import quote

from convert_classics import load_corrections
from extract_jicheng_punctuated import JichengParser, fetch


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT.parent / "source"
CORRECTIONS = ROOT / "data" / "classics_corrections"
CATALOG = ROOT / "data" / "classics_online_catalog.json"
BOOK_RE = re.compile(r"\[book\](.*?)\[/book\]", re.DOTALL | re.IGNORECASE)
TAG_RE = re.compile(r"\[/?[A-Za-z][A-Za-z0-9]*(?:=[^\]]*)?\]", re.IGNORECASE)
HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


def metadata_and_body(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    match = BOOK_RE.search(text)
    metadata: dict[str, str] = {}
    if match:
        for line in match.group(1).splitlines():
            separator = "：" if "：" in line else ":" if ":" in line else None
            if separator:
                key, value = line.split(separator, 1)
                metadata[key.strip()] = value.strip()
        text = text[: match.start()] + text[match.end() :]
    return metadata, text.strip()


def catalog_url(source_path: str, title: str) -> str:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    for item in catalog["books"]:
        if item["source"] == source_path and item.get("has_data_sec"):
            return item["url"]
    return f"https://jicheng.tw/tcm/book/{quote(title, safe='')}/index.html"


def nearest_han(text: str, index: int, direction: int, count: int) -> str:
    found: list[str] = []
    cursor = index + direction
    while 0 <= cursor < len(text) and len(found) < count:
        if HAN_RE.fullmatch(text[cursor]):
            found.append(text[cursor])
        cursor += direction
    if direction < 0:
        found.reverse()
    return "".join(found)


def unique_context(body: str, index: int) -> str | None:
    for radius in (18, 28, 40, 60):
        value = body[max(0, index - radius) : min(len(body), index + radius + 1)]
        if body.count(value) == 1:
            return value
    return None


def proposals(body: str, online_han: str, url: str, source_path: str) -> tuple[list[dict], dict[str, int]]:
    result: list[dict] = []
    stats = {"total_fullwidth_spaces": body.count("　"), "layout_confirmed": 0, "missing_confirmed": 0, "unresolved": 0}
    for index, char in enumerate(body):
        if char != "　":
            continue
        left = nearest_han(body, index, -1, 14)
        right = nearest_han(body, index, 1, 14)
        if len(left) < 8 or len(right) < 8:
            stats["unresolved"] += 1
            continue
        matches = list(re.finditer(re.escape(left) + r"([\u3400-\u9fff\uf900-\ufaff]{0,4})" + re.escape(right), online_han))
        if len(matches) != 1:
            stats["unresolved"] += 1
            continue
        supplied = matches[0].group(1)
        if not supplied:
            stats["layout_confirmed"] += 1
            continue
        if len(supplied) != 1:
            stats["unresolved"] += 1
            continue
        before = unique_context(body, index)
        if before is None or re.search(r"[A-Za-z0-9]", before):
            stats["unresolved"] += 1
            continue
        relative = index - body.index(before)
        after = before[:relative] + supplied + before[relative + 1 :]
        result.append({
            "before": before,
            "after": after,
            "expected_count": 1,
            "reason": "온라인 판본 고유 문맥 대조 결자 보충",
            "evidence_url": url,
            "evidence_note": f"{source_path}: 좌우 한자 각 14자 고유 일치",
        })
        stats["missing_confirmed"] += 1
    return result, stats


def correction_position(body: str, item: dict) -> int | None:
    before, after = item["before"], item["after"]
    if body.count(before) != 1:
        return None
    prefix = 0
    while prefix < min(len(before), len(after)) and before[prefix] == after[prefix]:
        prefix += 1
    return body.index(before) + prefix


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_path")
    parser.add_argument("--url")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    path = SOURCE_ROOT / args.source_path
    metadata, body = metadata_and_body(path)
    title = metadata.get("書名", path.stem)
    url = args.url or catalog_url(args.source_path, title)
    document, _ = fetch(url, 60)
    html_parser = JichengParser()
    html_parser.feed(document)
    online_han = "".join(HAN_RE.findall("".join(block.text for block in html_parser.blocks)))
    items, stats = proposals(body, online_han, url, args.source_path)
    payload = {"source_path": args.source_path, "title": title, "url": url, "count": len(items), "audit": stats, "corrections": items}
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    if args.apply:
        corrections = load_corrections(CORRECTIONS)
        existing = corrections.get(args.source_path, [])
        seen_positions = {position for item in existing if (position := correction_position(body, item)) is not None}
        added = [item for item in items if correction_position(body, item) not in seen_positions]
        corrections[args.source_path] = existing + added
        shard_name = args.source_path.split("/", 1)[0] + ".json"
        shard_path = CORRECTIONS / shard_name
        shard_payload = {
            key: value for key, value in corrections.items()
            if key.split("/", 1)[0] == args.source_path.split("/", 1)[0]
        }
        CORRECTIONS.mkdir(parents=True, exist_ok=True)
        shard_path.write_text(
            json.dumps(shard_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"교정안 {len(items)}건, 신규 적용 {len(added)}건")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
