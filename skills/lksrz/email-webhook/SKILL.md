---
name: email-webhook
description: Receive incoming emails via JSON webhooks and wake the agent. Built for AI Commander.
metadata: {"openclaw": {"requires": {"bins": ["node", "openclaw"], "env": ["WEBHOOK_SECRET"]}, "primaryEnv": "WEBHOOK_SECRET", "install": [{"id": "npm-deps", "kind": "node", "package": "express@4.21.2", "label": "Install Webhook dependencies"}]}}
---

# Email Webhook Receiver

This skill provides a secure endpoint to receive emails as standardized JSON webhooks and automatically wakes the agent.

## ⚡️ Wake Mechanism

When an email is received, the server invokes `openclaw system event --mode now`. This ensures the agent is notified immediately and can process the incoming communication without waiting for the next heartbeat cycle.

## 🚨 Security & Privacy

### Command Injection Protection
The server uses secure process spawning (`child_process.spawn`) with argument arrays instead of shell execution. User-controlled input (email headers) cannot be used to execute arbitrary system commands.

### Path Traversal Protection
The `INBOX_FILE` parameter is sanitized using `path.basename()`, ensuring that files are only written within the server's working directory.

### Authentication
A strong `WEBHOOK_SECRET` environment variable is **REQUIRED** for the server to start. All incoming requests must provide this secret in the `Authorization: Bearer <secret>` header.

### Data Storage
- **Local Inbox**: Incoming emails (raw body and metadata) are appended to a local `inbox.jsonl` file.
- **Cleanup**: Users should periodically rotate or delete the inbox file to save disk space and protect privacy.

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `WEBHOOK_SECRET` | **Yes** | — | Secret token for webhook authentication. |
| `PORT` | No | `19192` | Port to listen on. |
| `INBOX_FILE` | No | `inbox.jsonl` | Filename for the activity feed. |

## Setup

1. **Install dependencies**:
   ```bash
   npm install express@4.21.2
   ```
2. **Start Server**:
   ```bash
   WEBHOOK_SECRET=your-strong-token node scripts/webhook_server.js
   ```

## Runtime Requirements
Requires: `express`, `node`, `openclaw` CLI.
