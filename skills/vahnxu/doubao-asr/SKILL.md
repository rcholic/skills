---
name: Doubao ASR / 豆包语音转写
description: "Transcribe audio via Doubao Seed-ASR 2.0 (豆包录音文件识别模型2.0) API from ByteDance/Volcengine. Best-in-class Chinese speech recognition. 调用字节跳动火山引擎「豆包录音文件识别模型2.0」转写音频，中文识别效果业界领先。Use when the user needs high-quality Chinese transcription, or asks for Doubao/豆包/Volcengine/火山引擎 transcription."
homepage: https://www.volcengine.com/docs/6561/1354868
metadata:
  {
    "openclaw":
      {
        "emoji": "🫘",
        "requires": { "bins": ["python3"], "env": ["VOLCENGINE_API_KEY", "VOLCENGINE_ACCESS_KEY_ID", "VOLCENGINE_SECRET_ACCESS_KEY", "VOLCENGINE_TOS_BUCKET"], "pip": ["requests"] },
        "primaryEnv": "VOLCENGINE_API_KEY",
        "envHelp":
          {
            "VOLCENGINE_API_KEY":
              {
                "required": true,
                "description": "豆包 ASR API Key (UUID format). 从火山引擎语音控制台获取 / Get from Volcengine Speech console",
                "howToGet": "1. Open https://console.volcengine.com/speech/app\n2. Find '豆包录音文件识别模型2.0', create an API key\n3. Copy the UUID key (e.g. xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)\n\n1. 打开 https://console.volcengine.com/speech/app\n2. 找到「豆包录音文件识别模型2.0」，创建 API Key\n3. 复制 UUID 格式的 Key",
                "url": "https://console.volcengine.com/speech/app",
              },
            "VOLCENGINE_ACCESS_KEY_ID":
              {
                "required": true,
                "description": "IAM Access Key ID (starts with AKLT). 从火山引擎 IAM 控制台获取 / Get from Volcengine IAM console",
                "howToGet": "1. Open https://console.volcengine.com/iam/keymanage/\n2. Create an Access Key (or use existing)\n3. If using IAM sub-user, grant TOSFullAccess permission\n\n1. 打开 https://console.volcengine.com/iam/keymanage/\n2. 新建访问密钥（或使用已有的）\n3. 如使用子用户，需授权 TOSFullAccess 权限",
                "url": "https://console.volcengine.com/iam/keymanage/",
              },
            "VOLCENGINE_SECRET_ACCESS_KEY":
              {
                "required": true,
                "description": "IAM Secret Access Key (paired with Access Key ID above). 与上面的 Access Key ID 配对的密钥",
                "howToGet": "Created together with Access Key ID above / 与上面的 Access Key ID 一起创建",
              },
            "VOLCENGINE_TOS_BUCKET":
              {
                "required": true,
                "description": "TOS bucket name for audio upload. 用于音频上传的 TOS 存储桶名称",
                "howToGet": "1. Open https://console.volcengine.com/tos\n2. Create a bucket\n3. IMPORTANT: Choose region based on your server location:\n   - China mainland → cn-beijing\n   - Outside China (US/EU/SEA) → cn-hongkong (REQUIRED, otherwise upload will be ~15KB/s)\n4. Copy the bucket name\n\n1. 打开 https://console.volcengine.com/tos\n2. 新建存储桶\n3. 重要：根据服务器位置选区域：\n   - 中国内地服务器 → cn-beijing\n   - 海外服务器（美国/欧洲/东南亚）→ cn-hongkong（必须！否则上传速度只有约 15KB/s）\n4. 复制存储桶名称",
                "url": "https://console.volcengine.com/tos",
              },
            "VOLCENGINE_TOS_REGION":
              {
                "required": false,
                "description": "TOS region code (default: cn-beijing). 海外服务器必须设为 cn-hongkong / Overseas servers MUST use cn-hongkong",
                "howToGet": "Set to cn-hongkong if your server is outside China mainland. Do NOT use cn-beijing/cn-shanghai for overseas servers — upload will be extremely slow (~15KB/s).\n\n如果服务器在中国大陆以外，必须设为 cn-hongkong。海外服务器切勿使用 cn-beijing/cn-shanghai，否则上传极慢（约 15KB/s）。",
              },
          },
      },
  }
---

# Doubao ASR / 豆包语音转写

Transcribe audio files via ByteDance Volcengine's **Seed-ASR 2.0 Standard** (豆包录音文件识别模型2.0-标准版) API. Best-in-class accuracy for Chinese (Mandarin, Cantonese, Sichuan dialect, etc.) and supports 13+ languages.

调用字节跳动火山引擎**豆包录音文件识别模型2.0-标准版**（Seed-ASR 2.0 Standard）转写音频文件。中文识别（普通话、粤语、四川话等方言）准确率业界领先，支持 13+ 种语言。

## Sending audio to OpenClaw

Currently, audio files can be sent to OpenClaw via **Discord** or **WhatsApp**. Send the audio file in a chat message and ask the bot to transcribe it.

目前可通过 **Discord** 或 **WhatsApp** 向 OpenClaw 发送音频文件，发送后让 bot 转写即可。

> **Note**: Direct voice recording in the OpenClaw web UI is not yet supported. Use a messaging app to send pre-recorded audio files.
>
> **提示**：OpenClaw 网页端暂不支持直接录音，请通过即时通讯应用发送预录制的音频文件。

## Quick start

```bash
python3 {baseDir}/scripts/transcribe.py /path/to/audio.m4a
```

Defaults:

- Model: Seed-ASR 2.0 Standard / 豆包录音文件识别模型2.0-标准版
- Speaker diarization: enabled / 说话人分离：默认开启
- Output: stdout (transcript text with speaker labels / 带说话人标签的转写文本)

## Useful flags

```bash
python3 {baseDir}/scripts/transcribe.py /path/to/audio.m4a --out /tmp/transcript.txt
python3 {baseDir}/scripts/transcribe.py /path/to/audio.mp3 --format mp3
python3 {baseDir}/scripts/transcribe.py /path/to/audio.m4a --json --out /tmp/result.json
python3 {baseDir}/scripts/transcribe.py /path/to/audio.m4a --no-speakers  # disable speaker diarization / 关闭说话人分离
python3 {baseDir}/scripts/transcribe.py https://example.com/audio.mp3  # direct URL (skip upload)
```

## How it works

The Doubao API accepts audio via URL (not direct file upload). The script:

1. **Uploads audio to Volcengine TOS** (object storage) via presigned URL — audio stays within Volcengine infrastructure, no third-party services involved
2. Submits transcription task to Seed-ASR 2.0
3. Polls until complete (typically 1-3 minutes for a 10-min audio)
4. Returns transcript text

> **Privacy**: By default, audio is uploaded to your own Volcengine TOS bucket via presigned URL. No data is sent to third-party services.

You can also pass a direct audio URL as the argument to skip upload entirely:

```bash
python3 {baseDir}/scripts/transcribe.py https://your-bucket.tos.volces.com/audio.m4a
```

## Dependencies

- Python 3.9+
- `requests`: `pip install requests`

## Credentials

### Step 1: Doubao ASR API Key / 第一步：豆包 ASR API Key

Get your API key from the Volcengine Speech console:

从火山引擎语音控制台获取 API Key：

1. Open https://console.volcengine.com/speech/app
2. Find "豆包录音文件识别模型2.0" and create an API key
3. Copy the API key (UUID format, e.g. `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

```bash
export VOLCENGINE_API_KEY="your_api_key"
```

### Step 2: Volcengine TOS Bucket / 第二步：火山引擎 TOS 存储桶

The Doubao API requires audio to be accessible via URL. TOS provides secure, private temporary upload within Volcengine.

豆包 API 要求音频通过 URL 访问。TOS 对象存储提供安全的临时上传，数据留在火山引擎内部。

**Create a TOS bucket / 创建 TOS 存储桶：**

1. Open https://console.volcengine.com/tos
2. Create a bucket, **choose the right region (see below) / 选择正确的区域（见下方）**

**Region selection / 区域选择：**

| Server location / 服务器位置 | Recommended TOS region / 推荐 TOS 区域 | Region code |
|---|---|---|
| China mainland / 中国内地 | cn-beijing, cn-shanghai, cn-guangzhou | `cn-beijing` |
| Hong Kong / 香港 | cn-hongkong | `cn-hongkong` |
| Southeast Asia / 东南亚 | ap-southeast-1 (Singapore) | `ap-southeast-1` |
| US, Europe, other overseas / 美国、欧洲等海外 | **cn-hongkong** (recommended) | `cn-hongkong` |

> **Important**: If your server is **outside China mainland**, do NOT use `cn-beijing` / `cn-shanghai` — cross-border upload will be extremely slow (~15KB/s). Use `cn-hongkong` instead.
>
> **重要**：如果你的服务器在**中国大陆以外**，不要用 `cn-beijing` / `cn-shanghai`——跨境上传会非常慢（约 15KB/s）。请使用 `cn-hongkong`。

### Step 3: IAM Access Key / 第三步：IAM 访问密钥

Get your IAM access key for TOS upload:

获取 TOS 上传所需的 IAM 访问密钥：

1. Open https://console.volcengine.com/iam/keymanage/
2. Create an Access Key (or use an existing one)
3. If using a sub-user (IAM user), make sure it has **TOSFullAccess** permission

如果使用子用户（IAM 用户），请确保已授权 **TOSFullAccess** 权限。

```bash
export VOLCENGINE_ACCESS_KEY_ID="your_ak"
export VOLCENGINE_SECRET_ACCESS_KEY="your_sk"
export VOLCENGINE_TOS_BUCKET="your_bucket_name"
export VOLCENGINE_TOS_REGION="cn-hongkong"  # see region table above / 见上方区域表
```

### Summary of all environment variables / 环境变量汇总

| Variable | Required | Description |
|---|---|---|
| `VOLCENGINE_API_KEY` | Yes | ASR API key (UUID format) from Speech console / 语音控制台的 API Key |
| `VOLCENGINE_ACCESS_KEY_ID` | Yes | IAM Access Key ID (starts with `AKLT`) / IAM 访问密钥 ID |
| `VOLCENGINE_SECRET_ACCESS_KEY` | Yes | IAM Secret Access Key / IAM 访问密钥 |
| `VOLCENGINE_TOS_BUCKET` | Yes | TOS bucket name / TOS 存储桶名称 |
| `VOLCENGINE_TOS_REGION` | No | TOS region (default: `cn-beijing`). Overseas servers MUST use `cn-hongkong` / 海外服务器必须用 `cn-hongkong` |

## Supported formats

WAV, MP3, MP4, M4A, OGG, FLAC — up to 5 hours, 512MB max.

支持格式：WAV、MP3、MP4、M4A、OGG、FLAC——最长 5 小时，最大 512MB。
