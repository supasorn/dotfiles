#!/bin/zsh

# Define the node names and the files to process
# nodes=(v1 v2 v3 v4 v5 v6 v7 v8 v9 v10 v11 v12 v13 v14 v15 v16 v17 v18 v19 v20 v21 v22 v23)
nodes=(v1 v2 v3 v4 v5 v6 v7 v9 v10 v11 v12 v13 v14 v15 v16 v17 v19 v20 v21 v22 v23)
# nodes=(v1 v2 v3 v4 v5 v6 v7)
# nodes=(v1 v2)
folders=("/home" "/home2" "/data" "/data2")
files=(home.txt home2.txt data.txt data2.txt)

# Base directory where the files are stored on the remote nodes
remote_dir="/home/supasorn/dotfiles/scripts/"

# Output HTML file
output_html="summary.html"
# Start writing the HTML file
echo "<!DOCTYPE html>" > $output_html
echo "<html>" >> $output_html
echo "<head><title>Disk Usage Summary</title></head>" >> $output_html
echo "<style>
        table { border-collapse: collapse; width: 100%; table-layout: fixed; }
        th, td { border: 1px solid black; padding: 8px; text-align: left; word-wrap: break-word; }
        th { width: 25%; } /* Ensure equal spacing for the 4 columns */
      </style>" >> $output_html
echo "<body>" >> $output_html
echo "<h1>Disk Usage Summary</h1>" >> $output_html

# Iterate over nodes
for node in "${nodes[@]}"; do
  echo "Processing node: $node..."
  echo "<h2>Node: $node</h2>" >> $output_html

  # Get percentage usage for each folder
  header=()
  for folder in "${folders[@]}"; do
    usage=$(ssh "$node" "df --output=pcent $folder 2>/dev/null | tail -n 1 | tr -d ' %'" 2>/dev/null)
    if [[ $? -eq 0 && -n "$usage" ]]; then
      header+=("$folder $usage%")
    else
      header+=("$folder N/A")
    fi
  done

  # Start the table
  echo "<table>" >> $output_html
  echo "<tr><th>${header[1]}</th><th>${header[2]}</th><th>${header[3]}</th><th>${header[4]}</th></tr>" >> $output_html

  # Fetch the last 10 lines from each file and reverse them
  echo "<tr>" >> $output_html
  for file in "${files[@]}"; do
    echo "Fetching $file from $node (reversed last 10 lines)..."
    
    # Fetch the last 10 lines and reverse them via SSH
    content=$(ssh "$node" "tail -n 10 $remote_dir/$file | tac" 2>/dev/null)

    if [[ $? -eq 0 && -n "$content" ]]; then
      # Add the reversed file content to the table cell
      echo "<td><pre>$content</pre></td>" >> $output_html
    else
      echo "<td><em>File not found </em></td>" >> $output_html
    fi
  done
  echo "</tr>" >> $output_html

  # End the table
  echo "</table>" >> $output_html
done

# Finish the HTML
echo "</body>" >> $output_html
echo "</html>" >> $output_html

echo "HTML summary created: $output_html"
