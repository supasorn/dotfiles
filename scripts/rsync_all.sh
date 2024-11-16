#!/bin/bash

# Define the list of paths
paths=(
    "v1:/home2/supasorn/singularity/"
    # "pure-c2:/mnt/data/supasorn/singularity/"
    # "v21:/home2/supasorn/singularity/"
    # "v23:/home2/supasorn/singularity/"
    "10.204.100.61:/ist-nas/users/supasorn/singularity/"
    # "10.204.100.61:/ist/users/supasorn/singularity/"
)

# Display the list of paths
echo "Select the path you want to sync from:"
for i in "${!paths[@]}"; do
    echo " $((i+1)). ${paths[$i]}"
done

# Get user input
read -p "Enter the number of local host: " choice
selected_index=$((choice-1))

# Validate the input
if [[ $choice -lt 1 || $choice -gt ${#paths[@]} ]]; then
    echo "Invalid choice. Exiting."
    exit 1
fi

# Selected source path
selected_path="${paths[$selected_index]}"
selected_host="${selected_path%%:*}"
selected_dir="${selected_path#*:}"

echo "You selected: $selected_path"

# Loop through each destination and initiate remote rsync via SSH
for i in "${!paths[@]}"; do
    if [[ $i -ne $selected_index ]]; then
        # Destination path details
        target_path="${paths[$i]}"
        target_host="${target_path%%:*}"
        target_dir="${target_path#*:}"

        # Use SSH to execute rsync remotely
        # ssh "$selected_host" "rsync -avvh $selected_dir $target_host:$target_dir"
        rsync -avvh --delete $selected_dir $target_host:$target_dir
        # echo "$selected_dir $target_host:$target_dir"
    fi
done

