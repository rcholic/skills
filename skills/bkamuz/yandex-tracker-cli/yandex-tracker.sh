#!/usr/bin/env bash
set -e -o pipefail

# Yandex Tracker CLI
# Используйте: yandex-tracker <command> [args]
# Файл: yandex-tracker.sh (можно скопировать/переименовать в yandex-tracker)

# Приоритет 1: переменные окружения TOKEN и ORG_ID
# Приоритет 2: файл ~/.yandex-tracker-env (читается как key=value, без выполнения кода)

if [[ -z "${TOKEN}" || -z "${ORG_ID}" ]]; then
  CONFIG="${HOME}/.yandex-tracker-env"
  if [[ ! -f "$CONFIG" ]]; then
    echo "Error: Neither TOKEN/ORG_ID env vars nor config file $CONFIG found" >&2
    exit 1
  fi
  # Safe parse: only TOKEN and ORG_ID are read from KEY=value lines (no shell execution)
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%%#*}"
    line="${line#"${line%%[![:space:]]*}"}"
    line="${line%"${line##*[![:space:]]}"}"
    [[ -z "$line" ]] && continue
    if [[ "$line" =~ ^(TOKEN|ORG_ID)=(.+)$ ]]; then
      key="${BASH_REMATCH[1]}"
      value="${BASH_REMATCH[2]}"
      if [[ "$value" =~ ^\'(.*)\'$ ]]; then value="${BASH_REMATCH[1]}"; fi
      if [[ "$value" =~ ^\"(.*)\"$ ]]; then value="${BASH_REMATCH[1]}"; fi
      export "$key=$value"
    fi
  done < "$CONFIG"
fi

# Проверка, что TOKEN и ORG_ID определены
if [[ -z "$TOKEN" || -z "$ORG_ID" ]]; then
  echo "Error: TOKEN and ORG_ID must be set (via env or ~/.yandex-tracker-env)" >&2
  exit 1
fi

BASE="https://api.tracker.yandex.net/v2"
AUTH="Authorization: OAuth $TOKEN"
ORG="X-Org-Id: $ORG_ID"

urlencode() {
  local s="${1:-}"
  jq -nr --arg s "$s" '$s|@uri'
}

queues() {
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/queues" \
    | jq -r '.[] | "\(.key)\t\(.name)"'
}

queue_get() {
  local key="$1"
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/queues/$(urlencode "$key")"
}

queue_fields() {
  local key="$1"
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/queues/$(urlencode "$key")/fields"
}

issue_get() {
  local id="$1"
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/issues/$(urlencode "$id")"
}

issue_create() {
  local queue="$1"
  local summary="$2"
  local extra
  extra=$(cat)
  if [[ -z "$extra" ]]; then
    body="{\"queue\":\"$queue\",\"summary\":\"$summary\"}"
  else
    # Merge extra JSON fields into base object using jq
    base="{\"queue\":\"$queue\",\"summary\":\"$summary\"}"
    body=$(echo "$base" | jq --argjson extra "$extra" '. + $extra')
  fi
  curl -sS -X POST -H "$AUTH" -H "$ORG" -H "Content-Type: application/json" \
    -d "$body" "$BASE/issues/_new"
}

issue_update() {
  local id="$1"
  local payload
  payload=$(cat)
  curl -sS -X POST -H "$AUTH" -H "$ORG" -H "Content-Type: application/json" \
    -d "$payload" "$BASE/issues/$(urlencode "$id")"
}

issue_delete() {
  local id="$1"
  curl -sS -X DELETE -H "$AUTH" -H "$ORG" "$BASE/issues/$(urlencode "$id")"
}

issue_comment() {
  local id="$1"
  local text="$2"
  curl -sS -X POST -H "$AUTH" -H "$ORG" -H "Content-Type: application/json" \
    -d "{\"text\":\"$text\"}" "$BASE/issues/$(urlencode "$id")/comments"
}

issue_transitions() {
  local id="$1"
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/issues/$(urlencode "$id")/transitions"
}

issue_close() {
  local id="$1"
  local resolution="$2"
  curl -sS -X POST -H "$AUTH" -H "$ORG" -H "Content-Type: application/json" \
    -d "{\"resolution\":\"$resolution\"}" "$BASE/issues/$(urlencode "$id")/_close"
}

issue_worklog() {
  local id="$1"
  local duration="$2"
  local comment="${3:-}"
  local body="{\"duration\":\"$duration\"}"
  if [[ -n "$comment" ]]; then
    body="{\"duration\":\"$duration\",\"comment\":\"$comment\"}"
  fi
  curl -sS -X POST -H "$AUTH" -H "$ORG" -H "Content-Type: application/json" \
    -d "$body" "$BASE/issues/$(urlencode "$id")/_worklog"
}

# ---- NEW: Attachments ----
issue_attachments() {
  local id="$1"
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/issues/$(urlencode "$id")/attachments"
}

attachment_download() {
  local issue_id="$1"
  local file_id="$2"
  local output="${3:-/dev/stdout}"
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/issues/$(urlencode "$issue_id")/attachments/$(urlencode "$file_id")" -o "$output"
}

attachment_upload() {
  local issue_id="$1"
  local filepath="$2"
  local comment="${3:-}"
  local file_name
  file_name=$(basename "$filepath")
  local form_data
  if [[ -n "$comment" ]]; then
    form_data="comment=$comment"
  else
    form_data=""
  fi
  curl -sS -X POST -H "$AUTH" -H "$ORG" \
    -F "file=@$filepath;filename=$file_name" \
    ${form_data:+-F "$form_data"} \
    "$BASE/issues/$(urlencode "$issue_id")/attachments"
}

# ---- NEW: Comments edit/delete ----
issue_comment_edit() {
  local issue_id="$1"
  local comment_id="$2"
  local new_text="$3"
  curl -sS -X POST -H "$AUTH" -H "$ORG" -H "Content-Type: application/json" \
    -d "{\"text\":\"$new_text\"}" "$BASE/issues/$(urlencode "$issue_id")/comments/$(urlencode "$comment_id")"
}

issue_comment_delete() {
  local issue_id="$1"
  local comment_id="$2"
  curl -sS -X DELETE -H "$AUTH" -H "$ORG" "$BASE/issues/$(urlencode "$issue_id")/comments/$(urlencode "$comment_id")"
}

# ---- NEW: Sprints ----
sprints_list() {
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/sprints"
}

sprint_get() {
  local id="$1"
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/sprints/$(urlencode "$id")"
}

sprint_issues() {
  local id="$1"
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/sprints/$(urlencode "$id")/issues"
}

# ---- NEW: Search issues via YQL ----
issues_search() {
  # Expect YQL query as JSON via stdin, e.g.:
  #   {"query":"Queue = BIMLAB AND Status = Open","limit":50}
  local payload
  payload=$(cat)
  curl -sS -X POST -H "$AUTH" -H "$ORG" -H "Content-Type: application/json" \
    -d "$payload" "$BASE/issues/_search"
}

# ---- NEW: Projects ----
projects_list() {
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/projects"
}

project_get() {
  local id="$1"
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/projects/$(urlencode "$id")"
}

project_issues() {
  local id="$1"
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/projects/$(urlencode "$id")/issues"
}

# ---- NEW: Reference data (optional but useful) ----
users_list() {
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/users"
}

statuses_list() {
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/statuses"
}

resolutions_list() {
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/resolutions"
}

issue_types_list() {
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/issue-types"
}

case "$1" in
  queues) queues ;;
  queue-get) queue_get "$2" ;;
  queue-fields) queue_fields "$2" ;;
  issue-get) issue_get "$2" ;;
  issue-create) shift; queue="$1"; summary="$2"; issue_create "$queue" "$summary" ;;
  issue-update) issue_update "$2" ;;
  issue-delete) issue_delete "$2" ;;
  issue-comment) shift; issue_comment "$1" "$2" ;;
  issue-comment-edit) shift; issue_comment_edit "$1" "$2" "$3" ;;
  issue-comment-delete) shift; issue_comment_delete "$1" "$2" ;;
  issue-transitions) issue_transitions "$2" ;;
  issue-close) shift; issue_close "$1" "$2" ;;
  issue-worklog) shift; issue_worklog "$1" "$2" "$3" ;;
  issue-attachments) issue_attachments "$2" ;;
  attachment-download) shift; attachment_download "$1" "$2" "$3" ;;
  attachment-upload) shift; attachment_upload "$1" "$2" "$3" ;;
  issues-search) issues_search ;;
  projects-list) projects_list ;;
  project-get) project_get "$2" ;;
  project-issues) project_issues "$2" ;;
  sprints-list) sprints_list ;;
  sprint-get) sprint_get "$2" ;;
  sprint-issues) sprint_issues "$2" ;;
  users-list) users_list ;;
  statuses-list) statuses_list ;;
  resolutions-list) resolutions_list ;;
  issue-types-list) issue_types_list ;;
  *) echo "Usage: $0 {queues|queue-get <key>|queue-fields <key>|issue-get <id>|issue-create <queue> <summary>|issue-update <id>|issue-delete <id>|issue-comment <id> <text>|issue-comment-edit <id> <comment-id> <new-text>|issue-comment-delete <id> <comment-id>|issue-transitions <id>|issue-close <id> <resolution>|issue-worklog <id> <duration> [comment]|issue-attachments <id>|attachment-download <issue-id> <fileId> [output]|attachment-upload <issue-id> <filepath> [comment]|issues-search|projects-list|project-get <id>|project-issues <id>|sprints-list|sprint-get <id>|sprint-issues <id>|users-list|statuses-list|resolutions-list|issue-types-list}" >&2; exit 1 ;;
esac
