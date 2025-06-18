fzf_path_complete() {
  emulate -L zsh
  setopt local_options no_nomatch

  local original_dir="$PWD"

  # Extract the current "argument" being typed (i.e., last word on the line)
  local prefix="${LBUFFER%%[[:space:]]#([^[:space:]]#)}"  # Everything before the last word
  local base="${LBUFFER##* }"                             # The last word being typed
  base="${base/#\~/$HOME}"                                # Expand ~

  [[ -z "$base" ]] && base="."

  # Try to cd to that path (if valid)
  if [[ -d "$base" ]]; then
    cd "$base" || return
  fi

  local selected=""
  while true; do
    # Update the command line with current path
    local current_path="${PWD/#$HOME/~}"
    LBUFFER="${prefix}${current_path}/"
    zle reset-prompt

    # Run fzf
    local lsd=$(ls -ap | grep -vE '^\./?$|^\.\./?$') # exclude . and ..
    local output="$(printf '%s\n' "${lsd[@]}" |
        FZF_DEFAULT_OPTS="--height 40% --layout=reverse --prompt='$(pwd)/' --preview 'fzf-preview.sh {}'" \
        fzf --print-query --expect=ctrl-w,esc)"

    local search_query=$(echo "$output" | sed -n '1p')
    local key=$(echo "$output" | sed -n '2p')
    selected=$(echo "$output" | sed -n '3p')

    if [[ "$key" == "esc" ]]; then
      cd "$original_dir"
      zle reset-prompt
      return
    fi

    if [[ "$key" == "ctrl-w" ]]; then
      if [[ -z "$search_query" ]]; then
        cd ..
      fi
      continue
    fi

    if [[ -n "$selected" && -d "$selected" ]]; then
      cd "$selected"
      continue
    fi

    break
  done

  # Final update to command line with selected path
  if [[ -n "$selected" ]]; then
    local final_path="$(pwd)/$selected"
    final_path="${final_path/#$HOME/~}"
    LBUFFER="${prefix}${final_path}"
    zle reset-prompt
  fi
}

