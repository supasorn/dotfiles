import socket
import subprocess
import os
import psutil
import sys

# List of paths with hostnames
paths = [
    "v1:/home2/supasorn/singularity/",
    "pure-c2:/mnt/data/supasorn/singularity/",
    # "v21:/home2/supasorn/singularity/",
    "v23:/home2/supasorn/singularity/",
    # "10.204.100.61:/ist-nas/users/supasorn/singularity/",
    "10.204.100.61:/ist/users/supasorn/singularity/"
]

if len(sys.argv) < 2 or sys.argv[1] not in ['-u', '-d']:
    print("Usage: script.py -u|-d [rsync additional arguments...]")
    exit(1)
# Determine the action: upload or download
action = sys.argv[1]
rsync_extra_args = ' '.join(sys.argv[2:])  # Captu

def is_localhost(alias):
  try:
    ip_address = socket.gethostbyname(alias)
    local_ips = {addr.address for iface in psutil.net_if_addrs().values() for addr in iface}
    return ip_address in local_ips
  except socket.gaierror:
    # If the alias cannot be resolved, return False
    return False

# Identify the path belonging to the current machine
selected_path = None
for path in paths:
  if is_localhost(path.split(":")[0]):
    selected_path = path.split(":", 1)[1]
    break

if not selected_path:
    print("Could not find a matching path for this hostname.")
    exit(1)

print(f"Local path detected: {selected_path}")

# Execute rsync for all other paths
for path in paths:
    host, target_path = path.split(":", 1)

    # Skip the local machine's path
    if is_localhost(host):
        continue

    if action == '-u':  # Upload
      command = f"rsync -avh {rsync_extra_args} {selected_path} {host}:{target_path}"
    elif action == '-d':  # Download
      command = f"rsync -avh {rsync_extra_args} {host}:{target_path} {selected_path}"
    else:
      continue

    print(f"Running: {command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"Failed to execute: {command}")

