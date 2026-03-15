#!/usr/bin/env bash
set -euo pipefail

CUTOFF_DAYS="${CUTOFF_DAYS:-365}"
BATCH_SIZE="${BATCH_SIZE:-20}"
RATE_THRESHOLD="${RATE_THRESHOLD:-100}"
SLEEP_PAD_SECONDS="${SLEEP_PAD_SECONDS:-5}"
MAX_RETRIES="${MAX_RETRIES:-5}"

ACTIVE_FILE="active-following.txt"
INACTIVE_FILE="inactive-following.txt"
SKIPPED_FILE="skipped-users.txt"
CSV_FILE="following-activity.csv"
RAW_FILE="all-results.txt"

CACHE_DIR="graphql-batches"
FOLLOW_CACHE_FILE="$CACHE_DIR/following-logins.txt"
FOLLOW_CURSOR_FILE="$CACHE_DIR/following-cursor.txt"

mkdir -p "$CACHE_DIR"

touch "$ACTIVE_FILE" "$INACTIVE_FILE" "$SKIPPED_FILE" "$RAW_FILE" "$FOLLOW_CACHE_FILE"

if [[ ! -f "$CSV_FILE" ]]; then
    printf 'login,kind,created_at,last_pushed_at,followers,public_repos,primary_language,status\n' > "$CSV_FILE"
fi

cutoff_epoch="$(date -u -d "$CUTOFF_DAYS days ago" +%s)"

echo "Checking GitHub authentication..."
gh auth status >/dev/null

csv_escape() {
    printf '%s' "$1" | sed 's/"/""/g; s/.*/"&"/'
}

classify_status() {
    local pushed="$1"
    local epoch

    if [[ -z "$pushed" || "$pushed" == "null" ]]; then
        echo "INACTIVE"
        return
    fi

    epoch="$(date -u -d "$pushed" +%s 2>/dev/null || echo 0)"

    if [[ "$epoch" -ge "$cutoff_epoch" ]]; then
        echo "ACTIVE"
    else
        echo "INACTIVE"
    fi
}

sleep_until_reset() {
    local remaining="$1"
    local reset="$2"
    local now reset_epoch sleep_for

    if [[ "$remaining" =~ ^[0-9]+$ ]] && (( remaining < RATE_THRESHOLD )); then
        now="$(date -u +%s)"
        reset_epoch="$(date -u -d "$reset" +%s)"
        sleep_for=$(( reset_epoch - now + SLEEP_PAD_SECONDS ))

        if (( sleep_for > 0 )); then
            echo "Sleeping $sleep_for seconds until rate reset..."
            sleep "$sleep_for"
        fi
    fi
}

graphql_request() {
    local query="$1"
    local outfile="$2"
    local label="$3"
    local tmp="${outfile}.tmp"
    local err="${outfile}.err"
    local attempt sleep_time

    for ((attempt=1; attempt<=MAX_RETRIES; attempt+=1)); do
        echo "  $label attempt $attempt"

        if gh api graphql -f query="$query" > "$tmp" 2> "$err"; then
            if jq -e . >/dev/null 2>&1 < "$tmp"; then
                mv "$tmp" "$outfile"
                rm -f "$err"
                return 0
            fi
        fi

        sleep_time=$(( attempt * 5 ))
        echo "  retrying in $sleep_time seconds..."
        sleep "$sleep_time"
    done

    echo "ERROR: $label failed after $MAX_RETRIES attempts"
    exit 1
}

build_follow_query() {
    local cursor="$1"

    if [[ -n "$cursor" ]]; then
        cat <<EOF
query {
  rateLimit { remaining resetAt cost }
  viewer {
    following(first: 100, after: "$cursor") {
      totalCount
      nodes { login }
      pageInfo { hasNextPage endCursor }
    }
  }
}
EOF
    else
        cat <<'EOF'
query {
  rateLimit { remaining resetAt cost }
  viewer {
    following(first: 100) {
      totalCount
      nodes { login }
      pageInfo { hasNextPage endCursor }
    }
  }
}
EOF
    fi
}

build_activity_query() {
    local batch=("$@")
    local query='query { rateLimit { remaining resetAt cost }'
    local i login

    for i in "${!batch[@]}"; do
        login="${batch[$i]}"

        query+=$'\n'
        query+="u${i}: repositoryOwner(login:\"$login\") {"
        query+=$'\n  __typename'
        query+=$'\n  login'
        query+=$'\n  ... on User {'
        query+=$'\n    createdAt'
        query+=$'\n    followers { totalCount }'
        query+=$'\n  }'
        query+=$'\n  ... on Organization {'
        query+=$'\n    createdAt'
        query+=$'\n  }'
        query+=$'\n  repoCount: repositories(privacy: PUBLIC, isFork: false) { totalCount }'
        query+=$'\n  recentRepo: repositories(first: 1, privacy: PUBLIC, orderBy: {field: PUSHED_AT, direction: DESC}) {'
        query+=$'\n    nodes {'
        query+=$'\n      pushedAt'
        query+=$'\n      primaryLanguage { name }'
        query+=$'\n    }'
        query+=$'\n  }'
        query+=$'\n}'
    done

    query+=$'\n}'
    printf '%s\n' "$query"
}

process_batch() {
    local batch_index="$1"
    local total_batches="$2"
    local users_seen="$3"
    shift 3

    local batch=("$@")
    local batch_file="$CACHE_DIR/batch-$(printf '%06d' "$batch_index").json"
    local query remaining reset cost
    local i requested login kind created pushed followers repos lang status

    if [[ -f "$batch_file" ]]; then
        echo "Skipping cached batch $batch_index"
        return
    fi

    echo
    echo "Processing batch $batch_index / $total_batches"
    echo "Users in batch: ${#batch[@]}"
    echo "Users seen so far: $users_seen"
    echo "Accounts:"
    printf '  %s\n' "${batch[@]}"

    query="$(build_activity_query "${batch[@]}")"
    graphql_request "$query" "$batch_file" "batch $batch_index"

    remaining="$(jq -r '.data.rateLimit.remaining // 0' "$batch_file")"
    reset="$(jq -r '.data.rateLimit.resetAt // ""' "$batch_file")"
    cost="$(jq -r '.data.rateLimit.cost // 0' "$batch_file")"

    echo "Batch cost=$cost remaining=$remaining"

    for i in "${!batch[@]}"; do
        requested="${batch[$i]}"
        login="$(jq -r ".data.u${i}.login // empty" "$batch_file")"

        if [[ -z "$login" ]]; then
            printf 'SKIP\t%s\tnot found\n' "$requested" | tee -a "$RAW_FILE"
            echo "$requested" >> "$SKIPPED_FILE"
            continue
        fi

        kind="$(jq -r ".data.u${i}.__typename // \"Unknown\"" "$batch_file")"
        created="$(jq -r ".data.u${i}.createdAt // \"null\"" "$batch_file")"
        pushed="$(jq -r ".data.u${i}.recentRepo.nodes[0].pushedAt // \"null\"" "$batch_file")"
        followers="$(jq -r ".data.u${i}.followers.totalCount // 0" "$batch_file")"
        repos="$(jq -r ".data.u${i}.repoCount.totalCount // 0" "$batch_file")"
        lang="$(jq -r ".data.u${i}.recentRepo.nodes[0].primaryLanguage.name // \"null\"" "$batch_file")"

        status="$(classify_status "$pushed")"

        printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
            "$status" "$login" "$kind" "$created" "$pushed" "$followers" "$repos" "$lang" \
            | tee -a "$RAW_FILE"

        if [[ "$status" == "ACTIVE" ]]; then
            echo "$login" >> "$ACTIVE_FILE"
        else
            echo "$login" >> "$INACTIVE_FILE"
        fi

        printf '%s,%s,%s,%s,%s,%s,%s,%s\n' \
            "$(csv_escape "$login")" \
            "$(csv_escape "$kind")" \
            "$(csv_escape "$created")" \
            "$(csv_escape "$pushed")" \
            "$(csv_escape "$followers")" \
            "$(csv_escape "$repos")" \
            "$(csv_escape "$lang")" \
            "$(csv_escape "$status")" \
            >> "$CSV_FILE"
    done

    sleep_until_reset "$remaining" "$reset"
}

echo
echo "Enumerating follow graph..."

cursor=""
page=0
batch_index=1
users_seen=0
total=0

declare -a BATCH=()

while true; do
    page=$(( page + 1 ))
    page_file="$CACHE_DIR/follow-page-$(printf '%06d' "$page").json"

    echo
    echo "Fetching follow page $page"
    [[ -n "$cursor" ]] && echo "  after cursor: $cursor"

    query="$(build_follow_query "$cursor")"
    graphql_request "$query" "$page_file" "follow page $page"

    remaining="$(jq -r '.data.rateLimit.remaining' "$page_file")"
    reset="$(jq -r '.data.rateLimit.resetAt' "$page_file")"
    cost="$(jq -r '.data.rateLimit.cost' "$page_file")"

    total="$(jq -r '.data.viewer.following.totalCount' "$page_file")"
    has_next="$(jq -r '.data.viewer.following.pageInfo.hasNextPage' "$page_file")"
    next_cursor="$(jq -r '.data.viewer.following.pageInfo.endCursor' "$page_file")"

    echo "Follow-page cost=$cost remaining=$remaining"
    echo "GitHub reports following totalCount: $total"

    mapfile -t PAGE_USERS < <(jq -r '.data.viewer.following.nodes[].login' "$page_file")
    echo "Users returned: ${#PAGE_USERS[@]}"

    for login in "${PAGE_USERS[@]}"; do
        echo "$login" >> "$FOLLOW_CACHE_FILE"

        BATCH+=("$login")
        users_seen=$(( users_seen + 1 ))

        if (( ${#BATCH[@]} >= BATCH_SIZE )); then
            total_batches=$(( (total + BATCH_SIZE - 1) / BATCH_SIZE ))
            process_batch "$batch_index" "$total_batches" "$users_seen" "${BATCH[@]}"
            BATCH=()
            batch_index=$(( batch_index + 1 ))
        fi
    done

    printf '%s' "$next_cursor" > "$FOLLOW_CURSOR_FILE"

    sleep_until_reset "$remaining" "$reset"

    if [[ "$has_next" != "true" ]]; then
        echo "No more follow pages"
        break
    fi

    cursor="$next_cursor"
done

if (( ${#BATCH[@]} > 0 )); then
    total_batches=$(( (total + BATCH_SIZE - 1) / BATCH_SIZE ))
    process_batch "$batch_index" "$total_batches" "$users_seen" "${BATCH[@]}"
fi

echo
echo "Run complete"
echo "Users processed: $users_seen"
echo "Active: $(wc -l < "$ACTIVE_FILE")"
echo "Inactive: $(wc -l < "$INACTIVE_FILE")"
echo "Skipped: $(wc -l < "$SKIPPED_FILE")"
echo "CSV rows: $(( $(wc -l < "$CSV_FILE") - 1 ))"
echo "Raw lines: $(wc -l < "$RAW_FILE")"
