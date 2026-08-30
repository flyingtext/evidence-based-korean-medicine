#!/usr/bin/env python3
"""Extract a punctuated Markdown transcription from a jicheng.tw book page.

The extractor deliberately uses only the Python standard library.  It treats
elements carrying ``data-sec`` as the stable units of a jicheng.tw edition and
writes machine-readable provenance and validation statistics to stdout (and,
optionally, to a JSON file).
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import html
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen


EXTRACT_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6", "p", "div"}
IGNORED_TAGS = {"script", "style", "template", "noscript"}
HAN_RE = re.compile(
    "[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff"
    "\U00020000-\U0002fa1f]"
)
UNDERLINE_TAG_RE = re.compile(r"\[(/?)u\]", re.IGNORECASE)


@dataclass
class Block:
    tag: str
    sec: str
    parts: list[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        value = html.unescape("".join(self.parts))
        value = re.sub(r"[ \t\r\f\v]+", " ", value)
        value = re.sub(r" *\n *", "\n", value)
        return value.strip()


class JichengParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocks: list[Block] = []
        self._active: list[tuple[str, Block]] = []
        self._ignored_depth = 0
        self.title = ""
        self._in_title = False
        self.metadata: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attr = {key.lower(): (value or "") for key, value in attrs}
        if tag in IGNORED_TAGS:
            self._ignored_depth += 1
            return
        if self._ignored_depth:
            return
        if tag == "title":
            self._in_title = True
        if tag == "meta":
            key = attr.get("name") or attr.get("property")
            if key and attr.get("content"):
                self.metadata[key] = attr["content"]
        if tag in EXTRACT_TAGS and "data-sec" in attr:
            block = Block(tag=tag, sec=attr["data-sec"])
            self.blocks.append(block)
            self._active.append((tag, block))
        if tag == "br":
            for _, block in self._active:
                block.parts.append("\n")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in IGNORED_TAGS:
            self._ignored_depth = max(0, self._ignored_depth - 1)
            return
        if self._ignored_depth:
            return
        if tag == "title":
            self._in_title = False
        for index in range(len(self._active) - 1, -1, -1):
            if self._active[index][0] == tag:
                del self._active[index:]
                break

    def handle_data(self, data: str) -> None:
        if self._ignored_depth:
            return
        if self._in_title:
            self.title += data
        for _, block in self._active:
            block.parts.append(data)


def fetch(url: str, timeout: float) -> tuple[str, str]:
    request = Request(url, headers={"User-Agent": "classics-collation/1.0"})
    with urlopen(request, timeout=timeout) as response:
        raw = response.read()
        charset = response.headers.get_content_charset() or "utf-8"
    return raw.decode(charset, errors="replace"), charset


def korean_punctuation(text: str) -> str:
    """Apply the repository's punctuation convention without changing words."""
    text = text.translate(
        str.maketrans({"。": ".", "！": "!", "？": "?", "，": ",", "；": ";", "：": ":"})
    )
    # jicheng.tw 본문에는 BBCode식 밑줄 표지가 문자 데이터로 남아 있다.
    # Markdown에서 그대로 노출하지 않고 대응하는 안전한 HTML 표지로 렌더링한다.
    return UNDERLINE_TAG_RE.sub(lambda match: "</u>" if match.group(1) else "<u>", text)


def render_markdown(title: str, url: str, blocks: list[Block], page_title: str) -> str:
    lines = [f"# {title}", "", f"> 대조·표점 출처: [{page_title or title}]({url})", ""]
    for block in blocks:
        text = korean_punctuation(block.text)
        if not text:
            continue
        if block.tag.startswith("h"):
            level = max(2, min(6, int(block.tag[1]) + 1))
            lines.extend((f"{'#' * level} {text}", ""))
        else:
            lines.extend((text, ""))
    return "\n".join(lines).rstrip() + "\n"


def han_text(text: str) -> str:
    return "".join(HAN_RE.findall(text))


def validation_stats(markdown: str, source: str | None) -> dict[str, object]:
    extracted = han_text(markdown)
    result: dict[str, object] = {
        "extracted_han_characters": len(extracted),
        "extracted_han_sha256": hashlib.sha256(extracted.encode()).hexdigest(),
    }
    if source is None:
        result["source_comparison"] = "not_requested"
        return result
    original = han_text(source)
    matcher = difflib.SequenceMatcher(None, original, extracted)
    result.update(
        {
            "source_han_characters": len(original),
            "source_han_sha256": hashlib.sha256(original.encode()).hexdigest(),
            "han_length_ratio": round(len(extracted) / len(original), 6) if original else None,
            # ratio()는 수십만 자 판본에서 최악의 경우 지나치게 느리다.
            # quick_ratio()는 전수 문자 구성의 상한 검증이며, 실제 채택 여부는
            # 별도 7자 연속 표본 일치율로 더 엄격하게 판정한다.
            "han_sequence_quick_ratio": round(matcher.quick_ratio(), 6)
            if original and extracted
            else None,
            "han_exact_match": original == extracted,
        }
    )
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="jicheng.tw book index.html URL")
    parser.add_argument("--title", required=True, help="Markdown document title")
    parser.add_argument("--output", required=True, type=Path, help="output Markdown path")
    parser.add_argument("--source", type=Path, help="local unpunctuated source for comparison")
    parser.add_argument("--stats-output", type=Path, help="also write statistics as JSON")
    parser.add_argument("--timeout", type=float, default=30.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.url.startswith(("https://jicheng.tw/", "http://jicheng.tw/")):
        raise SystemExit("--url must point to jicheng.tw")

    document, charset = fetch(args.url, args.timeout)
    parser = JichengParser()
    parser.feed(document)
    blocks = [block for block in parser.blocks if block.text]
    if not blocks:
        raise SystemExit("no non-empty h1-h6/p/div data-sec elements found")

    page_title = re.sub(r"\s+", " ", parser.title).strip()
    markdown = render_markdown(args.title, args.url, blocks, page_title)
    source = args.source.read_text(encoding="utf-8") if args.source else None
    duplicate_sections = sorted(
        sec for sec, count in Counter(block.sec for block in blocks if block.sec).items() if count > 1
    )
    report = {
        "schema_version": 1,
        "source": {
            "url": args.url,
            "site": "jicheng.tw",
            "page_title": page_title,
            "charset": charset,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "html_sha256": hashlib.sha256(document.encode("utf-8")).hexdigest(),
            "page_metadata": parser.metadata,
        },
        "output": str(args.output),
        "blocks": {
            "total": len(blocks),
            "by_tag": dict(sorted(Counter(block.tag for block in blocks).items())),
            "unique_data_sec": len({block.sec for block in blocks if block.sec}),
            "duplicate_data_sec": duplicate_sections,
        },
        "validation": validation_stats(markdown, source),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")
    rendered_report = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.stats_output:
        args.stats_output.parent.mkdir(parents=True, exist_ok=True)
        args.stats_output.write_text(rendered_report, encoding="utf-8")
    sys.stdout.write(rendered_report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
