#!/bin/bash

# Name of the tmux session
tmux_session="ssh_grid"

# Check if a list of hosts is provided
if [ "$#" -eq 0 ]; then
    echo "Usage: $0 host1 host2 ... hostN or host range (e.g., v1-v23)"
    exit 1
fi

# Function to expand host range (e.g., v1-v23)
expand_host_range() {
    local input=$1
    if [[ $input =~ ^([a-zA-Z]+)([0-9]+)-([a-zA-Z]+)([0-9]+)$ ]]; then
        prefix=${BASH_REMATCH[1]}
        start=${BASH_REMATCH[2]}
        end=${BASH_REMATCH[4]}
        for ((i=start; i<=end; i++)); do
            printf "%s%s " "$prefix" "$i"
        done
    else
        echo "$input"
    fi
}

# Expand hosts if a range is provided
expanded_hosts=()
for host in "$@"; do
    for expanded in $(expand_host_range "$host"); do
        expanded_hosts+=("$expanded")
    done

done

echo "Expanded hosts: ${expanded_hosts[@]}"
# Get the total number of hosts
total_nodes=${#expanded_hosts[@]}

# Start a new tmux session (detached)
tmux new-session -d -s "$tmux_session"

# Apply specific pane border styles for this session
tmux set-option -t "$tmux_session" pane-active-border-style 'fg=#4a2900 bg=#e69823'
tmux set-option -t "$tmux_session" pane-border-style 'fg=#f6d1a2 bg=#916016'

tmux set-hook -w -t "$tmux_session" pane-focus-in 'run-shell "tmux set-window-option synchronize-panes off"'
tmux setw pane-border-status top

# Calculate number of columns needed for a balanced grid
cols=$(echo "sqrt($total_nodes)" | bc)
rows=$((($total_nodes + $cols - 1) / $cols))

# Loop through the provided hosts
for i in $(seq 0 $(($total_nodes - 1))); do
    host="${expanded_hosts[$i]}"

    # Create a new tmux window for the first host
    if [ $i -eq 0 ]; then
        tmux send-keys -t "$tmux_session" "ssh $host" C-m
    else
        # Split the window and navigate appropriately
        if (( $i % cols == 0 )); then
            tmux split-window -h -t "$tmux_session" "ssh $host"
        else
            tmux split-window -v -t "$tmux_session" "ssh $host"
        fi
        # Balance the layout after each split
        tmux select-layout -t "$tmux_session" tiled
    fi

done

# Attach to the tmux session
tmux attach-session -t "$tmux_session"

# turn out sync
tmux set-window-option -t "$tmux_session" synchronize-panes on
