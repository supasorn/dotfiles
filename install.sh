#!/usr/bin/env sh
ln -sf ~/dotfiles/tmux.conf ~/.tmux.conf
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm

ln -sf ~/dotfiles/zshrc ~/.zshrc

mkdir -p ~/.config/lf
ln -sf ~/dotfiles/lfrc ~/.config/lf/lfrc

git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf
~/.fzf/install

git clone https://github.com/supasorn/nvim ~/dotfiles/nvim
ln -sf ~/dotfiles/nvim -T ~/.config/nvim
nvim 

