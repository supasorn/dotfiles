#!/bin/bash

# Path to fuse.conf
FUSE_CONF="/etc/fuse.conf"

# Check if user_allow_other is already in the file
if ! grep -q "^user_allow_other" "$FUSE_CONF"; then
    echo "user_allow_other not found. Adding it to $FUSE_CONF."
    # Append user_allow_other to the file
    echo "user_allow_other" | sudo tee -a "$FUSE_CONF" > /dev/null
else
    echo "user_allow_other is already present in $FUSE_CONF."
fi

