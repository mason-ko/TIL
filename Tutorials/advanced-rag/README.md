# 고급 RAG 패턴 튜토리얼

Retrieval-Augmented Generation의 고급 기법 학습

## 개요

기본 RAG의 한계를 극복하는 고급 패턴들을 학습합니다.

## 기본 RAG의 문제점

```python
# 기본 RAG
문서 임베딩 → 벡터 검색 → LLM에 전달

# 문제:
1. 검색 정확도 낮음 (키워드 빠지면 못 찾음)
2. 관련 없는 문서 포함
3. 중요한 정보 누락
4. 컨텍스트 길이 제한
```

## 고급 패턴

### 1. Hybrid Search (하이브리드 검색)
- 키워드 검색 + 벡터 검색 결합
- BM25 + Dense Retrieval
- 정확도 30% 향상

### 2. Reranking (재순위화)
- 검색 결과 재정렬
- Cross-encoder 사용
- 관련 없는 문서 제거

### 3. Query Rewriting (쿼리 재작성)
- 사용자 질문 개선
- Multi-query: 여러 버전 생성
- HyDE: 가상 답변 생성 후 검색

### 4. Contextual Compression (컨텍스트 압축)
- 관련 부분만 추출
- 토큰 사용량 감소
- 핵심만 LLM에 전달

### 5. Parent Document Retrieval
- 작은 청크로 검색
- 큰 컨텍스트 반환
- 정확도 + 컨텍스트 유지

## 학습 목차

**Step 1**: Hybrid Search (BM25 + Vector)
**Step 2**: Reranking (Cohere, Cross-encoder)
**Step 3**: Query Rewriting (Multi-query, HyDE)
**Step 4**: Contextual Compression
**Step 5**: Parent Document Retrieval
**Step 6**: Self-Query (메타데이터 필터링)

## 성능 비교

| 패턴 | 정확도 | 속도 | 비용 |
|------|--------|------|------|
| 기본 RAG | 60% | 빠름 | 낮음 |
| + Hybrid | 75% | 중간 | 낮음 |
| + Reranking | 85% | 느림 | 중간 |
| + Query Rewriting | 90% | 느림 | 높음 |

## 실무 권장

```python
# 단계별 적용
1단계: 기본 RAG로 시작
2단계: Hybrid Search 추가 (쉬움)
3단계: Reranking 추가 (효과 큼)
4단계: 필요시 Query Rewriting
```

---

**학습 목표**: 고급 RAG 패턴을 적용하여 검색 정확도를 크게 향상시킬 수 있다.
