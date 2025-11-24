"""
Fine-tuning Step 3: QLoRA (효율적 Fine-tuning)

주의: 실제 학습은 GPU가 필요합니다
이 예제는 개념 설명용입니다

pip install transformers peft bitsandbytes
"""


def explain_qlo_ra():
    print("=== QLoRA (Quantized LoRA) ===\n")
    print("💡 핵심: 4bit 양자화 + LoRA\n")

    print("📊 메모리 비교:")
    print("   Full Fine-tuning: 70B 모델 = 280GB")
    print("   LoRA: 70B 모델 = 40GB")
    print("   QLoRA: 70B 모델 = 20GB ✅\n")

    print("🔧 QLoRA 구성 요소:")
    print("   1. 4bit NormalFloat (NF4) 양자화")
    print("   2. Double Quantization")
    print("   3. Paged Optimizers\n")

    print("="*60)

    code = '''
# QLoRA 설정 예시
from transformers import BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype="float16",
    bnb_4bit_use_double_quant=True
)

# 모델 로드 (4bit)
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b",
    quantization_config=bnb_config,
    device_map="auto"
)

# LoRA 추가
from peft import LoraConfig, get_peft_model

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"]
)

model = get_peft_model(model, lora_config)

# 학습 가능한 파라미터만 업데이트
trainable_params = sum(
    p.numel() for p in model.parameters() if p.requires_grad
)
print(f"학습 파라미터: {trainable_params:,} (전체의 0.1%)")
'''

    print("\n📝 QLoRA 코드:")
    print(code)

    print("\n✅ 장점:")
    print("   - RTX 3090 (24GB)에서 13B 모델 학습 가능")
    print("   - 비용 절감: $500 → $20")
    print("   - 품질: Full FT 대비 97%")

    print("\n⚠️ 단점:")
    print("   - 학습 속도 약간 느림 (1.5x)")
    print("   - 추론 시 디양자화 필요")

    print("\n💡 실무 권장:")
    print("   - 13B 이하: LoRA")
    print("   - 13B~70B: QLoRA")
    print("   - 70B 이상: QLoRA + 다중 GPU")


if __name__ == "__main__":
    explain_qlo_ra()
    print("\n📚 다음: step4.py - 평가 및 비교\n")
