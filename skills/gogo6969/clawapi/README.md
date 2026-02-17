# ClawAPI — OpenClaw Skill

**Model Switcher & Key Vault for OpenClaw**

A native macOS app that lets you switch AI models and securely manage API keys for OpenClaw. Supports 16 providers including OpenAI, Anthropic, xAI, Google, Groq, Ollama, LM Studio, and more.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/Gogo6969/clawapi/main/install.sh | bash
```

## Features

- One-click model switching across 16 providers
- API keys stored in macOS Keychain with Touch ID
- Auto-sync to OpenClaw config files
- VPS support via SSH
- JSON validation and `.bak` backups for config safety
- Built-in update checker
- Apple Developer ID signed and notarized

## Security & Privacy

- API keys never written to disk in plain text
- Touch ID / password authentication for sensitive operations
- No telemetry, no analytics, no data leaves your machine
- Only network requests: update check (GitHub) and local model discovery (Ollama/LM Studio)

## Links

- [GitHub](https://github.com/Gogo6969/clawapi)
- [Wiki](https://github.com/Gogo6969/clawapi/wiki)
- [User Guide](https://github.com/Gogo6969/clawapi/blob/main/docs/USER_GUIDE.md)

## License

MIT
