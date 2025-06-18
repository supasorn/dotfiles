fzf_path_complete() {
  emulate -L zsh
  setopt local_options no_nomatch

  local original_dir="$PWD"

  # Extract the current "argument" being typed (i.e., last word on the line)
  local prefix="${LBUFFER% *} "  # Everything before the last word, plus a space
  local base="${LBUFFER##* }"                             # The last word being typed
  base="${base/#\~/$HOME}"                                # Expand ~
  base="${base%/}"                                        # Remove trailing slash if present

  [[ -z "$base" ]] && base="."

  # Determine the starting directory for navigation
  local nav_dir="$original_dir"
  
  # If base is a valid directory and not ".", use it as starting point
  if [[ -d "$base" && "$base" != "." ]]; then
    nav_dir="$base"
  fi

  # Function to compute relative path from original_dir to nav_dir
  compute_relative_path() {
    local from="$original_dir"
    local to="$nav_dir"
    
    # If they're the same, return empty
    if [[ "$from" == "$to" ]]; then
      echo ""
      return
    fi
    
    # If nav_dir is a subdirectory of original_dir, compute relative path
    if [[ "$to" == "$from"/* ]]; then
      echo "${to#$from/}"
    else
      # Use realpath to compute relative path (much simpler!)
      echo "$to"
      # realpath --relative-to="$from" "$to" 2>/dev/null || echo "$to"
    fi
  }

  # Function to update the command line with final path
  update_final_path() {
    local selected_item="$1"
    local relative_path=$(compute_relative_path)
    local final_path
    
    if [[ -n "$relative_path" ]]; then
      if [[ -n "$selected_item" ]]; then
        # Remove trailing slash from relative_path if it exists, then add selected item
        final_path="${relative_path%/}/${selected_item}"
      else
        # Just use the relative path (for ESC key)
        final_path="$relative_path"
      fi
    else
      if [[ -n "$selected_item" ]]; then
        # No relative path, just use selected item
        final_path="$selected_item"
      else
        # No relative path and no selected item - check if we're back to original directory
        if [[ "$nav_dir" == "$original_dir" ]]; then
          # Same as original directory, return empty
          final_path=""
        elif [[ -d "$base" && "$base" != "." ]]; then
          # Use the original base if it was a full path
          final_path="$base"
        else
          final_path="$nav_dir"
        fi
      fi
    fi
    
    LBUFFER="${prefix}${final_path}"
    zle reset-prompt
  }

  local selected=""
  while true; do
    # Update the command line with current relative path
    local relative_path=$(compute_relative_path)
    if [[ -n "$relative_path" ]]; then
      LBUFFER="${prefix}${relative_path}/"
    else
      LBUFFER="${prefix}"
    fi
    zle reset-prompt

    # Run fzf from the navigation directory - use ls with -p to show trailing slashes for folders
    local lsd=$(cd "$nav_dir" && ls -ap | grep -vE '^\./?$|^\.\./?$') # exclude . and .. with trailing slashes
    local output="$(printf '%s\n' "${lsd[@]}" |
        FZF_DEFAULT_OPTS="--height 40% --layout=reverse --prompt='${nav_dir%/}/' --preview 'cd \"$nav_dir\" && fzf-preview.sh {}'" \
        fzf --print-query --expect=ctrl-w,esc)"

    local search_query=$(echo "$output" | sed -n '1p')
    local key=$(echo "$output" | sed -n '2p')
    selected=$(echo "$output" | sed -n '3p')
    
    # Clean up selected - remove any trailing slash
    selected="${selected%/}"

    if [[ "$key" == "esc" ]]; then
      # Use the current navigation directory as the final output
      update_final_path ""
      return
    fi

    if [[ "$key" == "ctrl-w" ]]; then
      if [[ -z "$search_query" ]]; then
        # Go up one directory
        nav_dir=$(dirname "$nav_dir")
      fi
      continue
    fi

    if [[ -n "$selected" && -d "$nav_dir/$selected" ]]; then
      # Go into the selected directory
      nav_dir="$nav_dir/$selected"
      continue
    fi

    zle reset-prompt
    break
  done

  # Final update to command line with selected path
  if [[ -n "$selected" ]]; then
    update_final_path "$selected"
  fi
}

