<skill>
  <id>clawbridge</id>
  <name>ClawBridge Dashboard</name>
  <version>1.0.0</version>
  <description>Mobile-first mission control for OpenClaw agents. Monitor real-time thoughts, track token costs, and manage cron tasks from your phone.</description>
  <author>DreamWing</author>
  <homepage>https://clawbridge.app</homepage>
  <license>MIT</license>
  <tags>dashboard,monitoring,mobile,ui,control-panel,cost-tracking</tags>
  <install>
    curl -sL https://clawbridge.app/install.sh | bash
  </install>
  <instructions>
    To update ClawBridge to the latest version, simply re-run the installation command:
    `curl -sL "https://clawbridge.app/install.sh?ref=update" | bash`
    The script will automatically detect the existing installation and pull the latest changes.
  </instructions>
</skill>

# ClawBridge Dashboard

**Your Agent. In Your Pocket.**

ClawBridge is a lightweight, mobile-first web interface for OpenClaw. It runs as a sidecar process and provides:

*   🧠 **Live Activity Feed**: Watch execution and thinking in real-time.
*   💰 **Token Economy**: Track costs across 340+ models.
*   🚀 **Mission Control**: Trigger cron jobs manually.
*   ⚡ **Zero-Config**: Auto-detects VPNs or creates quick tunnels.

## Installation

```bash
curl -sL https://clawbridge.app/install.sh | bash
```

See [README.md](https://github.com/dreamwing/clawbridge/blob/master/README.md) for full documentation.
