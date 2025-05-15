# zmodload zsh/zprof
# START_TIME=$(($(date +%s%3N)))
# If you come from bash you might have to change your $PATH.
# export PATH=$HOME/bin:/usr/local/bin:$PATH

# Path to your oh-my-zsh installation.
omz="~/.oh-my-zsh"
export ZSH="${omz/#\~/$HOME}"

# Set name of the theme to load --- if set to "random", it will
# load a random theme each time oh-my-zsh is loaded, in which case,
# to know which specific one was loaded, run: echo $RANDOM_THEME
# See https://github.com/robbyrussell/oh-my-zsh/wiki/Themes
# ZSH_THEME="robbyrussell"
# ZSH_THEME="blinks"

# Set list of themes to pick from when loading at random
# Setting this variable when ZSH_THEME=random will cause zsh to load
# a theme from this variable instead of looking in ~/.oh-my-zsh/themes/
# If set to an empty array, this variable will have no effect.
# ZSH_THEME_RANDOM_CANDIDATES=( "robbyrussell" "agnoster" )

# Uncomment the following line to use case-sensitive completion.
# CASE_SENSITIVE="true"

# Uncomment the following line to use hyphen-insensitive completion.
# Case-sensitive completion must be off. _ and - will be interchangeable.
# HYPHEN_INSENSITIVE="true"

# Uncomment the following line to disable bi-weekly auto-update checks.
# DISABLE_AUTO_UPDATE="true"

# Uncomment the following line to change how often to auto-update (in days).
# export UPDATE_ZSH_DAYS=13

# Uncomment the following line to disable colors in ls.
# DISABLE_LS_COLORS="true"

# Uncomment the following line to disable auto-setting terminal title.
# DISABLE_AUTO_TITLE="true"

# Uncomment the following line to enable command auto-correction.
# ENABLE_CORRECTION="true"

# Uncomment the following line to display red dots whilst waiting for completion.
# COMPLETION_WAITING_DOTS="true"

# Uncomment the following line if you want to disable marking untracked files
# under VCS as dirty. This makes repository status check for large repositories
# much, much faster.
# DISABLE_UNTRACKED_FILES_DIRTY="true"

# Uncomment the following line if you want to change the command execution time
# stamp shown in the history command output.
# You can set one of the optional three formats:
# "mm/dd/yyyy"|"dd.mm.yyyy"|"yyyy-mm-dd"
# or set a custom format using the strftime function format specifications,
# see 'man strftime' for details.
# HIST_STAMPS="mm/dd/yyyy"

# Would you like to use another custom folder than $ZSH/custom?
# ZSH_CUSTOM=/path/to/new-custom-folder

# Which plugins would you like to load?
# Standard plugins can be found in ~/.oh-my-zsh/plugins/*
# Custom plugins may be added to ~/.oh-my-zsh/custom/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
# Add wisely, as too many plugins slow down shell startup.
plugins=(
  git
  z
  extract
)

source $ZSH/oh-my-zsh.sh

# User configuration

# export MANPATH="/usr/local/man:$MANPATH"

# You may need to manually set your language environment
# export LANG=en_US.UTF-8

# Preferred editor for local and remote sessions
# if [[ -n $SSH_CONNECTION ]]; then
#   export EDITOR='vim'
# else
#   export EDITOR='mvim'
# fi
export EDITOR='nvim'

# Compilation flags
# export ARCHFLAGS="-arch x86_64"

# ssh
# export SSH_KEY_PATH="~/.ssh/rsa_id"

# Set personal aliases, overriding those provided by oh-my-zsh libs,
# plugins, and themes. Aliases can be placed here, though oh-my-zsh
# users are encouraged to define aliases within the ZSH_CUSTOM folder.
# For a full list of active aliases, run `alias`.
#
# Example aliases
# alias zshconfig="mate ~/.zshrc"
# alias ohmyzsh="mate ~/.oh-my-zsh"
# make ctl-r returns immediately

HISTFILE=~/.zsh_history
HISTSIZE=999999999
SAVEHIST=$HISTSIZE

# Appends every command to the history file once it is executed
setopt inc_append_history


export BAT_THEME="gruvbox-dark"

export FZF_MARKS_JUMP=^h

export FZFZ_SUBDIR_LIMIT=0
export FZFZ_EXTRA_OPTS="--reverse --preview-window up:0 --keep-right"
export FZF_CTRL_R_OPTS="--reverse"
# export FZF_CTRL_R_OPTS="--reverse --preview 'echo {} |sed -e \"s/^ *\([0-9]*\) *//\" -e \"s/.\\{\$COLUMNS\\}/&\\n/g\"' --preview-window down:3:hidden --bind ?:toggle-preview"

export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/lib/"

export TERM="xterm-256color"
#export TERM="screen-256color"

alias v="nvim"

[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh
export PATH="$HOME/.fzf/bin:$PATH"

export CUDA_DEVICE_ORDER=PCI_BUS_ID
export PATH="$HOME/.local/bin:$PATH"

space() {
  (setopt null_glob; sudo du -hsx -- "$@" | sort -h)
}
spaces() {
  (setopt null_glob; sudo du -hsx -- * .* | sort -h)
}

alias gp="~/dotfiles/scripts/gitpull.sh"
# alias rs="sudo -E python ~/dotfiles/scripts/rsync_singularity_ui.py"
# runfavs() {
  # local cmd
  # cmd=$(cat ~/dotfiles/commands.txt | fzf --prompt="Run: " --height=20% --reverse)
  # if [ -n "$cmd" ]; then
      # echo ">> $cmd"
      # eval "$cmd"
  # fi
# }

runfavs() {
    local raw key rawcmd cmd

    # let fzf return both the key pressed and the selection
    raw=$(fzf --expect=ctrl-e,enter --prompt="Run: " --height=20% --reverse < ~/dotfiles/commands.txt)
    [[ -z $raw ]] && return 0

    key=$(head -n1 <<< "$raw")
    rawcmd=$(tail -n +2 <<< "$raw")
    [[ -z $rawcmd ]] && return 0

    # if Ctrl-E pressed (or you still have the old `$` hack), drop into edit mode
    if [[ $key == ctrl-e ]] || [[ $rawcmd == *\$ ]]; then
        cmd=${rawcmd%\$}                        # strip trailing $, if any
          print -z -- "$cmd"                  # push into Zsh edit buffer
        return 0
    fi

    # otherwise run it straight
    cmd=$rawcmd
    echo ">> $cmd"
    print -s -- "$cmd"
    eval "$cmd"
}

alias r="runfavs"

alias tm="tmux -u"
alias tma="tmux -u a"

alias lss="ls -lahrS"

alias rgf='rg --files --no-ignore | rg'
alias rg1="rg --max-depth=1"

alias pdf='cd /Users/supasorn/projects/pdf_signer; source ~/Projects/forex/venv_forex/bin/activate; python3 multisign.py'

alias ssh="ssh -R 52698:localhost:22 "
# alias pdf='cd /Users/supasorn/projects/pdf_signer; python3 multisign.py'

fshere() {
  cmd="sshfs -o cache=no -o IdentityFile=/home/$USER/.ssh/id_rsa $USER@$@ $PWD"
  echo $cmd
  eval $cmd
  cd ..
  cd -
  #sshfs -o follow_symlinks -o cache=no -o IdentityFile=~/.ssh/id_rsa supasorn@v3:/data/supasorn/diffusers diffusers
} 

source-git() {
  target=~/.zsh/$1:t:r
  plugin=$target/$1:t:r.plugin.zsh
  if [ ! -d "$target" ] ; then
    git clone $1 $target
    #echo "git clone $1 $target"
  fi
  if [ ! -f "$plugin" ]; then
    plugin=$target/$1:t:r
  fi
  source $plugin
  #echo "source $plugin"
}

source-git https://github.com/supasorn/fzf-z.git  # ctrl-g function
source-git https://github.com/changyuheng/zsh-interactive-cd.git 
source-git https://github.com/zsh-users/zsh-autosuggestions.git 
source-git https://github.com/hchbaw/zce.zsh.git  # easy motion
source-git https://github.com/urbainvaes/fzf-marks
source-git https://github.com/zsh-users/zsh-syntax-highlighting

bindkey '^[[Z' autosuggest-accept
bindkey '^f' zce

zstyle ':zce:*' bg 'fg=3'

ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE='fg=23'

UNAME=$(uname | tr "[:upper:]" "[:lower:]")
# if [[ "$UNAME" == "linux" ]]; then
  # export NOCONDA_PATH="$PATH:/usr/local/cuda-11.8/bin"
  # export PATH="$NOCONDA_PATH:/home2/$USER/anaconda3/bin:/usr/local/go/bin"

  # export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/cuda-11.8/lib64:/usr/local/cuda/extras/CUPTI/lib64"
# fi

unset TMUX  # allow nested tmux
hn="$(hostname)"

LFCD="$HOME/.config/lf/lfcd.sh"                               
if [ -f "$LFCD" ]; then
    source "$LFCD"
fi
bindkey -s '^o' 'lfcd\n'  # zsh

FZFCD="$HOME/dotfiles/fzf-cd.sh"                               
if [ -f "$FZFCD" ]; then
    source "$FZFCD"
fi

if [[ $hn == "rog" ]]; then
  export PATH="/opt/nvim-linux64/bin:$PATH"
  tf-term() {
    tmux new-session \; \
    send-keys "$@" C-m \; \
    send-keys "source ~/venv_tf2/bin/activate" C-m \; \
    split-window -v \; \
    send-keys "$@" C-m \; \
    send-keys "source ~/venv_tf2/bin/activate" C-m \; \
    send-keys "tensorboard --logdir=." C-m \; \
    split-window -v \; \
    send-keys "$@" C-m \; \
  }

  tl-term() {
    tmux new-session \; \
    send-keys "/home2/; python remote_timelapse.py" C-m \; \
    split-window -h \; \
    send-keys "/home2; python timelapse_day_maker_runner.py" C-m \; \
  }

  alias run="python /home2/research/orbiter/cluster_utils/tasklauncher_uni.py"
  alias ul="tmux a -t UL"
  alias rs="python /home2/research/orbiter/cluster_utils/rsync_folder.py"
  alias mountall="python /home2/research/orbiter/cluster_utils/mountall.py"

elif [[ $hn == "ssmb.local" ]]; then
  alias ut="youtube-dl -f 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4'"
  alias run="python3 ~/research/cluster_utils/singularitylauncher.py"
  alias ul="tmux a -t UL"

  export DYLD_LIBRARY_PATH="/usr/local/lib"
  export LDFLAGS="-L/usr/local/lib"
  export CFLAGS="-I/usr/local/include"
else 
  # alias run="python3 /home/supasorn/cluster_utils/tasklauncher_uni.py"
  alias run="python3 /home/supasorn/cluster_utils/singularitylauncher.py"
  alias ul="tmux a -t UL"
fi
alias sg='python3 /ist-nas/users/supasorn/singularity_slim/run.py'
alias ns='python3 ~/dotfiles/scripts/lsgpu.py --local'
alias lsgpu='python3 ~/dotfiles/scripts/lsgpu.py'

source ~/.vim/export_lf_icons.sh 2> /dev/null 


if [[ -n $SSH_CLIENT ]]; then
    # Save the SSH_CLIENT to a file
    echo $SSH_CLIENT > ~/ssh_client_info.txt
fi


# don't call this by default, it's slow in singularity
load_nvm() {
  export NVM_DIR="$HOME/.nvm"
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  
  [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  
}

# if not inside singularity, call load_nvm()
if [[ -z $SINGULARITY_NAME ]]; then
  load_nvm
fi

# if not ssmb.local, run this
if [[ $hn != "ssmb.local" ]]; then
  function get_corrected_pwd() {
    local current_pwd=$PWD  
    if [[ -n "$SINGULARITY_NAME" || -n "$SINGULARITY_CONTAINER" ]]; then
      if [[ "$current_pwd" == /host* ]]; then
        echo "${current_pwd#/host}"
      elif [[ "$current_pwd" == /projects* ]]; then
        echo "/ist-nas/users/supasorn${current_pwd}"
      else
        echo "$current_pwd"
      fi
    else
      echo "$current_pwd"
    fi
  }
  function sshCopyIdIfNeeded() {
    if [[ $(ssh -o BatchMode=yes -o ConnectTimeout=5 -p 52698 localhost 'echo ok' 2>/dev/null) != "ok" ]]; then
      echo "Copying SSH key to -p 52698 localhost..."
      ssh-copy-id -p 52698 localhost
    fi
  }

  function vsc() {
    # Try ss first (modern systems)
    if command -v ss &>/dev/null; then
        # server_ip=$(ss -tnp | grep ':22 ' | awk '{print $4}' | cut -d: -f1 | head -n 1)
        # server_ip=$(ss -tnp | awk '$4 ~ /:22$/ { split($4, a, ":"); print a[1]; exit }')
        server_ip=$(printf '%s\n' "$SSH_CONNECTION" | awk '{print $3}')

    fi

    # Final check: If no IP found, exit with error
    if [[ -z "$server_ip" ]]; then
        echo "Error: Unable to detect server IP."
        return 1
    fi
    sshCopyIdIfNeeded

    ssh -p 52698 localhost "/usr/local/bin/code --remote ssh-remote+$(whoami)@$server_ip $(get_corrected_pwd)"
  }

  function finder() {
      # Try ss first (modern systems)
      if command -v ss &>/dev/null; then
          # server_ip=$(ss -tnp | grep ':22 ' | awk '{print $4}' | cut -d: -f1 | head -n 1)
          server_ip=$(printf '%s\n' "$SSH_CONNECTION" | awk '{print $3}')

      fi

      # Final check: If no IP found, exit with error
      if [[ -z "$server_ip" ]]; then
          echo "Error: Unable to detect server IP."
          return 1
      fi


      # Get the absolute path of the current directory
      absolute_path=$(get_corrected_pwd)

      # Convert absolute path into a valid folder name by replacing '/' with '_'
      sanitized_path=$(echo "$absolute_path" | sed 's#/#_#g')

      # Define the mount point on Mac using server IP and sanitized path
      mount_point="/Users/supasorn/mnt/${server_ip}${sanitized_path}"

      sshCopyIdIfNeeded
      # Run SSH command on Mac to handle mount
      ssh -p 52698 localhost "
          # Ensure the mount directory exists
          mkdir -p '$mount_point'

          # Check if the mount point is already mounted
          if mount | grep -q \"\$mount_point\"; then
              echo 'Unmounting stale connection...'
              umount '$mount_point'
          fi

          # Mount the remote directory
          echo 'Mounting $server_ip:$absolute_path to $mount_point'
          /usr/local/bin/sshfs $server_ip:$absolute_path '$mount_point' -o volname=\"${server_ip}${sanitized_path}\",reconnect,IdentityFile=~/.ssh/id_rsa

          # Open Finder if the mount was successful
          if mount | grep -q \"\$mount_point\"; then
              echo 'Opening Finder...'
              open '$mount_point'
          else
              echo 'Mount failed!'
          fi
      "
  }
fi




source ~/dotfiles/blinks_singularity.zsh-theme

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/opt/conda/bin/conda' 'shell.zsh' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/opt/conda/etc/profile.d/conda.sh" ]; then
        . "/opt/conda/etc/profile.d/conda.sh"
    else
        export PATH="/opt/conda/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

# Check if the directory exists
if [ -d "/startup_scripts" ]; then
  # Loop through all .sh files in the directory
  for script in /startup_scripts/*.sh; do
    # Check if there are any .sh files
    if [ -f "$script" ]; then
      echo "Running $script..."
      source "$script"
    fi
  done
fi

if [[ $1 == eval ]]
then
    "$@"
set --
fi


# zprof
# END_TIME=$(($(date +%s%3N)))
# TOTAL_TIME=$((END_TIME - START_TIME))
# echo "Total load time: ${TOTAL_TIME} milliseconds"
