#!/usr/bin/env sh
ln -sf ~dotfiles/tmux.conf ~/.tmux.conf
ln -sf ~/dotfiles/zshrc ~/.zshrc

mkdir -p ~/.config/lf
ln -sf ~/dotfiles/lfrc ~/.config/lf/lfrc
ln -sf ~/dotfiles/lfcd.sh ~/.config/lf/lfcd.sh

git clone https://github.com/supasorn/nvim ~/dotfiles/nvim
ln -sf ~/dotfiles/nvim -T ~/.config/nvim
nvim 

