#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

# Check if at least one folder is provided as an argument
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <folder1> <folder2> ... <folderN>"
    exit 1
fi

# Loop over each folder provided as an argument
for folder in "$@"; do
    # Check if the folder exists
    if [ ! -d "$folder" ]; then
        echo "Directory '$folder' does not exist. Skipping..."
        continue
    fi

    # Attempt to unmount the folder
    echo "Attempting to unmount '$folder'..."
    if umount "$folder"; then
        echo "'$folder' successfully unmounted."
    else
        # Check if the error was because the folder was not mounted
        if mountpoint -q "$folder"; then
            echo "Failed to unmount '$folder'. Skipping deletion..."
            continue
        else
            echo "'$folder' is not mounted, but continuing to delete if empty."
        fi
    fi

    # Check if the folder is empty
    if [ -z "$(ls -A "$folder")" ]; then
        # Delete the folder since it is empty
        echo "Deleting '$folder'..."
        rmdir "$folder" && echo "'$folder' deleted successfully."
    else
        echo "'$folder' is not empty. Skipping deletion..."
    fi
done

