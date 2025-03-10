# https://github.com/blinks zsh theme

# calling this causes buggy typing in singularity
function _prompt_char() {
  if $(git rev-parse --is-inside-work-tree >/dev/null 2>&1); then
    echo "%{%F{blue}%}±%{%f%k%b%}"
  else
    echo ' '
  fi
}

# This theme works with both the "dark" and "light" variants of the
# Solarized color schema.  Set the SOLARIZED_THEME variable to one of
# these two values to choose.  If you don't specify, we'll assume you're
# using the "dark" variant.

case ${SOLARIZED_THEME:-dark} in
    light) bkg=white;;
    *)     bkg=black;;
esac

ZSH_THEME_GIT_PROMPT_PREFIX=" [%{%B%F{blue}%}"
ZSH_THEME_GIT_PROMPT_SUFFIX="%{%f%k%b%K{${bkg}}%B%F{green}%}]"
ZSH_THEME_GIT_PROMPT_DIRTY=" %{%F{red}%}*%{%f%k%b%}"
ZSH_THEME_GIT_PROMPT_CLEAN=""

if [[ -n "$SINGULARITY_NAME" ]]; then
  # Add a small indicator before the current prompt
  # PROMPT="[S:$SINGULARITY_NAME]$PROMPT"
  SINGULARITY="%F{red}✼%f"
else
  SINGULARITY=""
fi

# this version calls _prompt_char() which causes typing bugs:
# PROMPT='%{%f%k%b%}
# %{%K{${bkg}}$SINGULARITY%B%F{green}%}%n%{%B%F{blue}%}@%{%B%F{cyan}%}%m%{%B%F{green}%} %{%b%F{yellow}%K{${bkg}}%}%~%{%B%F{green}%}$(git_prompt_info)%E%{%f%k%b%}
# %{%K{${bkg}}%}$(_prompt_char)%{%K{${bkg}}%} %#%{%f%k%b%} '

PROMPT='%{%f%k%b%}
%{%K{${bkg}}$SINGULARITY%B%F{green}%}%n%{%B%F{blue}%}@%{%B%F{cyan}%}%m%{%B%F{green}%} %{%b%F{yellow}%K{${bkg}}%}%~%{%B%F{green}%}$(git_prompt_info)%E%{%f%k%b%}
%{%K{${bkg}}%}%{%K{${bkg}}%} %#%{%f%k%b%} '



RPROMPT='!%{%B%F{cyan}%}%!%{%f%k%b%}'
