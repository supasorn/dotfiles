#!/bin/bash
echo "~dotfiles"
cd ~/dotfiles
git pull
echo "~dotfiles/nvim"
cd ~/dotfiles/nvim
git pull
echo "~/cluster_utils"
cd ~/cluster_utils
git pull
