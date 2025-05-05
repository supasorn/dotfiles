#!/usr/bin/env python3
import argparse
import subprocess

def get_gpu_uuid_to_info():
    """
    Returns dict mapping GPU UUID to tuple:
      (index, name, used_mb, total_mb)
    """
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
            uuid_to_info[uuid] = (
                int(idx), name,
                int(used_mb), int(total_mb)
            )
    except subprocess.CalledProcessError:
        pass
    return uuid_to_info

def get_gpu_process_users():
    """
    Returns dict mapping GPU UUID -> set of usernames
    that have compute processes on that GPU.
    """
    users_map = {}
    try:
        # ask nvidia-smi for pid and gpu_uuid of each compute process
        res = subprocess.run(
            ['nvidia-smi',
             '--query-compute-apps=pid,gpu_uuid',
             '--format=csv,noheader,nounits'],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, check=True
        )
        for line in res.stdout.splitlines():
            pid_str, gpu_uuid = [x.strip() for x in line.split(',')]
            # look up the user that owns this pid
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

def print_vram_usage(mem_thresh=15, show_user=False):
    info = get_gpu_uuid_to_info()
    gpu_users = get_gpu_process_users() if show_user else {}

    out_items = []
    for uuid, (idx, name, used_mb, total_mb) in info.items():
        pct = (used_mb / total_mb) * 100 if total_mb else 0
        pct = max(0, min(round(pct), 100))

        # choose background:
        if pct < mem_thresh:
            # pure green: R=0,G=5,B=0 → index=46
            bg = 46
        else:
            # interpolate yellow→red by ramping G 5→0 at R=5,B=0
            norm = (pct - mem_thresh) / (100 - mem_thresh)
            g_level = int(round((1 - norm) * 5))
            bg = 16 + 36*5 + 6*g_level  # R=5, G=g_level, B=0

        colored_pct = f"\033[38;5;0m\033[48;5;{bg}m{pct:02d}%\033[0m"

        if show_user:
            users = sorted(gpu_users.get(uuid, []))
            if users:
                colored_pct = f"{colored_pct} {', '.join(users)}"

        out_items.append(colored_pct)

    print(" | ".join(out_items))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Show GPU VRAM usage (and optional owners)."
    )
    parser.add_argument(
        '--ram', action='store_true',
        help='Display VRAM usage percentages'
    )
    parser.add_argument(
        '--user', action='store_true',
        help="Also show which users have processes on each GPU"
    )
    parser.add_argument(
        '--threshold', type=int, default=15,
        help='Threshold below which usage is pure green (default: 15%%)'
    )
    args = parser.parse_args()

    if args.ram:
        print_vram_usage(
            mem_thresh=args.threshold,
            show_user=args.user
        )

