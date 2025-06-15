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
# Use -print0 to handle spaces and special characters
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
    # Get the modification time and format it
    mtime=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$f")
    # Calculate elapsed time
    file_mtime=$(stat -f %m "$f")
    elapsed=$((current_time - file_mtime))
    elapsed_str=$(format_elapsed $elapsed)
    # Remove leading ./ for consistency and add modification time
    echo "${f#./} (${elapsed_str}, $mtime)" >> "$tmpfile"
done

# Get the modification time before opening nvim
orig_mtime=$(stat -f %m "$tmpfile")

nvim "$tmpfile"

# Get the modification time after nvim exits
new_mtime=$(stat -f %m "$tmpfile")

# If the file wasn't modified (user quit without saving), don't delete
if [[ "$orig_mtime" == "$new_mtime" ]]; then
    echo "No changes made or file not saved. Cancelled."
    rm -f "$tmpfile"
    exit 0
fi

# Delete files listed in the edited temp file
while IFS= read -r line; do
    # Skip empty lines
    [[ -z "$line" ]] && continue
    # Extract filename by removing the timestamp part
    f="${line% \(*}"
    # Prepend ./ if not absolute or already relative
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
