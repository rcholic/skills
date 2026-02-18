const express = require('express');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const app = express();
app.use(express.json({ limit: '50mb' }));

const PORT = process.env.PORT || 19192;
const SECRET = process.env.WEBHOOK_SECRET;

if (!SECRET) {
    console.error(`
╔══════════════════════════════════════════════════════════════╗
║           EMAIL WEBHOOK — CONFIGURATION REQUIRED             ║
╚══════════════════════════════════════════════════════════════╝

Missing required environment variable: WEBHOOK_SECRET

This server receives inbound emails from a Cloudflare Worker and
requires a shared secret to authenticate incoming requests.

To start the server, set WEBHOOK_SECRET:

  WEBHOOK_SECRET=your-strong-secret node scripts/webhook_server.js

The same secret must be configured in your Cloudflare Email Worker
as the Authorization Bearer token it sends with each request.

  Example Cloudflare Worker config:
    const WEBHOOK_SECRET = "your-strong-secret";
    fetch(WEBHOOK_URL, {
      headers: { "Authorization": "Bearer " + WEBHOOK_SECRET }
    });

Optional variables:
  PORT        - Port to listen on (default: 19192)
  INBOX_FILE  - Filename for storing emails (default: inbox.jsonl)
`);
    process.exit(1);
}

const RAW_INBOX_FILE = process.env.INBOX_FILE || 'inbox.jsonl';
const INBOX_FILE = path.basename(RAW_INBOX_FILE);
const INBOX_PATH = path.resolve(process.cwd(), INBOX_FILE);

app.post('/api/email', (req, res) => {
    const auth = req.headers['authorization'];
    if (auth !== `Bearer ${SECRET}`) {
        console.warn(`[AUTH] Unauthorized attempt from ${req.ip}`);
        return res.status(403).send('Forbidden');
    }

    const email = req.body;
    if (!email || typeof email !== 'object') {
        return res.status(400).send('Invalid payload');
    }

    console.log(`[OK] Email received: ${email.subject || '(no subject)'}`);

    try {
        const entry = JSON.stringify({
            receivedAt: new Date().toISOString(),
            ...email
        }) + '\n';
        
        fs.appendFileSync(INBOX_PATH, entry);
        
        // WAKE MECHANISM: Signal OpenClaw that a new email arrived.
        const wakeText = `New email from ${email.from || 'unknown'}: ${email.subject || '(no subject)'}`;
        const safeWakeText = wakeText.substring(0, 200).replace(/[\r\n]/g, ' ');

        const token = process.env.OPENCLAW_GATEWAY_TOKEN;
        // Use 'system event' with '--mode now' to force an immediate heartbeat run
        const args = ['system', 'event', '--text', safeWakeText, '--mode', 'now'];
        if (token) {
            args.push('--token', token);
        }

        const child = spawn('openclaw', args);

        child.on('error', (err) => {
            console.error(`[WAKE] Failed to spawn openclaw: ${err.message}`);
        });

        child.stdout.on('data', (data) => console.log(`[WAKE-OUT] ${data}`));
        child.stderr.on('data', (data) => console.error(`[WAKE-ERR] ${data}`));

        child.on('close', (code) => {
            if (code !== 0) console.error(`[WAKE] openclaw exited with code ${code}`);
            else console.log(`[WAKE] Gateway signaled: ${safeWakeText}`);
        });

        res.status(200).send({ success: true });
    } catch (e) {
        console.error(`[ERROR] Failed to process email: ${e.message}`);
        res.status(500).send('Internal Server Error');
    }
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`\n📧 EMAIL WEBHOOK SERVER v1.5.3`);
    console.log(`Port: ${PORT}`);
    console.log(`Inbox: ${INBOX_PATH}`);
    console.log(`Wake: Enabled (system event now)\n`);
});
