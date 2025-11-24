# Step 5: 배포 및 사용

## 목표

- Fine-tuned 모델 배포
- API 서버 구축
- 추론 최적화

## 배포 방식

### 1. 로컬 배포

```python
# LoRA 어댑터 로드
from peft import PeftModel

base_model = AutoModelForCausalLM.from_pretrained("llama-2-7b")
model = PeftModel.from_pretrained(base_model, "./lora-adapter")

# 추론
output = model.generate("...")
```

### 2. API 서버

```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/generate")
def generate(text: str):
    output = model.generate(text)
    return {"result": output}
```

---

**핵심**: LoRA 어댑터만 배포하면 됨 (경량)
