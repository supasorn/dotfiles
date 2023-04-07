rm -rf ~/.config/nvim ~/.local/share/nvim ~/.cache/nvim ~/dotfiles/nvim
rm -rf ~/dotfiles/nvim

git clone https://github.com/supasorn/nvim ~/dotfiles/nvim
ln -sf ~/dotfiles/nvim -T ~/.config/nvim
nvim 

