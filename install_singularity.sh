#!/bin/bash
cd /home2/supasorn
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    libssl-dev \
    uuid-dev \
    libgpgme11-dev \
    squashfs-tools \
    libseccomp-dev \
    pkg-config \
    libfuse3-dev \
    libglib2.0-dev
wget https://go.dev/dl/go1.23.2.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.23.2.linux-amd64.tar.gz
export PATH=/usr/local/go/bin:$PATH
wget https://github.com/sylabs/singularity/releases/download/v4.2.1/singularity-ce-4.2.1.tar.gz
tar -xzf singularity-ce-4.2.1.tar.gz
cd singularity-ce-4.2.1/
./mconfig
cd builddir/
make -j8
sudo make install

FUSE_CONF="/etc/fuse.conf"

# Check if user_allow_other is already in the file
if ! grep -q "^user_allow_other" "$FUSE_CONF"; then
    echo "user_allow_other not found. Adding it to $FUSE_CONF."
    # Append user_allow_other to the file
    echo "user_allow_other" | sudo tee -a "$FUSE_CONF" > /dev/null
else
    echo "user_allow_other is already present in $FUSE_CONF."
fi

