# Fine-tuning 기초 튜토리얼

오픈소스 LLM을 특정 도메인에 최적화

## 개요

**사전 학습된 모델**을 우리 데이터로 추가 학습시켜 성능을 향상시킵니다.

## 왜 Fine-tuning?

### Before (일반 모델)
```python
# 의료 도메인 질문
Q: "COPD의 1차 치료는?"
A: "잘 모르겠습니다..." ❌

# 회사 코딩 스타일
Q: "API 엔드포인트 만들어줘"
A: [Express.js 코드] ❌ (우리는 FastAPI 사용)
```

### After (Fine-tuned 모델)
```python
Q: "COPD의 1차 치료는?"
A: "기관지 확장제와 스테로이드..." ✅

Q: "API 엔드포인트 만들어줘"
A: [FastAPI 코드, 회사 스타일] ✅
```

## Fine-tuning 방법

### 1. Full Fine-tuning
- 모든 파라미터 업데이트
- 최고 품질, 느림, 비쌈
- GPU 메모리: 70B 모델 = 280GB+

### 2. LoRA (Low-Rank Adaptation)
- 작은 어댑터만 학습
- 빠름, 저렴, 품질 90%
- GPU 메모리: 70B 모델 = 40GB

### 3. QLoRA (Quantized LoRA)
- LoRA + 양자화
- 가장 효율적
- GPU 메모리: 70B 모델 = 20GB

## 학습 목차

**Step 1**: 데이터셋 준비
**Step 2**: LoRA Fine-tuning (기본)
**Step 3**: QLoRA (효율적)
**Step 4**: 평가 및 비교
**Step 5**: 배포 및 사용
**Step 6**: 고급 기법 (RLHF, DPO)

## 필요한 것

### 하드웨어
- **7B 모델**: RTX 3090 (24GB)
- **13B 모델**: RTX 4090 (24GB) + QLoRA
- **70B 모델**: A100 (40GB) x 2 + QLoRA

### 데이터
- 최소: 1,000개 예시
- 권장: 10,000개 이상
- 고품질 > 양

## 빠른 시작 (LoRA)

```python
from transformers import AutoModelForCausalLM
from peft import LoraConfig, get_peft_model

# 1. 베이스 모델 로드
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b")

# 2. LoRA 설정
lora_config = LoraConfig(
    r=16,  # Rank
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
)

# 3. LoRA 어댑터 추가
model = get_peft_model(model, lora_config)

# 4. 학습
trainer.train()
```

## 비용 분석

| 방법 | GPU | 시간 (10K 샘플) | 비용 |
|------|-----|-----------------|------|
| Full FT | A100 x 8 | 10시간 | $500 |
| LoRA | RTX 4090 | 5시간 | $50 |
| QLoRA | RTX 3090 | 8시간 | $20 |

## 실무 활용

### 1. 도메인 특화
- 의료, 법률, 금융 전문 모델
- 회사 내부 지식 학습

### 2. 스타일 맞춤
- 회사 코딩 스타일
- 브랜드 톤앤매너

### 3. 다국어 강화
- 한국어 성능 향상
- 저자원 언어 지원

---

**학습 목표**: 오픈소스 LLM을 LoRA/QLoRA로 효율적으로 fine-tuning할 수 있다.
