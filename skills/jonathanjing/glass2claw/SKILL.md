---
name: glass2claw
description: "A logic-based protocol for organizing life-captures into Notion. Routes images from WhatsApp into categorized Notion databases via your private Discord server channels using OpenClaw's sessions_send tool."
metadata:
  {
    "openclaw":
      {
        "emoji": "👁️",
        "requires": {
          "env": ["NOTION_API_KEY"],
          "configPaths": ["configs/vision_router.md"],
          "tools": ["sessions_send", "message", "web_fetch"]
        },
        "dataFlow": {
          "input": "Image URL forwarded from WhatsApp via sessions_send",
          "routing": "Agent reads configs/vision_router.md, classifies image intent (Wine/Tea/Contacts), then calls sessions_send to the matching Discord channel session key",
          "output": "Structured entry written to the corresponding Notion database using NOTION_API_KEY"
        }
      },
  }
---

# glass2claw: The Vision Router Protocol

`glass2claw` provides logical routing templates to organize visual captures from WhatsApp into structured Notion databases, via your private Discord server.

## 🏗️ Design Philosophy

This skill is **instruction-only**. No binaries, no curl, no exec commands. It relies entirely on native OpenClaw platform tools:

| Step | Tool Used | What it does |
|------|-----------|--------------|
| Receive image | `sessions_send` | WhatsApp session forwards image URL to Discord hub session |
| Classify intent | Agent reasoning | Determines Wine / Tea / Contacts from image |
| Route | `sessions_send` | Hub sends to the correct specialist Discord channel session |
| Store | `message` + Notion API | Specialist posts image and writes entry to Notion database |

**No data leaves your private OpenClaw infrastructure.** All routing happens between your own Discord server's channels.

## 🚀 Configuration

### 1. Required Config File: `configs/vision_router.md`

Create this file in your OpenClaw workspace at the exact path `configs/vision_router.md`. The Agent reads this file to resolve Notion database IDs. This path is declared in the skill metadata under `configPaths`.

```markdown
# Vision Router Config

## Notion Database IDs
- Wine Cellar: [YOUR_NOTION_DATABASE_ID]
- Tea Closet: [YOUR_NOTION_DATABASE_ID]
- Contacts: [YOUR_NOTION_DATABASE_ID]

## Discord Session Keys (hub → specialist routing)
- Wine session: agent:main:discord:channel:[YOUR_WINE_CHANNEL_ID]
- Tea session: agent:main:discord:channel:[YOUR_TEA_CHANNEL_ID]
- Contacts session: agent:main:discord:channel:[YOUR_CONTACTS_CHANNEL_ID]
```

### 2. Apply the Templates

- **Hub routing logic**: `SAMPLE_AGENT.md` — paste into your hub Discord channel's AGENTS.md or SOUL.md
- **Wine specialist persona**: `SAMPLE_SOUL_WINE.md` — paste into your wine channel's SOUL.md

## 🔄 Data Flow (explicit)

```
WhatsApp (image received)
  → sessions_send → Discord #hub channel session
      → Agent classifies: Wine | Tea | Contacts
      → sessions_send → matching Discord specialist channel session
          → message tool: posts image to channel
          → Notion API (NOTION_API_KEY): writes structured entry
```

All hops are within your private Discord server. The session keys in `configs/vision_router.md` are user-defined and point only to channels you own.

## 🛡️ Best Practices

- **Least Privilege**: Scope your Notion token to only the three required databases
- **Private channels only**: Use private Discord servers, never public ones
- **No agent discretion on destinations**: All target session keys are hardcoded in `configs/vision_router.md`, not inferred by the agent

---
*Created by JonathanJing | AI Reliability Architect*
