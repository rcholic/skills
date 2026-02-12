---
name: "MoltFlow — WhatsApp AI Automation Platform and More"
version: "2.0.3"
description: "MoltFlow — complete WhatsApp automation platform: bulk messaging, scheduled messages, custom groups, lead detection & CRM, AI replies with style cloning, knowledge base (RAG), voice transcription, group monitoring, labels, anti-spam, content safeguards, review collection, webhooks, GDPR compliance, and agent-to-agent protocol (JSON-RPC, encryption). 90+ API endpoints."
source: "MoltFlow Team"
risk: safe
homepage: "https://molt.waiflow.app"
requiredEnv:
  - MOLTFLOW_API_KEY
primaryEnv: MOLTFLOW_API_KEY
disable-model-invocation: true
metadata: {"openclaw":{"emoji":"📱","homepage":"https://molt.waiflow.app","requires":{"env":["MOLTFLOW_API_KEY"]},"primaryEnv":"MOLTFLOW_API_KEY"}}
---

# WhatsApp Automation & A2A

MoltFlow is a complete WhatsApp automation platform with 90+ API endpoints covering messaging, lead management, AI intelligence, and agent-to-agent communication.

> **Save up to 17% with yearly billing** — Free tier available, no credit card required.

### Platform Features

| Category | Features |
|----------|----------|
| **Messaging** | Send text, media, polls, stickers, GIFs, voice notes, locations, vCards. Reply, react, edit, unsend. Read receipts & typing simulation. |
| **Bulk Messaging** | Broadcast to custom groups with ban-safe throttling (random 30s–2min delays). Real-time progress via SSE. Pause/resume/cancel. |
| **Scheduled Messages** | One-time, daily, weekly, monthly, or custom cron. Timezone-aware. Pause, resume, edit. Execution history tracking. |
| **Custom Groups** | Build targeted contact lists. Import from WhatsApp groups or add manually. Feed into Bulk Send or Scheduled Messages. CSV/JSON export. |
| **Lead Detection & CRM** | Auto-detect purchase intent in monitored groups. Lead pipeline with status tracking (new → contacted → qualified → converted). Bulk status update, bulk add-to-group, CSV/JSON export. Reciprocity check (anti-spam). |
| **Group Monitoring** | Monitor 50+ groups simultaneously. Keyword/mention detection. Auto-respond with AI. Per-group prompts. Skip admins & existing contacts. |
| **Labels** | Create, sync to WhatsApp Business, import from WhatsApp. Color-coded contact organization. |
| **AI Replies** | GPT-4/Claude powered reply generation. Context-aware with RAG knowledge base. Preview before sending. |
| **Style Cloning (Learn Mode)** | Train style profiles from your message history. AI replies that match your tone, vocabulary, and patterns. Per-contact profiles. |
| **Knowledge Base (RAG)** | Upload PDF/TXT documents. Semantic search with embeddings. AI uses your docs to answer questions accurately. |
| **Voice Transcription** | Whisper-powered voice message transcription. Async task queue with status tracking. |
| **Review Collection** | Auto-collect positive feedback via sentiment analysis (14+ languages). Approve/reject. Export testimonials as JSON/HTML. |
| **Anti-Spam Engine** | Rate limits, duplicate blocking, pattern filters (block/flag/delay). Human-like typing simulation. Burst rate limiting (4 msgs/2 min). |
| **Content Safeguards** | Block API keys, credit cards, SSNs, PII, prompt injection. Custom regex rules. Test content against full policy stack. |
| **Webhooks** | 10+ event types (message.received, lead.detected, session.connected, etc.). HMAC-SHA256 signed. Delivery history. Test payloads. |
| **A2A Protocol** | JSON-RPC 2.0 agent-to-agent communication. X25519-AES256GCM encryption. Agent discovery, trust levels, encrypted messaging. |
| **GDPR Compliance** | Auto-expiring messages (90-day). Data minimization (500-char preview). Contact erasure. Data export. AI consent enforcement. DPA available. Named sub-processors (Art. 28). |
| **Billing & Usage** | Stripe-powered. Free/Starter/Pro/Business plans. Usage tracking, daily breakdown. Billing portal. **Yearly plans save up to 17%.** |

## When to use

Use this skill when you need to:
- **Send messages** — text, media, polls, stickers, GIFs, voice notes, locations, vCards
- **Bulk message** — broadcast to custom groups with ban-safe throttling and progress tracking
- **Schedule messages** — one-time, recurring (daily/weekly/monthly), or cron expressions with timezone support
- **Manage custom groups** — create contact lists, import from WhatsApp groups, export CSV/JSON
- **Detect and manage leads** — monitor groups for purchase intent, track lead pipeline, bulk operations
- **Monitor WhatsApp groups** — keyword detection, auto-respond, per-group AI prompts
- **Organize with labels** — create labels, sync with WhatsApp Business, import/export
- **Generate AI replies** — GPT-4/Claude powered, context-aware, with style cloning
- **Train style profiles** — Learn Mode analyzes your messages to clone your communication style
- **Build a knowledge base** — upload documents (PDF/TXT), semantic RAG search, AI-powered answers
- **Transcribe voice messages** — Whisper-powered async transcription
- **Collect reviews** — sentiment analysis across 14+ languages, testimonial export (JSON/HTML)
- **Configure anti-spam** — rate limits, duplicate blocking, custom pattern filters
- **Set content safeguards** — block secrets, PII, prompt injection with custom regex rules
- **Manage webhooks** — subscribe to 10+ event types, HMAC signing, delivery tracking
- **Connect AI agents** — A2A JSON-RPC 2.0 with X25519-AES256GCM encryption
- **Manage API keys** — create, rotate, revoke; SHA-256 hashed
- **Track usage & billing** — current period, daily breakdown, Stripe checkout/portal
- **Ensure GDPR compliance** — auto-expiring messages, data minimization, contact erasure, DPA

## Use cases

**Personal automation:**
- Auto-reply to WhatsApp messages while you're busy (AI learns your tone)
- Forward important group mentions to a private chat
- Schedule follow-up messages to contacts after meetings
- Collect and organize customer testimonials from group conversations

**Bulk messaging & scheduling:**
- Build "VIP Clients" list from WhatsApp group members, then broadcast a promo to all 200 contacts
- Schedule weekly Monday 9 AM updates to your "Newsletter" group — timezone-aware, fires even when your laptop is off
- Pause a running bulk send mid-flight, edit the message, then resume
- Set up daily cron job to send stock alerts to your trading group at market open

**Business & lead management:**
- Monitor industry groups for purchase-intent keywords ("looking for", "need help with")
- Auto-detect leads → track pipeline (new → contacted → qualified → converted)
- Bulk update 50 leads to "contacted" status and add them to your "Follow-up" custom group in one API call
- Export leads as CSV for your CRM, or JSON for your automation pipeline
- Auto-label new leads as VIP/Hot/Cold based on message sentiment
- Run feedback collectors across all chats — auto-approve positive reviews for your website

**AI & knowledge:**
- Train a style profile from 500+ of your messages — AI replies sound exactly like you
- Upload your product catalog as PDF → AI answers customer questions using RAG search
- Transcribe voice messages with Whisper and auto-respond with AI
- Generate context-aware replies that combine your style + your knowledge base

**Agent-to-Agent (A2A):**
- Build a support agent that escalates complex tickets to a human agent over A2A
- Connect your booking agent with a payment agent — encrypted end-to-end
- Create a multi-agent pipeline: lead detection → qualification → outreach → follow-up
- Let two businesses' agents negotiate and exchange data securely (X25519-AES256GCM)
- Resolve any WhatsApp number to check if they run a MoltFlow agent, then message directly

**Safety & compliance:**
- Block outgoing messages containing API keys, credit cards, or SSNs automatically
- Set rate limits to prevent accidental spam (typing indicators + random delays built-in)
- Create custom regex rules to flag sensitive content before it leaves your account
- Test any message against your full policy stack before sending

**GDPR & data privacy:**
- Message previews auto-expire after 90 days (configurable) — no indefinite storage
- Only first 500 characters stored — full messages are not retained
- Style training extracts only statistical patterns, never stores raw message text
- Full GDPR Article 13/14 compliant privacy policy with named sub-processors
- Data Controller (you) / Data Processor (MoltFlow) model with DPA available
- Third-party contact erasure process for GDPR right-to-be-forgotten requests

## Setup

> **Free tier available** — 1 session, 50 messages/month, no credit card required.
> Sign up at https://molt.waiflow.app/checkout?plan=free

Env vars:
- `MOLTFLOW_API_KEY` (required) — API key from waiflow.app dashboard
- `MOLTFLOW_API_URL` (optional) — defaults to `https://apiv2.waiflow.app`

**Security note:** Use the principle of least privilege. If you only need messaging and monitoring features, create a non-admin API key. Admin-level keys grant access to tenant management, user operations, and GDPR erasure endpoints. Only supply an admin key if you explicitly need those capabilities.

Authentication: `X-API-Key: $MOLTFLOW_API_KEY` header or `Authorization: Bearer $TOKEN` (JWT from login).

Base URL: `https://apiv2.waiflow.app/api/v2`

---

## 1. Sessions

```bash
# List all sessions
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/sessions

# Create new session
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "Main Line"}' \
  https://apiv2.waiflow.app/api/v2/sessions

# Start session (triggers QR code generation)
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/sessions/{session_id}/start

# Get QR code for pairing
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/sessions/{session_id}/qr

# Stop session
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/sessions/{session_id}/stop

# Restart session (preserves auth if previously paired)
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/sessions/{session_id}/restart

# Logout (clears WhatsApp auth, requires fresh QR scan)
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/sessions/{session_id}/logout

# Delete session
curl -X DELETE -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/sessions/{session_id}
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/sessions` | GET | List sessions |
| `/sessions` | POST | Create session |
| `/sessions/{id}` | GET | Get session details |
| `/sessions/{id}` | DELETE | Delete session |
| `/sessions/{id}/start` | POST | Start session (triggers QR code) |
| `/sessions/{id}/stop` | POST | Stop session |
| `/sessions/{id}/restart` | POST | Restart (preserves auth if paired) |
| `/sessions/{id}/qr` | GET | Get QR code for WhatsApp pairing |
| `/sessions/{id}/logout` | POST | Logout (clears auth, needs new QR) |
| `/sessions/{id}/events` | GET | SSE stream for real-time status updates |

**Session lifecycle:** `create` → `start` → scan QR → `working` → `stop`/`restart`/`logout`/`delete`

**SSE events:** Connect to `/sessions/{id}/events?token=JWT` for real-time status changes (stopped, starting, qr_code, working, failed).

## 2. Messages

```bash
# Send text message
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "uuid", "chat_id": "1234567890@c.us", "message": "Hello!"}' \
  https://apiv2.waiflow.app/api/v2/messages/send

# List chats for a session
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/messages/chats/{session_id}

# Get chat messages
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/messages/chat/{session_id}/{chat_id}
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/messages/send` | POST | Send text message |
| `/messages/send/poll` | POST | Send poll (question + options) |
| `/messages/send/sticker` | POST | Send sticker (WebP URL or base64) |
| `/messages/send/gif` | POST | Send GIF (MP4 URL or base64) |
| `/messages/chats/{session_id}` | GET | List chats |
| `/messages/chat/{session_id}/{chat_id}` | GET | Get messages in chat |
| `/messages/{message_id}` | GET | Get single message |

## 3. Groups

```bash
# List monitored groups
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/groups

# List available WhatsApp groups
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/groups/available/{session_id}

# Add group to monitor
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "uuid", "wa_group_id": "123456@g.us", "monitor_mode": "first_message"}' \
  https://apiv2.waiflow.app/api/v2/groups

# Update monitoring settings
curl -X PATCH -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"monitor_mode": "keywords", "monitor_keywords": ["looking for", "need help"]}' \
  https://apiv2.waiflow.app/api/v2/groups/{group_id}
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/groups` | GET | List monitored groups |
| `/groups/available/{session_id}` | GET | List available WhatsApp groups |
| `/groups` | POST | Add group to monitoring |
| `/groups/create` | POST | Create new WhatsApp group |
| `/groups/{id}` | GET | Get group details |
| `/groups/{id}` | PATCH | Update monitoring settings |
| `/groups/{id}` | DELETE | Remove from monitoring |
| `/groups/{wa_group_id}/participants/add` | POST | Add members to group |
| `/groups/{wa_group_id}/participants/remove` | POST | Remove members from group |
| `/groups/{wa_group_id}/admin/promote` | POST | Promote to admin |
| `/groups/{wa_group_id}/admin/demote` | POST | Demote from admin |

## 4. Labels

```bash
# Create label (color must be hex #RRGGBB)
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "VIP", "color": "#00FF00"}' \
  https://apiv2.waiflow.app/api/v2/labels

# Sync label to WhatsApp Business
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  "https://apiv2.waiflow.app/api/v2/labels/{label_id}/sync?session_id={session_id}"

# Import labels from WhatsApp Business
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  "https://apiv2.waiflow.app/api/v2/labels/sync-from-whatsapp?session_id={session_id}"
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/labels` | GET | List labels |
| `/labels` | POST | Create label |
| `/labels/business-check` | GET | Check WhatsApp Business status |
| `/labels/{id}` | GET / PATCH / DELETE | Get, update, delete label |
| `/labels/{id}/sync` | POST | Sync to WhatsApp Business |
| `/labels/sync-from-whatsapp` | POST | Import from WhatsApp |

## 5. Anti-Spam Rules

```bash
# Get anti-spam settings
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/antispam/settings

# Update anti-spam settings
curl -X PUT -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true, "rate_limit": 60, "rate_limit_window": 60, "block_duplicates": true, "auto_block_spammers": true, "max_violations": 5}' \
  https://apiv2.waiflow.app/api/v2/antispam/settings

# Create spam filter rule (actions: block, flag, delay)
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"pattern": "buy now|limited offer", "action": "block", "enabled": true}' \
  https://apiv2.waiflow.app/api/v2/antispam/rules

# Update rule
curl -X PUT -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"pattern": "buy now|limited offer|act fast", "action": "flag", "enabled": true}' \
  https://apiv2.waiflow.app/api/v2/antispam/rules/{rule_id}

# Delete rule
curl -X DELETE -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/antispam/rules/{rule_id}

# Get spam statistics
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/antispam/stats
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/antispam/settings` | GET | Get anti-spam settings |
| `/antispam/settings` | PUT | Update settings (rate limit, duplicate blocking, auto-block) |
| `/antispam/rules` | POST | Create spam filter rule |
| `/antispam/rules/{id}` | PUT | Update rule |
| `/antispam/rules/{id}` | DELETE | Delete rule |
| `/antispam/stats` | GET | Spam statistics (blocked, flagged, violations) |

**Rule actions:** `block` (drop message), `flag` (mark for review), `delay` (add cooldown)

**Settings fields:** `enabled`, `rate_limit` (msgs/window), `rate_limit_window` (seconds), `block_duplicates`, `duplicate_window`, `auto_block_spammers`, `max_violations`

## 6. Safeguards — Content Policy

```bash
# Get content policy settings
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/a2a-policy/settings

# Update content policy
curl -X PUT -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"block_api_keys": true, "block_credit_cards": true, "block_ssn": true, "block_emails": false, "max_message_length": 4096}' \
  https://apiv2.waiflow.app/api/v2/a2a-policy/settings

# View built-in safeguard patterns (prompt injection, secrets, PII)
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/a2a-policy/safeguards

# Create custom blocking rule
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"pattern": "sk-[a-zA-Z0-9]{48}", "description": "Block OpenAI API keys"}' \
  https://apiv2.waiflow.app/api/v2/a2a-policy/rules

# Toggle rule on/off
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/a2a-policy/rules/{rule_id}/toggle

# Delete custom rule
curl -X DELETE -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/a2a-policy/rules/{rule_id}

# Test content against all policies
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"content": "My API key is sk-abc123"}' \
  https://apiv2.waiflow.app/api/v2/a2a-policy/test

# Get blocking statistics
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/a2a-policy/stats

# Reset policy to defaults
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/a2a-policy/reset
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/a2a-policy/settings` | GET / PUT | Get or update content policy |
| `/a2a-policy/safeguards` | GET | View built-in safeguard patterns |
| `/a2a-policy/rules` | POST | Create custom blocking rule |
| `/a2a-policy/rules/{id}` | DELETE | Delete custom rule |
| `/a2a-policy/rules/{id}/toggle` | POST | Toggle rule on/off |
| `/a2a-policy/test` | POST | Test content against policies |
| `/a2a-policy/stats` | GET | Blocking statistics |
| `/a2a-policy/reset` | POST | Reset to defaults |

**Built-in safeguards:** prompt injection detection, secret patterns (API keys, tokens, private keys), PII patterns (SSN, credit cards, bank accounts)

**Policy fields:** `block_api_keys`, `block_passwords`, `block_tokens`, `block_private_keys`, `block_ssn`, `block_credit_cards`, `block_bank_accounts`, `block_phone_numbers`, `block_emails`, `max_message_length`, `max_urls_per_message`, `min_trust_level`, `log_blocked`

---

## 7. AI — Style Profiles

```bash
# Train style profile from message history
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -d '{"contact_id": "optional-contact-jid"}' \
  https://apiv2.waiflow.app/api/v2/ai/style/train

# Check training status
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/ai/style/status/{task_id}

# Get / list / delete style profiles
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/ai/style/profiles
```

## 8. AI — Reply Generation

```bash
# Generate AI reply (uses style profile)
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -d '{"contact_id": "jid", "context": "customer question", "apply_style": true}' \
  https://apiv2.waiflow.app/api/v2/ai/generate-reply

# Preview AI reply (no usage tracking)
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  "https://apiv2.waiflow.app/api/v2/ai/preview?contact_id=jid&context=question&apply_style=true"
```

### AI API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ai/style/train` | POST | Train style profile |
| `/ai/style/status/{task_id}` | GET | Training status |
| `/ai/style/profile` | GET | Get style profile |
| `/ai/style/profiles` | GET | List all profiles |
| `/ai/style/profile/{id}` | DELETE | Delete profile |
| `/ai/generate-reply` | POST | Generate AI reply |
| `/ai/preview` | GET | Preview reply (no tracking) |

---

## 9. A2A — Agent-to-Agent Protocol

**Requires Pro plan or above.** Uses JSON-RPC 2.0 over HTTPS with X25519-AES256GCM encryption.

### Bootstrap & encryption

```bash
# Get full configuration
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/agent/bootstrap

# Get your public key (auto-generates if none)
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/agent/public-key

# Rotate keypair
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/agent/rotate-keys
```

### Discover agents

```bash
# Resolve phone to MoltFlow agent
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/agents/resolve/+1234567890

# List peers
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/agents/peers

# Update trust level (discovered, verified, blocked)
curl -X PATCH -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"trust_level": "verified"}' \
  https://apiv2.waiflow.app/api/v2/agents/peers/{peer_id}/trust
```

### Send A2A messages (JSON-RPC 2.0)

```bash
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "agent.message.send",
    "params": {
      "phone": "+1234567890",
      "message": {"parts": [{"text": "Hello from my agent!"}]}
    },
    "id": "1"
  }' \
  https://apiv2.waiflow.app/api/v2/a2a
```

### A2A API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/agent/bootstrap` | GET | Full onboarding config |
| `/agent/public-key` | GET | Get X25519 public key |
| `/agent/rotate-keys` | POST | Rotate keypair |
| `/agent/peer/{tenant_id}/public-key` | GET | Peer's public key |
| `/agents/resolve/{phone}` | GET | Resolve phone to agent |
| `/agents/peers` | GET | List discovered peers |
| `/agents/peers/{id}/trust` | PATCH | Update trust level |
| `/a2a` | POST | JSON-RPC 2.0 endpoint |

**JSON-RPC methods:** `agent.message.send`, `group.getContext`, `agent.group.create`, `agent.group.invite`, `agent.group.list`, `webhook_manager`

**Trust levels:** `discovered` → `verified` → `blocked`

**Encryption:** X25519-AES256GCM, ECDH key exchange, HKDF-SHA256, 32-byte keys (base64)

---

## 10. Reviews — Feedback Collection & Testimonials

```bash
# Create review collector
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -d '{
    "name": "Customer Feedback",
    "session_id": "uuid-of-whatsapp-session",
    "source_type": "groups",
    "min_positive_words": 3,
    "min_sentiment_score": 0.6,
    "include_keywords": ["great", "excellent"],
    "languages": []
  }' \
  https://apiv2.waiflow.app/api/v2/reviews/collectors

# Trigger manual scan
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/reviews/collectors/{id}/run

# List reviews
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  "https://apiv2.waiflow.app/api/v2/reviews?approved_only=false&limit=50"

# Approve review
curl -X PATCH -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -d '{"is_approved": true}' \
  https://apiv2.waiflow.app/api/v2/reviews/{id}

# Export testimonials as HTML
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  "https://apiv2.waiflow.app/api/v2/reviews/testimonials/export?format=html"
```

### Reviews API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/reviews/collectors` | GET/POST | List/create collectors |
| `/reviews/collectors/{id}` | GET/PATCH/DELETE | Manage collector |
| `/reviews/collectors/{id}/run` | POST | Trigger scan |
| `/reviews` | GET | List reviews |
| `/reviews/stats` | GET | Review statistics |
| `/reviews/{id}` | GET/PATCH/DELETE | Manage review |
| `/reviews/testimonials/export` | GET | Export (format=json/html) |

**Supported languages (14+):** English, Spanish, Portuguese, French, German, Italian, Dutch, Russian, Arabic, Hebrew, Chinese, Japanese, Korean, Hindi, Turkish

**Collector fields:** `name`, `session_id`, `source_type` (all/groups/chats/selected), `min_positive_words` (1-10), `min_sentiment_score` (0.0-1.0), `include_keywords`, `exclude_keywords`, `languages`

---

## 11. Webhooks

```bash
# List webhooks
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/webhooks

# Create webhook
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "Order Bot", "url": "https://example.com/webhook", "events": ["message.received", "lead.detected"], "secret": "optional-hmac-secret"}' \
  https://apiv2.waiflow.app/api/v2/webhooks

# Update webhook
curl -X PATCH -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"events": ["message.received", "message.sent", "session.connected"]}' \
  https://apiv2.waiflow.app/api/v2/webhooks/{webhook_id}

# Test webhook (sends sample payload)
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/webhooks/{webhook_id}/test

# Delete webhook
curl -X DELETE -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/webhooks/{webhook_id}
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/webhooks` | GET | List webhooks |
| `/webhooks` | POST | Create webhook |
| `/webhooks/{id}` | GET | Get webhook details |
| `/webhooks/{id}` | PATCH | Update webhook |
| `/webhooks/{id}` | DELETE | Delete webhook |
| `/webhooks/{id}/test` | POST | Send test payload |

**Events:** `message.received`, `message.sent`, `message.delivered`, `message.read`, `lead.detected`, `session.connected`, `session.disconnected`, `group.message`

**Security:** Webhooks include HMAC-SHA256 signature in `X-Webhook-Signature` header when `secret` is set. URLs must not resolve to private IPs (SSRF protection).

---

## 12. Auth & API Keys

```bash
# Login
curl -X POST -d '{"email": "user@example.com", "password": "..."}' \
  https://apiv2.waiflow.app/api/v2/auth/login

# Get current user
curl -H "Authorization: Bearer $TOKEN" \
  https://apiv2.waiflow.app/api/v2/auth/me

# Create API key
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "Production Key", "expires_in_days": 90}' \
  https://apiv2.waiflow.app/api/v2/api-keys

# Revoke key
curl -X DELETE -H "Authorization: Bearer $TOKEN" \
  https://apiv2.waiflow.app/api/v2/api-keys/{id}

# Rotate key
curl -X POST -H "Authorization: Bearer $TOKEN" \
  https://apiv2.waiflow.app/api/v2/api-keys/{id}/rotate
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/login` | POST | Login (email/password), returns JWT |
| `/auth/refresh` | POST | Refresh token |
| `/auth/me` | GET | Current user + tenant |
| `/auth/logout` | POST | Invalidate refresh token |
| `/auth/magic-link/request` | POST | Request magic link |
| `/auth/magic-link/verify` | POST | Verify magic link token |
| `/auth/forgot-password` | POST | Request password reset email |
| `/auth/reset-password` | POST | Confirm password reset (token + new password) |
| `/auth/verify-email` | POST | Verify email address (token from signup email) |
| `/api-keys` | GET/POST | List/create API keys |
| `/api-keys/{id}` | GET/DELETE | Get/revoke key |
| `/api-keys/{id}/rotate` | POST | Rotate key |

## 13. Usage & Billing

```bash
# Current period usage
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/usage/current

# Daily breakdown
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  "https://apiv2.waiflow.app/api/v2/usage/daily?days=30"

# List plans
curl https://apiv2.waiflow.app/api/v2/billing/plans

# Create checkout session
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -d '{"plan": "pro", "cycle": "monthly", "success_url": "https://...", "cancel_url": "https://..."}' \
  https://apiv2.waiflow.app/api/v2/billing/checkout

# Billing portal
curl -X POST -H "Authorization: Bearer $TOKEN" \
  https://apiv2.waiflow.app/api/v2/billing/portal
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/usage/current` | GET | Current period usage + limits |
| `/usage/history` | GET | Historical usage |
| `/usage/daily` | GET | Daily breakdown |
| `/billing/plans` | GET | Available plans |
| `/billing/subscription` | GET | Subscription details (plan info, usage, next invoice) |
| `/billing/checkout` | POST | Stripe checkout session |
| `/billing/portal` | POST | Stripe billing portal |
| `/billing/cancel` | POST | Cancel subscription |

---

## 14. Scheduled Messages

```bash
# Create scheduled message (one-time)
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "Follow-up", "session_id": "uuid", "custom_group_id": "custom-group-uuid", "message_content": "Just checking in!", "schedule_type": "one_time", "scheduled_time": "2026-02-15T09:00:00", "timezone": "Asia/Jerusalem"}' \
  https://apiv2.waiflow.app/api/v2/scheduled-messages

# Create recurring schedule (cron)
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "Weekly Update", "session_id": "uuid", "custom_group_id": "custom-group-uuid", "message_content": "Weekly report...", "schedule_type": "cron", "cron_expression": "0 9 * * MON", "timezone": "America/New_York"}' \
  https://apiv2.waiflow.app/api/v2/scheduled-messages

# Pause / resume / cancel
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/scheduled-messages/{schedule_id}/pause

curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/scheduled-messages/{schedule_id}/resume

# View execution history
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/scheduled-messages/{schedule_id}/history
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/scheduled-messages` | GET | List all scheduled messages |
| `/scheduled-messages` | POST | Create scheduled message (one-time or recurring) |
| `/scheduled-messages/{id}` | GET | Get schedule with execution history |
| `/scheduled-messages/{id}` | PATCH | Update schedule and recalculate next run |
| `/scheduled-messages/{id}/cancel` | POST | Cancel schedule |
| `/scheduled-messages/{id}/pause` | POST | Pause active schedule |
| `/scheduled-messages/{id}/resume` | POST | Resume paused schedule |
| `/scheduled-messages/{id}` | DELETE | Delete cancelled/completed schedule |
| `/scheduled-messages/{id}/history` | GET | Execution history (paginated) |

**Schedule types:** `one_time`, `daily`, `weekly`, `monthly`, `cron`

**Required fields:** `name`, `session_id`, `custom_group_id`, `message_content`, `scheduled_time` (for one-time) or `cron_expression` (for cron)

---

## 15. Bulk Send

```bash
# Create bulk send job
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "uuid", "custom_group_id": "custom-group-uuid", "message_content": "Special offer for VIP clients!"}' \
  https://apiv2.waiflow.app/api/v2/bulk-send

# List bulk send jobs
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/bulk-send

# Stream real-time progress (SSE)
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/bulk-send/{job_id}/progress

# Pause / resume / cancel
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/bulk-send/{job_id}/pause
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/bulk-send` | POST | Create bulk send job (quota reserved) |
| `/bulk-send` | GET | List all bulk send jobs |
| `/bulk-send/{id}` | GET | Job details with recipients |
| `/bulk-send/{id}/pause` | POST | Pause running job |
| `/bulk-send/{id}/resume` | POST | Resume paused job |
| `/bulk-send/{id}/cancel` | POST | Cancel job (releases unused quota) |
| `/bulk-send/{id}/progress` | GET | Real-time progress via SSE |

**Anti-ban:** Random 30s–2min delays between messages, typing simulation, seen indicators. Zero ban risk.

---

## 16. Custom Groups

```bash
# Create custom group
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "VIP Clients", "members": [{"phone": "+15550123456"}, {"phone": "+15550987654"}]}' \
  https://apiv2.waiflow.app/api/v2/custom-groups

# List all custom groups
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/custom-groups

# Add members
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"contacts": [{"phone": "+15551112222"}, {"phone": "+15553334444"}]}' \
  https://apiv2.waiflow.app/api/v2/custom-groups/{group_id}/members/add

# Export as CSV
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/custom-groups/{group_id}/export/csv
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/custom-groups` | GET | List all custom groups |
| `/custom-groups` | POST | Create group (with optional initial members) |
| `/custom-groups/contacts` | GET | List all unique contacts across sessions |
| `/custom-groups/{id}` | GET | Group details with members |
| `/custom-groups/{id}` | PATCH | Update group name |
| `/custom-groups/{id}` | DELETE | Delete group and members |
| `/custom-groups/{id}/members/add` | POST | Add members (skips duplicates) |
| `/custom-groups/{id}/members/remove` | POST | Remove members by phone |
| `/custom-groups/{id}/export/csv` | GET | Export members as CSV |
| `/custom-groups/{id}/export/json` | GET | Export members as JSON |

**Note:** Custom Groups are MoltFlow contact lists, not WhatsApp groups. Use them for targeted Bulk Send and Scheduled Messages.

---

## 17. Leads

```bash
# List leads (with filters)
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  "https://apiv2.waiflow.app/api/v2/leads?status=new&source_group_id=uuid&search=pricing&limit=50"

# Get lead details
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/leads/{lead_id}

# Update lead status
curl -X PATCH -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"status": "contacted"}' \
  https://apiv2.waiflow.app/api/v2/leads/{lead_id}/status

# Bulk update status
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"lead_ids": ["uuid1", "uuid2"], "status": "qualified"}' \
  https://apiv2.waiflow.app/api/v2/leads/bulk/status

# Bulk add to custom group
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"lead_ids": ["uuid1", "uuid2"], "custom_group_id": "custom-group-uuid"}' \
  https://apiv2.waiflow.app/api/v2/leads/bulk/add-to-group

# Export as CSV (Pro+ plan)
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/leads/export/csv
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/leads` | GET | List leads (filter by status, group, search) |
| `/leads/{id}` | GET | Lead details |
| `/leads/{id}/status` | PATCH | Update status (state machine validated) |
| `/leads/{id}/reciprocity` | GET | Check if lead messaged you first (anti-spam) |
| `/leads/bulk/status` | POST | Bulk status update |
| `/leads/bulk/add-to-group` | POST | Bulk add leads to custom group |
| `/leads/export/csv` | GET | Export as CSV (Pro+ plan, max 10,000) |
| `/leads/export/json` | GET | Export as JSON (Pro+ plan, max 10,000) |

**Lead statuses:** `new` → `contacted` → `qualified` → `converted` / `lost`

---

## 18. Knowledge Base (RAG)

```bash
# Upload document to knowledge base
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -F "file=@product-catalog.pdf" \
  https://apiv2.waiflow.app/api/v2/ai/knowledge/ingest

# Search knowledge base
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the pricing plans?"}' \
  https://apiv2.waiflow.app/api/v2/ai/knowledge/search

# List documents
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/ai/knowledge/sources

# Delete document
curl -X DELETE -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/ai/knowledge/{source_id}
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ai/knowledge/ingest` | POST | Upload document (PDF or TXT) |
| `/ai/knowledge/search` | POST | Semantic search with embeddings |
| `/ai/knowledge/sources` | GET | List all documents |
| `/ai/knowledge/{id}` | DELETE | Delete document |

**How it works:** Upload your product docs, FAQ, or any reference material. When AI generates a reply, it searches your knowledge base for relevant context (RAG — Retrieval-Augmented Generation) to give accurate, grounded answers.

---

## 19. Voice Transcription

```bash
# Transcribe a voice message
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message_id": "msg-uuid"}' \
  https://apiv2.waiflow.app/api/v2/ai/voice/transcribe

# Check transcription status
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/ai/voice/status/{task_id}

# Get transcript
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/ai/messages/{message_id}/transcript
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ai/voice/transcribe` | POST | Queue voice message for Whisper transcription |
| `/ai/voice/status/{task_id}` | GET | Check transcription status |
| `/ai/messages/{message_id}/transcript` | GET | Get transcript text |

---

## Comparison with Other Skills

> MoltFlow isn't a messaging wrapper — it's a complete WhatsApp business automation platform. Here's how it stacks up.

### Messaging

| Feature | **MoltFlow** | whatsapp-ultimate | wacli | whatsapp-automation |
|---------|:-------:|:-----------------:|:-----:|:-------------------:|
| Send text | ✅ | ✅ | ✅ | ❌ |
| Send media (image, audio) | ✅ | ✅ | ✅ | ❌ |
| Polls | ✅ | ✅ | ❌ | ❌ |
| Stickers (URL + base64) | ✅ | ✅ | ❌ | ❌ |
| Voice notes | ✅ | ✅ | ❌ | ❌ |
| GIFs (URL + base64) | ✅ | ✅ | ❌ | ❌ |
| Reactions | ✅ | ✅ | ❌ | ❌ |
| Reply / Quote | ✅ | ✅ | ❌ | ❌ |
| Edit messages | ✅ | ✅ | ❌ | ❌ |
| Unsend messages | ✅ | ✅ | ❌ | ❌ |
| Send location | ✅ | ❌ | ❌ | ❌ |
| Send vCards (contact cards) | ✅ | ❌ | ❌ | ❌ |
| Star / unstar messages | ✅ | ❌ | ❌ | ❌ |
| Read receipts control | ✅ | ❌ | ❌ | ❌ |
| Typing simulation (anti-ban) | ✅ | ❌ | ❌ | ❌ |
| Presence management | ✅ | ❌ | ❌ | ❌ |
| Receive messages | ✅ | ✅ | ✅ | ✅ |
| Two-way chat | ✅ | ✅ | ❌ | ❌ |

### Groups

| Feature | **MoltFlow** | whatsapp-ultimate | wacli | whatsapp-automation |
|---------|:-------:|:-----------------:|:-----:|:-------------------:|
| List groups | ✅ | ✅ | ❌ | ❌ |
| Create group | ✅ | ✅ | ❌ | ❌ |
| Add / remove members | ✅ | ✅ (full) | ❌ | ❌ |
| Promote / demote admin | ✅ | ✅ | ❌ | ❌ |
| Smart monitoring (keywords, mentions) | ✅ | ❌ | ❌ | ❌ |
| Group lead auto-detection | ✅ | ❌ | ❌ | ❌ |
| Group auto-respond | ✅ | ❌ | ❌ | ❌ |
| Per-group AI prompts | ✅ | ❌ | ❌ | ❌ |

### Outreach & Scheduling

| Feature | **MoltFlow** | whatsapp-ultimate | wacli | whatsapp-automation |
|---------|:-------:|:-----------------:|:-----:|:-------------------:|
| Bulk messaging (ban-safe) | ✅ | ❌ | ❌ | ❌ |
| Scheduled messages (cron) | ✅ | ❌ | ❌ | ❌ |
| Custom contact groups | ✅ | ❌ | ❌ | ❌ |
| Timezone-aware scheduling | ✅ | ❌ | ❌ | ❌ |
| Pause/resume/cancel jobs | ✅ | ❌ | ❌ | ❌ |
| Real-time progress (SSE) | ✅ | ❌ | ❌ | ❌ |
| CSV/JSON export | ✅ | ❌ | ❌ | ❌ |

### CRM & Lead Management

| Feature | **MoltFlow** | whatsapp-ultimate | wacli | whatsapp-automation |
|---------|:-------:|:-----------------:|:-----:|:-------------------:|
| Contact management | ✅ | ❌ | ❌ | ❌ |
| Lead pipeline & scoring | ✅ | ❌ | ❌ | ❌ |
| Lead auto-detection | ✅ | ❌ | ❌ | ❌ |
| Bulk lead operations | ✅ | ❌ | ❌ | ❌ |
| Lead export (CSV/JSON) | ✅ | ❌ | ❌ | ❌ |
| Label system (WA Business sync) | ✅ | ❌ | ❌ | ❌ |
| Team assignment | ✅ | ❌ | ❌ | ❌ |

### AI & Intelligence

| Feature | **MoltFlow** | whatsapp-ultimate | wacli | whatsapp-automation |
|---------|:-------:|:-----------------:|:-----:|:-------------------:|
| AI reply suggestions | ✅ | ❌ | ❌ | ❌ |
| Style cloning (Learn Mode) | ✅ | ❌ | ❌ | ❌ |
| Knowledge base (RAG) | ✅ | ❌ | ❌ | ❌ |
| Voice transcription (Whisper) | ✅ | ❌ | ❌ | ❌ |
| AI auto-labeling | ✅ | ❌ | ❌ | ❌ |
| AI auto-responses | ✅ | ❌ | ❌ | ❌ |
| AI prompt templates | ✅ | ❌ | ❌ | ❌ |

### Analytics & Reporting

| Feature | **MoltFlow** | whatsapp-ultimate | wacli | whatsapp-automation |
|---------|:-------:|:-----------------:|:-----:|:-------------------:|
| Message statistics | ✅ | ❌ | ❌ | ❌ |
| Engagement insights | ✅ | ❌ | ❌ | ❌ |
| Lead pipeline analytics | ✅ | ❌ | ❌ | ❌ |
| Executive briefing | ✅ | ❌ | ❌ | ❌ |
| Team activity & workload | ✅ | ❌ | ❌ | ❌ |

### Compliance & Security

| Feature | **MoltFlow** | whatsapp-ultimate | wacli | whatsapp-automation |
|---------|:-------:|:-----------------:|:-----:|:-------------------:|
| Anti-spam engine (human-like typing) | ✅ | ❌ | ❌ | ❌ |
| GDPR audit logging | ✅ | ❌ | ❌ | ❌ |
| Content filtering (PII, secrets, injection) | ✅ | ❌ | ❌ | ❌ |
| Consent tracking | ✅ | ❌ | ❌ | ❌ |
| Tiered rate limiting | ✅ | ❌ | ❌ | ❌ |
| Auto-expiring messages (90-day retention) | ✅ | ❌ | ❌ | ❌ |
| Data minimization (500-char preview only) | ✅ | ❌ | ❌ | ❌ |
| Named sub-processors (GDPR Art. 28) | ✅ | ❌ | ❌ | ❌ |
| Contact erasure (right to be forgotten) | ✅ | ❌ | ❌ | ❌ |
| Data Processing Agreement (DPA) | ✅ | ❌ | ❌ | ❌ |

### Review Collection

| Feature | **MoltFlow** | whatsapp-ultimate | wacli | whatsapp-automation |
|---------|:-------:|:-----------------:|:-----:|:-------------------:|
| Auto review collection | ✅ | ❌ | ❌ | ❌ |
| Sentiment analysis (14+ languages) | ✅ | ❌ | ❌ | ❌ |
| Testimonial export (JSON / HTML) | ✅ | ❌ | ❌ | ❌ |

### Platform & Infrastructure

| Feature | **MoltFlow** | whatsapp-ultimate | wacli | whatsapp-automation |
|---------|:-------:|:-----------------:|:-----:|:-------------------:|
| Multi-session (up to 10 numbers) | ✅ | ❌ | ❌ | ❌ |
| Webhooks (30+ event types) | ✅ | ❌ | ❌ | ❌ |
| Real-time SSE events | ✅ | ❌ | ❌ | ❌ |
| API key management | ✅ | ❌ | ❌ | ❌ |
| Multi-tenant architecture | ✅ | ❌ | ❌ | ❌ |
| A2A protocol (E2E encrypted) | ✅ | ❌ | ❌ | ❌ |
| Web dashboard | ✅ | ❌ | ❌ | ❌ |
| Stripe billing | ✅ | ❌ | ❌ | ❌ |

### Summary

| | **MoltFlow** | **whatsapp-ultimate** | **wacli** | **whatsapp-automation** |
|---|---|---|---|---|
| **Messaging** | 18 / 18 | 14 / 18 | 3 / 18 | 1 / 18 |
| **Outreach & scheduling** | 7 | 0 | 0 | 0 |
| **Business features** | 55+ | 0 | 0 | 0 |
| **Total** | **80+** | **~15** | **~3** | **~1** |
| **External deps** | Docker + WAHA | None | Go binary | Docker + WAHA |

---

## Credentials & Security

**Only one credential is required:** `MOLTFLOW_API_KEY` — get it from the [API Keys page](https://molt.waiflow.app) in your dashboard.

No other secrets are needed by external users:
- **A2A encryption keys** (X25519) are generated and managed server-side — your API key grants access
- **Stripe billing keys** are handled internally — you interact via checkout/portal URLs
- **JWT tokens** are obtained via `/auth/login` using email/password, no separate secret needed

This skill is **documentation-only** — it provides API guidance to AI agents. The `scripts/` directory contains Python example scripts for common workflows, not executable dependencies.

## Example Scripts

The `scripts/` directory contains standalone Python examples (requires `requests`):

| Script | Purpose |
|--------|---------|
| `quickstart.py` | Create session, send first message |
| `send_message.py` | Send text messages to contacts |
| `a2a_client.py` | Discover agents, send A2A messages |
| `admin.py` | Login, create API keys, check billing |
| `ai_config.py` | Train style profiles, generate AI replies |
| `reviews.py` | Create collectors, export testimonials |
| `outreach.py` | Bulk send, scheduled messages, custom groups |
| `leads.py` | Lead pipeline, bulk ops, CSV/JSON export |

Run any script: `MOLTFLOW_API_KEY=your-key python scripts/quickstart.py`

---

## Pricing

> **Yearly plan available** — save up to 17% with annual billing. Pay once, use for 12 months.

| Plan | Monthly | Yearly | Messages/mo | Sessions | Groups | API Rate |
|------|---------|--------|-------------|----------|--------|----------|
| Free | $0 | — | 50 | 1 | 2 | 10/min |
| Starter | $9.90 | $99/yr | 500 | 1 | 5 | 20/min |
| Pro | $29.90 | $299/yr | 1,500 | 5 | 20 | 40/min |
| Business | $69.90 | $699/yr | 3,000 | 15 | 100 | 60/min |

Sign up: https://molt.waiflow.app/checkout?plan=free

---

## Blog & Guides

Tutorials and guides for common MoltFlow workflows:

- [Getting Started with WhatsApp Automation](https://molt.waiflow.app/blog/whatsapp-automation-getting-started)
- [MoltFlow API Complete Guide](https://molt.waiflow.app/blog/moltflow-api-complete-guide)
- [MoltFlow + n8n WhatsApp Automation](https://molt.waiflow.app/blog/moltflow-n8n-whatsapp-automation)
- [n8n + WhatsApp + Google Sheets](https://molt.waiflow.app/blog/n8n-whatsapp-google-sheets)
- [n8n WhatsApp Group Auto-Reply](https://molt.waiflow.app/blog/n8n-whatsapp-group-auto-reply)
- [n8n WhatsApp Lead Pipeline](https://molt.waiflow.app/blog/n8n-whatsapp-lead-pipeline)
- [n8n Multi-Model AI Orchestration](https://molt.waiflow.app/blog/n8n-multi-model-ai-orchestration)
- [AI Auto-Replies for WhatsApp Setup](https://molt.waiflow.app/blog/ai-auto-replies-whatsapp-setup)
- [WhatsApp Group Lead Generation Guide](https://molt.waiflow.app/blog/whatsapp-group-lead-generation-guide)
- [A2A Protocol: Agent-to-Agent Communication](https://molt.waiflow.app/blog/a2a-protocol-agent-communication)
- [OpenClaw WhatsApp Customer Support](https://molt.waiflow.app/blog/openclaw-whatsapp-customer-support)
- [Scaling WhatsApp Automation ROI](https://molt.waiflow.app/blog/scaling-whatsapp-automation-roi)

Full blog: https://molt.waiflow.app/blog

---

## Notes

- All messages include anti-spam compliance (typing indicators, random delays)
- API rate limits by plan: Free 10/min, Starter 20/min, Pro 40/min, Business 60/min
- Sessions require QR code pairing on first connect
- Use E.164 phone format without `+` where required
- AI features (auto-responses, RAG, Learn Mode) require Pro plan or above
- A2A protocol requires Pro plan or above
- Anti-spam rules support pattern matching with block, flag, or delay actions
- Content safeguards filter secrets (API keys, tokens), PII (SSN, credit cards), and prompt injection
- AI reply generation includes safety: input sanitization, intent verification, output filtering
- API keys use name + expires_in_days (no scopes param); raw key shown only once at creation
- Respect WhatsApp opt-in, business hours, and opt-out requests

---

## Changelog

### v2.0.0 (2026-02-12)

**New API sections:**
- **Scheduled Messages** (Section 14) — one-time, daily/weekly/monthly, cron, timezone-aware, pause/resume/cancel, execution history
- **Bulk Send** (Section 15) — ban-safe broadcast to custom groups, real-time SSE progress, pause/resume/cancel, quota management
- **Custom Groups** (Section 16) — contact lists for targeted outreach, import from WhatsApp, CSV/JSON export, member management
- **Leads** (Section 17) — auto-detected lead pipeline, status tracking (new→contacted→qualified→converted), bulk operations, CSV/JSON export, reciprocity check
- **Knowledge Base / RAG** (Section 18) — upload PDF/TXT documents, semantic search with embeddings, AI uses your docs for grounded answers
- **Voice Transcription** (Section 19) — Whisper-powered async transcription with task status tracking

**Updated:**
- Complete feature matrix at the top with all 18 platform capabilities
- Expanded "When to use" list covering all features
- New use case categories: Bulk messaging & scheduling, AI & knowledge
- Comparison table: added Outreach & Scheduling section (7 features), Bulk lead operations, Lead export
- Updated totals: 80+ features (was 63+)
- Yearly billing offer highlighted in pricing and feature matrix

### v1.6.0 (2026-01-28)
- Added GDPR compliance section (auto-expiring messages, data minimization, contact erasure, DPA)
- Added AI consent enforcement documentation
- Updated comparison tables with compliance features (10 new entries)

### v1.5.0 (2026-01-15)
- Added Reviews & Testimonials API (Section 10)
- Added A2A Protocol with X25519-AES256GCM encryption
- Added Content Safeguards API (Section 6)
- Added blog & guides section

### v1.0.0 (2025-12-01)
- Initial release: Sessions, Messages, Groups, Labels, Anti-Spam, AI, Webhooks, Auth, Billing

<!-- FILEMAP:BEGIN -->
```text
[moltflow file map]|root: .
|.:{SKILL.md,CHANGELOG.md,package.json}
|scripts:{quickstart.py,a2a_client.py,send_message.py,admin.py,ai_config.py,reviews.py,outreach.py,leads.py}
|moltflow:{SKILL.md}
|moltflow-ai:{SKILL.md}
|moltflow-a2a:{SKILL.md}
|moltflow-reviews:{SKILL.md}
|moltflow-outreach:{SKILL.md}
|moltflow-leads:{SKILL.md}
|moltflow-admin:{SKILL.md}
```
<!-- FILEMAP:END -->
