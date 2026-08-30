#!/usr/bin/env python3
"""고전 TXT 자료를 추적 가능한 Markdown과 번역 작업 단위로 변환한다.

원본은 읽기만 하며 기본 출력은 docs/원문/_가져오기다. 사람이 정리한 기존
원문과 자동 산출물이 충돌하지 않도록 별도 staging 영역을 사용한다.
"""

from __future__ import annotations

import argparse
import difflib
import fcntl
import hashlib
import json
import re
import shutil
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT.parent / "source"
DEFAULT_OUTPUT = ROOT / "docs" / "원문" / "_가져오기"
DEFAULT_CORRECTIONS = ROOT / "data" / "classics_corrections.json"
DEFAULT_METADATA_OVERRIDES = ROOT / "data" / "classics_metadata_overrides.json"
BOOK_RE = re.compile(r"\[book\](.*?)\[/book\]", re.DOTALL | re.IGNORECASE)
LEGACY_CATALOG_RE = re.compile(
    r"\A(?P<metadata>.*?)\s*<目錄>\s*<篇名>(?P<title>[^\n]+)\s*"
    r"內容[：:]\s*(?P<body>.*?)(?:\s*更新[：:](?P<updated>[^\n]+))?\s*\Z",
    re.DOTALL | re.IGNORECASE,
)
HEADING_RE = re.compile(
    r"^\[h([1-6])\]((?:(?!\[/?h[1-6]\]).)*?)\[/h\1\]\s*$",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)
TAG_RE = re.compile(r"\[(/?)([A-Za-z][A-Za-z0-9]*)(?:=[^\]]*)?\]", re.IGNORECASE)
INLINE_TAGS = {
    "b": ("**", "**"),
    "i": ("*", "*"),
    "u": ("<ins>", "</ins>"),
    "s": ("~~", "~~"),
    # 짧은 歌訣 자료의 [j]는 본문에 끼워 넣은 이문 주석이다.
    "j": ("（", "）"),
    # [djb]는 원자료의 주석 상자 외곽 표식이다. 내부의 강조와 줄바꿈은 보존한다.
    "djb": ("", ""),
    # [dzb]도 판본의 자주(自注) 상자 외곽 표식이며 본문 자체는 그대로 둔다.
    "dzb": ("", ""),
    # [dj]는 장·항목명 표식으로, 본문 안에서는 굵은 소제목으로 보존한다.
    "dj": ("**", "**"),
    # [id]는 조문·목록 번호를 감싸는 식별 표식이다. 번호 내용만 보존한다.
    "id": ("", ""),
}


@dataclass
class Book:
    source_path: Path
    relative_source: str
    source_key: str
    metadata: dict[str, str]
    body: str
    sha256: str
    warnings: list[str] = field(default_factory=list)
    corrections: list[dict] = field(default_factory=list)

    @property
    def title(self) -> str:
        return self.metadata.get("書名") or self.metadata.get("篇名") or self.source_key


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    # utf-8-sig removes a BOM while leaving ordinary UTF-8 untouched.
    return raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")


def parse_metadata(block: str) -> dict[str, str]:
    result: dict[str, str] = {}
    pending_key: str | None = None
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if "：" in line:
            key, value = line.split("：", 1)
        elif ":" in line:
            key, value = line.split(":", 1)
        else:
            if pending_key is not None:
                result[pending_key] = line
                pending_key = None
            continue
        key = key.strip()
        value = value.strip()
        result[key] = value
        pending_key = key if not value else None
    return result


def load_book(
    path: Path,
    source_root: Path,
    metadata_overrides: dict[str, dict[str, str]] | None = None,
) -> Book:
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    match = BOOK_RE.search(text)
    metadata = parse_metadata(match.group(1)) if match else {}
    body = (text[: match.start()] + text[match.end() :]) if match else text
    # 초기 jicheng 내보내기 중 일부는 [book]을 서지 블록이 아니라 문서 전체를
    # 감싸고, <目錄>/<篇名>/內容： 표식 뒤에 본문을 둔다. 이 형식을 일반
    # [book] 메타데이터처럼 제거하면 본문이 통째로 사라지므로 먼저 풀어낸다.
    legacy = LEGACY_CATALOG_RE.match(match.group(1).strip()) if match else None
    if legacy:
        metadata = parse_metadata(legacy.group("metadata"))
        if legacy.group("updated"):
            metadata["更新"] = legacy.group("updated").strip()
        body = f'[h1]{legacy.group("title").strip()}[/h1]\n{legacy.group("body").strip()}'
    rel = path.relative_to(source_root).as_posix()
    if metadata_overrides is None and DEFAULT_METADATA_OVERRIDES.exists():
        metadata_overrides = json.loads(DEFAULT_METADATA_OVERRIDES.read_text(encoding="utf-8"))
    override = (metadata_overrides or {}).get(rel, {})
    if not isinstance(override, dict) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in override.items()
    ):
        raise ValueError(f"유효하지 않은 메타데이터 오버레이: {rel}")
    metadata.update(override)
    key = path.stem
    warnings: list[str] = []
    if not match and not override:
        warnings.append("book 메타데이터 없음")
    if not (metadata.get("書名") or metadata.get("篇名")):
        warnings.append("서명 없음")
    return Book(path, rel, key, metadata, body.strip(), hashlib.sha256(raw).hexdigest(), warnings)


def apply_corrections(book: Book, corrections: dict[str, list[dict]]) -> None:
    original = book.body
    edits: list[tuple[int, int, str]] = []
    for correction in corrections.get(book.relative_source, []):
        before = correction["before"]
        after = correction["after"]
        expected = correction.get("expected_count", 1)
        actual = original.count(before)
        if actual != expected:
            book.warnings.append(f"교정 불일치: {before!r} ({actual}/{expected})")
            continue
        starts = [match.start() for match in re.finditer(re.escape(before), original)]
        local_edits = []
        for start in starts:
            matcher = difflib.SequenceMatcher(a=before, b=after, autojunk=False)
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag != "equal":
                    local_edits.append((start + i1, start + i2, after[j1:j2]))
        edits.extend(local_edits)
        book.corrections.append(correction)
    # 모든 근거 문맥을 수정 전 원문에서 검증한 뒤 뒤쪽 좌표부터 적용한다.
    # 이 방식은 가까운 결자의 문맥이 겹쳐도 앞선 치환이 뒤 교정을 막지 않는다.
    occupied: list[tuple[int, int]] = []
    for start, end, replacement in sorted(edits, reverse=True):
        if any(start < used_end and end > used_start for used_start, used_end in occupied):
            book.warnings.append(f"교정 좌표 중첩: {start}:{end}")
            continue
        book.body = book.body[:start] + replacement + book.body[end:]
        occupied.append((start, end))


def safe_name(value: str, fallback: str) -> str:
    value = unicodedata.normalize("NFC", value).strip()
    value = re.sub(r"[\\/:*?\"<>|]", "-", value)
    value = re.sub(r"\s+", " ", value).strip(" .")
    return value[:120] or fallback


def plain_text(value: str) -> str:
    return TAG_RE.sub("", value).strip()


def slug(value: str, fallback: str) -> str:
    cleaned = safe_name(plain_text(value), fallback)
    cleaned = re.sub(r"\s+", "-", cleaned)
    return cleaned[:80] or fallback


def replace_inline_tags(text: str, warnings: list[str]) -> str:
    for name, (opening, closing) in INLINE_TAGS.items():
        text = re.sub(rf"\[{name}\]", opening, text, flags=re.IGNORECASE)
        text = re.sub(rf"\[/{name}\]", closing, text, flags=re.IGNORECASE)
    text = re.sub(r"\[br\s*/?\]", "  \n", text, flags=re.IGNORECASE)
    text = re.sub(r"\[p\]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\[/p\]", "\n\n", text, flags=re.IGNORECASE)
    # 일부 원자료는 제목 태그 뒤에 본문을 같은 줄에 이어 쓴다. 이 경우
    # 블록 헤딩으로 분리하면 원문 위치가 달라지므로 인라인 강조로 보존한다.
    text = re.sub(r"\[h[1-6]\](.*?)\[/h[1-6]\]", r"**\1**", text, flags=re.IGNORECASE)
    unknown = sorted({m.group(2).lower() for m in TAG_RE.finditer(text)})
    if unknown:
        warnings.append("미처리 태그: " + ", ".join(unknown))
    return text


def translation_chunks(text: str, max_chars: int = 6000) -> list[str]:
    """문단 경계를 우선해 번역 모델에 적당한 크기로 나눈다."""
    text = text.strip()
    if not text:
        return []
    paragraphs = re.split(r"\n\s*\n", text)
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if len(paragraph) > max_chars:
            if current:
                chunks.append(current)
                current = ""
            # 비정상적으로 긴 단일 문단은 문장부호 다음을 우선 경계로 삼는다.
            sentences = re.split(r"(?<=[。！？!?；;])", paragraph)
            piece = ""
            for sentence in sentences:
                if piece and len(piece) + len(sentence) > max_chars:
                    chunks.append(piece)
                    piece = ""
                if len(sentence) > max_chars:
                    chunks.extend(sentence[i : i + max_chars] for i in range(0, len(sentence), max_chars))
                else:
                    piece += sentence
            if piece:
                chunks.append(piece)
            continue
        candidate = paragraph if not current else current + "\n\n" + paragraph
        if len(candidate) > max_chars:
            chunks.append(current)
            current = paragraph
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


def split_h2(book: Book) -> list[tuple[str, str]]:
    matches = [m for m in HEADING_RE.finditer(book.body) if int(m.group(1)) <= 2]
    if not matches:
        return [(book.title, book.body)]
    parts: list[tuple[str, str]] = []
    prefix = book.body[: matches[0].start()].strip()
    if prefix:
        parts.append(("머리말", prefix))
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(book.body)
        title = plain_text(match.group(2)) or f"부분-{index + 1}"
        content = book.body[match.end() : end].strip()
        parts.append((title, content))
    return parts


def convert_part(book: Book, part_index: int, title: str, content: str) -> tuple[str, list[dict]]:
    source_id = f"{book.source_key}:p{part_index:03d}"
    lines = [
        f"# {title}",
        "",
        f"<!-- source-id: {source_id} -->",
        f"> 서명: {book.title}",
        f"> 원본 파일: `{book.relative_source}`",
        f"> 원본 SHA-256: `{book.sha256}`",
        ("> 상태: 인터넷 판본 1차 결자 대조 완료·전면 교감 전"
         if book.corrections else "> 상태: 자동 변환 원문·정본 미대조"),
        "",
    ]
    tasks: list[dict] = []
    cursor = 0
    section_no = 0
    headings = list(HEADING_RE.finditer(content))
    for match in headings:
        preceding = content[cursor : match.start()].strip()
        if preceding:
            lines.append(replace_inline_tags(preceding, book.warnings))
            lines.append("")
        section_no += 1
        original_level = int(match.group(1))
        md_level = min(6, max(2, original_level - 1))
        heading = replace_inline_tags(match.group(2).strip(), book.warnings)
        section_id = f"{source_id}:s{section_no:04d}"
        lines.extend(["#" * md_level + " " + heading, "", f"<!-- source-id: {section_id} -->", ""])
        next_start = headings[section_no].start() if section_no < len(headings) else len(content)
        section_text = content[match.end() : next_start].strip()
        translated_text = replace_inline_tags(section_text, book.warnings)
        chunks = translation_chunks(translated_text)
        for chunk_index, chunk in enumerate(chunks, 1):
            tasks.append({
                "source_id": section_id if len(chunks) == 1 else f"{section_id}:c{chunk_index:04d}",
                "parent_source_id": section_id,
                "chunk_index": chunk_index,
                "chunk_count": len(chunks),
                "book": book.title,
                "heading": plain_text(match.group(2)),
                "source_path": book.relative_source,
                "text": chunk,
            })
        cursor = match.end()
    tail = content[cursor:].strip()
    if tail:
        lines.append(replace_inline_tags(tail, book.warnings))
        lines.append("")
    if not headings and content.strip():
        translated_text = replace_inline_tags(content.strip(), book.warnings)
        chunks = translation_chunks(translated_text)
        for chunk_index, chunk in enumerate(chunks, 1):
            tasks.append({
                "source_id": source_id if len(chunks) == 1 else f"{source_id}:c{chunk_index:04d}",
                "parent_source_id": source_id,
                "chunk_index": chunk_index,
                "chunk_count": len(chunks),
                "book": book.title,
                "heading": title,
                "source_path": book.relative_source,
                "text": chunk,
            })
    rendered = "\n".join(lines)
    rendered = re.sub(r"[ \t]+$", "", rendered, flags=re.MULTILINE)
    return rendered.rstrip() + "\n", tasks


def book_readme(book: Book, outputs: list[tuple[str, str]], has_punctuated: bool = False) -> str:
    meta = book.metadata
    lines = [
        f"# {book.title}",
        "",
        "> 이 문서는 jicheng.tw의 고전 의서 데이터를 기반으로 자동 생성했다. 정본과 대조하기 전에는 교감 완료 원문으로 간주하지 않는다.",
        "",
        "## 서지 정보",
        "",
        f"- 원본 파일: `{book.relative_source}`",
        f"- SHA-256: `{book.sha256}`",
    ]
    for key in ("作者", "朝代", "年份", "出處", "更新"):
        if meta.get(key):
            lines.append(f"- {key}: {meta[key]}")
    if book.corrections:
        lines.append(f"- 인터넷 대조 교정: {len(book.corrections)}건 (`corrections-applied.json` 참조)")
        lines.append("- 교감 상태: 인터넷 판본 1차 결자 대조 완료·전면 교감 전")
    lines.extend(["", "## 원문 목차", ""])
    lines.extend(f"- [{title}]({filename})" for filename, title in outputs)
    lines.extend([
        "",
        "## 번역 작업 원칙",
        "",
        "번역은 `translation-tasks.jsonl`의 `source_id`를 유지해 별도 산출물로 작성한다. 원문의 글자·표점·결자를 번역 과정에서 수정하지 않으며, 직역과 역자 해설을 구분한다.",
        "",
    ])
    if has_punctuated:
        lines.extend([
            "## 표점본",
            "",
            "- [표점본](표점본.md) — 원문 보존본과 분리된 검증 완료 파생본",
            "- 검증 근거: `punctuation-report.json`",
            "",
        ])
    return "\n".join(lines)


def collation_record(book: Book) -> str:
    """적용된 교정의 범위와 근거를 원서 단위로 명시한다."""
    urls = sorted({item.get("evidence_url", "") for item in book.corrections if item.get("evidence_url")})
    lines = [
        f"# {book.title} 교감 기록",
        "",
        "## 현재 상태",
        "",
        "인터넷 판본과의 1차 결자 대조를 완료했다. 이 기록은 결락된 글자를 보충한 결과이며, 이체자·표점·판본 간 문구 차이까지 확정한 전면 교감본을 뜻하지 않는다.",
        "",
        "## 대조 범위",
        "",
        f"- 원자료: `{book.relative_source}`",
        f"- 원자료 SHA-256: `{book.sha256}`",
        f"- 확인·적용한 교정: {len(book.corrections)}건",
        "- 적용 내역: `corrections-applied.json`",
        "- 판정 방법: 원자료의 전각 공백 위치와 대조 판본의 문자를 장·절 순서와 앞뒤 문맥으로 대응시키고, 문맥이 유일하게 일치하는 항목만 반영",
        "",
        "## 대조 판본",
        "",
    ]
    lines.extend(f"- {url}" for url in urls)
    lines.extend([
        "",
        "## 유보 사항",
        "",
        "비결자 차이, 이체자, 표점 및 판본별 증감은 후속 교감에서 별도로 판정한다. 번역은 해당 판정이 끝나기 전까지 원문과 역자 주를 분리해 진행한다.",
        "",
    ])
    return "\n".join(lines)


def convert_book(book: Book, output_root: Path) -> dict:
    book_dir = output_root / f"{safe_name(book.title, book.source_key)}({book.source_key})"
    supplemental_names = {"표점본.md", "punctuation-report.json"}
    supplemental: dict[str, bytes] = {}
    if book_dir.exists():
        for name in supplemental_names:
            path = book_dir / name
            if path.is_file():
                supplemental[name] = path.read_bytes()
        # book_dir는 output_root와 원본 키로 결정된 자동 산출물 경로다.
        # 재실행 때 이전 분할 파일이 남아 검증을 왜곡하지 않게 원서 단위로 교체한다.
        shutil.rmtree(book_dir)
    book_dir.mkdir(parents=True, exist_ok=True)
    outputs: list[tuple[str, str]] = []
    tasks: list[dict] = []
    used: set[str] = set()
    for index, (title, content) in enumerate(split_h2(book), 1):
        base = f"{index:03d}-{slug(title, f'부분-{index}') }"
        filename = base + ".md"
        suffix = 2
        while filename in used:
            filename = f"{base}-{suffix}.md"
            suffix += 1
        used.add(filename)
        rendered, part_tasks = convert_part(book, index, title, content)
        (book_dir / filename).write_text(rendered, encoding="utf-8")
        outputs.append((filename, title))
        for task in part_tasks:
            task["target_original"] = f"{book_dir.relative_to(output_root).as_posix()}/{filename}"
        tasks.extend(part_tasks)
    (book_dir / "README.md").write_text(
        book_readme(book, outputs, has_punctuated="표점본.md" in supplemental), encoding="utf-8"
    )
    (book_dir / "corrections-applied.json").write_text(
        json.dumps(book.corrections, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if book.corrections:
        (book_dir / "교감기록.md").write_text(collation_record(book), encoding="utf-8")
    for name, content in supplemental.items():
        (book_dir / name).write_bytes(content)
    with (book_dir / "translation-tasks.jsonl").open("w", encoding="utf-8") as handle:
        for task in tasks:
            handle.write(json.dumps(task, ensure_ascii=False) + "\n")
    return {
        "source_path": book.relative_source,
        "source_key": book.source_key,
        "sha256": book.sha256,
        "metadata": book.metadata,
        "output_directory": book_dir.relative_to(output_root).as_posix(),
        "markdown_files": len(outputs),
        "translation_units": len(tasks),
        "corrections_applied": len(book.corrections),
        "punctuated": "표점본.md" in supplemental,
        "warnings": sorted(set(book.warnings)),
    }


def collection_readme(manifest: list[dict]) -> str:
    corrected_count = sum(bool(item.get("corrections_applied")) for item in manifest)
    punctuated_count = sum(bool(item.get("punctuated")) for item in manifest)
    lines = [
        "# 자동 변환 고전 원문",
        "",
        "> 이 문서들은 jicheng.tw의 고전 의서 데이터를 기반으로 자동 생성했다. 정본 대조와 교감이 완료된 판본이 아니며, 원본 경로와 SHA-256은 `manifest.json`에서 확인할 수 있다.",
        "",
        f"총 {len(manifest)}개 원자료를 수록한다. 결자 교정이 적용된 문헌은 {corrected_count}권, 검증된 표점본이 있는 문헌은 {punctuated_count}권이다. 각 원서의 `translation-tasks.jsonl`은 `source_id`로 원문과 연결되는 Codex 번역 작업 단위다.",
        "",
        "## 원서 목록",
        "",
    ]
    current_group = None
    for item in manifest:
        group = item["source_path"].split("/", 1)[0] if "/" in item["source_path"] else "기타"
        if group != current_group:
            lines.extend([f"### {group}", ""])
            current_group = group
        metadata = item.get("metadata", {})
        title = metadata.get("書名") or metadata.get("篇名") or item["source_key"]
        directory = item.get("output_directory")
        if directory:
            lines.append(f"- [{title} ({item['source_key']})]({directory}/README.md)")
        else:
            lines.append(f"- {title} ({item['source_key']})")
    lines.extend(["", "## 상태 표기", "", "개별 README의 ‘자동 변환 원문·정본 미대조’ 표기는 텍스트 구조만 변환했으며 판본 대조, 교감, 번역 검수가 아직 끝나지 않았음을 뜻한다.", ""])
    return "\n".join(lines)


def discover(source: Path, patterns: list[str]) -> list[Path]:
    paths = sorted(source.rglob("*.txt"))
    if not patterns:
        return paths
    return [p for p in paths if any(re.search(pattern, p.relative_to(source).as_posix()) for pattern in patterns)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--include", action="append", default=[], help="원본 상대경로 정규식(반복 가능)")
    parser.add_argument("--catalog-only", action="store_true")
    parser.add_argument("--corrections", type=Path, default=DEFAULT_CORRECTIONS)
    parser.add_argument("--metadata-overrides", type=Path, default=DEFAULT_METADATA_OVERRIDES)
    args = parser.parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    metadata_overrides = {}
    if args.metadata_overrides.exists():
        metadata_overrides = json.loads(args.metadata_overrides.read_text(encoding="utf-8"))
    books = [
        load_book(path, source, metadata_overrides)
        for path in discover(source, args.include)
    ]
    corrections = {}
    if args.corrections.exists():
        corrections = json.loads(args.corrections.read_text(encoding="utf-8"))
    for book in books:
        apply_corrections(book, corrections)
    converted = []
    for book in books:
        if args.catalog_only:
            converted.append({
                "source_path": book.relative_source,
                "source_key": book.source_key,
                "sha256": book.sha256,
                "metadata": book.metadata,
                "warnings": book.warnings,
            })
        else:
            converted.append(convert_book(book, output))

    # 부분 변환은 기존 전권 목록에 증분 병합한다. 파일 잠금과 원자적 교체로
    # 여러 문헌을 병렬 교감해도 마지막 단권이 전체 목록을 덮어쓰지 않게 한다.
    lock_path = output / ".catalog.lock"
    with lock_path.open("w", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        manifest_path = output / "manifest.json"
        if args.include and manifest_path.is_file():
            existing = json.loads(manifest_path.read_text(encoding="utf-8")).get("books", [])
            by_source = {item["source_path"]: item for item in existing}
            by_source.update({item["source_path"]: item for item in converted})
            manifest = sorted(by_source.values(), key=lambda item: item["source_path"])
        else:
            manifest = converted
        payload = {"source_root": str(source), "count": len(manifest), "books": manifest}
        manifest_tmp = output / ".manifest.json.tmp"
        readme_tmp = output / ".README.md.tmp"
        manifest_tmp.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        readme_tmp.write_text(collection_readme(manifest), encoding="utf-8")
        manifest_tmp.replace(manifest_path)
        readme_tmp.replace(output / "README.md")
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
    print(f"처리 완료: {len(converted)}권 → {output} (목록 {len(manifest)}권)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
