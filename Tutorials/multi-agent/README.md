# 멀티 에이전트 시스템 튜토리얼

여러 AI 에이전트가 협업하는 복잡한 시스템 구축

## 개요

**여러 전문 에이전트**가 협력하여 복잡한 문제를 해결하는 시스템을 학습합니다.

## 단일 vs 멀티 에이전트

### 단일 에이전트
```python
# 모든 일을 혼자 처리
Agent: 코딩도 하고, 검색도 하고, 분석도 하고...
→ 복잡도 증가, 성능 저하
```

### 멀티 에이전트
```python
# 전문 에이전트 협업
Researcher: 정보 검색 전문
Coder: 코드 작성 전문
Reviewer: 코드 리뷰 전문
→ 각자 전문 분야, 높은 품질
```

## 아키텍처 패턴

### 1. Sequential (순차)
```
Agent 1 → Agent 2 → Agent 3
(검색)    (분석)    (요약)
```

### 2. Hierarchical (계층)
```
    Manager
   /    |    \
Agent1 Agent2 Agent3
```

### 3. Network (네트워크)
```
Agent1 ↔ Agent2
  ↕         ↕
Agent3 ↔ Agent4
```

## 학습 목차

**Step 1**: 기본 멀티 에이전트 (순차 실행)
**Step 2**: Supervisor 패턴 (관리자 + 작업자)
**Step 3**: Collaborative 패턴 (대화형 협업)
**Step 4**: Tool Sharing (도구 공유)
**Step 5**: State Management (상태 관리)
**Step 6**: 실전 프로젝트 (자동 리서치 봇)

## 실무 예시

### 1. 소프트웨어 개발팀
```python
Product Manager: 요구사항 정의
Architect: 시스템 설계
Developer: 코드 구현
Tester: 테스트 작성
Reviewer: 코드 리뷰
```

### 2. 리서치 팀
```python
Searcher: 웹 검색, 논문 검색
Analyzer: 데이터 분석
Writer: 보고서 작성
```

### 3. 고객 지원
```python
Classifier: 문의 분류
Responder: 답변 생성
Escalator: 복잡한 문의 → 인간에게 전달
```

## 프레임워크

| 프레임워크 | 특징 |
|-----------|------|
| **LangGraph** | 상태 머신 기반, 유연 |
| **AutoGen** | Microsoft, 대화형 |
| **CrewAI** | 역할 기반, 쉬움 |
| **MetaGPT** | 소프트웨어 회사 시뮬레이션 |

---

**학습 목표**: 여러 전문 에이전트를 조율하여 복잡한 작업을 자동화할 수 있다.
