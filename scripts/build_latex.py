#!/usr/bin/env python3
"""폴더 안의 마크다운 문서를 폴더 구조를 보존한 단일 LaTeX 문서로 병합한다.

폴더 계층을 chapter/section/subsection으로, 각 파일을 그 아래 헤딩으로 매핑해
하나의 마크다운으로 합친 뒤, pandoc의 --standalone 템플릿(xelatex + xeCJK)으로
LaTeX(.tex)을 생성한다. --pdf를 주면 latexmk(xelatex)로 PDF까지 빌드한다.

사용 예:
    python3 scripts/build_latex.py --root docs --out build/wiki.tex --pdf
    python3 scripts/build_latex.py --root docs/기초한의학/방제학 --out build/방제학.tex --pdf
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

MAX_STRUCT_LEVEL = 3   # 폴더 계층은 chapter(1)/section(2)/subsection(3)까지만 구조화
MAX_HEADING_LEVEL = 6  # CommonMark ATX 헤딩 최대 레벨(그 이상은 clamp)

HEADING_RE = re.compile(r"^(#{1,6})(\s+)(.*)$")
FOOTNOTE_RE = re.compile(r"\[\^([^\]\s]+)\]")


# ---------------------------------------------------------------------------
# 마크다운 전처리: 헤딩 레벨 시프트, 각주 식별자 네임스페이스 처리
# ---------------------------------------------------------------------------

def first_heading_level(text: str) -> int | None:
    for line in text.splitlines():
        if not line.strip():
            continue
        m = HEADING_RE.match(line)
        return len(m.group(1)) if m else None
    return None


def shift_headings(text: str, shift: int) -> str:
    """코드블록 내부는 건드리지 않고 ATX 헤딩만 shift만큼 이동(레벨은 1~6로 clamp)."""
    out = []
    in_code = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code = not in_code
            out.append(line)
            continue
        if not in_code:
            m = HEADING_RE.match(line)
            if m:
                level = len(m.group(1))
                new_level = max(1, min(level + shift, MAX_HEADING_LEVEL))
                out.append("#" * new_level + m.group(2) + m.group(3))
                continue
        out.append(line)
    return "\n".join(out)


def shift_whole_file(text: str, target_level: int) -> str:
    """문서 첫 헤딩(보통 '# 제목')이 target_level이 되도록 전체를 shift."""
    lvl = first_heading_level(text)
    if lvl is None:
        return f"{'#' * target_level} (제목 없음)\n\n{text}"
    return shift_headings(text, target_level - lvl)


THEMATIC_RULE_RE = re.compile(r"^\s*(-{3,}|={3,}|\*{3,}|_{3,})\s*$")


def isolate_thematic_breaks(text: str) -> str:
    """구분선(`---`)이 빈 줄로 앞뒤가 분리되도록 보정한다.

    양쪽 모두 문제가 된다.

    - **앞에 빈 줄이 없으면**: 본문 줄 바로 아래의 `---`는 수평선이 아니라
      setext 헤딩(H2)이 되어, 바로 앞 줄이 통째로 제목이 되어버린다.
      (각주 정의 한 줄이 목차에 섹션으로 올라온 사례가 있었다.)
    - **뒤에 빈 줄이 없으면**: pandoc의 pipe_tables는 머리글 없는 표를
      허용하므로 `---`를 표의 구분행으로 읽고, 뒤따르는 헤딩·문단을 전부
      표의 행으로 삼켜버린다. (`## 제2편 병태생리` 이하가 통째로 1열
      longtable에 갇혀 글자가 한 자씩 세로로 흐른 사례가 있었다.)

    저장소 문서는 헤딩을 전부 ATX(`#`)로 쓰므로 이런 배치는 언제나 실수다.
    표 구분선(`|---|`)은 `|`로 시작하므로 여기 걸리지 않는다.
    """
    lines = text.splitlines()
    out: list[str] = []
    in_code = False
    pending_blank_after = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code = not in_code
            pending_blank_after = False
            out.append(line)
            continue
        if pending_blank_after and stripped:
            out.append("")
        pending_blank_after = False
        if not in_code and THEMATIC_RULE_RE.match(line) and not stripped.startswith("|"):
            if out and out[-1].strip():
                out.append("")
            pending_blank_after = True
        out.append(line)
    return "\n".join(out)


# 조판용 문자 치환표.
#
# 저장소 문서는 폴더 README의 상태 범례에 이모지(✅·🔄)를 쓰고, 본문에서는
# 아래첨자 기호를 쓴다. 이 글자들은 컬러 이모지 폰트나 특수 폰트에만 있어
# xelatex 본문 폰트 체인으로는 조판되지 않고 빈 네모(tofu)로 떨어진다.
# 마크다운 원본의 관례는 그대로 두고, PDF로 낼 때만 같은 뜻의 텍스트로
# 바꿔 준다.
TYPESET_SUBSTITUTIONS = {
    "\u2705": "[완료]",   # ✅
    "\U0001F504": "[진행]",  # 🔄
    "\u2099": "n",        # 아래첨자 n — 폰트에 글리프가 없어 일반 n으로 낮춘다
}


def apply_typeset_substitutions(text: str) -> str:
    for src, dst in TYPESET_SUBSTITUTIONS.items():
        text = text.replace(src, dst)
    return text


def namespace_footnotes(text: str, file_id: str) -> str:
    """각 파일이 독립적으로 [^1], [^2]...를 쓰므로, 하나의 문서로 합칠 때
    식별자가 서로 충돌하지 않도록 파일별 고유 접두어를 붙인다."""
    return FOOTNOTE_RE.sub(lambda m: f"[^{file_id}_{m.group(1)}]", text)


def struct_level_for_depth(depth: int) -> int:
    return min(max(depth, 1), MAX_STRUCT_LEVEL)


BULLET_RE = re.compile(r"^\s*[-*]\s+(.*)$")


def readme_order_key(readme_path: Path, subdirs: list, files: list):
    """README.md의 불릿 목록 등장 순서를 반영하는 정렬 키 함수를 만든다.

    각 파일은 확장자를 뗀 파일명(문서 제목과 거의 동일)을, 각 하위 폴더는
    저장소 관례상 `폴더명/` 형태(백틱 감싼 표기)로 README 본문에 언급된다.
    README에서 언급을 찾지 못한 항목은 목록 뒤쪽에 이름순으로 붙인다.
    """
    name_to_pos: dict[str, int] = {}
    if readme_path.exists():
        text = readme_path.read_text(encoding="utf-8")
        pos = 0
        for line in text.splitlines():
            m = BULLET_RE.match(line)
            if not m:
                continue
            bullet_text = m.group(1)
            pos += 1
            for d in subdirs:
                key = f"{d.name}/"
                if key in bullet_text and d.name not in name_to_pos:
                    name_to_pos[d.name] = pos
            for f in files:
                stem = f.stem
                # 정확히 일치하면 우선 사용하고, 안 되면 괄호 앞 주 명칭(한글명 등)만으로
                # 비교한다 — README 불릿에 약어(TRH 등)가 파일명에 없이 추가로 붙는 경우가 있다.
                prefix = stem.split("(", 1)[0].strip()
                matched = stem in bullet_text or (len(prefix) >= 2 and prefix in bullet_text)
                if matched and f.name not in name_to_pos:
                    name_to_pos[f.name] = pos

    def key(name: str):
        if name in name_to_pos:
            return (0, name_to_pos[name], name)
        return (1, 0, name)

    return key


# ---------------------------------------------------------------------------
# 트리 순회 → 하나의 마크다운 문자열로 병합
# ---------------------------------------------------------------------------

class Collector:
    def __init__(self) -> None:
        self.parts: list[str] = []
        self._file_counter = 0
        self.file_count = 0
        # 문서 파일의 제목이 배치되는 최대 헤딩 레벨. LaTeX 자동 번호를 이
        # 레벨까지만 매기고 그보다 깊은(=각 문서 내부의) 헤딩은 번호를 붙이지
        # 않기 위해 기록한다. 저장소 문서는 본문에서 이미 "제1편", "1.",
        # "1-1." 같은 자체 번호를 쓰므로, 그 위에 LaTeX 번호까지 찍히면
        # "2.1.1.1.1  1-1. 간의 배속" 처럼 번호가 이중으로 나온다.
        self.max_file_level = 0
        # 가장 얕은 곳에 있는 문서의 레벨. 폴더 깊이가 뒤섞인 트리에서는
        # 이 값을 번호 매김 한계로 삼아야 어떤 문서에서도 본문 헤딩에 번호가
        # 겹치지 않는다(가장 얕은 문서의 본문이 곧 가장 낮은 번호 레벨이므로).
        self.min_file_level = MAX_HEADING_LEVEL

    def next_file_id(self) -> str:
        self._file_counter += 1
        return f"f{self._file_counter}"

    def add_folder_heading(self, dir_path: Path, depth: int) -> None:
        level = struct_level_for_depth(depth)
        readme = dir_path / "README.md"
        if readme.exists():
            body = readme.read_text(encoding="utf-8")
            body = apply_typeset_substitutions(body)
            body = isolate_thematic_breaks(body)
            body = namespace_footnotes(body, self.next_file_id())
            body = shift_whole_file(body, level)
            self.file_count += 1
        else:
            body = f"{'#' * level} {dir_path.name}"
        self.parts.append(body)
        self.parts.append("")

    def add_file(self, file_path: Path, depth: int) -> None:
        level = min(struct_level_for_depth(depth) + 1, MAX_HEADING_LEVEL)
        body = file_path.read_text(encoding="utf-8")
        body = apply_typeset_substitutions(body)
        body = isolate_thematic_breaks(body)
        body = namespace_footnotes(body, self.next_file_id())
        body = shift_whole_file(body, level)
        self.file_count += 1
        self.max_file_level = max(self.max_file_level, level)
        self.min_file_level = min(self.min_file_level, level)
        self.parts.append(body)
        self.parts.append("")

    def walk(self, dir_path: Path, depth: int) -> None:
        try:
            entries = list(dir_path.iterdir())
        except FileNotFoundError:
            return
        entries = [p for p in entries if not p.name.startswith(".")]
        subdirs = [p for p in entries if p.is_dir()]
        files = [p for p in entries if p.is_file() and p.suffix.lower() == ".md" and p.name != "README.md"]

        order_key = readme_order_key(dir_path / "README.md", subdirs, files)
        subdirs.sort(key=lambda p: order_key(p.name))
        files.sort(key=lambda p: order_key(p.name))

        # 루트 폴더(depth 0)도 포함한다. 예전에는 depth >= 1 조건을 두어
        # 루트 README를 통째로 빠뜨렸고, 그 결과 루트 바로 아래의 문서들이
        # 앞선 chapter 없이 section으로 시작해 번호가 "0.1"부터 매겨졌다.
        self.add_folder_heading(dir_path, max(depth, 1))

        for f in files:
            self.add_file(f, depth)

        for d in subdirs:
            self.walk(d, depth + 1)

    def build(self, root: Path) -> str:
        self.walk(root, 0)
        return "\n\n".join(self.parts)


# ---------------------------------------------------------------------------
# pandoc용 header-includes 조각 (xeCJK 폴백 폰트 + hyperref 색상 등)
# ---------------------------------------------------------------------------

HEADER_INCLUDES_TEMPLATE = r"""
\xeCJKsetup{{AutoFallBack = true}}
% 폴백 폰트는 반드시 한 번의 호출에 쉼표로 나열해야 한다. setCJKfallbackfamilyfont를
% 여러 번 부르면 목록이 누적되지 않고 마지막 호출이 앞의 것을 덮어쓴다.
\setCJKfallbackfamilyfont{{\CJKrmdefault}}{{{cjk_fallback_font}, {cjk_fallback_font2}, {cjk_fallback_font3}}}
\XeTeXlinebreaklocale "ko"
\XeTeXlinebreakskip = 0pt plus 1pt
% 번호는 저장소 구조(폴더→문서 제목)까지만 매긴다. 그보다 깊은 헤딩은
% 각 문서의 본문이며, 본문은 이미 "제1편", "1.", "1-1." 같은 자체 번호를
% 쓰고 있어 LaTeX 번호를 겹쳐 매기면 이중 번호가 된다.
% (tocdepth는 pandoc이 --toc-depth로 이 뒤에 다시 설정하므로 여기서 다루지 않는다)
\setcounter{{secnumdepth}}{{{secnumdepth}}}

% 원문 인용에 흔한 동그라미숫자(①-⑳)·전각/특수 대시·따옴표 등은
% 라틴 메인폰트(Times New Roman 등)에 글리프가 없는 경우가 많으므로,
% CJK 문자 클래스에 편입시켜 CJK 메인폰트+폴백 체인이 대신 처리하게 한다.
\xeCJKDeclareCharClass{{CJK}}{{
  "2010, "2011, "2012, "2013, "2014, "2015,
  "2018, "2019, "201C, "201D, "2026,
  "2070 -> "209F,
  "2150 -> "218F,
  "2460 -> "24FF,
  "25A0 -> "25FF,
  % 폴더 구조 아스키 아트(README의 트리 그림)에 쓰이는 괘선 문자와
  % 상태 범례 기호(☐ 등). 라틴 고정폭 폰트에는 대개 글리프가 없다.
  "2100 -> "214F,
  "2500 -> "257F,
  "2580 -> "259F,
  "2600 -> "27BF,
  % 화살표·수학 연산자(∛ 등). 본문 수식·단위 표기에 간간이 등장한다.
  "2190 -> "22FF,
  "2C60 -> "2C7F,
  "3000 -> "303F
}}
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default="docs", help="병합할 루트 폴더 (기본: docs)")
    ap.add_argument("--out", default="build/wiki.tex", help="출력 .tex 경로")
    ap.add_argument("--title", default="근거 기반 한의학 저장소", help="문서 제목")
    ap.add_argument("--author", default="윤지현", help="저자 표기")
    ap.add_argument("--pandoc-bin", default="pandoc")
    ap.add_argument("--latin-font", default="Times New Roman")
    ap.add_argument("--cjk-main-font", default="Apple SD Gothic Neo",
                     help="본문 CJK(한글) 폰트")
    ap.add_argument("--cjk-fallback-font", default="AppleMyungjo",
                     help="본문 폰트에 없는 한자(고전 원문 이체자 등)를 위한 1차 대체 폰트")
    ap.add_argument("--cjk-fallback-font2", default="Songti SC",
                     help="2차 대체 폰트")
    ap.add_argument("--cjk-fallback-font3", default="Apple Symbols",
                     help="3차 대체 폰트 — 단위·수학 기호(℃·∛·아래첨자 등) 담당")
    ap.add_argument("--date", default=None,
                     help="표지에 찍을 날짜 (기본: 빌드 당일, 예 '2026년 8월 29일')")
    ap.add_argument("--secnumdepth", type=int, default=None,
                     help="번호를 매길 최대 헤딩 깊이. 기본값은 문서 제목이 놓이는 "
                          "레벨로 자동 설정되어, 각 문서 본문의 자체 번호(제1편·1-1. 등)와 "
                          "LaTeX 번호가 겹치지 않게 한다.")
    ap.add_argument("--pdf", action="store_true", help="latexmk(xelatex)로 PDF까지 빌드")
    ap.add_argument("--keep-md", action="store_true", help="병합된 중간 마크다운(.merged.md)도 보존")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"오류: 루트 폴더가 없습니다 — {root}", file=sys.stderr)
        return 1

    pandoc_bin = shutil.which(args.pandoc_bin)
    if pandoc_bin is None:
        print(f"오류: pandoc을 찾을 수 없습니다 ({args.pandoc_bin})", file=sys.stderr)
        return 1

    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"[1/3] {root} 하위 마크다운 파일 수집 및 병합 중...")
    collector = Collector()
    merged_md = collector.build(root)
    print(f"      총 {collector.file_count}개 마크다운 조각(폴더 README 포함)을 병합했습니다.")

    # 번호는 문서 제목 레벨까지만 매기고, 그보다 깊은 각 문서 본문은 자체
    # 번호(제1편·1-1. 등)를 쓰므로 LaTeX 번호를 붙이지 않는다.
    # 주의: LaTeX의 secnumdepth는 chapter=0 기준이라 마크다운 헤딩 레벨보다 1 작다
    # (--top-level-division=chapter 기준: md 1=chapter(0), 2=section(1), 3=subsection(2)).
    md_level = args.secnumdepth if args.secnumdepth is not None else max(collector.min_file_level, 2)
    secnumdepth = md_level - 1
    # 목차는 문서 제목보다 한 단계 더(각 문서의 편·막 수준까지) 보여준다.
    # pandoc의 --toc-depth는 마크다운 레벨 단위다.
    toc_depth_md = min(md_level + 1, MAX_HEADING_LEVEL)
    print(f"      번호 매김: 마크다운 레벨 {md_level}까지 (LaTeX secnumdepth={secnumdepth}), "
          f"목차: 마크다운 레벨 {toc_depth_md}까지")

    doc_date = args.date if args.date is not None else (
        f"{date.today().year}년 {date.today().month}월 {date.today().day}일"
    )

    if args.keep_md:
        merged_md_path = out_path.with_suffix(".merged.md")
        merged_md_path.write_text(merged_md, encoding="utf-8")
        print(f"      병합 마크다운 저장: {merged_md_path}")

    print("[2/3] pandoc으로 standalone LaTeX 문서 생성 중...")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        md_path = tmp / "merged.md"
        md_path.write_text(merged_md, encoding="utf-8")

        header_path = tmp / "header-includes.tex"
        header_path.write_text(
            HEADER_INCLUDES_TEMPLATE.format(
                cjk_fallback_font=args.cjk_fallback_font,
                cjk_fallback_font2=args.cjk_fallback_font2,
                cjk_fallback_font3=args.cjk_fallback_font3,
                secnumdepth=secnumdepth,
            ),
            encoding="utf-8",
        )

        cmd = [
            pandoc_bin,
            str(md_path),
            "-o", str(out_path),
            "--standalone",
            # yaml_metadata_block을 끄는 것이 중요하다. 문서 본문에서 구분선으로 쓰는
            # `---`가 여러 파일에 흩어져 있는데, 하나로 병합하면 pandoc이 두 `---` 사이를
            # YAML 메타데이터 블록으로 오인해 파싱에 실패한다(저장소 규칙상 문서에는
            # YAML front matter를 두지 않으므로 이 확장은 애초에 필요 없다).
            # 제목·저자는 아래 -M 옵션으로 전달하므로 영향받지 않는다.
            "-f", "markdown-yaml_metadata_block+east_asian_line_breaks+pipe_tables+footnotes",
            "-t", "latex",
            "--pdf-engine=xelatex",
            "--toc", f"--toc-depth={toc_depth_md}",
            "--top-level-division=chapter",
            "-V", "documentclass=report",
            "-V", "papersize=a4",
            "-V", "geometry:margin=2.5cm",
            "-V", "fontsize=11pt",
            "-V", f"mainfont={args.latin_font}",
            "-V", f"CJKmainfont={args.cjk_main_font}",
            "-V", "CJKoptions=AutoFakeBold=3",
            "-V", "colorlinks=true",
            "-V", "linkcolor=NavyBlue",
            "-V", "urlcolor=NavyBlue",
            "-V", "citecolor=NavyBlue",
            "-V", "toccolor=black",
            "--include-in-header", str(header_path),
            "-M", f"title={args.title}",
            "-M", f"author={args.author}",
            "-M", f"date={doc_date}",
            "--wrap=preserve",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            sys.stderr.write(proc.stderr)
            print("오류: pandoc 변환 실패", file=sys.stderr)
            return 1
        if proc.stderr.strip():
            sys.stderr.write(proc.stderr)

    print(f"      LaTeX 파일 작성 완료: {out_path}")

    if args.pdf:
        print("[3/3] latexmk(xelatex)로 PDF 빌드 중... (문서가 크면 수 분 소요될 수 있습니다)")
        latexmk = shutil.which("latexmk")
        if latexmk is None:
            print("경고: latexmk를 찾을 수 없어 PDF 빌드를 건너뜁니다.", file=sys.stderr)
            return 0
        proc = subprocess.run(
            [latexmk, "-xelatex", "-interaction=nonstopmode", "-halt-on-error", out_path.name],
            cwd=out_path.parent,
        )
        if proc.returncode != 0:
            print("경고: PDF 빌드 중 오류가 발생했습니다. 로그를 확인하세요.", file=sys.stderr)
            return proc.returncode
        pdf_path = out_path.with_suffix(".pdf")
        print(f"      PDF 빌드 완료: {pdf_path}")
    else:
        print("[3/3] --pdf 옵션이 없어 PDF 빌드는 건너뜁니다.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
