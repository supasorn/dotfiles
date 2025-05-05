import subprocess
from collections import defaultdict
import re
import argparse

def get_gpu_uuid_to_info():
    uuid_to_info = {}
    try:
        result = subprocess.run(
            ['nvidia-smi',
             '--query-gpu=index,uuid,name,memory.used,memory.total',
             '--format=csv,noheader,nounits'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            idx, uuid, name, used_mb, total_mb = [p.strip() for p in line.split(',')]
            uuid_to_info[uuid] = {
                'idx': int(idx),
                'name': name,
                'used_mb': int(used_mb),
                'total_mb': int(total_mb),
            }
    except Exception as e:
        print(e.stdout)
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


def get_gpu_processes():
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
        usage_str = colorUsedVRAM(pct) + f" {used_gb:4.1f}/" + colorTotalVRAM(round(total_mb / 1024))
                    

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
            f" {str(r[j]).rjust(widths[j])} " if j in [1, 3, 5] else f" {str(r[j]).ljust(widths[j])} "
            for j in range(len(headers))
        ) + '|'
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

def colorUsedVRAM(pct, mem_thresh=15):
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

def print_vram_usage(mem_thresh=15, show_spec=False):
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

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Show GPU VRAM usage (and optional owners/specs)."
    )
    parser.add_argument('--compact', action='store_true',
                        help='Show compact info')
    parser.add_argument('--spec', action='store_true',
                        help="Show GPU name and total VRAM specs")
    parser.add_argument('--threshold', type=int, default=15,
                        help='Threshold below which usage is pure green (default: 15%%)')
    args = parser.parse_args()

    if args.compact:
        print_vram_usage(mem_thresh=args.threshold,
                         show_spec=args.spec)
    else:
        get_gpu_processes()

