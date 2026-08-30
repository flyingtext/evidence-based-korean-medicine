#!/usr/bin/env python3
"""jicheng.tw 기반 고전 표점본과 산출 보고서를 검증한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

from convert_classics import DEFAULT_CORRECTIONS, DEFAULT_SOURCE, apply_corrections, load_book


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "원문" / "_가져오기"
REPORT_NAME = "punctuation-report.json"
PUNCTUATED_NAME = "표점본.md"
HAN_RE = re.compile(
    "[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff"
    "\U00020000-\U0002fa1f]"
)
ASCII_PUNCTUATION_RE = re.compile(r"[.,!?;:]")
FORBIDDEN_CHINESE_PUNCTUATION_RE = re.compile(r"[。！？]")
BOOK_RE = re.compile(r"\[book\].*?\[/book\]", re.DOTALL | re.IGNORECASE)
HEADING_TAG_RE = re.compile(r"\[h([1-6])\](.*?)\[/h\1\]", re.DOTALL | re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"원서 폴더 루트 (기본값: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--min-length-ratio",
        type=float,
        default=0.85,
        help="보고서의 최소 한자 길이비 (기본값: 0.85)",
    )
    parser.add_argument(
        "--min-match-ratio",
        type=float,
        default=0.80,
        help="보고서의 최소 한자 배열 일치도 (기본값: 0.80)",
    )
    parser.add_argument(
        "--min-punctuation-density",
        type=float,
        default=0.005,
        help="한자 수 대비 최소 ASCII 표점 밀도 (기본값: 0.005)",
    )
    parser.add_argument(
        "--allow-empty",
        action="store_true",
        help="punctuation-report.json이 하나도 없어도 성공으로 처리",
    )
    args = parser.parse_args()
    for name in ("min_length_ratio", "min_match_ratio", "min_punctuation_density"):
        value = getattr(args, name)
        if not math.isfinite(value) or value < 0:
            parser.error(f"--{name.replace('_', '-')} must be a finite non-negative number")
    return args


def is_jicheng_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    hostname = (parsed.hostname or "").lower().rstrip(".")
    return parsed.scheme in {"http", "https"} and (
        hostname == "jicheng.tw" or hostname.endswith(".jicheng.tw")
    )


def content_signature(text: str) -> str:
    return "".join(
        char
        for char in text
        if not char.isspace() and not unicodedata.category(char).startswith("P")
    )


def missing_punctuation_spaces(text: str) -> int:
    count = 0
    for index, char in enumerate(text[:-1]):
        if char not in {",", "."}:
            continue
        following = text[index + 1]
        if following.isspace() or following in ",.!?;:)]}\"'":
            continue
        preceding = text[index - 1] if index else ""
        if char == "." and preceding.isdigit() and following.isdigit():
            continue
        count += 1
    return count


def numeric_field(
    validation: object,
    field: str,
    label: str,
    errors: list[str],
) -> float | None:
    if not isinstance(validation, dict):
        errors.append(f"{label}: validation 객체가 없음")
        return None
    value = validation.get(field)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append(f"{label}: validation.{field} 숫자 필드가 없음")
        return None
    value = float(value)
    if not math.isfinite(value) or value < 0:
        errors.append(f"{label}: validation.{field} 값이 유효하지 않음 ({value})")
        return None
    return value


def validate_report(
    report_path: Path,
    root: Path,
    min_length_ratio: float,
    min_match_ratio: float,
    min_punctuation_density: float,
) -> list[str]:
    try:
        label = str(report_path.relative_to(root))
    except ValueError:
        label = str(report_path)
    errors: list[str] = []
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"{label}: 보고서 JSON을 읽을 수 없음 ({exc})"]
    if not isinstance(report, dict):
        return [f"{label}: 보고서 최상위 값이 JSON 객체가 아님"]

    if report.get("generator") == "codex exec":
        preservation = report.get("character_preservation")
        if not isinstance(preservation, dict) or preservation.get("verified") is not True:
            errors.append(f"{label}: Codex 표점본 문자 보존 검증 실패")
        source = report.get("source")
        source_value = source.get("path") if isinstance(source, dict) else None
        if not isinstance(source_value, str):
            errors.append(f"{label}: Codex 원자료 경로 없음")
        else:
            source_path = (ROOT / source_value.split(" + ", 1)[0]).resolve()
            if not source_path.is_file():
                errors.append(f"{label}: Codex 원자료 없음 ({source_value})")
            else:
                raw = source_path.read_bytes()
                expected_sha256 = source.get("raw_source_sha256", source.get("sha256"))
                if hashlib.sha256(raw).hexdigest() != expected_sha256:
                    errors.append(f"{label}: Codex 원자료 SHA-256 불일치")
    else:
        source = report.get("source")
        if not isinstance(source, dict):
            errors.append(f"{label}: source 객체가 없음")
        else:
            if source.get("site") != "jicheng.tw":
                errors.append(f"{label}: source.site가 jicheng.tw가 아님")
            if not is_jicheng_url(source.get("url")):
                errors.append(f"{label}: source.url이 jicheng.tw URL이 아님")

        validation = report.get("validation")
        length_ratio = numeric_field(validation, "han_length_ratio", label, errors)
        match_ratio = numeric_field(validation, "han_sequence_quick_ratio", label, errors)
        if length_ratio is not None and length_ratio < min_length_ratio:
            errors.append(
                f"{label}: 한자 길이비 {length_ratio:.6f} < {min_length_ratio:.6f}"
            )
        if match_ratio is not None and match_ratio < min_match_ratio:
            errors.append(
                f"{label}: 한자 배열 일치도 {match_ratio:.6f} < {min_match_ratio:.6f}"
            )

    punctuated_path = report_path.parent / PUNCTUATED_NAME
    punctuated_label = f"{label}: {PUNCTUATED_NAME}"
    if not punctuated_path.is_file():
        errors.append(f"{punctuated_label} 없음")
        return errors
    try:
        text = punctuated_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"{punctuated_label}을 읽을 수 없음 ({exc})")
        return errors
    if report.get("generator") == "codex exec" and isinstance(report.get("source"), dict):
        source_value = report["source"].get("path")
        source_path = (
            (ROOT / source_value.split(" + ", 1)[0]).resolve()
            if isinstance(source_value, str)
            else None
        )
        if source_path and source_path.is_file():
            source_root = DEFAULT_SOURCE.resolve()
            book = load_book(source_path, source_root)
            corrections = json.loads(DEFAULT_CORRECTIONS.read_text(encoding="utf-8"))
            apply_corrections(book, corrections)
            if book.warnings:
                errors.append(f"{label}: 현재 교정 오버레이 적용 경고 {len(book.warnings)}건")
            original = HEADING_TAG_RE.sub(lambda match: match.group(2), book.body)
            rendered_body = re.sub(r"\A# [^\n]*\n", "", text, count=1)
            rendered_body = re.sub(r"^#{2,6} +", "", rendered_body, flags=re.MULTILINE)
            if content_signature(original) != content_signature(rendered_body):
                errors.append(f"{label}: 실제 원자료와 표점본의 비표점 문자 배열 불일치")
    forbidden = FORBIDDEN_CHINESE_PUNCTUATION_RE.findall(text)
    if forbidden:
        counts = {mark: forbidden.count(mark) for mark in sorted(set(forbidden))}
        rendered = ", ".join(f"{mark} {count}개" for mark, count in counts.items())
        errors.append(f"{punctuated_label}에 금지된 중국식 표점 존재 ({rendered})")
    missing_spaces = missing_punctuation_spaces(text)
    if missing_spaces:
        errors.append(f"{punctuated_label}의 쉼표·마침표 뒤 공백 누락 {missing_spaces}곳")
    han_count = len(HAN_RE.findall(text))
    punctuation_count = len(ASCII_PUNCTUATION_RE.findall(text))
    if han_count == 0:
        errors.append(f"{punctuated_label}에 한자가 없음")
    else:
        density = punctuation_count / han_count
        if density < min_punctuation_density:
            errors.append(
                f"{punctuated_label} 표점 밀도 {density:.6f} "
                f"({punctuation_count}/{han_count}) < {min_punctuation_density:.6f}"
            )
    return errors


def main() -> int:
    args = parse_args()
    output = args.output.resolve()
    if not output.is_dir():
        print(f"오류: 표점본 루트 디렉터리 없음: {output}")
        return 1
    reports = sorted(output.rglob(REPORT_NAME))
    if not reports and not args.allow_empty:
        print(f"검증: 보고서 0건, 통과 0건, 실패 1건")
        print(f"ERROR {output} 아래에 {REPORT_NAME}이 없음 (--allow-empty로 허용 가능)")
        return 1

    failed_reports = 0
    all_errors: list[str] = []
    for report_path in reports:
        errors = validate_report(
            report_path,
            output,
            args.min_length_ratio,
            args.min_match_ratio,
            args.min_punctuation_density,
        )
        if errors:
            failed_reports += 1
            all_errors.extend(errors)
    passed_reports = len(reports) - failed_reports
    print(
        f"검증: 보고서 {len(reports)}건, 통과 {passed_reports}건, "
        f"실패 {failed_reports}건, 오류 {len(all_errors)}건"
    )
    for error in all_errors:
        print(f"ERROR {error}")
    return 1 if all_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
