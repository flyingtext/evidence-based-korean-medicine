#!/usr/bin/env python3
"""검증된 고전 번역 JSONL을 원문 파일 구성과 같은 Markdown으로 렌더링한다."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


REQUIRED_RESULT_FIELDS = {
    "source_id",
    "target_language",
    "translation",
    "translator_notes",
    "unresolved",
    "model",
    "status",
}

LANGUAGE_LABELS = {
    "ko": ("번역", "원전", "번역 모델", "번역 상태", "원문", "직역", "역자 해설", "없음.", "미확정"),
    "ja": ("翻訳", "原典", "翻訳モデル", "翻訳状態", "原文", "逐語訳", "訳注", "なし。", "未確定"),
    "en": ("Translation", "Source work", "Translation model", "Translation status", "Source Text", "Literal Translation", "Translator's Notes", "None.", "Unresolved"),
}


def read_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, 1):
            if not raw_line.strip():
                raise ValueError(f"빈 JSONL 행: {path}:{line_number}")
            try:
                value = json.loads(raw_line)
            except json.JSONDecodeError as error:
                raise ValueError(f"잘못된 JSON: {path}:{line_number}: {error}") from error
            if not isinstance(value, dict):
                raise ValueError(f"JSON 객체가 아닌 행: {path}:{line_number}")
            records.append(value)
    return records


def validate(tasks: list[dict], results: list[dict], partial: bool) -> list[dict]:
    task_positions = {task.get("source_id"): index for index, task in enumerate(tasks)}
    if len(task_positions) != len(tasks) or None in task_positions:
        raise ValueError("입력 작업의 source_id가 없거나 중복됨")
    if not partial and len(tasks) != len(results):
        raise ValueError(f"입출력 행 수 불일치: 입력 {len(tasks)}행, 출력 {len(results)}행")
    if partial and not results:
        raise ValueError("부분 결과가 비어 있음")

    seen: set[str] = set()
    languages: set[str] = set()
    selected_tasks: list[dict] = []
    positions: list[int] = []
    for index, result in enumerate(results, 1):
        missing = REQUIRED_RESULT_FIELDS - result.keys()
        if missing:
            raise ValueError(f"출력 {index}행 필드 누락: {', '.join(sorted(missing))}")
        source_id = result["source_id"]
        if source_id not in task_positions:
            raise ValueError(f"입력에 없는 source_id: {source_id}")
        if source_id in seen:
            raise ValueError(f"중복 source_id: {source_id}")
        seen.add(source_id)
        position = task_positions[source_id]
        positions.append(position)
        selected_tasks.append(tasks[position])
        language = result["target_language"]
        if language not in LANGUAGE_LABELS:
            raise ValueError(f"지원하지 않는 target_language: {source_id}: {language!r}")
        languages.add(language)
        if not isinstance(result["translation"], str) or not result["translation"].strip():
            raise ValueError(f"빈 번역: {source_id}")
        for field in ("translator_notes", "unresolved"):
            if not isinstance(result[field], list) or not all(
                isinstance(item, str) for item in result[field]
            ):
                raise ValueError(f"{field}는 문자열 배열이어야 함: {source_id}")
        if result["status"] not in {"machine_translated", "reviewed", "final"}:
            raise ValueError(f"알 수 없는 번역 상태: {source_id}: {result['status']!r}")
    if len(languages) != 1:
        raise ValueError(f"한 결과 파일에는 대상 언어가 하나여야 함: {sorted(languages)}")
    if positions != list(range(positions[0], positions[0] + len(positions))):
        raise ValueError("부분 결과는 입력에서 서로 겹치지 않는 연속 source_id 구간이어야 함")
    if not partial and (positions[0] != 0 or len(positions) != len(tasks)):
        raise ValueError("전체 결과가 모든 입력 작업을 포함하지 않음")
    return selected_tasks


def relative_target(task: dict, book_dir: Path) -> Path:
    target = Path(str(task.get("target_original", "")))
    if not target.name or target.suffix.lower() != ".md":
        raise ValueError(f"잘못된 target_original: {target}")

    # target_original은 보통 '<서명>(ID)/파일.md' 형식이다.
    if len(target.parts) > 1 and target.parts[0] == book_dir.name:
        target = Path(*target.parts[1:])
    elif target.is_absolute():
        try:
            target = target.relative_to(book_dir)
        except ValueError as error:
            raise ValueError(f"문헌 폴더 밖의 target_original: {target}") from error

    if target.is_absolute() or ".." in target.parts:
        raise ValueError(f"안전하지 않은 target_original: {target}")
    return target


def markdown_document(book: str, source_file: Path, rows: list[tuple[dict, dict]]) -> str:
    model_names = sorted({str(result["model"]) for _, result in rows})
    statuses = sorted({str(result["status"]) for _, result in rows})
    language = str(rows[0][1]["target_language"])
    title_suffix, source_label, model_label, status_label, original_label, translation_label, notes_label, none_label, unresolved_label = LANGUAGE_LABELS[language]
    title = source_file.stem
    if source_file.exists():
        first_line = source_file.read_text(encoding="utf-8").splitlines()[:1]
        if first_line and first_line[0].startswith("# "):
            title = first_line[0][2:].strip()

    lines = [
        f"# {title} {title_suffix}",
        "",
        f"> {source_label}: {book}",
        f"> Language: {language}",
        f"> {model_label}: {', '.join(model_names)}",
        f"> {status_label}: {', '.join(statuses)}",
        "> Machine translation; it is not definitive until its status is `final`.",
        "",
    ]

    for task, result in rows:
        source_id = task["source_id"]
        heading = str(task.get("heading") or source_id)
        notes = list(result["translator_notes"])
        unresolved = list(result["unresolved"])
        lines.extend(
            [
                f"<!-- source-id: {source_id} -->",
                "",
                f"## {heading}",
                "",
                f"### {original_label}",
                "",
                str(task.get("text", "")).strip(),
                "",
                f"### {translation_label}",
                "",
                result["translation"].strip(),
                "",
                f"### {notes_label}",
                "",
            ]
        )
        if not notes and not unresolved:
            lines.append(f"- {none_label}")
        else:
            lines.extend(f"- {note}" for note in notes)
            lines.extend(f"- {unresolved_label}: {item}" for item in unresolved)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--book-dir", type=Path, required=True, help="교감 완료 정본 폴더")
    parser.add_argument("--results", type=Path, required=True, help="LLM 번역 결과 JSONL")
    parser.add_argument("--output", type=Path, required=True, help="Markdown 출력 폴더")
    parser.add_argument("--partial", action="store_true", help="연속된 일부 source_id만 검증·렌더링")
    parser.add_argument("--tasks", type=Path, help="번역 작업 JSONL (기본: book-dir/translation-tasks.jsonl). 3문장 조각 입력을 사용할 때 지정")
    args = parser.parse_args()

    book_dir = args.book_dir.resolve()
    task_path = args.tasks.resolve() if args.tasks else book_dir / "translation-tasks.jsonl"
    if not book_dir.is_dir():
        raise ValueError(f"정본 폴더가 없음: {book_dir}")
    if "_가져오기" in book_dir.parts:
        raise ValueError("_가져오기 문헌은 번역 대상으로 사용할 수 없음")
    if not task_path.is_file():
        raise ValueError(f"번역 작업 파일이 없음: {task_path}")

    tasks = read_jsonl(task_path)
    results = read_jsonl(args.results)
    selected_tasks = validate(tasks, results, args.partial)

    grouped: dict[Path, list[tuple[dict, dict]]] = defaultdict(list)
    for task, result in zip(selected_tasks, results):
        grouped[relative_target(task, book_dir)].append((task, result))

    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    for relative_path, rows in grouped.items():
        destination = output / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        source_file = book_dir / relative_path
        destination.write_text(
            markdown_document(str(tasks[0].get("book", book_dir.name)), source_file, rows),
            encoding="utf-8",
        )

    print(f"번역 Markdown 생성: {len(grouped)}파일 → {output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as error:
        print(f"오류: {error}", file=sys.stderr)
        raise SystemExit(1)
