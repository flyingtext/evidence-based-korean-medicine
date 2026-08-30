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
    "translation",
    "translator_notes",
    "unresolved",
    "model",
    "status",
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


def validate(tasks: list[dict], results: list[dict]) -> None:
    if len(tasks) != len(results):
        raise ValueError(f"입출력 행 수 불일치: 입력 {len(tasks)}행, 출력 {len(results)}행")

    seen: set[str] = set()
    for index, (task, result) in enumerate(zip(tasks, results), 1):
        source_id = task.get("source_id")
        if not source_id:
            raise ValueError(f"입력 {index}행에 source_id가 없음")
        missing = REQUIRED_RESULT_FIELDS - result.keys()
        if missing:
            raise ValueError(f"출력 {index}행 필드 누락: {', '.join(sorted(missing))}")
        if result["source_id"] != source_id:
            raise ValueError(
                f"출력 {index}행 source_id 불일치: {source_id!r} != {result['source_id']!r}"
            )
        if source_id in seen:
            raise ValueError(f"중복 source_id: {source_id}")
        seen.add(source_id)
        if not isinstance(result["translation"], str) or not result["translation"].strip():
            raise ValueError(f"빈 번역: {source_id}")
        for field in ("translator_notes", "unresolved"):
            if not isinstance(result[field], list) or not all(
                isinstance(item, str) for item in result[field]
            ):
                raise ValueError(f"{field}는 문자열 배열이어야 함: {source_id}")
        if result["status"] not in {"machine_translated", "reviewed", "final"}:
            raise ValueError(f"알 수 없는 번역 상태: {source_id}: {result['status']!r}")


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
    title = source_file.stem
    if source_file.exists():
        first_line = source_file.read_text(encoding="utf-8").splitlines()[:1]
        if first_line and first_line[0].startswith("# "):
            title = first_line[0][2:].strip()

    lines = [
        f"# {title} 번역",
        "",
        f"> 원전: {book}",
        f"> 번역 모델: {', '.join(model_names)}",
        f"> 번역 상태: {', '.join(statuses)}",
        "> 이 문서는 기계 번역 결과이며 `final` 검수 전에는 확정 번역으로 간주하지 않는다.",
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
                "### 원문",
                "",
                str(task.get("text", "")).strip(),
                "",
                "### 직역",
                "",
                result["translation"].strip(),
                "",
                "### 역자 해설",
                "",
            ]
        )
        if not notes and not unresolved:
            lines.append("- 없음.")
        else:
            lines.extend(f"- {note}" for note in notes)
            lines.extend(f"- 미확정: {item}" for item in unresolved)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--book-dir", type=Path, required=True, help="교감 완료 정본 폴더")
    parser.add_argument("--results", type=Path, required=True, help="LLM 번역 결과 JSONL")
    parser.add_argument("--output", type=Path, required=True, help="Markdown 출력 폴더")
    args = parser.parse_args()

    book_dir = args.book_dir.resolve()
    task_path = book_dir / "translation-tasks.jsonl"
    if not book_dir.is_dir():
        raise ValueError(f"정본 폴더가 없음: {book_dir}")
    if "_가져오기" in book_dir.parts:
        raise ValueError("_가져오기 문헌은 번역 대상으로 사용할 수 없음")
    if not task_path.is_file():
        raise ValueError(f"번역 작업 파일이 없음: {task_path}")

    tasks = read_jsonl(task_path)
    results = read_jsonl(args.results)
    validate(tasks, results)

    grouped: dict[Path, list[tuple[dict, dict]]] = defaultdict(list)
    for task, result in zip(tasks, results):
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
