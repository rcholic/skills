---
name: clawapi
description: Switch AI models and manage API keys for OpenClaw with a native macOS app. Supports 16 providers including OpenAI, Anthropic, xAI, Google, Groq, Ollama, LM Studio, and more.
homepage: https://github.com/Gogo6969/clawapi
user-invocable: true
metadata: {"openclaw":{"emoji":"🔑","requires":{"bins":["curl"],"config":["skills.entries.clawapi"]},"install":[{"kind":"script","command":"curl -fsSL https://raw.githubusercontent.com/Gogo6969/clawapi/main/install.sh | bash"}]}}
---

# ClawAPI — Model Switcher & Key Vault for OpenClaw

ClawAPI is a native macOS app that lets you switch AI models and securely manage API keys for OpenClaw.

## What It Does

- **One-click model switching** — Pick any model from any provider and apply it instantly
- **Secure key vault** — API keys stored in the macOS Keychain with hardware encryption
- **Touch ID** — Biometric authentication for adding and deleting API keys
- **16 providers** — OpenAI, Anthropic, xAI, Google, Groq, Mistral, OpenRouter, Cerebras, Kimi, MiniMax, Z.AI, OpenCode Zen, Vercel AI, HuggingFace, Ollama, LM Studio
- **Auto-sync** — Changes are written directly to OpenClaw's config files automatically
- **Auto-update** — Built-in update checker fetches new releases from GitHub
- **VPS support** — Manage OpenClaw on a remote server via SSH
- **Config safety** — JSON validation before writing, automatic `.bak` backups

## Installation

```bash
curl -fsSL https://raw.githubusercontent.com/Gogo6969/clawapi/main/install.sh | bash
```

Installs `ClawAPI.app` to `/Applications`. Requires macOS 14+. Signed with Apple Developer ID and notarized.

## How It Works

1. **Add a provider** — Click `+`, pick a provider, paste your API key
2. **Pick a model** — Use the dropdown to choose a sub-model (GPT-4.1, Claude Sonnet 4, Grok 4, etc.)
3. **Done** — ClawAPI syncs everything to OpenClaw automatically

ClawAPI writes your API keys into `auth-profiles.json` and sets the active model in `openclaw.json`. No proxy, no middleware — OpenClaw talks directly to provider APIs.

## Supported Providers

### Cloud Providers

| Provider | Key Format |
|----------|-----------|
| OpenAI | `sk-...` |
| Anthropic | `sk-ant-...` |
| xAI | `xai-...` |
| Google AI | `AIza...` |
| Groq | `gsk_...` |
| Mistral | — |
| OpenRouter | `sk-or-...` |
| Cerebras | — |
| Kimi (Moonshot) | — |
| MiniMax | — |
| Z.AI (GLM) | — |
| OpenCode Zen | — |
| Vercel AI | — |
| HuggingFace | `hf_...` |

### Local Providers (No API Key)

| Provider | Endpoint |
|----------|----------|
| Ollama | `localhost:11434` |
| LM Studio | `localhost:1234` |

## Security & Privacy

- All API keys are stored in the **macOS Keychain** — never on disk in plain text
- **Touch ID** authentication for adding/deleting keys (password fallback on Macs without Touch ID)
- The app is **signed with Apple Developer ID** and **notarized by Apple**
- Hardened runtime enabled
- **No data leaves your machine** — ClawAPI only reads/writes local OpenClaw config files (or remote via SSH if you configure VPS mode)
- No telemetry, no analytics, no phone-home

## External Endpoints

| Endpoint | Purpose | Data Sent |
|----------|---------|-----------|
| `raw.githubusercontent.com` | Check for app updates | None (reads `update.json`) |
| `localhost:11434` | Discover Ollama models | None (reads local API) |
| `localhost:1234` | Discover LM Studio models | None (reads local API) |
| SSH (user-configured) | VPS mode config sync | API keys (encrypted in transit) |

No other network requests are made by ClawAPI.

## Links

- **GitHub:** [github.com/Gogo6969/clawapi](https://github.com/Gogo6969/clawapi)
- **Wiki:** [github.com/Gogo6969/clawapi/wiki](https://github.com/Gogo6969/clawapi/wiki)
- **Website:** [clawapi.app](https://clawapi.app)
- **User Guide:** [docs/USER_GUIDE.md](https://github.com/Gogo6969/clawapi/blob/main/docs/USER_GUIDE.md)
