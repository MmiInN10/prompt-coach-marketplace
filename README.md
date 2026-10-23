# prompt-coach

두서없이 쓴 말을 Claude Code가 알아듣는 요청으로 정리하고, 질문이 잘 전달됐는지 점검하는 스킬이다.

## 설치

Claude Code에서 아래 두 명령을 순서대로 입력한다.

```
/plugin marketplace add MmiInN10/prompt-coach-marketplace
/plugin install prompt-coach@prompt-coach-marketplace
```

설치 후 `/reload-plugins`를 입력하거나 새 세션을 시작한다.

플러그인 없이 쓰려면 `plugins/prompt-coach/skills/prompt-coach` 폴더를 `~/.claude/skills/prompt-coach`로 복사한다. 이 경우 호출 이름은 `/prompt-coach`이다.

## 사용법

```
/prompt-coach:prompt-coach 이 코드 좀 봐줘
```

플러그인으로 설치한 스킬은 플러그인 이름이 앞에 붙어 위와 같이 호출한다.

## 기능

| 기능 | 내용 |
|------|------|
| 요청 정리 | 입력을 `[ROLE] [GOAL] [CONSTRAINTS] [CONTEXT] [QUESTION]`으로 정리해 제시하고, 승인 후 실행한다. 입력에 없는 내용은 임의로 채우지 않고 되묻는다. |
| 역할 자동 판단 | 코드와 요청을 읽고 "시니어 백엔드 엔지니어, 성능 최적화 중심"처럼 역할과 중점을 정해 밝힌다. 근거가 약하면 "추측"으로 표시한다. |
| 큰 요청 분해 | "전체 로그인 시스템 다 만들어줘" 같은 요청은 분석, 문제 설명, 해결 방법의 3단계 계획을 먼저 제시한다. 승인 후 구현한다. |
| 긴 로그 처리 | 100줄 이상의 로그에서 오류 관련 줄만 추려 `[Relevant Logs Only]`로 분석한다. 추린 기준과 제외한 줄 수를 함께 밝힌다. |
| 전달력 점검 | 사용자가 쓴 글을 목표, 대상, 맥락, 제약, 초점의 5개 항목(5점 만점)으로 평가하고 보완할 점을 제시한다. |
| 학습 기록과 통계 | 점수와 빠뜨린 항목을 기록한다. `/prompt-coach:prompt-coach 통계`로 자주 빠뜨리는 항목과 점수 변화를 확인할 수 있다. |

## 출력 예시

입력: `너의 스킬에 대해 짧게 요약해봐`

```
전달력 점검: 3/5 (보통)
- ✓ 목표: "요약해봐"
- ✗ 대상: 어떤 스킬인지 알 수 없음 → "prompt-coach 스킬"처럼 이름 적기
- ✗ 맥락: 요약이 필요한 이유가 없음 → "엑셀 제출용으로"
- ✓ 제약: "짧게"
- ✓ 초점: 요청이 하나

이렇게 물으면 됩니다:
엑셀 제출용으로 prompt-coach 스킬을 세 줄 이내로 요약해줘.
```

## 전달력 점수 기준

| 항목 | 기준 |
|------|------|
| 목표 | 원하는 결과가 드러난다. |
| 대상 | 다룰 파일, 코드, 문서가 지정되어 있다. |
| 맥락 | 현재 상태, 에러, 환경 중 하나 이상이 적혀 있다. |
| 제약 | 범위, 금지 사항, 형식, 기한 중 하나 이상이 적혀 있다. |
| 초점 | 요청이 하나로 좁혀져 있다. |

항목당 1점이며 4~5점은 "잘 전달됨", 2~3점은 "보통", 0~1점은 "보완 필요"로 구분한다.
평가는 사용자가 쓴 글만 기준으로 한다. Claude가 파일을 읽어 알게 된 내용은 점수에 반영하지 않는다. 따라서 점수는 사용자의 작성 습관을 나타낸다.

## 기록과 개인정보

- 기록은 로컬의 `~/.claude/ask-log.jsonl`에만 저장되며 외부로 전송되지 않는다.
- 입력은 앞 200자만 저장한다. 토큰, 키, 비밀번호, 이메일 패턴은 `***`로 가린다.
- 기록을 삭제하려면 해당 파일을 지우면 된다.
- 기록과 통계 기능에는 Python 3이 필요하다. 설치되어 있지 않으면 이 두 기능만 제외하고 동작한다.

## 유의사항

- 역할과 중점은 코드와 요청에서 추정한 값이다. 틀렸다고 지적하면 해당 부분만 고쳐 다시 제시한다.
- 승인 전에는 파일 수정, 삭제, 커밋 같은 실행을 하지 않는다.
- 이전에 `ask-marketplace`를 추가한 적이 있다면 `/plugin marketplace remove ask-marketplace`로 제거한 뒤 설치한다.

## 구성

```
.claude-plugin/marketplace.json                              # 마켓플레이스 목록
plugins/prompt-coach/.claude-plugin/plugin.json              # 플러그인 정보
plugins/prompt-coach/skills/prompt-coach/SKILL.md            # 스킬 본문
plugins/prompt-coach/skills/prompt-coach/scripts/ask_log.py  # 기록·통계 스크립트
```
