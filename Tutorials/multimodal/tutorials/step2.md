# Step 2: Audio - Whisper로 음성 인식

## 목표

- Whisper 모델 이해
- 음성 → 텍스트 변환
- Whisper + LLM 조합
- 실무 활용 사례

## Whisper란?

**OpenAI의 오픈소스 음성 인식 모델**

```
음성 파일 (MP3, WAV, ...)
  ↓
[Whisper]
  ↓
텍스트 (자막, 스크립트)
```

### 특징

- **99개 언어 지원** (한국어 포함)
- **로컬 실행 가능** (오프라인 OK)
- **무료 오픈소스**
- **높은 정확도**

## 설치

```bash
pip install openai-whisper
pip install ffmpeg-python
```

### FFmpeg 설치 (필수)

```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt install ffmpeg

# Windows
# https://ffmpeg.org/download.html
```

## 기본 사용법

### 1. 모델 로드

```python
import whisper

# 모델 로드 (최초 1회 다운로드)
model = whisper.load_model("base")
```

**모델 크기:**
- `tiny`: 39MB (빠름, 정확도 낮음)
- `base`: 74MB (권장 ✅)
- `small`: 244MB (정확도 좋음)
- `medium`: 769MB (매우 정확)
- `large`: 1550MB (최고 품질)

### 2. 음성 파일 → 텍스트

```python
# 음성 파일 transcribe
result = model.transcribe("audio.mp3", language="ko")

# 결과
print(result["text"])
```

**출력:**
```
안녕하세요. 오늘은 LangGraph에 대해 설명하겠습니다.
```

### 3. 상세 결과

```python
result = model.transcribe("audio.mp3", language="ko")

# 전체 텍스트
print(result["text"])

# 세그먼트별 (타임스탬프 포함)
for segment in result["segments"]:
    print(f"[{segment['start']:.2f}s - {segment['end']:.2f}s] {segment['text']}")
```

**출력:**
```
[0.00s - 2.50s] 안녕하세요.
[2.50s - 5.80s] 오늘은 LangGraph에 대해 설명하겠습니다.
[5.80s - 10.20s] LangGraph는 상태 기반 워크플로우 라이브러리입니다.
```

## 모델 비교

| 모델 | 크기 | 속도 | 품질 | 메모리 | 권장 |
|------|------|------|------|--------|------|
| tiny | 39M | ⭐⭐⭐⭐⭐ | ⭐⭐ | 1GB | 초경량 |
| base | 74M | ⭐⭐⭐⭐ | ⭐⭐⭐ | 1GB | 일반 ✅ |
| small | 244M | ⭐⭐⭐ | ⭐⭐⭐⭐ | 2GB | 고품질 |
| medium | 769M | ⭐⭐ | ⭐⭐⭐⭐⭐ | 5GB | 전문가 |
| large | 1550M | ⭐ | ⭐⭐⭐⭐⭐ | 10GB | 최고급 |

### 권장 사항

```python
# 일반 용도 (한국어도 잘 인식)
model = whisper.load_model("base")  ✅

# 정확도 중요
model = whisper.load_model("small")

# 최고 품질 (GPU 권장)
model = whisper.load_model("large")
```

## Whisper + LLM 조합

### 1. 회의록 요약

```python
import whisper
from langchain_community.llms import Ollama

# 1. 음성 → 텍스트
model = whisper.load_model("base")
result = model.transcribe("meeting.mp3", language="ko")
text = result["text"]

print("원본 회의록:")
print(text)

# 2. 텍스트 → 요약
llm = Ollama(model="llama3")
summary = llm.invoke(f"""
다음 회의록을 요약해줘. 액션 아이템만 추출:

{text}
""")

print("\n요약:")
print(summary)
```

**출력:**
```
원본 회의록:
오늘 회의에서는 신규 프로젝트 일정을 논의했습니다.
개발은 다음 주 월요일부터 시작하며, QA는 2주 후에 진행합니다.
담당자는 김철수 님입니다.

요약:
액션 아이템:
1. 개발 시작: 다음 주 월요일
2. QA 진행: 2주 후
3. 담당자: 김철수
```

### 2. 유튜브 자막 생성

```python
# 1. 유튜브 영상 다운로드 (yt-dlp)
# yt-dlp -x --audio-format mp3 "https://youtube.com/..."

# 2. Whisper로 자막 생성
result = model.transcribe("video.mp3", language="ko")

# 3. SRT 파일로 저장
def save_srt(segments, filename):
    with open(filename, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, 1):
            f.write(f"{i}\n")
            f.write(f"{format_time(seg['start'])} --> {format_time(seg['end'])}\n")
            f.write(f"{seg['text'].strip()}\n\n")

def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

save_srt(result["segments"], "subtitles.srt")
```

**subtitles.srt:**
```
1
00:00:00,000 --> 00:00:02,500
안녕하세요.

2
00:00:02,500 --> 00:00:05,800
오늘은 LangGraph에 대해 설명하겠습니다.
```

### 3. 음성 명령 → LLM 처리

```python
# 실시간 음성 명령
def voice_command_llm(audio_file):
    # 1. 음성 인식
    model = whisper.load_model("base")
    result = model.transcribe(audio_file, language="ko")
    command = result["text"]

    print(f"인식된 명령: {command}")

    # 2. LLM으로 처리
    llm = Ollama(model="llama3")
    response = llm.invoke(command)

    return response

# 사용
response = voice_command_llm("command.mp3")
print(response)
```

## 실무 활용 사례

### 1. 고객 상담 녹음 분석

```python
# 1. 상담 녹음 → 텍스트
result = model.transcribe("call.mp3", language="ko")

# 2. 감정 분석
llm = Ollama(model="llama3")
sentiment = llm.invoke(f"""
다음 상담 내용의 고객 만족도를 분석해줘:
{result['text']}

만족/보통/불만 중 하나로 답하고, 이유를 설명해줘.
""")

print(sentiment)
```

### 2. 팟캐스트 검색 가능하게

```python
# 1. 팟캐스트 → 텍스트
episodes = ["ep1.mp3", "ep2.mp3", "ep3.mp3"]

texts = []
for ep in episodes:
    result = model.transcribe(ep, language="ko")
    texts.append(result["text"])

# 2. Vector DB에 저장
import chromadb
client = chromadb.Client()
collection = client.create_collection("podcast")

collection.add(
    documents=texts,
    ids=[f"ep{i}" for i in range(len(texts))]
)

# 3. 검색
results = collection.query(
    query_texts=["GraphRAG가 뭐야?"],
    n_results=1
)

print(f"관련 에피소드: {results['ids'][0]}")
```

### 3. 강의 자동 요약

```python
# 강의 녹음 → 요약 → 학습 노트
lecture = model.transcribe("lecture.mp3", language="ko")

llm = Ollama(model="llama3")
notes = llm.invoke(f"""
다음 강의를 학습 노트로 만들어줘:

{lecture['text']}

형식:
## 핵심 개념
- ...

## 주요 예제
- ...

## 요약
- ...
""")

with open("lecture_notes.md", "w", encoding="utf-8") as f:
    f.write(notes)
```

## 언어 자동 감지

```python
# language 파라미터 생략 → 자동 감지
result = model.transcribe("mixed_language.mp3")

# 감지된 언어
print(result["language"])  # "ko" 또는 "en" 등
```

## 성능 최적화

### 1. GPU 사용

```python
import torch

# GPU 사용 가능하면 자동 사용
device = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("base", device=device)
```

**속도 차이:**
```
CPU: ~10분 (1시간 오디오)
GPU: ~2분 (1시간 오디오) ✅
```

### 2. 배치 처리

```python
files = ["audio1.mp3", "audio2.mp3", "audio3.mp3"]

for file in files:
    result = model.transcribe(file, language="ko")
    with open(f"{file}.txt", "w", encoding="utf-8") as f:
        f.write(result["text"])
```

## 오류 처리

### 파일 없음

```python
import os

if not os.path.exists("audio.mp3"):
    print("❌ 파일이 없습니다")
else:
    result = model.transcribe("audio.mp3")
```

### 지원하지 않는 형식

```python
# Whisper는 FFmpeg를 사용하므로 대부분 형식 지원
# mp3, wav, m4a, flac, ogg 등
# 안 되면 FFmpeg로 변환:
# ffmpeg -i input.xyz -ar 16000 output.wav
```

## 다음 단계

**Step 3: Multimodal RAG**
- 이미지 + 텍스트 검색
- 음성 + 문서 질의응답
- 멀티모달 벡터 DB

---

**핵심 요약:**
1. Whisper = 음성 → 텍스트 (99개 언어)
2. 로컬 실행 가능, 무료
3. LLM 조합 = 음성 기반 AI 앱
4. 실무: 회의록, 자막, 검색

**권장 모델: `base` (한국어도 충분)** ✅
