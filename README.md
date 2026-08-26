# 근거 기반 한의학 저장소

**Evidence-Based Korean Medicine Repository**

PubMed · Crossref · KCI(한국학술지인용색인)의 논문 데이터를 AI로 분석해 만든 근거 기반 한의학 저장소입니다.
모든 문서는 [med.symbolicinfo.com](https://med.symbolicinfo.com) 검색 API로 수집한 논문 근거에 기반하며, 임상적 주장에는 출처(DOI/PMID)를 명시합니다.

## 개요

- **운영 원칙**: 근거 우선 · 출처 명시 · AI 생성물 명시 · 과장 금지
- **분류 체계**: 한의과대학 교과과정을 참고한 대분류(기초한의학 · 임상한의학) → 중분류(과목) → 소분류(개별 문서) 3단계
- **문서 형식**: 순수 마크다운(`.md`)

## 기술 스택

| 구성 | 도구 |
|---|---|
| 콘텐츠 | 순수 마크다운 문서 파일 (`wiki/`) |
| 자동화 | Python 스크립트 (`scripts/`) — 논문 검색(`search.py`), 품질 검증(`validate.py`), 워크플로우 실행(`run.py`) |
| 데이터 소스 | [med.symbolicinfo.com](https://med.symbolicinfo.com) 검색 API |

## 명령어

```bash
# 논문 검색 → 근거 수집
python3 scripts/search.py "요통" --km --human --analyzed

# 문서 품질 검증 (링크·KCD·표기)
python3 scripts/validate.py

# 전체 워크플로우 실행 (검증 + 최근 업데이트 재생성 + 링크 점검)
python3 scripts/run.py
```

## 프로젝트 구조

```
wiki/                 # 저장소 콘텐츠 (마크다운)
├── 기초한의학/     # 원전 · 진단학 · 한방생리학 · 한방병리학 · 경락경혈학 · 본초학 · 방제학 · 기공학 · 의사학 · 예방한의학
├── 임상한의학/     # 내과(장부) · 산부인과 · 소아과 · 신경정신과 · 안이비인후피부과 · 침구과 · 추나의학 · 재활의학 · 사상의학
scripts/              # 자동화 스크립트
AGENTS.md             # 프로젝트 운영 규칙
RUN.md                # 작성·보강 명령어
```

## 문서 작성 규칙

- 모든 임상적 주장은 검색 API로 확인 가능한 논문 근거에 기반하며, 근거가 없으면 "근거 미확인"으로 명시한다.
- 핵심 주장에는 DOI/PMID와 논문 제목을 각주로 함께 기록한다.
- 연구 유형(체계적 고찰/메타분석 > 임상시험 > 관찰연구 > 증례)이 높은 논문을 우선 인용하되, 임상 참고 가치가 있는 논문은 빠짐없이 반영한다.
- 상업적 효능 주장·절대적 효능 표현은 금지한다.
- 자세한 규칙은 [AGENTS.md](./AGENTS.md) 참조.

## Maintainer

- **윤지현** (flyingtext@nate.com)

> 내용상 오류를 발견하신 경우 운영자에게 이메일(flyingtext@nate.com)로 알려주시면 신속히 수정하겠습니다.
