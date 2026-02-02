---
name: computer-use
description: Full desktop computer use for headless Linux servers and VPS. Creates a virtual display (Xvfb + XFCE) to control GUI applications without a physical monitor. Screenshots, mouse clicks, keyboard input, scrolling, dragging — all 17 standard actions. Includes VNC setup for live remote viewing and interaction. Model-agnostic, works with any LLM.
version: 1.1.0
---

# Computer Use Skill

Full desktop GUI control for headless Linux servers. Creates a virtual display (Xvfb + XFCE) so you can run and control desktop applications on VPS/cloud instances without a physical monitor.

## Environment

- **Display**: `:99`
- **Resolution**: 1024x768 (XGA, Anthropic recommended)
- **Desktop**: XFCE4

## Quick Start

```bash
export DISPLAY=:99

# Take screenshot
./scripts/screenshot.sh

# Click at coordinates
./scripts/click.sh 512 384 left

# Type text
./scripts/type_text.sh "Hello world"

# Press key combo
./scripts/key.sh "ctrl+s"

# Scroll down
./scripts/scroll.sh down 5
```

## Actions Reference

| Action | Script | Arguments | Description |
|--------|--------|-----------|-------------|
| screenshot | `screenshot.sh` | — | Capture screen → base64 PNG |
| cursor_position | `cursor_position.sh` | — | Get current mouse X,Y |
| mouse_move | `mouse_move.sh` | x y | Move mouse to coordinates |
| left_click | `click.sh` | x y left | Left click at coordinates |
| right_click | `click.sh` | x y right | Right click |
| middle_click | `click.sh` | x y middle | Middle click |
| double_click | `click.sh` | x y double | Double click |
| triple_click | `click.sh` | x y triple | Triple click (select line) |
| left_click_drag | `drag.sh` | x1 y1 x2 y2 | Drag from start to end |
| left_mouse_down | `mouse_down.sh` | — | Press mouse button |
| left_mouse_up | `mouse_up.sh` | — | Release mouse button |
| type | `type_text.sh` | "text" | Type text (50 char chunks, 12ms delay) |
| key | `key.sh` | "combo" | Press key (Return, ctrl+c, alt+F4) |
| hold_key | `hold_key.sh` | "key" secs | Hold key for duration |
| scroll | `scroll.sh` | dir amt [x y] | Scroll up/down/left/right |
| wait | `wait.sh` | seconds | Wait then screenshot |
| zoom | `zoom.sh` | x1 y1 x2 y2 | Cropped region screenshot |

## Workflow Pattern

1. **Screenshot** — Always start by seeing the screen
2. **Analyze** — Identify UI elements and coordinates
3. **Act** — Click, type, scroll
4. **Screenshot** — Verify result
5. **Repeat**

## Tips

- Screen is 1024x768, origin (0,0) at top-left
- Click to focus before typing in text fields
- Use `ctrl+End` to jump to page bottom in browsers
- Most actions auto-screenshot after 2 sec delay
- Long text is chunked (50 chars) with 12ms keystroke delay

## System Services

```bash
# Services auto-start on boot
sudo systemctl status virtual-desktop   # Xvfb on :99
sudo systemctl status xfce-desktop      # XFCE session

# Manual restart if needed
sudo systemctl restart virtual-desktop xfce-desktop
```

## Opening Applications

```bash
export DISPLAY=:99
chromium-browser --no-sandbox &    # Web browser
xfce4-terminal &                   # Terminal
thunar &                           # File manager
```

## Live Desktop Viewing (VNC)

Watch the desktop in real-time and optionally interact with it.

### Setup (one-time)

```bash
sudo apt install -y x11vnc novnc websockify
```

### Start VNC Services

```bash
# Start VNC server (shares display :99)
x11vnc -display :99 -forever -shared -nopw -listen localhost &

# Start noVNC web bridge (browser access)
websockify --web=/usr/share/novnc 6080 localhost:5900 &
```

Or use the helper script:
```bash
./scripts/vnc_start.sh
```

### Connect from Your Machine

**Option 1: Browser (noVNC)**
```bash
# SSH tunnel
ssh -L 6080:localhost:6080 your-server

# Open in browser
http://localhost:6080/vnc.html?autoconnect=true
```

**Option 2: VNC Client App**
```bash
# SSH tunnel
ssh -L 5900:localhost:5900 your-server

# Connect VNC client to localhost:5900
```

### SSH Config (recommended)

Add to `~/.ssh/config` for automatic tunneling:
```
Host your-server
  HostName your.server.ip
  User your-user
  LocalForward 6080 127.0.0.1:6080
  LocalForward 5900 127.0.0.1:5900
```

Then just `ssh your-server` and VNC is available.

### Stop VNC Services

```bash
./scripts/vnc_stop.sh
# or
pkill x11vnc; pkill websockify
```

## Requirements

System packages (install once):
```bash
sudo apt install -y xvfb xfce4 xfce4-terminal xdotool scrot imagemagick dbus-x11 chromium-browser x11vnc novnc websockify
```
