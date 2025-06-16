#!/bin/zsh

# Show help message
show_help() {
    echo "Usage: $0 [minutes]"
    echo "List and optionally delete recent image/video files."
    echo
    echo "Arguments:"
    echo "  minutes    Time window in minutes (default: 180)"
    echo
    echo "Examples:"
    echo "  $0         # Show files from last 180 minutes"
    echo "  $0 60      # Show files from last 60 minutes"
    exit 1
}

# Handle help flag
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_help
fi

# Default time window in minutes
minutes=${1:-180}

# Validate minutes is a number
if ! [[ "$minutes" =~ ^[0-9]+$ ]]; then
    echo "Error: minutes must be a positive number"
    show_help
fi

# Determine platform-specific stat command
if stat --version &>/dev/null; then
    # GNU stat (Linux)
    get_mtime() { stat -c "%y" "$1"; }
    get_epoch() { stat -c "%Y" "$1"; }
else
    # BSD stat (macOS)
    get_mtime() { stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$1"; }
    get_epoch() { stat -f "%m" "$1"; }
fi

# Function to format elapsed time
format_elapsed() {
    local seconds=$1
    if (( seconds < 60 )); then
        echo "${seconds}s"
    elif (( seconds < 3600 )); then
        echo "$((seconds / 60))m"
    elif (( seconds < 86400 )); then
        echo "$((seconds / 3600))h"
    else
        echo "$((seconds / 86400))d"
    fi
}

# Find image and video files modified or created within the specified time window
files=()
while IFS= read -r -d '' f; do
    files+=("$f")
done < <(find . -type f \( -mmin -$minutes -o -cmin -$minutes \) \
    \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.gif" -o -iname "*.bmp" -o -iname "*.webp" \
    -o -iname "*.mp4" -o -iname "*.mov" -o -iname "*.avi" -o -iname "*.mkv" -o -iname "*.webm" \) \
    -print0 | sort -z)

if [[ ${#files[@]} -eq 0 ]]; then
    echo "No recent image or video files found in the last $minutes minutes."
    exit 0
fi

tmpfile=$(mktemp /tmp/recent_files.XXXXXX)
current_time=$(date +%s)

for f in "${files[@]}"; do
    mtime=$(get_mtime "$f")
    file_mtime=$(get_epoch "$f")

    if ! [[ "$file_mtime" =~ ^[0-9]+$ ]]; then
        echo "Warning: Could not get mtime for '$f'" >&2
        continue
    fi

    elapsed=$((current_time - file_mtime))
    elapsed_str=$(format_elapsed "$elapsed")

    echo "${f#./} (${elapsed_str}, $mtime)" >> "$tmpfile"
done

orig_mtime=$(get_epoch "$tmpfile")

nvim "$tmpfile"

new_mtime=$(get_epoch "$tmpfile")

if [[ "$orig_mtime" == "$new_mtime" ]]; then
    echo "No changes made or file not saved. Cancelled."
    rm -f "$tmpfile"
    exit 0
fi

while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    f="${line% \(*}"
    if [[ "$f" != /* && "$f" != ./* ]]; then
        f="./$f"
    fi
    if [[ -f "$f" ]]; then
        rm -f -- "$f"
        echo "Deleted: $f"
    else
        echo "File not found: $f"
    fi
done < "$tmpfile"

rm -f "$tmpfile"

