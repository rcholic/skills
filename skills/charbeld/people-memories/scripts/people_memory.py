#!/usr/bin/env python3
"""People Memories

A lightweight JSON-backed store for informal notes about people.

Enhancements over the original:
- Atomic writes to prevent store corruption.
- Faster, cleaner keyword indexing (stopwords + min length).
- Partial keyword search fallback.
- Note IDs for edit/delete operations.
- Person rename + merge.
- Improved event date storage: month/day always, year optional.
"""

import argparse
import calendar
import json
import os
import re
import tempfile
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path

try:
    from dateutil.parser import ParserError, parse
except Exception:  # pragma: no cover
    ParserError = Exception
    parse = None

# Allow override for portability/testing
PEOPLE_FILE = os.path.expanduser(os.getenv("PEOPLE_MEMORIES_STORE", "~/.clawdbot/people-memory.json"))

WORD_RE = re.compile(r"\b[\w']+\b")
YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2}|21\d{2})\b")

# Keep indexing lightweight
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "from",
    "has",
    "have",
    "he",
    "her",
    "his",
    "i",
    "in",
    "is",
    "it",
    "its",
    "me",
    "my",
    "of",
    "on",
    "or",
    "our",
    "she",
    "that",
    "the",
    "their",
    "them",
    "they",
    "this",
    "to",
    "was",
    "we",
    "were",
    "with",
    "you",
    "your",
}

EVENT_TYPES = {"birthday", "anniversary"}
EVENT_KEYWORDS = {
    "birthday": {
        "tags": {"birthday", "birthdays", "birthdate", "bday"},
        "text": ["birthday", "bday", "born", "born on"],
    },
    "anniversary": {
        "tags": {"anniversary", "anniv", "wedding"},
        "text": ["anniversary", "wedding", "married on"],
    },
}


def normalize_person_key(name: str) -> str:
    return name.strip().lower()


def utc_now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def find_event_type(note, tags, override=None):
    if override and override.lower() in EVENT_TYPES:
        return override.lower()
    normalized_tags = {t.lower() for t in tags if t}
    note_lower = (note or "").lower()
    for event_type, criteria in EVENT_KEYWORDS.items():
        if normalized_tags & criteria["tags"]:
            return event_type
        if any(keyword in note_lower for keyword in criteria["text"]):
            return event_type
    return None


def parse_event_components(text, reference=None):
    """Parse month/day and optional year.

    We always try to extract a usable month/day. Year is kept only if it appears
    explicitly (e.g., "1992", "2020") or is supplied in --event-date.

    Returns: (month:int, day:int, year:int|None) or None
    """
    if not text or parse is None:
        return None

    reference = reference or datetime.utcnow()
    # Anchor defaults in a neutral year to avoid inferring a meaningful year.
    default = datetime(2000, 1, 1)
    try:
        parsed = parse(text, fuzzy=True, default=default)
    except (ParserError, ValueError, OverflowError, TypeError):
        return None

    month = getattr(parsed, "month", None)
    day = getattr(parsed, "day", None)
    if not month or not day:
        return None

    # Only keep year if explicitly present in the input.
    year = None
    year_match = YEAR_RE.search(text)
    if year_match:
        try:
            year = int(year_match.group(1))
        except ValueError:
            year = None

    # For cases like "next May 5" dateutil may infer a year; we still ignore
    # unless explicitly written.
    return (int(month), int(day), year)


def build_event_metadata(event_type, month, day, year, note, source):
    payload = {
        "type": event_type,
        "month": month,
        "day": day,
        "note": note.strip(),
        "source": source,
    }
    if year is not None:
        payload["year"] = year
        try:
            payload["date"] = date(year, month, day).isoformat()
        except ValueError:
            pass
    return payload


def detect_event_metadata(note, tags, provided_type=None, provided_date=None, source="chat"):
    event_type = find_event_type(note, tags, provided_type)
    if not event_type:
        return None

    components = parse_event_components(provided_date or note)
    if not components:
        return None
    month, day, year = components
    return build_event_metadata(event_type, month, day, year, note, source)


def load_store():
    if os.path.exists(PEOPLE_FILE):
        with open(PEOPLE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"people": {}, "index": {}, "version": 2}

    # Migrations/backfills
    data.setdefault("people", {})
    data.setdefault("index", {})
    data.setdefault("version", 2)

    # Ensure note IDs exist (for edit/delete)
    changed = False
    for person_key, entry in data.get("people", {}).items():
        notes = entry.get("notes", [])
        for n in notes:
            if "id" not in n:
                n["id"] = str(uuid.uuid4())
                changed = True
        # Normalize display name presence
        if "displayName" not in entry:
            entry["displayName"] = person_key
            changed = True

    if changed:
        rebuild_index(data)
        save_store(data)

    return data


def save_store(data):
    os.makedirs(os.path.dirname(PEOPLE_FILE), exist_ok=True)

    # Atomic write to avoid corrupting the store on crash/interruption
    dirpath = os.path.dirname(PEOPLE_FILE) or "."
    fd, tmp_path = tempfile.mkstemp(prefix="people-memory.", suffix=".tmp", dir=dirpath)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, PEOPLE_FILE)
    finally:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except OSError:
            pass


def ensure_person_entry(store, person_key, display_name):
    people = store["people"]
    if person_key not in people:
        people[person_key] = {"displayName": display_name.strip(), "notes": [], "events": {}}
    else:
        people[person_key]["displayName"] = display_name.strip()
        people[person_key].setdefault("notes", [])
        people[person_key].setdefault("events", {})
    return people[person_key]


def extract_keywords(note, tags):
    keywords = set(t.strip().lower() for t in tags if t and t.strip())
    for w in WORD_RE.findall(note or ""):
        wl = w.lower().strip("'")
        if len(wl) < 3:
            continue
        if wl in STOPWORDS:
            continue
        keywords.add(wl)
    return keywords


def rebuild_index(store):
    index = {}
    for person_key, entry in store.get("people", {}).items():
        for n in entry.get("notes", []):
            tags = n.get("tags", [])
            note = n.get("note", "")
            keywords = extract_keywords(note, tags)
            for kw in keywords:
                s = set(index.get(kw, []))
                s.add(person_key)
                index[kw] = sorted(s)
    store["index"] = index


def add_note(person, note, source, tags, event_type=None, event_date=None):
    store = load_store()
    person_key = normalize_person_key(person)
    entry = ensure_person_entry(store, person_key, person.strip())

    timestamp = utc_now_iso()
    clean_tags = [t.strip().lower() for t in tags if t.strip()]

    note_entry = {
        "id": str(uuid.uuid4()),
        "timestamp": timestamp,
        "note": note.strip(),
        "source": source,
        "tags": clean_tags,
    }

    event = detect_event_metadata(note, clean_tags, provided_type=event_type, provided_date=event_date, source=source)
    if event:
        note_entry["event"] = event
        entry.setdefault("events", {})[event["type"]] = {**event, "updatedAt": timestamp}

    entry["notes"].append(note_entry)

    # Update index (fast path for inserts)
    keywords = extract_keywords(note, clean_tags)
    idx = store.setdefault("index", {})
    for kw in keywords:
        s = set(idx.get(kw, []))
        s.add(person_key)
        idx[kw] = sorted(s)

    store["version"] = max(int(store.get("version", 2)), 2)
    save_store(store)
    print(f"Saved note for {entry['displayName']}: {note}")


def _get_person_entry(store, person):
    person_key = normalize_person_key(person)
    entry = store.get("people", {}).get(person_key)
    return person_key, entry


def recall(person, limit):
    store = load_store()
    person_key, entry = _get_person_entry(store, person)
    if not entry or not entry.get("notes"):
        print(f"No notes found for {person.strip()}.")
        return

    notes = entry["notes"]
    # Show newest first
    for idx, n in enumerate(reversed(notes[-limit:]), 1):
        tags = f" [tags: {', '.join(n.get('tags', []))}]" if n.get("tags") else ""
        print(f"{idx}. {n['note']} (id: {n.get('id')}, source: {n.get('source')}, {n.get('timestamp')}){tags}")


def summarize(person):
    store = load_store()
    _, entry = _get_person_entry(store, person)
    if not entry or not entry.get("notes"):
        print(f"No notes found for {person.strip()}.")
        return

    notes = entry["notes"]
    last_updated = notes[-1]["timestamp"]

    tag_counts = {}
    for n in notes:
        for tag in n.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    top_tags = sorted(tag_counts, key=lambda k: (-tag_counts[k], k))[:5]

    print(f"Person: {entry.get('displayName')}")
    print(f"Notes count: {len(notes)}")
    print(f"Last updated: {last_updated}")
    if top_tags:
        print(f"Top tags: {', '.join(top_tags)}")

    # Events summary
    events = entry.get("events", {})
    if events:
        print("Events:")
        for etype, e in events.items():
            y = e.get("year")
            y_str = f"/{y}" if y else ""
            print(f"- {etype}: {e.get('month')}/{e.get('day')}{y_str} (updated {e.get('updatedAt')})")

    print("Recent notes:")
    for n in notes[-3:]:
        print(f"- {n['note']} ({n['timestamp']})")


def search(query, limit):
    store = load_store()
    query_lower = query.lower()
    index = store.get("index", {})

    # Exact keyword hits first
    person_keys = index.get(query_lower, [])
    if person_keys:
        for idx, key in enumerate(person_keys[:limit], 1):
            person = store["people"][key]
            latest = person["notes"][-1]
            print(f"{idx}. {person['displayName']}: {latest['note']} ({latest['timestamp']})")
        return

    # Partial keyword match over index
    candidate_people = set()
    for kw, keys in index.items():
        if query_lower in kw:
            candidate_people.update(keys)

    if candidate_people:
        results = []
        for key in candidate_people:
            person = store["people"][key]
            latest = person["notes"][-1]
            results.append((person["displayName"], latest["note"], latest["timestamp"]))
        results.sort(key=lambda x: x[0].lower())
        for idx, (name, note, ts) in enumerate(results[:limit], 1):
            print(f"{idx}. {name}: {note} ({ts})")
        return

    # Last resort: scan notes
    matches = []
    for _, person in store.get("people", {}).items():
        for n in person.get("notes", []):
            if query_lower in (n.get("note", "").lower()):
                matches.append((person["displayName"], n))

    if not matches:
        print("No entries match that query.")
        return

    for idx, (person, n) in enumerate(matches[:limit], 1):
        tags = f" [tags: {', '.join(n.get('tags', []))}]" if n.get("tags") else ""
        print(f"{idx}. {person}: {n.get('note')} ({n.get('timestamp')}){tags}")


def list_people():
    store = load_store()
    people = sorted(store.get("people", {}).items(), key=lambda x: x[1].get("displayName", x[0]).lower())
    if not people:
        print("No people stored yet.")
        return

    for _, entry in people:
        notes = entry.get("notes", [])
        updated = notes[-1]["timestamp"] if notes else "n/a"
        print(f"- {entry.get('displayName')} ({len(notes)} notes, updated {updated})")


def export_person(person, fmt, out_path):
    store = load_store()
    _, entry = _get_person_entry(store, person)
    if not entry or not entry.get("notes"):
        print(f"No notes found for {person.strip()}.")
        return

    notes = entry["notes"]
    if fmt == "md":
        lines = [f"# {entry['displayName']}\n", f"*Updated {notes[-1]['timestamp']}*\n"]
        for n in notes:
            tags = f" (tags: {', '.join(n.get('tags', []))})" if n.get("tags") else ""
            lines.append(f"- {n['note']}{tags} [{n['timestamp']}] (id: {n.get('id')})\n")
        out = "".join(lines)
    else:
        out = json.dumps(entry, ensure_ascii=False, indent=2)

    if out_path:
        Path(out_path).write_text(out, encoding="utf-8")
        print(f"Exported {entry['displayName']} to {out_path}.")
    else:
        print(out)


def next_occurrence(event, reference_date):
    month = event.get("month")
    day = event.get("day")
    if not month or not day:
        return None

    for year in (reference_date.year, reference_date.year + 1):
        if month == 2 and day == 29 and not calendar.isleap(year):
            continue
        try:
            candidate = date(year, month, day)
        except ValueError:
            continue
        if candidate >= reference_date:
            return candidate
    return None


def gather_upcoming_events(store, reference_date, lookahead=0, include_types=None):
    results = []
    people = store.get("people", {})
    for entry in people.values():
        display = entry.get("displayName", "Unknown")
        events = entry.get("events", {})
        for event_type, data in events.items():
            if include_types and event_type not in include_types:
                continue

            occurrence = next_occurrence(data, reference_date)
            if not occurrence:
                continue

            days_until = (occurrence - reference_date).days
            if 0 <= days_until <= lookahead:
                event_year = data.get("year")
                age = None
                if event_type == "birthday" and event_year and event_year <= occurrence.year:
                    age = occurrence.year - event_year
                results.append(
                    {
                        "person": display,
                        "event_type": event_type,
                        "occurrence": occurrence,
                        "note": data.get("note"),
                        "age": age,
                        "days_until": days_until,
                    }
                )

    results.sort(key=lambda e: (e["days_until"], e["person"].lower()))
    return results


def format_reminder_message(events, reference_date, lookahead, fmt="text"):
    if not events:
        return f"No birthday or anniversary reminders for {reference_date.strftime('%B %d, %Y')}"

    if lookahead == 0:
        header = f"People memories reminders for {reference_date.strftime('%B %d, %Y')}:"
    else:
        end_date = reference_date + timedelta(days=lookahead)
        header = (
            f"People memories reminders from {reference_date.strftime('%b %d')}"
            f" through {end_date.strftime('%b %d')}:"
        )

    lines = []
    for event in events:
        date_str = event["occurrence"].strftime("%b %d")
        suffix = ""
        if event["event_type"] == "birthday" and event["age"]:
            suffix = f" (turning {event['age']})"
        note_info = f": {event['note']}" if event.get("note") else ""
        lines.append(f"- {event['person']} ({event['event_type'].title()}) on {date_str}{suffix}{note_info}")

    if fmt == "message":
        return "\n".join(lines)
    return "\n".join([header] + lines)


def run_reminders(reference_offset=0, lookahead=0, type_filter="all", fmt="text"):
    store = load_store()
    reference_date = datetime.utcnow().date() + timedelta(days=reference_offset)
    types = None if type_filter == "all" else [type_filter]
    events = gather_upcoming_events(store, reference_date, lookahead, types)
    message = format_reminder_message(events, reference_date, lookahead, fmt)
    print(message)


def find_note(entry, note_id=None, idx=None):
    notes = entry.get("notes", [])
    if note_id:
        for i, n in enumerate(notes):
            if n.get("id") == note_id:
                return i, n
        return None, None

    if idx is not None:
        # idx is 1-based, newest-first
        if idx <= 0:
            return None, None
        newest_first = list(reversed(notes))
        if idx > len(newest_first):
            return None, None
        n = newest_first[idx - 1]
        # translate to original index
        original_index = notes.index(n)
        return original_index, n

    return None, None


def delete_note(person, note_id=None, idx=None):
    store = load_store()
    person_key, entry = _get_person_entry(store, person)
    if not entry or not entry.get("notes"):
        print(f"No notes found for {person.strip()}.")
        return

    i, n = find_note(entry, note_id=note_id, idx=idx)
    if n is None:
        print("Note not found (check --note-id or --idx).")
        return

    deleted = entry["notes"].pop(i)

    # Rebuild index + events (safe and simple)
    entry["events"] = {}
    for note in entry["notes"]:
        if "event" in note:
            ev = note["event"]
            entry["events"][ev["type"]] = {**ev, "updatedAt": note.get("timestamp")}

    rebuild_index(store)
    save_store(store)
    print(f"Deleted note for {entry['displayName']}: {deleted.get('note')}")


def edit_note(person, note_id=None, idx=None, new_note=None, new_tags=None):
    store = load_store()
    _, entry = _get_person_entry(store, person)
    if not entry or not entry.get("notes"):
        print(f"No notes found for {person.strip()}.")
        return

    i, n = find_note(entry, note_id=note_id, idx=idx)
    if n is None:
        print("Note not found (check --note-id or --idx).")
        return

    if new_note is not None:
        n["note"] = new_note.strip()
    if new_tags is not None:
        n["tags"] = [t.strip().lower() for t in new_tags if t.strip()]

    # Re-detect event metadata for this note after edits
    clean_tags = n.get("tags", [])
    event = detect_event_metadata(n.get("note", ""), clean_tags, provided_type=None, provided_date=None, source=n.get("source", "chat"))
    if event:
        n["event"] = event
    else:
        n.pop("event", None)

    # Rebuild events index for person
    entry["events"] = {}
    for note in entry["notes"]:
        if "event" in note:
            ev = note["event"]
            entry["events"][ev["type"]] = {**ev, "updatedAt": note.get("timestamp")}

    rebuild_index(store)
    save_store(store)
    print(f"Updated note for {entry['displayName']} (id: {n.get('id')})")


def rename_person(old, new):
    store = load_store()
    old_key = normalize_person_key(old)
    new_key = normalize_person_key(new)

    if old_key not in store.get("people", {}):
        print(f"Person not found: {old}")
        return

    if new_key in store.get("people", {}) and new_key != old_key:
        print(f"Target person already exists: {new}")
        return

    entry = store["people"].pop(old_key)
    entry["displayName"] = new.strip()
    store["people"][new_key] = entry

    rebuild_index(store)
    save_store(store)
    print(f"Renamed person '{old}' -> '{new}'")


def merge_person(source_person, target_person):
    store = load_store()
    src_key = normalize_person_key(source_person)
    tgt_key = normalize_person_key(target_person)

    if src_key not in store.get("people", {}):
        print(f"Source person not found: {source_person}")
        return
    if tgt_key not in store.get("people", {}):
        print(f"Target person not found: {target_person}")
        return

    src = store["people"][src_key]
    tgt = store["people"][tgt_key]

    tgt.setdefault("notes", [])
    tgt.setdefault("events", {})

    # Move notes (keep timestamps; de-dupe by note id)
    existing_ids = {n.get("id") for n in tgt.get("notes", [])}
    moved = 0
    for n in src.get("notes", []):
        if n.get("id") not in existing_ids:
            tgt["notes"].append(n)
            moved += 1

    # Sort notes by timestamp (best-effort)
    def ts_key(n):
        return n.get("timestamp", "")

    tgt["notes"].sort(key=ts_key)

    # Rebuild target events from notes
    tgt["events"] = {}
    for n in tgt["notes"]:
        if "event" in n:
            ev = n["event"]
            tgt["events"][ev["type"]] = {**ev, "updatedAt": n.get("timestamp")}

    # Remove source
    store["people"].pop(src_key, None)

    rebuild_index(store)
    save_store(store)
    print(f"Merged '{source_person}' -> '{target_person}' (moved {moved} notes)")


def main():
    parser = argparse.ArgumentParser(description="Store and recall informal notes about people.")
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    remember = subparsers.add_parser("remember", help="Save a note about someone.")
    remember.add_argument("--person", required=True)
    remember.add_argument("--note", required=True)
    remember.add_argument("--source", default="chat")
    remember.add_argument("--event-type", choices=["birthday", "anniversary"], help="Optional event type to associate with this note.")
    remember.add_argument("--event-date", help="Optional event date (natural language) for birthdays or anniversaries.")
    remember.add_argument("--tags", default="", help="Comma-separated keywords.")

    recall_parser = subparsers.add_parser("recall", help="Show latest notes for a person.")
    recall_parser.add_argument("--person", required=True)
    recall_parser.add_argument("--limit", type=int, default=5)

    summarize_parser = subparsers.add_parser("summarize", help="Summarize notes for a person.")
    summarize_parser.add_argument("--person", required=True)

    search_parser = subparsers.add_parser("search", help="Search notes by keyword.")
    search_parser.add_argument("--query", required=True)
    search_parser.add_argument("--limit", type=int, default=5)

    export_parser = subparsers.add_parser("export", help="Export a person’s notes.")
    export_parser.add_argument("--person", required=True)
    export_parser.add_argument("--format", choices=["md", "json"], default="md")
    export_parser.add_argument("--out", help="Optional output file path.")

    subparsers.add_parser("list", help="List all people tracked.")

    remind_parser = subparsers.add_parser("reminders", help="List upcoming birthday/anniversary reminders.")
    remind_parser.add_argument("--days", type=int, default=0, help="Days from today to anchor the reminder window.")
    remind_parser.add_argument("--window", type=int, default=0, help="How many days forward (inclusive) to check for events.")
    remind_parser.add_argument("--event-types", choices=["all", "birthday", "anniversary"], default="all")
    remind_parser.add_argument("--format", choices=["text", "message"], default="text")

    del_parser = subparsers.add_parser("delete-note", help="Delete a note for a person.")
    del_parser.add_argument("--person", required=True)
    del_group = del_parser.add_mutually_exclusive_group(required=True)
    del_group.add_argument("--note-id", help="Exact note id (recommended).")
    del_group.add_argument("--idx", type=int, help="1-based index in newest-first order (use recall to view).")

    edit_parser = subparsers.add_parser("edit-note", help="Edit a note for a person.")
    edit_parser.add_argument("--person", required=True)
    edit_group = edit_parser.add_mutually_exclusive_group(required=True)
    edit_group.add_argument("--note-id", help="Exact note id (recommended).")
    edit_group.add_argument("--idx", type=int, help="1-based index in newest-first order (use recall to view).")
    edit_parser.add_argument("--note", help="New note text.")
    edit_parser.add_argument("--tags", default=None, help="New comma-separated tags.")

    rename_parser = subparsers.add_parser("rename-person", help="Rename a person key + display name.")
    rename_parser.add_argument("--from", dest="old", required=True)
    rename_parser.add_argument("--to", dest="new", required=True)

    merge_parser = subparsers.add_parser("merge-person", help="Merge one person into another.")
    merge_parser.add_argument("--from", dest="source", required=True)
    merge_parser.add_argument("--to", dest="target", required=True)

    args = parser.parse_args()

    if args.cmd == "remember":
        tags = args.tags.split(",") if args.tags else []
        add_note(args.person, args.note, args.source, tags, event_type=args.event_type, event_date=args.event_date)
    elif args.cmd == "recall":
        recall(args.person, args.limit)
    elif args.cmd == "summarize":
        summarize(args.person)
    elif args.cmd == "search":
        search(args.query, args.limit)
    elif args.cmd == "export":
        export_person(args.person, args.format, args.out)
    elif args.cmd == "list":
        list_people()
    elif args.cmd == "reminders":
        run_reminders(reference_offset=args.days, lookahead=args.window, type_filter=args.event_types, fmt=args.format)
    elif args.cmd == "delete-note":
        delete_note(args.person, note_id=args.note_id, idx=args.idx)
    elif args.cmd == "edit-note":
        tags = args.tags.split(",") if args.tags is not None else None
        edit_note(args.person, note_id=args.note_id, idx=args.idx, new_note=args.note, new_tags=tags)
    elif args.cmd == "rename-person":
        rename_person(args.old, args.new)
    elif args.cmd == "merge-person":
        merge_person(args.source, args.target)


if __name__ == "__main__":
    main()
