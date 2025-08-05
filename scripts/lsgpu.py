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
import re
import sys
from collections import defaultdict

if "clusters" not in os.environ:
  clusters = ["v%d" % i for i in range(1, 25)]
else:
  clusters = os.environ["clusters"].split(",")

console = Console()

def showGPUs_fn(cluster):
    # build the ssh command

    subargs = sys.argv[1:].copy()

    ssh_cmd = [
        "ssh",
        cluster,
        "python3",       # or just "python" if that's what your remote uses
        "-u",            # unbuffered
        "-",             # read program from stdin
        "--local",
        "--compact",
        *subargs,  # pass any args to the script
    ]

    try:
        # read the script once per call
        with open(__file__, 'r') as f:
            script_text = f.read()

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
    table = Table(title="", expand=True, padding=(0, 0), show_header=False)
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

def lsgpu():
  with Live(update_table(), console=console, refresh_per_second=10, transient=False) as live:
    with Pool(len(clusters)) as p:
      for cluster, status in p.imap_unordered(showGPUs_fn, clusters):
        cluster_status[cluster] = status
        live.update(update_table())

def get_gpu_uuid_to_info():
    uuid_to_info = {}
    try:
        result = subprocess.run(
            ['nvidia-smi',
             '--query-gpu=index,uuid,name,memory.used,memory.total',
             '--format=csv,noheader,nounits'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"{result.stdout}")

        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            if len(line.split(',')) == 5:
                idx, uuid, name, used_mb, total_mb = [p.strip() for p in line.split(',')]
                uuid_to_info[uuid] = {
                    'idx': int(idx),
                    'name': name,
                    'used_mb': int(used_mb),
                    'total_mb': int(total_mb),
                }
            else:
                match = re.search(r'GPU(\d+)', line)
                if match:
                    idx = int(match.group(1))
                else:
                    idx = -1

                uuid_to_info["e"] = {
                    'idx': idx,
                    'name': "Error",
                    'used_mb': 0,
                    'total_mb': 0,
                }


    except Exception as e:
        print(e)
    return uuid_to_info

def color_bar(used, total, width=20):
    ratio = used / total if total else 0
    filled = int(width * ratio)
    empty = width - filled
    if ratio < 0.4:
        col = "\033[92m"
    elif ratio < 0.8:
        col = "\033[93m"
    else:
        col = "\033[91m"
    reset = "\033[0m"
    return f"{col}{'█'*filled}{' '*empty}{reset}"

def strip_ansi(s):
    return re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', s)

def truncate_prefix(s: str, max_len: int = 40) -> str:
    # if it's already short enough, just return it
    if len(s) <= max_len:
        return s
    # otherwise take the last (max_len-3) chars and prepend "..."
    return '...' + s[-(max_len - 3):]

                  

def visible_len(s):
    ANSI_ESCAPE = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return len(ANSI_ESCAPE.sub('', s))

def rjust_ansi(s, width):
    vis_len = visible_len(s)
    padding = max(0, width - vis_len)
    return ' ' * padding + s

def ljust_ansi(s, width):
    vis_len = visible_len(s)
    padding = max(0, width - vis_len)
    return s + ' ' * padding


def get_gpu_processes(mem_thresh):
    info = get_gpu_uuid_to_info()

    # Build a map: uuid -> list of processes
    proc_map = defaultdict(list)
    try:
        r = subprocess.run(
            ['nvidia-smi',
             '--query-compute-apps=gpu_uuid,pid,process_name,used_memory',
             '--format=csv,noheader,nounits'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        for line in r.stdout.splitlines():
            parts = [p.strip() for p in line.split(',')]
            if len(parts) != 4 or not parts[1].isdigit():
                continue
            uuid, pid, pname, proc_used_mb = parts
            # lookup user
            user = subprocess.run(
                ['ps', '-o', 'user=', '-p', pid],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            ).stdout.strip()
            proc_map[uuid].append({
                'pid': pid,
                'pname': pname,
                'user': user,
                'used_mb': int(proc_used_mb),
            })
    except Exception:
        pass

    # Prepare table structure
    headers = ['GPU', 'Usage %GB', 'User', '  GB', 'Process Name', 'PID']
    rows = []

    # Iterate GPUs in index order
    for uuid, g in sorted(info.items(), key=lambda x: x[1]['idx']):
        idx = g['idx']
        name = g['name'].replace('NVIDIA ', '').replace('GeForce ', '')
        used_mb = g['used_mb']
        total_mb = g['total_mb']
        used_gb = used_mb / 1024

        pct = (used_mb / total_mb) * 100 if total_mb else 0
        pct = max(0, min(round(pct), 100))
        if pct == 100:
            pct = 99
        # usage_str = colorUsedVRAM(pct) + f"{used_gb:4.1f} / {tot_gb:2.0f}GB " \
                    # + color_bar(used_mb, total_mb)
        usage_str = colorUsedVRAM(pct, mem_thresh) + f" {used_gb:4.1f}/" + colorTotalVRAM(round(total_mb / 1024))
                    

        procs = proc_map.get(uuid, [])
        if procs:
            # first process row shows GPU and Usage
            first = procs[0]
            rows.append([
                f"{idx}: {name}",
                usage_str,
                first['user'],
                f"{first['used_mb']/1024:4.1f}",
                truncate_prefix(first['pname']),
                first['pid'],
            ])
            # subsequent processes indent GPU/Usage columns
            for p in procs[1:]:
                rows.append([
                    '',
                    '',
                    p['user'],
                    f"{p['used_mb']/1024:4.1f}",
                    truncate_prefix(p['pname']),
                    p['pid'],
                ])
        else:
            # no processes: single blank row
            rows.append([
                f"{idx}: {name}",
                usage_str,
                '',
                '',
                '',
                '',
            ])

    # Compute column widths
    widths = [len(h) for h in headers]
    for r in rows:
        for i, cell in enumerate(r):
            l = len(strip_ansi(str(cell)))
            widths[i] = max(widths[i], l)

    sep = '+' + '+'.join('-'*(w+2) for w in widths) + '+'
    hdr = '|' + '|'.join(f" {headers[i].ljust(widths[i])} " for i in range(len(headers))) + '|'
    sep_eq = sep.replace('-', '=')

    # Print table
    print(sep)
    print(hdr)
    print(sep_eq)
    for r in rows:
        if r[0] != '' and r != rows[0]:
            print(sep)
        line = '|' + '|'.join(
            f" {rjust_ansi(str(r[j]), widths[j])} " if j in [3, 5] else f" {ljust_ansi(str(r[j]), widths[j])} "
            for j in range(len(headers))
        ) + '|'
        xx = r[1] 
        # print(rjust_ansi(str(r[1]), 30)+"]")
        # print(widths[1])
        print(line)
        # separate GPU blocks
    print(sep)

def get_gpu_process_users():
    users_map = {}
    try:
        res = subprocess.run(
            ['nvidia-smi',
             '--query-compute-apps=pid,gpu_uuid',
             '--format=csv,noheader,nounits'],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, check=True
        )
        for line in res.stdout.splitlines():
            pid_str, gpu_uuid = [x.strip() for x in line.split(',')]
            user_res = subprocess.run(
                ['ps', '-o', 'user=', '-p', pid_str],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                text=True
            )
            user = user_res.stdout.strip()
            if user:
                users_map.setdefault(gpu_uuid, set()).add(user)
    except Exception as e:
        pass
    return users_map

def colorUsedVRAM(pct, mem_thresh):
    if pct < mem_thresh:
        bg = 46  # pure green
    else:
        norm = (pct - mem_thresh) / (100 - mem_thresh)
        g_level = int(round((1 - norm) * 5))
        bg = 16 + 36*5 + 6*g_level  # yellow->red ramp

    return f"\033[38;5;0m\033[48;5;{bg}m{pct:02d}\033[0m"

def colorTotalVRAM(gb):
    ansi_bg = f"\x1b[48;2;{0};{54};{127}m"
    ansi_fg = "\x1b[38;2;255;255;255m"
    reset   = "\x1b[0m"
    return f"{ansi_bg}{ansi_fg}{gb}{reset}"

def print_vram_usage(mem_thresh, show_spec=False):
    info = get_gpu_uuid_to_info()
    gpu_users = get_gpu_process_users() 

    pct_items = []
    idx_list = []
    user_items = []
    spec_items = []
    vram_items = []

    # sort by GPU index
    for uuid, g  in sorted(info.items(), key=lambda x: x[1]['idx']):
        (idx, name, used_mb, total_mb) = (
            g['idx'],
            g['name'],
            g['used_mb'],
            g['total_mb']
        )
        # percentage
        pct = (used_mb / total_mb) * 100 if total_mb else 0
        pct = max(0, min(round(pct), 100))

        pct_items.append(colorUsedVRAM(pct, mem_thresh))
        idx_list.append(idx)

        users = sorted(gpu_users.get(uuid, []))
        user_items.append(','.join(users))

        if show_spec:
            gb = round(total_mb / 1024)
            clean_name = name.replace("NVIDIA", "").replace("GeForce", "").strip()
            spec_items.append(f"{idx}:{clean_name}")
            vram_items.append(colorTotalVRAM(gb))

    # build base output: percentages
    out = ' '.join(pct_items)
    out += ' ' + ' | '.join(f"{i}:{u}" for i, u in zip(idx_list, user_items))

    # append spec
    if show_spec:
        out += "\n"
        out += ' '.join(vram_items)
        # out += ' :' + ' '.join(vram_items)
        out += ' ' + ' | '.join(spec_items)

    print(out)


def expand_nodes(nodes_str: str):
    out = []
    for part in nodes_str.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-', 1)
            # extract the non-digit prefix and the numeric suffix
            m1 = re.match(r'([^\d]+)(\d+)$', start)
            m2 = re.match(r'([^\d]+)(\d+)$', end)
            if m1 and m2 and m1.group(1) == m2.group(1):
                prefix = m1.group(1)
                s = int(m1.group(2))
                e = int(m2.group(2))
                # build v2, v3, …, v5
                out.extend(f"{prefix}{i}" for i in range(s, e+1))
                continue
        # fallback: just append whatever it was
        out.append(part)
    return out

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Show GPU VRAM usage (and optional owners/specs)."
    )
    parser.add_argument('--local', action='store_true',
                        help='Show info of current node')
    parser.add_argument('--compact', action='store_true',
                        help='Show compact info')
    parser.add_argument('--full', action='store_true',
                        help='Show full info')
    parser.add_argument('--spec', action='store_true',
                        help="Show GPU name and total VRAM specs")
    parser.add_argument('--threshold', type=int, default=15,
                        help='Threshold below which usage is pure green (default: 15%%)')
    parser.add_argument('--nodes', default="", help='compute nodes')
    args = parser.parse_args()

    if args.nodes:
        clusters = expand_nodes(args.nodes)


    cluster_status = {cluster: "waiting" for cluster in clusters}

    if args.local:
        if args.compact and not args.full:
            print_vram_usage(mem_thresh=args.threshold,
                             show_spec=args.spec)
        else:
            get_gpu_processes(mem_thresh=args.threshold)
    else:
        lsgpu()

