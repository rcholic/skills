# MLX Local Inference Stack

在 Apple Silicon Mac 上运行完整的本地 AI 推理服务，无需云端 API。

## 功能

| 能力 | 模型 | 说明 |
|------|------|------|
| **LLM 推理** | Qwen3-14B, Gemma3-12B | 中英双语对话、代码生成、深度推理 |
| **语音识别** | Qwen3-ASR, Whisper-v3-turbo | 粤语/普通话 + 99语言 |
| **文本向量化** | Qwen3-Embedding 0.6B/4B | RAG、语义搜索、文档索引 |
| **OCR** | PaddleOCR-VL-1.5 | 中英文场景文字、票据、文档 |
| **语音合成** | Qwen3-TTS-1.7B | 支持自定义音色克隆 |
| **自动转录** | ASR + LLM 联合 | 文件监听、自动转录+智能纠错 |

所有模型通过 [MLX](https://github.com/ml-explore/mlx) 在本机 GPU 运行。延迟低、完全离线、零成本。

## 前置条件

- Apple Silicon Mac（M1/M2/M3/M4）
- macOS 14+
- Python 3.10+
- 推荐 32GB+ 内存

## 安装

```bash
# 安装 OpenClaw skill
clawhub install mlx-local-inference

# 安装 Python 依赖
pip install mlx mlx-lm mlx-audio mlx-vlm openai
```

## 服务端口

| 服务 | 默认端口 | 监听范围 | 包含模型 |
|------|----------|----------|----------|
| 主服务 | 8787 | 可配置 | LLM, Whisper, Embedding |
| ASR 服务 | 8788 | localhost | Qwen3-ASR, TTS |

所有 API 均为 OpenAI 兼容格式，`api_key` 随意填写即可。

## 使用示例

### LLM 对话

```bash
curl http://localhost:8787/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-14b",
    "messages": [{"role": "user", "content": "用一句话解释量子计算"}]
  }'
```

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8787/v1", api_key="unused")
r = client.chat.completions.create(
    model="qwen3-14b",
    messages=[{"role": "user", "content": "Hello"}]
)
print(r.choices[0].message.content)
```

Qwen3 会输出 `<think>...</think>` 思维链标签，按需过滤：

```python
import re
text = re.sub(r'<think>.*?</think>\s*', '', text, flags=re.DOTALL)
```

### 语音识别

```bash
# Qwen3-ASR（粤语/普通话首选）
curl http://localhost:8788/v1/audio/transcriptions \
  -F file=@audio.wav \
  -F model=mlx-community/Qwen3-ASR-1.7B-8bit \
  -F language=zh

# Whisper（多语言）
curl http://localhost:8787/v1/audio/transcriptions \
  -F file=@audio.wav \
  -F model=whisper-large-v3-turbo
```

支持格式：wav, mp3, m4a, flac, ogg, webm

长音频先切分为 10 分钟片段：

```bash
ffmpeg -y -ss 0 -t 600 -i long.wav -ar 16000 -ac 1 chunk_000.wav
```

### 文本向量化

```bash
curl http://localhost:8787/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen3-embedding-0.6b", "input": "要向量化的文本"}'

# 批量
curl http://localhost:8787/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen3-embedding-4b", "input": ["文本一", "文本二"]}'
```

### OCR 文字识别

```bash
python -m mlx_vlm.generate \
  --model mlx-community/PaddleOCR-VL-1.5-6bit \
  --image photo.jpg \
  --prompt "OCR:" \
  --max-tokens 512 \
  --temp 0.0
```

注意：Prompt 必须为 `OCR:`，temperature 设 0 以确保确定性输出。

### 语音合成

```bash
curl http://localhost:8788/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit","input":"你好世界"}' \
  -o speech.wav
```

### 自动转录守护进程

将音频文件放入 `~/transcribe/` 目录，守护进程自动处理：

1. Qwen3-ASR 转录 → `文件名_raw.md`
2. Qwen3-14B 智能校对 → `文件名_corrected.md`
3. 结果移入 `~/transcribe/done/`

校对规则：修正同音字、保留粤语用字（嘅/唔/咁/喺）、补全标点、去除语气词。

## 模型选型

### LLM

| 场景 | 推荐模型 |
|------|----------|
| 中文 / 粤语任务 | qwen3-14b |
| 英文 / 代码生成 | gemma-3-12b |
| 需要深度推理 | qwen3-14b（think 模式） |
| 快速问答 | gemma-3-12b |

### ASR

| 场景 | 推荐模型 |
|------|----------|
| 粤语 / 普通话 | Qwen3-ASR |
| 多语言（99 种） | Whisper |

### Embedding

| 场景 | 推荐模型 |
|------|----------|
| 快速检索 / 低延迟 | qwen3-embedding-0.6b |
| 高精度语义匹配 | qwen3-embedding-4b |

## 架构

```
┌──────────────────────────────────────────┐
│         Apple Silicon Mac (MLX)          │
├────────────────┬─────────────────────────┤
│   Port 8787    │      Port 8788          │
│   (主服务)      │      (ASR 服务)         │
│                │                         │
│  · Qwen3-14B  │  · Qwen3-ASR            │
│  · Gemma3-12B │  · Qwen3-TTS            │
│  · Whisper    │                         │
│  · Embedding  │                         │
├────────────────┴─────────────────────────┤
│  OCR: PaddleOCR-VL (CLI, 按需调用)       │
│  转录守护进程 (文件监听, ASR→LLM 校对)    │
└──────────────────────────────────────────┘
```

## 服务管理

```bash
# 主服务（LLM + Whisper + Embedding）
launchctl kickstart -k gui/$(id -u)/com.mlx-server

# ASR + TTS 服务
launchctl kickstart -k gui/$(id -u)/com.mlx-audio-server

# 转录守护进程
launchctl kickstart gui/$(id -u)/com.mlx-transcribe-daemon
```

## 目录结构

```
mlx-local-inference/
├── SKILL.md              # OpenClaw skill 定义
├── README.md             # 说明文档
├── LICENSE               # MIT
└── references/           # 各模型详细参考
    ├── asr-qwen3.md
    ├── asr-whisper.md
    ├── embedding-qwen3.md
    ├── llm-qwen3-14b.md
    ├── llm-gemma3-12b.md
    ├── llm-models-reference.md
    ├── ocr.md
    ├── transcribe-daemon.md
    └── tts-qwen3.md
```

## License

MIT
