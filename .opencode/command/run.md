---
description: RUN.md 워크플로우(검증·링크·빌드)를 실행한다.
---

RUN.md에 정의된 위키 워크플로우를 실행한다. 작업이 끝날 때마다 이 커맨드를 호출해 품질을 확인한다.

```bash
python3 scripts/run.py
```

- `--skip-build`: 빌드 단계 생략
- `--health`: API 헬스 체크 포함

실패한 단계가 있으면 RUN.md의 유의사항을 확인하고 수정한 뒤 다시 실행한다.
