#!/bin/bash
#sh -c "$(curl -fsSL https://raw.githubusercontent.com/supasorn/dotfiles/master/install0.sh)"
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get update
sudo apt -y install neovim vim zsh tmux curl ripgrep git exuberant-ctags nodejs unzip
chsh -s /usr/bin/zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh) --unattended"
sh ~/dotfiles/install.sh
zsh



