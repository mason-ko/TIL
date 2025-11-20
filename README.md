# TIL (Today I Learned)

개발 학습 기록 및 튜토리얼 모음

## 📚 AI/LLM 튜토리얼

AI 시대의 필수 기술들을 단계별로 학습할 수 있는 튜토리얼 모음입니다.

### 🎯 학습 로드맵

```
[기초] LangGraph, GraphRAG
   ↓
[필수] LangSmith, Vector DB
   ↓
[중급] Advanced RAG, Multi-Agent
   ↓
[고급] Model Serving, Fine-tuning, MLOps
   ↓
[확장] Multimodal
```

## 튜토리얼 목록

### 1️⃣ [LangGraph](./Tutorials/langgraph/)
**AI 워크플로우의 상태 관리**

- 기본 개념: StateGraph, 노드, 엣지
- 조건부 분기 및 루프
- 체크포인트를 통한 대화 히스토리 관리
- 6단계 실습 가이드

**난이도**: ⭐ 입문
**소요 시간**: 2-3시간
**선수 지식**: Python 기초, LangChain 기본

### 2️⃣ [GraphRAG](./Tutorials/langgraph/graphrag_tutorial/)
**그래프 기반 문서 검색 증강 생성**

- 문서 처리 및 임베딩
- 지식 그래프 구축
- 검색 증강 생성 (RAG)
- 6단계 심화 가이드

**난이도**: ⭐⭐ 초급
**소요 시간**: 3-4시간
**선수 지식**: LangGraph, Vector 개념

### 3️⃣ [LangSmith](./Tutorials/langsmith/)
**프로덕션 LLM 모니터링 플랫폼**

- 실시간 트레이싱 및 디버깅
- 성능 메트릭 모니터링 (토큰, 비용, 지연시간)
- 평가 프레임워크 (Evaluation)
- A/B 테스팅 및 데이터셋 관리

**난이도**: ⭐⭐ 초급
**소요 시간**: 2-3시간
**핵심 가치**: 프로덕션 필수 도구

### 4️⃣ [Vector Database](./Tutorials/vectordb/)
**의미 기반 검색을 위한 벡터 DB**

- ChromaDB 로컬 설정
- 임베딩 모델 (OpenAI, HuggingFace)
- 유사도 검색 및 하이브리드 검색
- Pinecone 프로덕션 배포
- RAG 시스템 통합

**난이도**: ⭐⭐ 초급
**소요 시간**: 3-4시간
**핵심 가치**: RAG의 핵심 기술

### 5️⃣ [Advanced RAG](./Tutorials/advanced-rag/)
**고급 RAG 패턴으로 검색 정확도 향상**

- Hybrid Search (BM25 + 벡터)
- Reranking (재순위화)
- Query Rewriting (쿼리 개선)
- Contextual Compression (컨텍스트 압축)
- Parent Document Retrieval

**난이도**: ⭐⭐⭐ 중급
**소요 시간**: 4-5시간
**효과**: 검색 정확도 30-50% 향상

### 6️⃣ [Model Serving](./Tutorials/model-serving/)
**자체 LLM 모델 운영**

- Ollama 로컬 실행
- vLLM 고성능 배포
- API 서버 구축 (FastAPI)
- 로드 밸런싱 및 확장
- Fine-tuned 모델 배포

**난이도**: ⭐⭐⭐ 중급
**소요 시간**: 5-6시간
**비용 절감**: API 비용 50-90% 감소

### 7️⃣ [Multi-Agent Systems](./Tutorials/multi-agent/)
**여러 AI 에이전트의 협업**

- Sequential, Hierarchical, Network 패턴
- Supervisor 패턴 (관리자 + 작업자)
- Collaborative 패턴 (대화형 협업)
- Tool Sharing, State Management
- 실전: 자동 리서치 봇

**난이도**: ⭐⭐⭐⭐ 고급
**소요 시간**: 6-8시간
**활용**: 복잡한 작업 자동화

### 8️⃣ [Fine-tuning](./Tutorials/fine-tuning/)
**오픈소스 LLM 커스터마이징**

- 데이터셋 준비
- LoRA Fine-tuning
- QLoRA (효율적 학습)
- 평가 및 비교
- 고급: RLHF, DPO

**난이도**: ⭐⭐⭐⭐ 고급
**소요 시간**: 8-10시간
**필요**: GPU (RTX 3090 이상 권장)

### 9️⃣ [MLOps](./Tutorials/mlops/)
**LLM 애플리케이션 배포 및 운영**

- Docker 컨테이너화
- FastAPI 서버 구축
- CI/CD 파이프라인
- 모니터링 (Prometheus, Grafana)
- 프로덕션 최적화

**난이도**: ⭐⭐⭐⭐ 고급
**소요 시간**: 8-12시간
**핵심 가치**: 안정적 운영

### 🔟 [Multimodal](./Tutorials/multimodal/)
**텍스트 + 이미지 + 오디오 통합 AI**

- Vision (이미지 이해)
- Audio (음성 처리)
- Vision + Text RAG
- Audio + Text 챗봇
- Video 분석

**난이도**: ⭐⭐⭐ 중급
**소요 시간**: 4-6시간
**활용**: 다양한 입력 형식 처리

---

## 📖 학습 가이드

### 초보자 추천 순서
1. LangGraph (기본)
2. Vector DB
3. LangSmith
4. GraphRAG

### 실무자 추천 순서
1. LangSmith (모니터링 필수)
2. Advanced RAG (성능 개선)
3. Multi-Agent (복잡한 작업)
4. MLOps (안정적 운영)

### 비용 절감 목표
1. Vector DB (RAG 구축)
2. Model Serving (자체 운영)
3. Advanced RAG (정확도 향상 → 재시도 감소)

### 고급 개발자
1. Fine-tuning (도메인 특화)
2. MLOps (전체 파이프라인)
3. Multi-Agent (고도화)

---

## 🛠️ 공통 환경 설정

### 필요한 도구
```bash
# Python 3.11+
python --version

# Git
git --version

# 가상환경 (권장)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
```

### API Keys
대부분의 튜토리얼은 다음 중 하나 이상의 API Key가 필요합니다:

- **Google Gemini**: https://ai.google.dev/
- **OpenAI**: https://platform.openai.com/
- **LangSmith**: https://smith.langchain.com/

각 튜토리얼 폴더의 `.env.example`을 참고하세요.

---

## 📊 기술 스택 비교

| 기술 | 난이도 | 비용 | 프로덕션 | 학습 우선순위 |
|------|--------|------|----------|--------------|
| LangGraph | ⭐ | 무료 | ⭐⭐⭐ | 🔥 높음 |
| LangSmith | ⭐⭐ | 무료/유료 | ⭐⭐⭐⭐⭐ | 🔥 높음 |
| Vector DB | ⭐⭐ | 무료/유료 | ⭐⭐⭐⭐ | 🔥 높음 |
| Advanced RAG | ⭐⭐⭐ | 중간 | ⭐⭐⭐⭐ | 중간 |
| Model Serving | ⭐⭐⭐ | 높음(인프라) | ⭐⭐⭐⭐ | 중간 |
| Multi-Agent | ⭐⭐⭐⭐ | 높음 | ⭐⭐⭐ | 낮음 |
| Fine-tuning | ⭐⭐⭐⭐ | 높음(GPU) | ⭐⭐⭐ | 낮음 |
| MLOps | ⭐⭐⭐⭐ | 중간 | ⭐⭐⭐⭐⭐ | 높음 |
| Multimodal | ⭐⭐⭐ | 중간 | ⭐⭐⭐⭐ | 중간 |

---

## 💡 실무 활용 시나리오

### 시나리오 1: 사내 문서 검색 챗봇
```
필요한 튜토리얼:
1. Vector DB → 문서 임베딩
2. Advanced RAG → 검색 정확도 향상
3. LangSmith → 품질 모니터링
4. MLOps → 안정적 배포
```

### 시나리오 2: 자동화된 고객 지원
```
필요한 튜토리얼:
1. LangGraph → 대화 플로우
2. Multi-Agent → 문의 분류 + 답변
3. LangSmith → 성능 추적
4. Multimodal → 이미지 문의 처리
```

### 시나리오 3: 비용 최적화
```
필요한 튜토리얼:
1. Model Serving → 자체 모델 운영
2. Advanced RAG → 재시도 감소
3. Fine-tuning → 작은 모델로 고품질
```

---

## 🤝 기여 및 피드백

이 저장소는 지속적으로 업데이트됩니다.

- 오류 발견: Issue 등록
- 개선 제안: Pull Request
- 질문: Discussions

---

## 📝 라이선스

MIT License

---

**마지막 업데이트**: 2025-11-20

**작성자**: mason-ko

**연락처**: gym1029@gmail.com
