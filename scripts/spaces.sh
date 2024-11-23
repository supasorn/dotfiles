#!/bin/bash


if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi
# Define the directories and output files
declare -A directories=(
  ["/home"]="home.txt"
  ["/home2"]="home2.txt"
  ["/data"]="data.txt"
  ["/data2"]="data2.txt"
)

# Iterate over the directories
for dir in "${!directories[@]}"; do
  output_file="${directories[$dir]}"
  
  # Check if the directory exists
  if [ -d "$dir" ]; then
    echo "Processing $dir..."
    
    # Run the du command with sudo and save the output
    du -hsx "$dir"/* "$dir"/.[!.]* "$dir"/..?* 2>/dev/null | sort -h > "$output_file"
    
    echo "Saved results to $output_file"
  else
    echo "Directory $dir does not exist, skipping."
  fi
done

echo "Done!"
