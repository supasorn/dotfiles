function cd() {
    if [[ "$#" != 0 ]]; then
        builtin cd "$@";
        return
    fi

    local original_dir="$(pwd)"
    
    while true; do
        local lsd=$(ls -ap | grep '/$' | sed 's;/$;;')
        local dir="$(printf '%s\n' "${lsd[@]}" |
            FZF_DEFAULT_OPTS="--height 40% --layout=reverse --prompt='$(pwd)/'" \
            fzf --bind 'ctrl-w:execute-silent(builtin cd ..; echo ..)' --expect=ctrl-w,esc)"
        
        # Extract the selected directory and key press event
        local key=$(echo "$dir" | head -1)
        local selected_dir=$(echo "$dir" | tail -n +2)

        # If ESC is pressed, revert to the original directory and exit
        if [[ "$key" == "esc" ]]; then
            builtin cd "$original_dir"
            return 0
        fi

        # If Ctrl-W is pressed, go up one level
        if [[ "$key" == "ctrl-w" ]]; then
            builtin cd ..
            continue
        fi

        # If a directory was selected, change to that directory
        [[ -n "$selected_dir" ]] || return 0
        builtin cd "$selected_dir" &> /dev/null
    done
}

