#!/bin/bash
#sh -c "$(curl -fsSL https://raw.githubusercontent.com/supasorn/dotfiles/master/install0.sh)"
cd ~
git clone https://github.com/supasorn/dotfiles
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
sudo apt-get update
sudo apt -y install zsh tmux ripgrep git exuberant-ctags unzip
chsh -s /usr/bin/zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh) --unattended"
sh ~/dotfiles/install.sh
zsh



