#!/usr/bin/env python3
import argparse
import subprocess
import os
from rich.live import Live
from rich.console import Console
from rich.table import Table
from rich.text import Text
from multiprocessing import Pool
from rich import box
from rich.spinner import Spinner
from pathlib import Path

if "clusters" not in os.environ:
  clusters = ["v%d" % i for i in range(1, 24)]
else:
  clusters = os.environ["clusters"].split(",")

cluster_status = {cluster: "waiting" for cluster in clusters}
console = Console()

SCRIPT_PATH = Path.home() / "dotfiles" / "scripts" / "gpu_info3.py"

def showGPUs_fn(cluster):
    # build the ssh command
    ssh_cmd = [
        "ssh",
        cluster,
        "python3",       # or just "python" if that's what your remote uses
        "-u",            # unbuffered
        "-",             # read program from stdin
        "--ram",         # your script's flags
        "--user",
        # "--spec",
    ]

    try:
        # read the script once per call
        script_text = SCRIPT_PATH.read_text()
        # run ssh, piping in the script
        proc = subprocess.run(
            ssh_cmd,
            input=script_text,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=120,        # avoid hanging forever
        )
        # prefer stdout; fall back to stderr if nothing came over stdout
        raw = proc.stdout.strip() or proc.stderr.strip()
        # status = raw.replace("\n", " | ")  # squash multi-line into one row
        status = raw
    except Exception as e:
        status = f"Error: {e}"

    return cluster, status
# def showGPUs_fn(cluster):
    # status = ...
  # return cluster, status

def update_table():
    table = Table(title="", expand=True, padding=(0, 0))
    # table.row_styles = ["none", "dim"]
    table.show_lines = True
    table.box = box.SIMPLE
    table.add_column("#", justify="right", no_wrap=True)
    table.add_column("Status", justify="left", no_wrap=False, ratio=1)

    for cl, st in cluster_status.items():
        if st == "waiting":
          # Use a spinner for the "waiting" state
            spinner = Spinner("point", text="")
            table.add_row(cl, spinner)
        else:
            table.add_row(cl, Text.from_ansi(st))
    return table

def main():
  with Live(update_table(), console=console, refresh_per_second=10, transient=False) as live:
    with Pool(len(clusters)) as p:
      for cluster, status in p.imap_unordered(showGPUs_fn, clusters):
        cluster_status[cluster] = status
        live.update(update_table())

if __name__== "__main__":
  main()
