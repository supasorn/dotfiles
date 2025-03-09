function cd() {
    if [[ "$#" != 0 ]]; then
        builtin cd "$@";
        return
    fi

    local original_dir="$(pwd)"
    
    while true; do
        local lsd=$(ls -ap | grep -vE '^\./?$|^\.\./?$') # exclude . and ..
        local output="$(printf '%s\n' "${lsd[@]}" |
            FZF_DEFAULT_OPTS="--height 40% --layout=reverse --prompt='$(pwd)/' --preview 'fzf-preview.sh {}'" \
            fzf --print-query --expect=ctrl-w,esc)"
        
        # Extract the selected directory and key press event
        local search_query=$(echo "$output" | sed -n '1p')  # First line is search query
        local key=$(echo "$output" | sed -n '2p')          # Second line is key event (if any)
        local selected_dir=$(echo "$output" | sed -n '3p')
        # echo "search_query: $search_query"
        # echo "key: $key"
        # echo "selected_dir: $selected_dir"

        if [[ "$key" == "esc" ]]; then
            builtin cd "$original_dir"
            return 0
        fi

        # If Ctrl-W ggis pressed
        if [[ "$key" == "ctrl-w" ]]; then
            # if [[ -z "$selected_dir" ]]; then
            # echo "search_query: $search_query"
            # if search query is empty, go up one level
            if [[ -z "$search_query" ]]; then
                builtin cd ..
            else
                continue
            fi
        fi

        # If a directory was selected, change to that directory
        [[ -n "$selected_dir" ]] || return 0
        builtin cd "$selected_dir" &> /dev/null
    done
}

