#!/bin/bash
cd /home2/supasorn
# sudo apt-get update
# sudo apt-get install -y \
    # build-essential \
    # libssl-dev \
    # uuid-dev \
    # libgpgme11-dev \
    # squashfs-tools \
    # libseccomp-dev \
    # pkg-config \
    # libfuse3-dev \
    # libglib2.0-dev
# wget https://go.dev/dl/go1.23.2.linux-amd64.tar.gz
# sudo tar -C /usr/local -xzf go1.23.2.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin
wget https://github.com/sylabs/singularity/releases/download/v4.2.1/singularity-ce-4.2.1.tar.gz
tar -xzf singularity-ce-4.2.1.tar.gz
cd singularity-ce-4.2.1/
./mconfig
cd builddir/
make -j8
sudo make install

