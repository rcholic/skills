import { execFile } from "node:child_process";

// Resolve the script relative to this extension file (works regardless of cwd)
const SCRIPT_URL = new URL("../../scripts/people_memory.py", import.meta.url);
const SCRIPT_PATH = SCRIPT_URL.pathname.startsWith("/") && process.platform === "win32"
  ? decodeURIComponent(SCRIPT_URL.pathname.slice(1)).replace(/\//g, "\\")
  : decodeURIComponent(SCRIPT_URL.pathname);

// Allow explicit interpreter override (useful on Windows)
const PYTHON_CANDIDATES = [
  process.env.PEOPLE_MEMORIES_PYTHON,
  "python3",
  "python",
  "py",
].filter(Boolean);

// Matches common voice patterns:
// - "remember Alex likes cats"
// - "remember Alex: likes cats"
// - "remember that Alex likes cats"
// - "remember for Alex likes cats"
const REMEMBER_PATTERN = /\bremember\b\s+(?:that\s+|for\s+)?(?<person>[\p{L}][\p{L}'\-]*(?:\s+[\p{L}][\p{L}'\-]*)*)\s*[:\-–—]?\s+(?<note>.+)$/iu;

function execPython(args, cb) {
  let i = 0;
  const tryNext = () => {
    if (i >= PYTHON_CANDIDATES.length) {
      cb?.(new Error("No working python interpreter found (tried: " + PYTHON_CANDIDATES.join(", ") + ")"));
      return;
    }
    const bin = PYTHON_CANDIDATES[i++];
    execFile(bin, args, { windowsHide: true }, (err) => {
      // If interpreter is missing, try the next candidate.
      if (err && (err.code === "ENOENT" || /not recognized|ENOENT/i.test(String(err.message)))) {
        return tryNext();
      }
      cb?.(err);
    });
  };
  tryNext();
}

function runRemember(person, note, source = "voice") {
  const args = [SCRIPT_PATH, "remember", "--person", person, "--note", note, "--source", source];
  execPython(args, (err) => {
    if (err) console.error("people-memories remember failed", err);
  });
}

export default async function registerPeopleMemories(api) {
  const handle = async ({ text, source }) => {
    if (!text) return;
    const match = text.match(REMEMBER_PATTERN);
    if (!match?.groups) return;

    const person = match.groups.person.trim();
    const note = match.groups.note.trim();
    runRemember(person, note, source || "voice");
    api?.log?.("People memory noted", person, note);
  };

  api?.on?.("voice-chat:transcript", handle);
  return {
    name: "people-memories",
    unload: () => {
      api?.off?.("voice-chat:transcript", handle);
    },
  };
}
