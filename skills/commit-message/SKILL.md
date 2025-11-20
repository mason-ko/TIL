---
name: commit-message
description: "Guide for creating Git commit messages using Conventional Commits format with Korean language. Use when Claude needs to create, suggest, or review commit messages. This skill ensures commits follow the type(scope): title format with Korean descriptions for better readability in Korean development teams."
---

# Commit Message

## Overview

This skill provides guidelines for creating Git commit messages using the Conventional Commits format with Korean language content. It ensures consistency and clarity in commit history while maintaining Korean as the primary language for descriptions.

## Conventional Commits Format

Every commit message must follow this structure:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type (필수)

Commit type은 영문으로 작성하며, 다음 중 하나를 사용:

- `feat`: 새로운 기능 추가
- `fix`: 버그 수정
- `docs`: 문서 수정
- `style`: 코드 포맷팅, 세미콜론 누락 등 (코드 변경 없음)
- `refactor`: 코드 리팩토링 (기능 변경 없음)
- `test`: 테스트 코드 추가 또는 수정
- `chore`: 빌드 업무, 패키지 매니저 설정 등
- `perf`: 성능 개선
- `ci`: CI/CD 설정 변경
- `build`: 빌드 시스템 또는 외부 종속성 변경
- `revert`: 이전 커밋 되돌리기

### Scope (선택)

변경 범위를 나타내는 명사 (영문 또는 한글 가능):

- 모듈명, 컴포넌트명, 파일명 등
- 예: `auth`, `user`, `api`, `database`

### Subject (필수)

커밋의 간단한 설명을 **한글**로 작성:

- 50자 이내로 작성
- 명령형 또는 현재 시제 사용 ("추가함" 대신 "추가")
- 마침표 없이 작성
- 첫 글자는 대문자로 시작하지 않음

### Body (선택)

커밋의 상세 설명을 **한글**로 작성:

- 무엇을, 왜 변경했는지 설명
- 어떻게 변경했는지는 코드에서 확인 가능하므로 생략 가능
- 한 줄당 72자 이내
- subject와 한 줄 띄우기

### Footer (선택)

이슈 추적 또는 Breaking Changes 명시:

- `Fixes: #123` - 이슈 번호 참조
- `BREAKING CHANGE:` - 호환성이 깨지는 변경사항
- `Co-authored-by:` - 공동 작업자 명시

## 작성 예시

### 기본 예시

```
feat(auth): 소셜 로그인 기능 추가
```

```
fix(user): 프로필 이미지 업로드 오류 수정
```

```
docs(readme): 설치 가이드 업데이트
```

### Body 포함 예시

```
feat(payment): 결제 모듈 구현

- 카카오페이, 네이버페이 연동
- 결제 내역 조회 API 추가
- 환불 처리 로직 구현
```

```
refactor(api): REST API 구조 개선

기존 컨트롤러 계층을 서비스 계층과 분리하여
코드 재사용성과 테스트 용이성 향상
```

### Footer 포함 예시

```
fix(database): 트랜잭션 처리 오류 수정

중첩된 트랜잭션에서 발생하는 데드락 문제 해결

Fixes: #456
```

```
feat(api): 사용자 인증 방식 변경

JWT 기반 인증에서 OAuth2로 전환

BREAKING CHANGE: 기존 API 토큰은 더 이상 사용 불가
```

## 작성 가이드라인

### DO

- 변경사항을 명확하게 설명
- 한 커밋에는 하나의 논리적 변경만 포함
- 왜 변경했는지 이유 명시 (body 사용 시)
- 이슈 번호 연결 (관련 이슈가 있는 경우)

### DON'T

- 너무 긴 subject 작성 (50자 초과)
- 불명확한 표현 ("수정", "변경" 등만 작성)
- 여러 가지 변경사항을 하나의 커밋에 포함
- 코드 변경 없이 공백이나 포맷만 변경 (별도 커밋으로 분리)

## 추가 리소스

더 자세한 예시와 패턴은 `references/examples.md`를 참고하세요.
