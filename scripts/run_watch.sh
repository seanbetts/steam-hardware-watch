#!/bin/sh
set -eu

usage() {
  echo "usage: $0 [--komodo-only] YYYY-MM-DD [base_dir] [tracking_dir]" >&2
}

KOMODO_ONLY=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    --komodo-only)
      KOMODO_ONLY=1
      shift
      ;;
    --)
      shift
      break
      ;;
    -*)
      usage
      exit 1
      ;;
    *)
      break
      ;;
  esac
done

if [ "$#" -lt 1 ]; then
  usage
  exit 1
fi

RUN_DATE="$1"

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
REPO_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
BASE_DIR="${2:-$REPO_DIR/runs}"
TRACKING_DIR="${3:-/tmp/SteamTracking-master}"
KOMODO_ENV_FILE="${KOMODO_ENV_FILE:-$REPO_DIR/.local/komodo-env.sh}"
STEAMDB_ENV_FILE="${STEAMDB_ENV_FILE:-$REPO_DIR/.local/steamdb-env.sh}"

cleanup() {
  if [ "${KOMODO_KEEP_BROWSER_OPEN:-1}" = "1" ]; then
    :
  elif [ -f "$KOMODO_ENV_FILE" ] && [ -x "$SCRIPT_DIR/close_komodo.sh" ]; then
    "$SCRIPT_DIR/close_komodo.sh" >/dev/null 2>&1 || true
  fi

  if [ "${STEAMDB_KEEP_BROWSER_OPEN:-1}" = "1" ]; then
    :
  elif [ -f "$STEAMDB_ENV_FILE" ] && [ -x "$SCRIPT_DIR/close_steamdb.sh" ]; then
    "$SCRIPT_DIR/close_steamdb.sh" >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT INT TERM

find_previous_run_dir() {
  previous_dir=""
  for candidate in $(find "$BASE_DIR" -mindepth 1 -maxdepth 1 -type d -name '????-??-??' | sort); do
    if [ "$candidate" = "$RUN_DIR" ]; then
      continue
    fi
    case "$(basename "$candidate")" in
      "$RUN_DATE") ;;
      *)
        if [ "$(basename "$candidate")" \< "$RUN_DATE" ]; then
          previous_dir="$candidate"
        fi
        ;;
    esac
  done
  printf '%s\n' "$previous_dir"
}

komodo_timestamp_summary() {
  awk -F '\t' 'NF >= 2 {
    if (out != "") {
      out = out ", "
    }
    out = out $1 "=" $2
  } END {
    print out
  }' "$1"
}

komodo_timestamp_changes() {
  awk -F '\t' 'NR == FNR {
    previous[$1] = $2
    previous_order[++previous_count] = $1
    next
  }
  NF >= 2 {
    current_seen[$1] = 1
    if (!($1 in previous)) {
      print "- " $1 ": added " $2
    } else if (previous[$1] != $2) {
      print "- " $1 ": " previous[$1] " -> " $2
    }
  }
  END {
    for (i = 1; i <= previous_count; i++) {
      key = previous_order[i]
      if (!(key in current_seen)) {
        print "- " key ": removed " previous[key]
      }
    }
  }' "$1" "$2"
}

komodo_asset_count() {
  awk -F '\t' 'NF >= 3 && $3 ~ /^https?:/ {
    count++
  } END {
    print count + 0
  }' "$1"
}

komodo_new_asset_urls() {
  awk -F '\t' 'NR == FNR {
    if (NF >= 3 && $3 ~ /^https?:/) {
      previous[$3] = 1
    }
    next
  }
  NF >= 3 && $3 ~ /^https?:/ && !($3 in previous) {
    print "- " $3
  }' "$1" "$2"
}

print_komodo_update_status() {
  current_report="$RUN_DIR/reports/komodo-product-modified.tsv"

  if [ ! -s "$current_report" ]; then
    printf '%s\n' "Komodo updated: unknown (current Komodo timestamps unavailable)"
    return 0
  fi

  current_summary="$(komodo_timestamp_summary "$current_report")"
  previous_dir="$(find_previous_run_dir)"

  if [ -z "$previous_dir" ]; then
    printf '%s\n' "Komodo updated: unknown (no previous run found)"
    printf '%s\n' "Komodo timestamps: $current_summary"
    return 0
  fi

  previous_report="$previous_dir/reports/komodo-product-modified.tsv"
  previous_date="$(basename "$previous_dir")"

  if [ ! -s "$previous_report" ]; then
    printf '%s\n' "Komodo updated: unknown (previous run $previous_date has no Komodo timestamp report)"
    printf '%s\n' "Komodo timestamps: $current_summary"
    return 0
  fi

  if cmp -s "$previous_report" "$current_report"; then
    printf '%s\n' "Komodo updated: no (matches previous run $previous_date)"
  else
    printf '%s\n' "Komodo updated: yes (changed since previous run $previous_date)"
    printf '%s\n' "Komodo changes:"
    komodo_timestamp_changes "$previous_report" "$current_report"
  fi

  printf '%s\n' "Komodo timestamps: $current_summary"
}

print_komodo_asset_status() {
  current_report="$RUN_DIR/reports/komodo-visual-assets.tsv"

  if [ ! -s "$current_report" ]; then
    printf '%s\n' "Komodo new assets: unknown (current Komodo asset report unavailable)"
    return 0
  fi

  current_count="$(komodo_asset_count "$current_report")"
  previous_dir="$(find_previous_run_dir)"

  if [ -z "$previous_dir" ]; then
    printf '%s\n' "Komodo new assets: unknown ($current_count current, no previous run found)"
    return 0
  fi

  previous_report="$previous_dir/reports/komodo-visual-assets.tsv"
  previous_date="$(basename "$previous_dir")"

  if [ ! -s "$previous_report" ]; then
    printf '%s\n' "Komodo new assets: unknown ($current_count current, previous run $previous_date has no Komodo asset report)"
    return 0
  fi

  new_urls="$(komodo_new_asset_urls "$previous_report" "$current_report")"
  new_count="$(printf '%s\n' "$new_urls" | sed '/^$/d' | wc -l | tr -d ' ')"

  if [ "$new_count" = "0" ]; then
    printf '%s\n' "Komodo new assets: no ($current_count current, matches previous run $previous_date)"
  else
    printf '%s\n' "Komodo new assets: yes ($new_count new, $current_count current, since previous run $previous_date)"
    printf '%s\n' "Komodo new asset URLs:"
    printf '%s\n' "$new_urls"
  fi
}

INIT_OUTPUT="$("$SCRIPT_DIR/init_run.sh" "$RUN_DATE" "$BASE_DIR")"
RUN_DIR="$(printf '%s\n' "$INIT_OUTPUT" | awk -F= '/^RUN_DIR=/{print $2}')"
RUN_NOTE="$(printf '%s\n' "$INIT_OUTPUT" | awk -F= '/^RUN_NOTE=/{print $2}')"

if [ -z "$RUN_DIR" ] || [ -z "$RUN_NOTE" ]; then
  echo "failed to initialize run folder" >&2
  exit 1
fi

printf '%s\n' "Run dir: $RUN_DIR"
printf '%s\n' "Run note: $RUN_NOTE"

"$SCRIPT_DIR/check_komodo.sh" "$RUN_DIR"

if [ "$KOMODO_ONLY" = "1" ]; then
  print_komodo_update_status
  print_komodo_asset_status
  RUN_SUMMARY_OUT="$RUN_DIR/reports/run-summary.md"
  python3 "$SCRIPT_DIR/write_run_summary.py" \
    --run-dir "$RUN_DIR" \
    --output "$RUN_SUMMARY_OUT"
  printf '%s\n' "Run summary: $RUN_SUMMARY_OUT"
  printf '%s\n' "Komodo-only run complete."
  exit 0
fi

"$SCRIPT_DIR/check_steamkit_pics.sh" "$RUN_DIR"
"$SCRIPT_DIR/check_steamdb.sh" "$RUN_DIR"
"$SCRIPT_DIR/check_steamtracking.sh" "$RUN_DIR" "$TRACKING_DIR"
"$SCRIPT_DIR/check_steamvr_depots.sh" "$RUN_DIR"
"$SCRIPT_DIR/check_steamos_mirror.sh" "$RUN_DIR"
"$SCRIPT_DIR/check_valve_endpoints.sh" "$RUN_DIR"
"$SCRIPT_DIR/check_customs_shipments.sh" "$RUN_DIR"
python3 "$SCRIPT_DIR/save_visual_assets.py" --run-dir "$RUN_DIR" --base-dir "$BASE_DIR"

PREVIOUS_DIR=""
PREVIOUS_DIR="$(find_previous_run_dir)"

if [ -n "$PREVIOUS_DIR" ]; then
  COMPARE_OUT="$RUN_DIR/reports/compare-vs-$(basename "$PREVIOUS_DIR").md"
  python3 "$SCRIPT_DIR/compare_runs.py" \
    --previous "$PREVIOUS_DIR" \
    --current "$RUN_DIR" \
    --output "$COMPARE_OUT"
  printf '%s\n' "Comparison report: $COMPARE_OUT"
else
  printf '%s\n' "No previous run folder found under $BASE_DIR"
fi

FRAME_FOCUS_OUT="$RUN_DIR/reports/frame-focus.md"
python3 "$SCRIPT_DIR/write_frame_focus_report.py" \
  --run-dir "$RUN_DIR" \
  --output "$FRAME_FOCUS_OUT"
printf '%s\n' "Frame focus report: $FRAME_FOCUS_OUT"

STATUS_DRAFT_OUT="$RUN_DIR/reports/status-draft.md"
python3 "$SCRIPT_DIR/draft_status_update.py" \
  --run-dir "$RUN_DIR" \
  --output "$STATUS_DRAFT_OUT"
printf '%s\n' "Status draft: $STATUS_DRAFT_OUT"

RUN_SUMMARY_OUT="$RUN_DIR/reports/run-summary.md"
python3 "$SCRIPT_DIR/write_run_summary.py" \
  --run-dir "$RUN_DIR" \
  --output "$RUN_SUMMARY_OUT"
printf '%s\n' "Run summary: $RUN_SUMMARY_OUT"

printf '%s\n' "Run complete."
