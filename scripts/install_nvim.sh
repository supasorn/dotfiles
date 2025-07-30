#!/bin/bash
set -e

# Clone or update the Neovim repository
if [ ! -d neovim ]; then
    git clone https://github.com/neovim/neovim.git
else
    echo "Updating existing neovim repository..."
    cd neovim
    git pull
    cd ..
fi

# Build and install Neovim
cd neovim
echo "Cleaning previous build..."
rm -rf build/

make CMAKE_BUILD_TYPE=Release -j8
sudo make install

# Ask the user whether to delete the source folder
read -p "Do you want to delete the ~/neovim source folder? [y/N]: " choice
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    echo "Deleting neovim..."
    rm -rf "neovim"
else
    echo "Keeping neovim."
fi
