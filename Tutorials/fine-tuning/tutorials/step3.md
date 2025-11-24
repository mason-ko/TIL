# Step 3: QLoRA (효율적 Fine-tuning)

## 목표

- Quantized LoRA로 메모리 절감
- 4bit 양자화
- 소규모 GPU에서 대형 모델 학습

## QLoRA란?

**LoRA + 4bit Quantization**

```python
일반 Fine-tuning: 70B 모델 = 280GB GPU 메모리
LoRA: 70B 모델 = 40GB
QLoRA: 70B 모델 = 20GB ✅ (RTX 3090에서 가능!)
```

## 핵심 기술

### 1. 4bit NormalFloat (NF4)

```python
# 32bit → 4bit 압축
모델 크기: 1/8로 감소
메모리: 대폭 절감
정확도: 99% 유지
```

### 2. Double Quantization

```python
# Quantization 상수도 양자화
추가 메모리 절감: 평균 0.4GB
```

### 3. Paged Optimizers

```python
# Adam optimizer 상태를 CPU로 페이징
GPU 메모리 부족 시 CPU 사용
OOM 에러 방지
```

## 구현

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model

# QLoRA 설정
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)

# 모델 로드 (4bit)
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b",
    quantization_config=bnb_config,
    device_map="auto"
)

# LoRA 어댑터
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)

# 학습
trainer.train()
```

## 성능 비교

| 방법 | GPU 메모리 | 속도 | 품질 |
|------|-----------|------|------|
| Full FT | 280GB | 1x | 100% |
| LoRA | 40GB | 2x | 98% |
| QLoRA | 20GB | 1.5x | 97% |

## 실무 활용

```python
# RTX 3090 (24GB)에서 13B 모델 학습 가능!
model_name = "meta-llama/Llama-2-13b"

# QLoRA 설정
config = {
    "load_in_4bit": True,
    "bnb_4bit_quant_type": "nf4"
}

# 학습 데이터 1만개로 3시간 학습
# 비용: $20 (vs Full FT $500)
```

---

**핵심**: 4bit 양자화로 메모리 1/8 감소, 소규모 GPU에서 대형 모델 학습 가능
