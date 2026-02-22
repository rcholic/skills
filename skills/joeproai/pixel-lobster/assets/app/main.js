const { app, BrowserWindow, screen, desktopCapturer, session, globalShortcut } = require('electron');
const path = require('path');
const fs = require('fs');

app.commandLine.appendSwitch('disable-gpu-shader-disk-cache');

// Load config
let config = {};
try {
  config = JSON.parse(fs.readFileSync(path.join(__dirname, 'config.json'), 'utf8'));
} catch (e) {
  console.log('No config.json found, using defaults');
}

const AUDIO_MODE = config.audioMode || 'system';
const MONITOR = config.monitor || 'primary';

let win;

function getDisplay() {
  const displays = screen.getAllDisplays();
  const primary = screen.getPrimaryDisplay();

  if (MONITOR === 'primary') return primary;
  if (MONITOR === 'secondary') return displays.find(d => d.id !== primary.id) || primary;

  // Monitor by index (0-based)
  const idx = parseInt(MONITOR);
  if (!isNaN(idx) && displays[idx]) return displays[idx];

  // Monitor by position keyword
  if (MONITOR === 'left') return displays.reduce((a, b) => a.bounds.x < b.bounds.x ? a : b);
  if (MONITOR === 'right') return displays.reduce((a, b) => a.bounds.x > b.bounds.x ? a : b);

  return primary;
}

function createWindow() {
  const display = getDisplay();
  const { width, height } = display.bounds;

  win = new BrowserWindow({
    width: width,
    height: height,
    x: display.bounds.x,
    y: display.bounds.y,
    frame: false,
    transparent: true,
    alwaysOnTop: config.alwaysOnTop !== false,
    resizable: true,
    skipTaskbar: false,
    hasShadow: false,
    focusable: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // Auto-approve permissions
  session.defaultSession.setPermissionRequestHandler((webContents, permission, callback) => {
    callback(true);
  });

  // Auto-select primary screen with system audio loopback (for system audio mode)
  session.defaultSession.setDisplayMediaRequestHandler((request, callback) => {
    desktopCapturer.getSources({ types: ['screen'] }).then((sources) => {
      callback({ video: sources[0], audio: 'loopback' });
    });
  });

  // Pass config to renderer via URL params
  const params = new URLSearchParams({
    audioMode: AUDIO_MODE,
    ttsUrl: config.ttsUrl || 'http://127.0.0.1:8787',
    ttsEnvelopePath: config.ttsEnvelopePath || '/audio/envelope',
    ttsPollIdleMs: config.ttsPollIdleMs || 500,
    ttsPollActiveMs: config.ttsPollActiveMs || 45,
    ttsPlayStartOffsetMs: config.ttsPlayStartOffsetMs || 1100,
    lobsterScale: config.lobsterScale || 4,
    swimEnabled: config.swimEnabled !== false,
    swimSpeed: config.swimSpeed || 1.0,
  });

  win.loadFile(path.join(__dirname, 'lobster.html'), { query: Object.fromEntries(params) });

  // Start interactive (draggable), F9 toggles click-through
  let clickThrough = config.clickThrough || false;
  win.setIgnoreMouseEvents(clickThrough, { forward: true });

  globalShortcut.register('F9', () => {
    clickThrough = !clickThrough;
    if (win) {
      win.setIgnoreMouseEvents(clickThrough, { forward: true });
      console.log('Click-through:', clickThrough);
    }
  });

  globalShortcut.register('F12', () => {
    if (win) win.webContents.toggleDevTools();
  });

  win.on('closed', () => { win = null; });
}

app.whenReady().then(createWindow);
app.on('window-all-closed', () => app.quit());
