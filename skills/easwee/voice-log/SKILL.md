---
name: voice-log
description: Background voice journaling with Soniox realtime STT for OpenClaw. Use when the user asks to start or stop passive speech logging (especially commands like "start voice journal", "start voice log", and "end voice journal"), or asks for a summary/transcript of the last N minutes of conversation.
---

# Voice Journal (Soniox)

Use Soniox realtime STT in a background daemon that:
- Captures microphone audio continuously.
- Reconnects Soniox every 15 minutes.
- Stores only text (no token objects), bucketed by minute.
- Keeps only the latest 60 minutes.

## Commands

Run from this skill directory:

```bash
npm install
node scripts/voice_journal_ctl.js start
node scripts/voice_journal_ctl.js end
node scripts/voice_journal_ctl.js status
node scripts/voice_journal_ctl.js last 10
```

## OpenClaw trigger handling

When user says:
- `start voice journal`: run `node scripts/voice_journal_ctl.js start`.
- `start voice log`: run `node scripts/voice_journal_ctl.js start`.
- `start voice log ["en","si"]`: run `node scripts/voice_journal_ctl.js start '["en","si"]'`.
- `end voice journal`: run `node scripts/voice_journal_ctl.js end`.
- `summarize what we talked about for last 10 minutes`: run `node scripts/voice_journal_ctl.js last 10`, then summarize the returned text.

Always:
- Reply with only the requested outcome in one short sentence.
- Do not paste raw command output or transcript snippets unless the user explicitly asks for raw transcript/log text.
- If no text exists in range, report that explicitly.
- Never fabricate transcript text.

## Required env

Set:
- `SONIOX_API_KEY` (required)

Optional:
- `VOICE_JOURNAL_DATA_DIR` (default `./.data`)
- `VOICE_JOURNAL_AUDIO_CMD` (custom microphone capture command; must output 16kHz mono PCM s16le to stdout)
- `VOICE_JOURNAL_LANGUAGE_HINTS` (JSON array, e.g. `["en","si"]`; usually set via start command args)

## Audio capture defaults

Auto-selects available command by platform. Recommended:
- Linux: `arecord -q -f S16_LE -r 16000 -c 1 -t raw`
- macOS: `sox -q -d -t raw -b 16 -e signed-integer -r 16000 -c 1 -`

If auto-detection fails, set `VOICE_JOURNAL_AUDIO_CMD`.
