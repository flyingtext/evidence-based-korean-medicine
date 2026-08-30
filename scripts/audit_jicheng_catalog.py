#!/usr/bin/env python3
"""원자료 서명과 jicheng.tw 문헌 페이지의 대응 여부를 점검한다.

서명을 URL 경로로 인용해 요청하고 HTTP 상태, 최종 URL, ``data-sec`` 표식과
응답 크기를 기록한다. 결과는 요청이 끝날 때마다 원자적으로 저장하므로 중단 후
``--resume``으로 이어서 실행할 수 있다.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import json
import os
import random
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT.parent / "source"
DEFAULT_OUTPUT = ROOT / "data" / "classics_online_catalog.json"
BOOK_RE = re.compile(r"\[book\](.*?)\[/book\]", re.DOTALL | re.IGNORECASE)
TITLE_RE = re.compile(r"^\s*書名\s*[：:]\s*(.*?)\s*$", re.MULTILINE)
DATA_SEC_RE = re.compile(br"\bdata-sec\s*=")
TRANSIENT_STATUS = {408, 425, 429, 500, 502, 503, 504}
# 사이트의 실제 경로가 원자료 書名을 단순 인용한 값과 다른 예외다. 슬래시는
# jicheng.tw가 문헌/하위편을 표현하는 경로 구분자로 사용하므로 보존한다.
URL_SLUG_OVERRIDES = {
    "A/A000a.txt": "黃帝內經素問遺篇_1",
    "B/B015.txt": "證治準繩/傷寒",
    "P/P0101.txt": "證治準繩/傷寒",
    "C/C011.txt": "本草品彙精要",
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def load_books(source_root: Path) -> list[dict[str, str]]:
    books: list[dict[str, str]] = []
    for path in sorted(source_root.rglob("*.txt")):
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        block = BOOK_RE.search(text)
        title_match = TITLE_RE.search(block.group(1) if block else text)
        title = title_match.group(1).strip() if title_match else path.stem
        relative_source = path.relative_to(source_root).as_posix()
        url_slug = URL_SLUG_OVERRIDES.get(relative_source, title)
        encoded = "/".join(urllib.parse.quote(part, safe="") for part in url_slug.split("/"))
        books.append(
            {
                "source": relative_source,
                "source_id": path.stem,
                "title": title,
                "url_slug": url_slug,
                "url": f"https://jicheng.tw/tcm/book/{encoded}/index.html",
            }
        )
    return books


def fetch(book: dict[str, str], timeout: float, retries: int) -> dict:
    checked_at = utc_now()
    last_error: str | None = None
    for attempt in range(1, retries + 2):
        request = urllib.request.Request(
            book["url"],
            headers={
                "User-Agent": "evidence-based-korean-medicine-catalog-audit/1.0",
                "Accept": "text/html,application/xhtml+xml",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = response.read()
                status = response.status
                return {
                    **book,
                    "http_status": status,
                    "final_url": response.geturl(),
                    "has_data_sec": bool(DATA_SEC_RE.search(body)),
                    "data_sec_count": len(DATA_SEC_RE.findall(body)),
                    "html_bytes": len(body),
                    "checked_at": checked_at,
                    "attempts": attempt,
                    "error": None,
                }
        except urllib.error.HTTPError as exc:
            body = exc.read()
            if exc.code not in TRANSIENT_STATUS or attempt > retries:
                return {
                    **book,
                    "http_status": exc.code,
                    "final_url": exc.geturl(),
                    "has_data_sec": bool(DATA_SEC_RE.search(body)),
                    "data_sec_count": len(DATA_SEC_RE.findall(body)),
                    "html_bytes": len(body),
                    "checked_at": checked_at,
                    "attempts": attempt,
                    "error": f"HTTP {exc.code}",
                }
            last_error = f"HTTP {exc.code}"
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt > retries:
                break
        time.sleep(min(8.0, 0.75 * (2 ** (attempt - 1))) + random.random() * 0.25)
    return {
        **book,
        "http_status": None,
        "final_url": None,
        "has_data_sec": False,
        "data_sec_count": 0,
        "html_bytes": 0,
        "checked_at": checked_at,
        "attempts": retries + 1,
        "error": last_error or "unknown error",
    }


def load_existing(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {item["source"]: item for item in payload.get("books", [])}


def write_catalog(path: Path, records: dict[str, dict], source_count: int) -> None:
    books = sorted(records.values(), key=lambda item: item["source"])
    payload = {
        "schema_version": 1,
        "generated_at": utc_now(),
        "source_count": source_count,
        "checked_count": len(books),
        "summary": {
            "http_200": sum(item.get("http_status") == 200 for item in books),
            "http_404": sum(item.get("http_status") == 404 for item in books),
            "with_data_sec": sum(bool(item.get("has_data_sec")) for item in books),
            "request_errors": sum(item.get("http_status") is None for item in books),
        },
        "books": books,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--workers", type=int, default=8, choices=range(1, 9), metavar="1..8")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--resume", action="store_true", help="이미 기록된 source 항목은 건너뛴다")
    parser.add_argument("--limit", type=int, help="개발·점검용 최대 요청 수")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    books = load_books(args.source.resolve())
    records = load_existing(args.output) if args.resume else {}
    pending = [book for book in books if book["source"] not in records]
    if args.limit is not None:
        pending = pending[: args.limit]
    print(f"source={len(books)} existing={len(records)} pending={len(pending)} workers={args.workers}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(fetch, book, args.timeout, args.retries): book for book in pending}
        for completed, future in enumerate(concurrent.futures.as_completed(futures), 1):
            book = futures[future]
            try:
                record = future.result()
            except Exception as exc:  # 한 비정상 응답이 전수 점검을 중단시키지 않게 한다.
                record = {
                    **book,
                    "http_status": None,
                    "final_url": None,
                    "has_data_sec": False,
                    "data_sec_count": 0,
                    "html_bytes": 0,
                    "checked_at": utc_now(),
                    "attempts": args.retries + 1,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            records[record["source"]] = record
            write_catalog(args.output, records, len(books))
            if completed % 25 == 0 or completed == len(pending):
                print(f"checked={completed}/{len(pending)} total_recorded={len(records)}")
    if not pending:
        write_catalog(args.output, records, len(books))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
