# 근거 기반 한의학 위키

**Evidence-Based Korean Medicine Wiki**

PubMed · Crossref의 논문 데이터를 AI로 분석해 만든 근거 기반 한의학 위키입니다.

## 개요

모든 문서는 [med.symbolicinfo.com](https://med.symbolicinfo.com) 검색 API로 수집한 논문 근거에 기반합니다.
임상적 주장에는 출처(DOI/PMID)를 명시합니다.

> 운영 원칙: 근거 우선 · 출처 명시 · AI 생성물 명시 · 과장 금지
> (자세한 규칙은 [AGENTS.md](./AGENTS.md) 참조)

**운영자**: 윤지현 (flyingtext@nate.com)

> 본 위키는 AI를 활용해 생성한 문서로 오류나 오타가 있을 수 있습니다.
> 개별 논문 데이터 추출에는 **Gemma 4 31B**, 위키 본문 작성에는 **DeepSeek V4 Flash**를 사용했습니다.
> 내용상 오류를 발견하신 경우 운영자에게 이메일(flyingtext@nate.com)로 알려주시면 신속히 수정하겠습니다.

## 작성 워크플로우

1. 주제 선정 → `GET /search`로 논문 수집 (`analyzed=1` 우선)
2. 논문 메타데이터와 `clinical_summary` 기반으로 문서 작성 ([템플릿](./_template.md))
3. 검증 스크립트로 링크·근거·표기 점검
4. MkDocs로 빌드

자세한 명령어는 [RUN.md](./RUN.md) 참조.
