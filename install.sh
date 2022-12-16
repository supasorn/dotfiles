#!/usr/bin/env sh
ln -sf /dotfiles/tmux.conf ~/.tmux.conf
ln -sf ~/dotfiles/zshrc ~/.zshrc

mkdir -p ~/.config/nvim
ln -sf ~/.vim/init.vim ~/.config/nvim/init.vim

mkdir -p ~/.config/lf
ln -sf ~/dotfiles/lfrc ~/.config/lf/lfrc
ln -sf ~/dotfiles/lfcd.sh ~/.config/lf/lfcd.sh
