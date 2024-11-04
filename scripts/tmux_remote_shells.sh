#!/bin/bash

# Name of the tmux session
tmux_session="ssh_grid"

# Start a new tmux session (detached)
tmux new-session -d -s "$tmux_session"

# Loop through the range of hosts from v1 to v23
for i in {1..23}; do
    host="v$i"

    # Create a new tmux window for the first host
    if [ $i -eq 1 ]; then
        tmux send-keys -t "$tmux_session" "ssh $host" C-m
        tmux select-pane -T "$host"
    else
        # Split the window and navigate appropriately
        if (( (i-1) % 3 == 0 )); then
            tmux split-window -h -t "$tmux_session" "ssh $host"
        else
            tmux split-window -v -t "$tmux_session" "ssh $host"
        fi

        # Set pane title
        tmux select-pane -T "$host"

        # Balance the layout after each split
        tmux select-layout -t "$tmux_session" tiled
    fi

done

# Attach to the tmux session
tmux attach-session -t "$tmux_session"

