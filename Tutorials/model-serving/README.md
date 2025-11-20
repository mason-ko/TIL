# Model Serving 튜토리얼

자체 LLM 모델 운영 및 배포

## 개요

OpenAI API 대신 **자체 오픈소스 모델**을 운영하는 방법을 학습합니다.

## 왜 자체 모델을 운영하나?

### 장점
- **비용 절감**: API 비용 50-90% 감소
- **데이터 프라이버시**: 외부로 데이터 전송 안 함
- **커스터마이징**: Fine-tuning, 특화 모델
- **속도**: 내부 네트워크, 낮은 지연시간

### 단점
- 인프라 관리 필요
- 초기 설정 복잡
- GPU 리소스 필요

## 주요 도구

| 도구 | 특징 | 사용 사례 |
|------|------|----------|
| **Ollama** | 로컬 실행, 쉬움 | 개발, 프로토타입 |
| **vLLM** | 고성능, 배치 처리 | 프로덕션 |
| **TGI** | HuggingFace 공식 | 다양한 모델 |
| **LM Studio** | GUI, 초보자용 | 테스트 |

## 학습 목차

**Step 1**: Ollama 로컬 설정 (Llama 3, Mistral)
**Step 2**: vLLM 프로덕션 배포
**Step 3**: API 서버 구축 (FastAPI)
**Step 4**: 로드 밸런싱 및 확장
**Step 5**: 모니터링 및 최적화
**Step 6**: Fine-tuned 모델 배포

## 빠른 시작 (Ollama)

```bash
# 1. Ollama 설치
curl -fsSL https://ollama.com/install.sh | sh

# 2. 모델 다운로드
ollama pull llama3

# 3. 실행
ollama run llama3
```

```python
# Python에서 사용
from langchain_community.llms import Ollama

llm = Ollama(model="llama3")
response = llm.invoke("안녕하세요!")
```

## 성능 비교

| 모델 | 파라미터 | 속도 | 품질 |
|------|----------|------|------|
| Llama 3 8B | 8B | 빠름 | 좋음 |
| Llama 3 70B | 70B | 느림 | 우수 |
| Mistral 7B | 7B | 빠름 | 좋음 |
| Mixtral 8x7B | 47B | 중간 | 우수 |

## 비용 분석

```
OpenAI GPT-3.5:
$0.50 / 1M tokens (입력)
→ 월 10M 토큰 = $5,000

자체 서버 (RTX 4090):
서버 비용: $2,000/월
→ 4개월이면 본전

대규모 (100M 토큰/월):
OpenAI: $50,000/월
자체: $5,000/월 (GPU 서버)
→ 90% 절감
```

---

**학습 목표**: 오픈소스 LLM을 자체 서버에 배포하고 운영할 수 있다.
