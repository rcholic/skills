---
name: pixel-lobster
description: "Desktop pixel art lobster avatar that lip-syncs to TTS speech. Use when: (1) user wants a visual avatar or desktop pet, (2) user wants lip-sync animation for their AI agent's voice, (3) user asks for a talking lobster or desktop overlay. Launches an Electron app that polls the XTTS envelope endpoint and animates a pixel art lobster with 6 viseme mouth shapes, spring physics, and swimming animation. Requires Electron (npx electron) and a running XTTS/TTS server with /audio/envelope endpoint."
---

# Pixel Lobster

A transparent desktop overlay featuring a pixel art lobster that lip-syncs to TTS speech output. Swims around the screen, only moves its mouth when the AI speaks.

## Quick Start

```bash
cd <skill_dir>/assets/app
npm install
npm start
```

## Setup

1. Ensure XTTS server is running on port 8787 (or configure `ttsUrl` in `config.json`)
2. The server must expose `GET /audio/envelope` returning `{ id, envelope[], elapsedMs, intervalMs }`
3. Launch the Electron app — lobster appears as a transparent overlay

## Configuration

Edit `assets/app/config.json`:

- `audioMode`: `"tts"` (default for this skill) — only reacts to TTS speech
- `ttsUrl`: URL of your TTS server (default `http://127.0.0.1:8787`)
- `monitor`: `"primary"`, `"secondary"`, `"left"`, `"right"`, or index number
- `lobsterScale`: sprite scale factor (default 4 = 480px)
- `swimEnabled`: enable/disable swimming (default true)
- `clickThrough`: start in click-through mode (default false)

## Keyboard Shortcuts

- **F9** — toggle click-through (lobster stops blocking mouse clicks)
- **F12** — toggle DevTools

## How It Works

The lobster polls the TTS server's `/audio/envelope` endpoint. When new speech audio is detected (new envelope ID), it plays through the amplitude envelope sample-by-sample, driving:

- **Mouth openness** via spring physics (natural jaw movement)
- **Viseme selection** from envelope shape analysis (jitter, delta, syllable onsets)
- **6 distinct mouth shapes** (A=wide ah, B=grin ee, C=round oh, D=pucker oo, E=medium eh, F=teeth ff)
- **Variety enforcement** — never repeats same shape 3x in a row

The lobster swims around the screen, slows down while talking, and has idle animations (blinking, breathing, eye movement, claw motion).

## Files

- `assets/app/` — complete Electron app (main.js, lobster.html, preload.js, package.json, config.json)
- `scripts/launch.sh` — helper script to install deps and launch

## Sync Tuning

If lip sync is off, adjust `ttsPlayStartOffsetMs` in config.json:
- Mouth moves too early → increase the value
- Mouth moves too late → decrease the value
- Default: 1100ms (tuned for PowerShell MediaPlayer playback)
