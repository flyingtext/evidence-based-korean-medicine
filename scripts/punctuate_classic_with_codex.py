#!/usr/bin/env python3
"""Codex CLI로 한문 원문의 문자를 보존하며 표점만 추가한다.

입력의 ``[book]`` 메타데이터는 제외하고 ``[h1]``~``[h6]`` 구조는 Markdown
헤딩으로 옮긴다. 본문은 경계가 안정적인 작은 청크로 나누며, 각 응답에서
표점을 제거한 문자열이 입력과 완전히 같을 때만 결과를 채택한다.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
import time
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from convert_classics import DEFAULT_CORRECTIONS, DEFAULT_SOURCE, apply_corrections, load_book


ROOT = Path(__file__).resolve().parents[1]
BOOK_RE = re.compile(r"\[book\].*?\[/book\]", re.DOTALL | re.IGNORECASE)
HEADING_RE = re.compile(
    r"\[h([1-6])\](.*?)\[/h\1\]", re.DOTALL | re.IGNORECASE
)
CHINESE_TO_ASCII = str.maketrans(
    {
        "。": ".",
        "．": ".",
        "，": ",",
        "、": ",",
        "；": ";",
        "：": ":",
        "！": "!",
        "？": "?",
        "（": "(",
        "）": ")",
        "［": "[",
        "］": "]",
        "｛": "{",
        "｝": "}",
        "「": '"',
        "」": '"',
        "『": '"',
        "』": '"',
        "《": '"',
        "》": '"',
        "〈": '"',
        "〉": '"',
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "…": "...",
        "—": "--",
        "―": "--",
    }
)
ASCII_PUNCT_RE = re.compile(r"[.,!?;:]")


@dataclass(frozen=True)
class Block:
    kind: str
    text: str
    level: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="[book]/[hN] 태그가 있는 UTF-8 TXT")
    parser.add_argument("output", type=Path, help="생성할 Markdown 파일")
    parser.add_argument("report", type=Path, help="생성 보고서 JSON 파일")
    parser.add_argument("--title", required=True, help="Markdown 문서 제목")
    parser.add_argument("--model", help="codex exec에 전달할 모델(생략 시 사용자 기본값)")
    parser.add_argument("--codex", default="codex", help="Codex CLI 실행 파일")
    parser.add_argument("--checkpoint", type=Path, help="체크포인트 경로")
    parser.add_argument("--target-chars", type=int, default=2500)
    parser.add_argument("--min-chars", type=int, default=2000)
    parser.add_argument("--max-chars", type=int, default=3000)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=600, help="청크당 제한 시간(초)")
    args = parser.parse_args()
    if not 1 <= args.min_chars <= args.target_chars <= args.max_chars:
        parser.error("청크 크기는 1 <= min <= target <= max여야 합니다")
    if args.retries < 1:
        parser.error("--retries는 1 이상이어야 합니다")
    if args.timeout < 1:
        parser.error("--timeout은 1 이상이어야 합니다")
    return args


def read_source(path: Path) -> tuple[str, str]:
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    body = BOOK_RE.sub("", text).strip()
    return body, hashlib.sha256(raw).hexdigest()


def parse_blocks(body: str) -> list[Block]:
    blocks: list[Block] = []
    cursor = 0
    for match in HEADING_RE.finditer(body):
        if match.start() > cursor:
            blocks.append(Block("text", body[cursor : match.start()]))
        blocks.append(Block("heading", match.group(2).strip(), int(match.group(1))))
        cursor = match.end()
    if cursor < len(body):
        blocks.append(Block("text", body[cursor:]))
    return [block for block in blocks if block.kind == "heading" or block.text]


def choose_boundary(text: str, start: int, target: int, minimum: int, maximum: int) -> int:
    remaining = len(text) - start
    if remaining <= maximum:
        return len(text)
    low = start + minimum
    ideal = min(start + target, len(text))
    high = min(start + maximum, len(text))
    # 문단/줄 경계, 공백 순으로 가까운 안전 경계를 고른다.
    candidates: list[tuple[int, int]] = []
    for marker, priority in (("\n\n", 0), ("\n", 1), ("　", 2), (" ", 3)):
        pos = text.find(marker, ideal, high)
        if pos >= 0:
            candidates.append((abs(pos + len(marker) - ideal) + priority * maximum, pos + len(marker)))
        pos = text.rfind(marker, low, ideal)
        if pos >= 0:
            candidates.append((abs(pos + len(marker) - ideal) + priority * maximum, pos + len(marker)))
    return min(candidates)[1] if candidates else ideal


def split_text(text: str, target: int, minimum: int, maximum: int) -> list[str]:
    if not text:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = choose_boundary(text, start, target, minimum, maximum)
        chunks.append(text[start:end])
        start = end
    assert "".join(chunks) == text
    return chunks


def batch_indices(pieces: list[tuple[int, str]], target: int, maximum: int) -> list[list[int]]:
    """짧은 절을 표식으로 묶어 호출 수를 줄인다."""
    groups: list[list[int]] = []
    current: list[int] = []
    size = 0
    for index, (_, chunk) in enumerate(pieces):
        extra = len(chunk) + (32 if current else 0)
        if current and size + extra > maximum:
            groups.append(current)
            current = []
            size = 0
        current.append(index)
        size += extra
        if size >= target:
            groups.append(current)
            current = []
            size = 0
    if current:
        groups.append(current)
    return groups


def batch_delimiter(index: int) -> str:
    return f"<<<CODEX_SEGMENT_{index:06d}>>>"


def is_punctuation(char: str) -> bool:
    return unicodedata.category(char).startswith("P") or char in {"…", "—", "―"}


def without_punctuation(text: str) -> str:
    return "".join(char for char in text if not is_punctuation(char) and not char.isspace())


def normalize_punctuation(text: str) -> str:
    return text.translate(CHINESE_TO_ASCII)


def extract_response(value: str) -> str:
    value = value.strip()
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError("Codex 응답이 JSON 객체가 아닙니다") from exc
    if not isinstance(parsed, dict) or not isinstance(parsed.get("text"), str):
        raise ValueError("Codex 응답에 문자열 text 필드가 없습니다")
    return parsed["text"]


def make_prompt(chunk: str) -> str:
    return (
        "다음 한문 원문에 문맥에 맞는 표점만 추가하라. 한자, 공백, 줄바꿈, "
        "숫자, 라틴 문자 등 기존의 비표점 문자는 단 하나도 추가·삭제·교체·이동하지 "
        "말라. 설명, Markdown, 번역을 덧붙이지 말라. 중국식 표점 대신 ASCII 표점 "
        "(. , ! ? ; :)을 사용하라. 반드시 {\"text\": \"...\"} JSON 객체 하나로 "
        "응답하라.\n\n<원문>\n" + chunk + "\n</원문>"
    )


def run_codex(
    executable: str,
    chunk: str,
    model: str | None,
    timeout: int,
    schema_path: Path,
    workdir: Path,
) -> str:
    result_fd, result_name = tempfile.mkstemp(prefix="codex-punctuation-", suffix=".json")
    os.close(result_fd)
    result_path = Path(result_name)
    command = [
        executable,
        "exec",
        "--ephemeral",
        "--ignore-rules",
        "--skip-git-repo-check",
        "-s",
        "read-only",
        "-C",
        str(workdir),
        "--output-schema",
        str(schema_path),
        "--output-last-message",
        str(result_path),
    ]
    if model:
        command.extend(["--model", model])
    command.append("-")
    try:
        completed = subprocess.run(
            command,
            input=make_prompt(chunk),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        if completed.returncode:
            detail = completed.stderr.strip() or completed.stdout.strip()
            raise RuntimeError(f"codex exec 실패({completed.returncode}): {detail[-1000:]}")
        return extract_response(result_path.read_text(encoding="utf-8"))
    finally:
        result_path.unlink(missing_ok=True)


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        temporary = Path(handle.name)
    temporary.replace(path)


def load_checkpoint(path: Path, identity: dict[str, Any], count: int) -> dict[str, Any]:
    if not path.exists():
        return {"identity": identity, "chunks": [None] * count}
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("identity") != identity:
        raise RuntimeError(f"입력 또는 실행 설정과 맞지 않는 체크포인트입니다: {path}")
    chunks = data.get("chunks")
    if not isinstance(chunks, list) or len(chunks) != count:
        raise RuntimeError(f"청크 수가 맞지 않는 체크포인트입니다: {path}")
    return data


def main() -> int:
    args = parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    report_path = args.report.resolve()
    checkpoint = (args.checkpoint or output.with_suffix(output.suffix + ".checkpoint.json")).resolve()
    raw = source.read_bytes()
    source_sha256 = hashlib.sha256(raw).hexdigest()
    book = load_book(source, DEFAULT_SOURCE.resolve())
    corrections_raw = DEFAULT_CORRECTIONS.read_bytes()
    corrections = json.loads(corrections_raw.decode("utf-8"))
    apply_corrections(book, corrections)
    applied_correction_count = len(book.corrections)
    if book.warnings:
        raise RuntimeError(f"교정 오버레이 적용 경고 {len(book.warnings)}건: {book.warnings[:3]}")
    body = book.body
    blocks = parse_blocks(body)

    pieces: list[tuple[int, str]] = []
    expanded: list[Block] = []
    for block in blocks:
        if block.kind == "heading":
            expanded.append(block)
            continue
        for chunk in split_text(block.text, args.target_chars, args.min_chars, args.max_chars):
            pieces.append((len(expanded), chunk))
            expanded.append(Block("chunk", chunk))

    identity = {
        "source_sha256": source_sha256,
        "corrections_sha256": hashlib.sha256(corrections_raw).hexdigest(),
        "applied_corrections": applied_correction_count,
        "title": args.title,
        "model": args.model or "codex-default",
        "target_chars": args.target_chars,
        "min_chars": args.min_chars,
        "max_chars": args.max_chars,
        "batch_version": 1,
    }
    state = load_checkpoint(checkpoint, identity, len(pieces))
    schema = {
        "type": "object",
        "properties": {"text": {"type": "string"}},
        "required": ["text"],
        "additionalProperties": False,
    }
    with tempfile.TemporaryDirectory(prefix="codex-punctuation-schema-") as temp_dir:
        schema_path = Path(temp_dir) / "schema.json"
        schema_path.write_text(json.dumps(schema), encoding="utf-8")
        for group in batch_indices(pieces, args.target_chars, args.max_chars):
            pending = []
            for index in group:
                chunk = pieces[index][1]
                saved = state["chunks"][index]
                if isinstance(saved, dict) and isinstance(saved.get("text"), str):
                    if without_punctuation(saved["text"]) == without_punctuation(chunk):
                        continue
                pending.append(index)
            if not pending:
                continue
            combined = pieces[pending[0]][1]
            for index in pending[1:]:
                combined += "\n" + batch_delimiter(index) + "\n" + pieces[index][1]
            failures: list[str] = []
            for attempt in range(1, args.retries + 1):
                try:
                    candidate = normalize_punctuation(
                        run_codex(
                            args.codex,
                            combined,
                            args.model,
                            args.timeout,
                            schema_path,
                            source.parent,
                        )
                    )
                    outputs = [candidate]
                    if len(pending) > 1:
                        pattern = "|".join(re.escape(batch_delimiter(index)) for index in pending[1:])
                        outputs = re.split(pattern, candidate)
                    if len(outputs) != len(pending):
                        raise ValueError("묶음 표식이 보존되지 않았습니다")
                    for index, output_chunk in zip(pending, outputs):
                        chunk = pieces[index][1]
                        if without_punctuation(output_chunk) != without_punctuation(chunk):
                            raise ValueError(f"청크 {index + 1} 비표점 문자 배열이 입력과 다릅니다")
                    for index, output_chunk in zip(pending, outputs):
                        chunk = pieces[index][1]
                        state["chunks"][index] = {
                            "text": output_chunk,
                            "input_sha256": hashlib.sha256(chunk.encode()).hexdigest(),
                            "output_sha256": hashlib.sha256(output_chunk.encode()).hexdigest(),
                            "attempts": attempt,
                        }
                    atomic_json(checkpoint, state)
                    break
                except (OSError, subprocess.SubprocessError, RuntimeError, ValueError) as exc:
                    failures.append(str(exc))
                    if attempt < args.retries:
                        time.sleep(min(attempt, 3))
            else:
                atomic_json(checkpoint, state)
                raise RuntimeError(
                    f"청크 묶음 {pending[0] + 1}-{pending[-1] + 1}/{len(pieces)} 표점 실패: "
                    + " | ".join(failures)
                )

    chunk_outputs = [item["text"] for item in state["chunks"]]
    chunk_cursor = 0
    rendered: list[str] = [f"# {args.title}\n\n"]
    for block in expanded:
        if block.kind == "heading":
            rendered.append(
                "#" * min(block.level + 1, 6) + " " + block.text + "\n\n"
            )
        else:
            rendered.append(chunk_outputs[chunk_cursor].rstrip() + "\n\n")
            chunk_cursor += 1
    markdown = "".join(rendered).strip() + "\n"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(markdown, encoding="utf-8")

    input_nonpunct = sum(len(without_punctuation(chunk)) for _, chunk in pieces)
    output_nonpunct = sum(len(without_punctuation(chunk)) for chunk in chunk_outputs)
    punctuation_count = sum(len(ASCII_PUNCT_RE.findall(chunk)) for chunk in chunk_outputs)
    chunk_details = []
    for index, ((_, source_chunk), output_chunk) in enumerate(
        zip(pieces, chunk_outputs), start=1
    ):
        source_plain = without_punctuation(source_chunk)
        output_plain = without_punctuation(output_chunk)
        chunk_punctuation = len(ASCII_PUNCT_RE.findall(output_chunk))
        chunk_details.append(
            {
                "index": index,
                "input_characters": len(source_chunk),
                "output_characters": len(output_chunk),
                "nonpunctuation_characters_preserved": source_plain == output_plain,
                "punctuation_count": chunk_punctuation,
                "punctuation_density": round(
                    chunk_punctuation / max(len(output_plain), 1), 8
                ),
                "attempts": state["chunks"][index - 1]["attempts"],
            }
        )
    report = {
        "generator": "codex exec",
        "model": args.model or "codex-default",
        "source": {"path": str(args.source), "sha256": source_sha256},
        "correction_overlay": {
            "path": str(DEFAULT_CORRECTIONS.relative_to(ROOT)),
            "sha256": hashlib.sha256(corrections_raw).hexdigest(),
            "applied_count": applied_correction_count,
        },
        "output": str(args.output),
        "chunks": {
            "total": len(pieces),
            "resumable_completed": sum(item is not None for item in state["chunks"]),
            "min_chars": min((len(chunk) for _, chunk in pieces), default=0),
            "max_chars": max((len(chunk) for _, chunk in pieces), default=0),
            "target_chars": args.target_chars,
            "attempts": [item["attempts"] for item in state["chunks"]],
            "items": chunk_details,
        },
        "character_preservation": {
            "verified": input_nonpunct == output_nonpunct
            and all(
                without_punctuation(source_chunk) == without_punctuation(output_chunk)
                for (_, source_chunk), output_chunk in zip(pieces, chunk_outputs)
            ),
            "input_nonpunctuation_characters": input_nonpunct,
            "output_nonpunctuation_characters": output_nonpunct,
        },
        "punctuation": {
            "ascii_count": punctuation_count,
            "density_per_nonpunctuation_character": round(
                punctuation_count / max(output_nonpunct, 1), 8
            ),
            "chinese_punctuation_normalized": True,
        },
    }
    if not report["character_preservation"]["verified"]:
        raise RuntimeError("최종 문자 보존 검증에 실패했습니다")
    atomic_json(report_path, report)
    print(f"완료: {output} ({len(pieces)}청크, 표점 {punctuation_count}개)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
