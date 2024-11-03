#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

# Check for required arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <username> <new_id>"
    exit 1
fi

USERNAME=$1
NEW_ID=$2

# Check if the new ID is already in use
if id -u "$NEW_ID" &>/dev/null || getent group "$NEW_ID" &>/dev/null; then
    echo "Error: The ID $NEW_ID is already in use as a UID or GID. Please choose a different ID."
    exit 1
fi

# Get the current UID and GID of the user
OLD_UID=$(id -u "$USERNAME")
OLD_GID=$(id -g "$USERNAME")

# Confirm that the user exists
if [ -z "$OLD_UID" ] || [ -z "$OLD_GID" ]; then
    echo "User $USERNAME does not exist."
    exit 1
fi

read -p "All processes of the user $USERNAME need to be killed? (y/n): " confirm
if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
    echo "Killing all processes of user $USERNAME..."
    pkill -u "$USERNAME"
    echo "Waiting 3 seconds for processes to terminate..."
    sleep 3 
    while pgrep -u "$USERNAME" > /dev/null; do
        echo "Processes still running for user $USERNAME. Waiting..."
    sleep 1  # Check every second
done
else
    echo "Skipping process termination for user $USERNAME."
    exit 1
fi

# Display the current UID and GID
echo "Current UID: $OLD_UID"
echo "Current GID: $OLD_GID"
echo "New UID and GID: $NEW_ID"

groupmod -g "$NEW_ID" "$USERNAME"
usermod -u "$NEW_ID" -g "$NEW_ID" "$USERNAME"

# Update file ownership in the specified directories
DIRECTORIES=("/home/$USERNAME" "/home2/$USERNAME" "/data/$USERNAME" "/data2/$USERNAME")

echo "Updating file ownership in ${DIRECTORIES[*]}..."
for DIR in "${DIRECTORIES[@]}"; do
    if [ -d "$DIR" ]; then
        echo "Updating files with old UID $OLD_UID in $DIR..."
        find "$DIR" -xdev -user "$OLD_UID" -exec chown -h "$NEW_ID" {} +

        echo "Updating files with old GID $OLD_GID in $DIR..."
        find "$DIR" -xdev -group "$OLD_GID" -exec chgrp -h "$NEW_ID" {} +
    else
        echo "Directory $DIR does not exist, skipping..."
    fi
done
