#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <remote_host> <script_path>"
    exit 1
fi

# Parse the arguments
REMOTE_HOST=$1
SCRIPT_PATH=$2

# Check if the provided script path exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Script '$SCRIPT_PATH' not found."
    exit 1
fi

# Transfer the script to the remote machine using scp
scp "$SCRIPT_PATH" "$REMOTE_HOST:/tmp/$(basename $SCRIPT_PATH)"

# Check if the scp command was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to copy the script to the remote host."
    exit 1
fi

# Execute the script on the remote machine
ssh "$REMOTE_HOST" "bash /tmp/$(basename $SCRIPT_PATH)"

# Check if the ssh command was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to execute the script on the remote host."
    exit 1
fi

# Optionally clean up the remote script after execution
ssh "$REMOTE_HOST" "rm /tmp/$(basename $SCRIPT_PATH)"

echo "Script executed successfully on $REMOTE_HOST."

