#!/usr/bin/env python3
import argparse
import subprocess

def get_gpu_uuid_to_info():
    uuid_to_info = {}
    try:
        result = subprocess.run(
            ['nvidia-smi',
             '--query-gpu=index,uuid,name,memory.used,memory.total',
             '--format=csv,noheader,nounits'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, check=True
        )
        for line in result.stdout.splitlines():
            idx, uuid, name, used_mb, total_mb = [p.strip() for p in line.split(',')]
            uuid_to_info[uuid] = (int(idx), name, int(used_mb), int(total_mb))
    except subprocess.CalledProcessError:
        pass
    return uuid_to_info

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
    except subprocess.CalledProcessError:
        pass
    return users_map

def print_vram_usage(mem_thresh=15, show_user=False, show_spec=False):
    info = get_gpu_uuid_to_info()
    gpu_users = get_gpu_process_users() if show_user else {}

    pct_items = []
    idx_list = []
    user_items = []
    spec_items = []
    vram_items = []

    # sort by GPU index
    for uuid, (idx, name, used_mb, total_mb) in sorted(info.items(), key=lambda x: x[1][0]):
        # percentage
        pct = (used_mb / total_mb) * 100 if total_mb else 0
        pct = max(0, min(round(pct), 100))

        # choose background color
        if pct < mem_thresh:
            bg = 46  # pure green
        else:
            norm = (pct - mem_thresh) / (100 - mem_thresh)
            g_level = int(round((1 - norm) * 5))
            bg = 16 + 36*5 + 6*g_level  # yellow->red ramp

        # formatted percent (no % sign)
        colored_pct = f"\033[38;5;0m\033[48;5;{bg}m{pct:02d}\033[0m"
        pct_items.append(colored_pct)
        idx_list.append(idx)

        # collect users
        if show_user:
            users = sorted(gpu_users.get(uuid, []))
            user_items.append(','.join(users))

        # collect spec: clean name and total GB (rounded)
        if show_spec:
            gb = round(total_mb / 1024)
            clean_name = name.replace("NVIDIA", "").replace("GeForce", "").strip()
            r, g, b = (0, 54, 127)
            # build the ANSI-wrapped string
            ansi_bg = f"\x1b[48;2;{r};{g};{b}m"
            ansi_fg = "\x1b[38;2;255;255;255m"
            reset   = "\x1b[0m"

            spec_items.append(f"{idx}:{clean_name}")
            vram_items.append(f"{ansi_bg}{ansi_fg}{gb}{reset}")

    # build base output: percentages
    out = ' '.join(pct_items)

    # append users
    if show_user:
        out += ' ' + ' | '.join(f"{i}:{u}" for i, u in zip(idx_list, user_items))

    # append spec
    out += "\n"
    if show_spec:
        out += ' '.join(vram_items)
        # out += ' :' + ' '.join(vram_items)
        out += ' ' + ' | '.join(spec_items)

    print(out)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Show GPU VRAM usage (and optional owners/specs)."
    )
    parser.add_argument('--ram', action='store_true',
                        help='Display VRAM usage percentages')
    parser.add_argument('--user', action='store_true',
                        help="Also show which users have processes on each GPU")
    parser.add_argument('--spec', action='store_true',
                        help="Show GPU name and total VRAM specs")
    parser.add_argument('--threshold', type=int, default=15,
                        help='Threshold below which usage is pure green (default: 15%%)')
    args = parser.parse_args()

    if args.ram:
        print_vram_usage(mem_thresh=args.threshold,
                         show_user=args.user,
                         show_spec=args.spec)

