#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <script_path>"
    exit 1
fi

# Parse the argument
SCRIPT_PATH=$1

# Check if the provided script path exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Script '$SCRIPT_PATH' not found."
    exit 1
fi

# Predefined list of machines
MACHINES=(v1 v2 v3 v4 v5 v6 v7 v8 v9 v10 v11 v12 v13 v14 v15 v16 v17 v18 v19 v20 v21 v22 v23)

# Iterate over each machine in the list
for REMOTE_HOST in "${MACHINES[@]}"; do
    echo "Executing script on $REMOTE_HOST..."
    ./run_remote.sh "$REMOTE_HOST" "$SCRIPT_PATH"

    if [ $? -ne 0 ]; then
        echo "Error: Script execution failed on $REMOTE_HOST."
    else
        echo "Script executed successfully on $REMOTE_HOST."
    fi
done

echo "All machines processed."

