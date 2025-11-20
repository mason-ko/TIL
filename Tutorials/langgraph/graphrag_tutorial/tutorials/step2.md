# Step 2: 문서 처리와 청킹

## 개요
RAG 시스템의 성능은 문서를 얼마나 잘 청킹하느냐에 크게 좌우됩니다.
이번 단계에서는 다양한 청킹 전략과 최적화 방법을 배웁니다.

## 사전 준비

### 필요한 패키지 설치
```bash
pip install langchain langchain-text-splitters langchain-google-genai langchain-community faiss-cpu numpy
```

### 실행
```bash
python tutorials/step2.py
```

## 청킹이 중요한 이유

### 문제: 긴 문서는 직접 사용할 수 없다

1. **토큰 제한**
   - LLM은 입력 토큰 제한이 있음 (예: GPT-4o-mini는 128K 토큰)
   - 긴 문서 전체를 넣을 수 없음

2. **비용**
   - 토큰 사용량에 비례하여 비용 발생
   - 불필요한 내용까지 넣으면 비용 낭비

3. **품질**
   - 관련 없는 정보가 많으면 LLM이 혼란
   - 정확한 답변 어려움

### 해결책: 청킹

```
큰 문서 → 작은 청크들 → 관련 청크만 검색 → LLM
```

## 청킹 전략

### 1. 고정 크기 청킹

**CharacterTextSplitter:**
```python
splitter = CharacterTextSplitter(
    separator="\n\n",
    chunk_size=200,
    chunk_overlap=20
)
```

**특징:**
- 간단하고 빠름
- 구분자 기준으로 분할
- 고정된 크기 유지

**장점:** ✅ 구현 간단, 빠름
**단점:** ❌ 의미 단위 무시, 문장 중간에 끊길 수 있음

### 2. Recursive 청킹 (추천)

**RecursiveCharacterTextSplitter:**
```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", ". ", " ", ""]
)
```

**동작 방식:**
1. 먼저 `\n\n`로 분할 시도
2. 청크가 여전히 크면 `\n`로 분할
3. 계속해서 더 작은 구분자 사용
4. 마지막으로 문자 단위 분할

**장점:**
✅ 자연스러운 경계 유지
✅ 의미 단위 보존
✅ 가장 널리 사용됨

**사용 사례:** 대부분의 텍스트 문서

### 3. 토큰 기반 청킹

**TokenTextSplitter:**
```python
splitter = TokenTextSplitter(
    chunk_size=100,  # 100 토큰
    chunk_overlap=10
)
```

**특징:**
- LLM의 토큰 계산 방식과 일치
- 정확한 토큰 수 제어

**장점:** ✅ 토큰 제한 정확히 준수
**단점:** ❌ 느림 (토큰화 과정)

**사용 사례:** 토큰 제한이 엄격한 경우

### 4. 구조 기반 청킹

**MarkdownHeaderTextSplitter:**
```python
markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[
        ("#", "Header 1"),
        ("##", "Header 2"),
    ]
)
```

**특징:**
- 문서 구조 활용
- 헤더 기준 분할
- 메타데이터에 헤더 정보 보존

**장점:**
✅ 논리적 구조 유지
✅ 문맥 정보 풍부 (헤더가 메타데이터로)

**사용 사례:** Markdown, HTML 문서

### 5. 의미 기반 청킹

**임베딩으로 의미적 경계 찾기:**
```python
# 문단별 임베딩
embeddings = model.embed_documents(paragraphs)

# 연속 문단 간 유사도 계산
similarity = cosine_similarity(emb[i], emb[i+1])

# 유사도 낮으면 (주제 전환) 새 청크 시작
if similarity < threshold:
    start_new_chunk()
```

**장점:**
✅ 주제별로 그룹화
✅ 의미적 일관성

**단점:**
❌ 느림 (임베딩 계산)
❌ 복잡함

**사용 사례:** 품질이 매우 중요한 경우

## 핵심 파라미터

### chunk_size
```python
chunk_size=500  # 최대 청크 크기
```

**고려사항:**
- 너무 작으면: 문맥 부족, 검색 정확도 하락
- 너무 크면: 관련 없는 정보 포함, 비용 증가

**권장값:**
- 짧은 FAQ: 200-500자
- 일반 문서: 500-1000자
- 기술 문서: 1000-1500자

### chunk_overlap
```python
chunk_overlap=50  # 청크 간 중복
```

**목적:**
- 경계에서 잘린 문장 복구
- 문맥 연속성 유지

**권장값:**
- chunk_size의 10-20%

**예시:**
```
청크1: "...이것은 중요한 개념입니다. 이 개념은..."
청크2:           "이 개념은 다음과 같이 적용됩니다..."
         ↑ 중복 부분
```

## 코드 설명

### 1. 기본 청킹 (`basic_chunking_example`)

```python
text_splitter = CharacterTextSplitter(
    separator="\n\n",
    chunk_size=200,
    chunk_overlap=20
)
chunks = text_splitter.split_text(long_text)
```

**분할 과정:**
1. `\n\n`로 텍스트 분할
2. 각 조각이 200자 이하인지 확인
3. 너무 크면 더 분할
4. 20자씩 중복하여 청크 생성

### 2. Recursive Splitter (`recursive_splitter_example`)

**우선순위:**
```python
separators=["\n\n", "\n", " ", ""]
```

1. 먼저 단락(`\n\n`)으로 나누기 시도
2. 여전히 크면 줄바꿈(`\n`)으로
3. 그래도 크면 공백(` `)으로
4. 마지막으로 문자 단위

**왜 좋은가?**
- 자연스러운 경계 우선
- 의미 단위 보존
- 유연함

### 3. Markdown Splitter (`markdown_splitter_example`)

```python
headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
]
```

**결과:**
```python
Document(
    page_content="이 프로젝트는...",
    metadata={
        "Header 1": "프로젝트 문서",
        "Header 2": "1. 개요"
    }
)
```

**메타데이터의 가치:**
- 문서 구조 정보 보존
- 검색 시 필터링 가능
- LLM에게 문맥 제공

### 4. 의미 기반 청킹 (`semantic_chunking_example`)

**알고리즘:**
```python
current_chunk = [paragraphs[0]]

for i in range(len(paragraphs) - 1):
    similarity = cosine_similarity(emb[i], emb[i+1])

    if similarity > threshold:
        current_chunk.append(paragraphs[i+1])  # 같은 주제
    else:
        chunks.append(current_chunk)  # 주제 전환, 새 청크
        current_chunk = [paragraphs[i+1]]
```

**코사인 유사도:**
- 1에 가까우면: 매우 유사
- 0에 가까우면: 관련 없음

**임계값 선택:**
- 높게 (0.9): 매우 유사한 것만 묶음 → 많은 청크
- 낮게 (0.7): 느슨하게 묶음 → 적은 청크

### 5. 메타데이터 활용 (`chunking_with_metadata`)

**메타데이터 추가:**
```python
Document(
    page_content=chunk_text,
    metadata={
        "source": "products.txt",
        "product": "Alpha Pro",
        "category": "premium",
        "chunk_id": 0
    }
)
```

**필터링 검색:**
```python
results = vectorstore.similarity_search(
    query,
    filter={"category": "premium"}
)
```

**장점:**
- 특정 범위만 검색 (빠름)
- 정확도 향상 (관련 없는 문서 제외)
- 출처 추적 용이

## 청킹 베스트 프랙티스

### 1. 문서 타입별 전략

| 문서 타입 | 추천 Splitter | chunk_size |
|-----------|---------------|------------|
| 일반 텍스트 | RecursiveCharacterTextSplitter | 500-1000 |
| Markdown | MarkdownHeaderTextSplitter | 구조 기반 |
| 코드 | RecursiveCharacterTextSplitter (언어별) | 1000-1500 |
| FAQ | CharacterTextSplitter | 200-500 |

### 2. 청크 크기 결정 기준

**고려 요소:**
1. 질문의 복잡도
   - 단순: 작은 청크
   - 복잡: 큰 청크 (더 많은 문맥 필요)

2. 문서의 밀도
   - 정보 밀도 높음: 작은 청크
   - 설명적/장황함: 큰 청크

3. 검색 정확도 vs 비용
   - 작은 청크: 정확도↑, 검색 횟수↑
   - 큰 청크: 비용↓, 노이즈↑

### 3. 메타데이터 설계

**필수 메타데이터:**
```python
{
    "source": "문서 출처",
    "title": "문서 제목",
    "chunk_id": "청크 번호",
    "total_chunks": "전체 청크 수"
}
```

**선택 메타데이터:**
```python
{
    "author": "작성자",
    "date": "작성일",
    "category": "카테고리",
    "tags": ["태그1", "태그2"],
    "section": "섹션 제목"
}
```

### 4. 청크 품질 검증

```python
# 1. 청크 크기 분포 확인
sizes = [len(chunk) for chunk in chunks]
print(f"평균: {np.mean(sizes)}")
print(f"표준편차: {np.std(sizes)}")

# 2. 빈 청크 제거
chunks = [c for c in chunks if len(c.strip()) > 0]

# 3. 너무 작은 청크 병합
min_size = 100
# 병합 로직...
```

## 고급 테크닉

### 1. 계층적 청킹

```
큰 청크 (요약용) + 작은 청크 (상세 검색용)
```

**전략:**
- 먼저 작은 청크로 검색
- 관련 청크 발견 시 큰 청크(부모) 사용

### 2. Sliding Window

```
청크1: [0:500]
청크2: [400:900]  ← 100자 중복
청크3: [800:1300]
```

**장점:**
- 경계 문제 최소화
- 문맥 손실 감소

### 3. 문장 경계 존중

```python
# 문장 중간에 끊지 않기
import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize

sentences = sent_tokenize(text)
# 문장 단위로 청크 구성
```

## 실험과 최적화

### A/B 테스트

1. **다양한 chunk_size 시도**
   - 300, 500, 1000자 비교
   - 검색 정확도 측정

2. **Overlap 비율 실험**
   - 0%, 10%, 20% overlap
   - 답변 품질 평가

3. **Splitter 비교**
   - Character vs Recursive vs Semantic
   - 도메인별 최적 방법 선택

### 평가 지표

```python
# 1. 검색 정확도
# 관련 문서를 잘 찾는가?

# 2. 답변 품질
# LLM이 정확한 답변을 생성하는가?

# 3. 효율성
# 검색 속도, 비용은 적절한가?
```

## 핵심 개념 정리

### 1. 청킹은 RAG의 핵심
- 품질이 답변의 질을 결정
- 도메인별 최적화 필요

### 2. Recursive Splitter 추천
- 대부분의 경우 최선
- 자연스러운 경계 유지

### 3. 메타데이터 활용
- 필터링으로 정확도 향상
- 출처 추적 가능

### 4. 실험이 중요
- 정답은 없음
- 데이터와 유스케이스에 따라 다름

## 다음 단계

문서 처리와 청킹을 마스터했습니다!

다음 단계(Step 3)에서는 드디어 **그래프 구조 구축**을 배웁니다.

**Step 3에서 배울 내용:**
- 문서 간 관계 추출
- 지식 그래프 구축
- 엔티티와 관계 인식
- 그래프 저장 및 쿼리
