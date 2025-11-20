# GraphRAG 학습 튜토리얼

GraphRAG (Graph-based Retrieval-Augmented Generation) 기술을 처음부터 배우는 단계별 튜토리얼입니다.
기본 RAG부터 시작하여 고급 GraphRAG 시스템 구축까지 다룹니다.

## 대상 독자

- 백엔드 개발 경험이 있는 개발자
- RAG 및 GraphRAG를 처음 배우는 분
- Python 기본 문법을 알고 있는 분
- **실제로 동작하는 코드**와 **작동 원리 이해**가 목표인 분

## GraphRAG란?

**기본 RAG의 한계:**
- 단순 벡터 유사도만 고려
- 문서 간 관계 무시
- 다중 홉 추론 어려움

**GraphRAG의 해결책:**
- 문서를 지식 그래프로 표현
- 엔티티 간 관계 활용
- 다중 홉 추론 가능
- 전역적 질문 처리

```
기본 RAG: 문서 → 벡터 → 유사도 검색
GraphRAG: 문서 → 그래프(엔티티+관계) → 그래프 탐색 + 벡터 검색
```

## 사전 준비

### 1. Python 환경
Python 3.9 이상 권장

### 2. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. Google Gemini API 키 설정

[Google AI Studio](https://aistudio.google.com/app/apikey)에서 API 키를 발급받으세요.

**방법 1: .env 파일 사용 (추천)**

프로젝트 루트 디렉토리에 `.env` 파일을 생성하세요:

```bash
# .env.example을 복사하여 .env 파일 생성
cp .env.example .env
```

`.env` 파일을 열고 API 키를 입력하세요:
```
GOOGLE_API_KEY=your-actual-api-key-here
```

**방법 2: 환경변수 직접 설정**

Linux/Mac:
```bash
export GOOGLE_API_KEY='your-api-key-here'
```

Windows (PowerShell):
```powershell
$env:GOOGLE_API_KEY='your-api-key-here'
```

Windows (CMD):
```cmd
set GOOGLE_API_KEY=your-api-key-here
```

**중요:** `.env` 파일은 절대 Git에 커밋하지 마세요! (`.gitignore`에 포함되어 있어야 합니다)

## 튜토리얼 구조

각 단계마다 두 개의 파일이 있습니다:
- `stepN.py`: 실행 가능한 Python 코드
- `stepN.md`: 상세한 설명과 개념 정리

### Step 1: 기본 RAG 개념
**위치:** `tutorials/step1.py`, `tutorials/step1.md`

**내용:**
- RAG가 필요한 이유
- 벡터 저장소와 임베딩
- 기본 RAG 파이프라인
- 다양한 검색 방법

**실행:**
```bash
python tutorials/step1.py
```

**핵심 개념:**
- RAG = Retrieval + Generation
- 임베딩과 벡터 검색
- FAISS, Pinecone 등 벡터 DB
- 유사도 측정

### Step 2: 문서 처리와 청킹
**위치:** `tutorials/step2.py`, `tutorials/step2.md`

**내용:**
- 다양한 청킹 전략
- RecursiveCharacterTextSplitter
- 토큰 기반 청킹
- 의미 기반 청킹
- 메타데이터 활용

**실행:**
```bash
python tutorials/step2.py
```

**핵심 개념:**
- 청킹이 RAG 성능을 결정
- chunk_size와 chunk_overlap
- 문서 타입별 최적 전략
- 메타데이터로 필터링 검색

### Step 3: 그래프 구조 구축
**위치:** `tutorials/step3.py`, `tutorials/step3.md`

**내용:**
- 엔티티 추출
- 관계 추출
- 지식 그래프 생성
- NetworkX 사용법
- 커뮤니티 감지

**실행:**
```bash
python tutorials/step3.py
```

**핵심 개념:**
- 엔티티 (노드): 사람, 조직, 개념 등
- 관계 (엣지): 엔티티 간 연결
- 지식 그래프 = 구조화된 지식
- 그래프 쿼리와 분석

### Step 4: GraphRAG 기본
**위치:** `tutorials/step4.py`, `tutorials/step4.md`

**내용:**
- 하이브리드 검색 (벡터 + 그래프)
- 다중 홉 추론
- 그래프 기반 컨텍스트 확장
- 완전한 GraphRAG 파이프라인

**실행:**
```bash
python tutorials/step4.py
```

**핵심 개념:**
- 벡터 검색으로 진입점 찾기
- 그래프로 관계 확장
- 다중 홉으로 간접 정보 활용
- 통합 컨텍스트로 답변 생성

### Step 5: 커뮤니티 감지와 요약
**위치:** `tutorials/step5.py`, `tutorials/step5.md`

**내용:**
- 커뮤니티 감지 알고리즘
- 계층적 요약
- 전역 검색 vs 지역 검색
- Map-Reduce 패턴

**실행:**
```bash
python tutorials/step5.py
```

**핵심 개념:**
- 커뮤니티 = 밀접하게 연결된 노드 그룹
- 커뮤니티별 요약으로 전역 질문 처리
- 전역 검색: 넓은 질문
- 지역 검색: 구체적 질문

### Step 6: 실전 GraphRAG 시스템
**위치:** `tutorials/step6.py`, `tutorials/step6.md`

**내용:**
- 완전한 GraphRAG 시스템 구현
- 검색 전략 선택
- RAG vs GraphRAG 비교
- 실전 활용 팁

**실행:**
```bash
python tutorials/step6.py
```

**핵심 개념:**
- 전체 파이프라인 통합
- 상황에 맞는 검색 전략
- 성능 최적화
- 프로덕션 고려사항

## 학습 순서

1. **Step 1부터 순서대로 진행하세요**
   - 각 단계가 이전 단계를 기반으로 합니다

2. **코드를 직접 실행하세요**
   - 결과를 보면서 이해도를 높이세요

3. **코드를 수정해보세요**
   - 파라미터를 바꿔보고 결과를 관찰하세요
   - 다른 문서로 테스트해보세요

4. **문서를 함께 읽으세요**
   - `.md` 파일에 개념 설명과 내부 동작이 상세히 나와 있습니다

## 프로젝트 구조

```
graphrag_tutorial/
├── README.md                 # 이 파일
├── requirements.txt          # 필요한 패키지
├── tutorials/
│   ├── step1.py             # Step 1 코드
│   ├── step1.md             # Step 1 설명
│   ├── step2.py             # Step 2 코드
│   ├── step2.md             # Step 2 설명
│   ├── step3.py             # Step 3 코드
│   ├── step3.md             # Step 3 설명
│   ├── step4.py             # Step 4 코드
│   ├── step4.md             # Step 4 설명
│   ├── step5.py             # Step 5 코드
│   ├── step5.md             # Step 5 설명
│   ├── step6.py             # Step 6 코드
│   └── step6.md             # Step 6 설명
```

## 주요 개념 요약

### GraphRAG 핵심 요소

| 요소 | 설명 | 예시 |
|------|------|------|
| **엔티티** | 그래프의 노드 | PERSON, ORGANIZATION, CONCEPT |
| **관계** | 노드 간 연결 | WORKS_AT, DEVELOPS, USES |
| **커뮤니티** | 밀집된 노드 그룹 | AI/ML 커뮤니티, 언어 커뮤니티 |
| **요약** | 커뮤니티 설명 | "AI 관련 개념들의 집합" |
| **다중 홉** | 여러 단계 추론 | A→B→C 경로 탐색 |

### 학습 경로

```
기본 RAG 이해 (Step 1)
    ↓
문서 처리와 청킹 (Step 2)
    ↓
그래프 구조 구축 (Step 3)
    ↓
GraphRAG 검색 (Step 4)
    ↓
커뮤니티와 계층적 요약 (Step 5)
    ↓
실전 시스템 구축 (Step 6)
```

## 문제 해결

### API 키 오류
```
Error: API key not found
```
→ 환경변수 `GOOGLE_API_KEY`가 설정되었는지 확인하세요.

### 패키지 import 오류
```
ModuleNotFoundError: No module named 'networkx'
```
→ `pip install -r requirements.txt` 실행하세요.

### 그래프 시각화 오류
```
Matplotlib backend error
```
→ GUI 없는 환경에서는 `plt.savefig()` 사용하세요.

## GraphRAG vs 기본 RAG

### 언제 GraphRAG를 사용할까?

**GraphRAG가 유리한 경우:**
✅ 복잡한 도메인 지식 (법률, 의료, 기술 문서)
✅ 다중 문서 간 관계가 중요
✅ 전역적 질문 ("전체 시스템 구조는?")
✅ 다중 홉 추론 필요

**기본 RAG가 충분한 경우:**
✅ 단순 FAQ
✅ 독립적인 문서들
✅ 빠른 응답 필요
✅ 단일 문서 검색

## 참고 자료

### 공식 문서 및 논문
- [Microsoft GraphRAG](https://github.com/microsoft/graphrag)
- [GraphRAG 논문](https://arxiv.org/abs/2404.16130)
- [LangChain 공식 문서](https://python.langchain.com/)
- [Google Gemini API 문서](https://ai.google.dev/docs)
- [NetworkX 문서](https://networkx.org/)

### 추가 학습
- Neo4j 그래프 데이터베이스
- 지식 그래프 구축 도구
- NER (Named Entity Recognition)
- 관계 추출 (Relation Extraction)

## 다음 단계

이 튜토리얼을 완료했다면:

1. **실제 프로젝트에 적용**
   - 자신의 도메인 문서로 GraphRAG 구축
   - 성능 비교 (RAG vs GraphRAG)

2. **고급 기능 탐색**
   - Microsoft GraphRAG 라이브러리
   - Neo4j 통합
   - 실시간 그래프 업데이트
   - 분산 그래프 처리

3. **성능 최적화**
   - 그래프 크기 최적화
   - 캐싱 전략
   - 병렬 처리
   - 비용 관리

4. **프로덕션 배포**
   - 확장성 고려
   - 모니터링
   - A/B 테스트
   - 지속적 개선

## 기여

이 튜토리얼에 대한 피드백이나 개선 사항이 있다면 이슈를 열어주세요!

## 라이센스

이 튜토리얼은 학습 목적으로 자유롭게 사용할 수 있습니다.

---

**Happy Learning! 🚀**

GraphRAG로 더 스마트한 AI 시스템을 만들어보세요!
