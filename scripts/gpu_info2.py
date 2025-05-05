import subprocess
import sys
import math

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
            parts = [p.strip() for p in line.split(',')]
            if len(parts) != 5:
                continue
            idx, uuid, name, gpu_used_mb, gpu_total_mb = parts
            uuid_to_info[uuid] = (idx, name,
                                  int(gpu_used_mb), int(gpu_total_mb))
    except Exception as e:
        print(f"[Error] GPU query failed: {e}")
    return uuid_to_info


def color_bar(used, total, width=20):
    ratio = used/total if total else 0
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
    import re
    return re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', s)


def get_gpu_processes():
    info = get_gpu_uuid_to_info()
    try:
        # Query each process's GPU memory usage
        cmd = ['nvidia-smi',
               '--query-compute-apps=gpu_uuid,pid,process_name,used_memory',
               '--format=csv,noheader,nounits']
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        lines = [l.strip() for l in r.stdout.splitlines() if l.strip()]

        headers = ['GPU', 'Usage', 'User', 'Mem', 'Process Name', 'PID']
        rows = []
        current_gpu = None

        for line in lines:
            parts = [p.strip() for p in line.split(',')]
            if len(parts) < 4 or not parts[1].isdigit():
                continue
            uuid, pid, pname, proc_used_mb = parts[0], parts[1], ','.join(parts[2:-1]), parts[-1]
            idx, name, gpu_used_mb, gpu_total_mb = info.get(uuid, ('?', 'Unknown', 0, 0))
            user = subprocess.run(
                ['ps', '-o', 'user=', '-p', pid],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            ).stdout.strip()

            # Convert to GB
            p_used_gb = int(proc_used_mb) / 1024
            g_used_gb = gpu_used_mb / 1024
            g_tot_gb = gpu_total_mb / 1024

            # Prepare Usage and Memory columns
            if idx != current_gpu:
                gpu_cell = f"{idx}: {name.replace('NVIDIA ', '').replace('GeForce ', '')}"
                usage_cell = f"{g_used_gb:4.1f} / {g_tot_gb:2.0f}GB ({(g_used_gb/g_tot_gb)*100:4.1f}%) " + color_bar(gpu_used_mb, gpu_total_mb)
                current_gpu = idx
            else:
                gpu_cell = ''
                usage_cell = ''

            memory_cell = f"{p_used_gb:4.1f}G"

            rows.append([gpu_cell, usage_cell, user, memory_cell, pname, pid])

        # Compute column widths
        widths = [len(h) for h in headers]
        for r in rows:
            for i, cell in enumerate(r):
                l = len(strip_ansi(str(cell)))
                if l > widths[i]:
                    widths[i] = l

        sep = '+' + '-'.join('-'*(w+2) for w in widths) + '+'

        # Print header
        print(sep)
        print('|' + ' '.join(f" {headers[i].ljust(widths[i])} " for i in range(len(headers))) + '|')
        print(sep.replace("-", "="))

        # Print each row, separating GPU blocks
        for i, r in enumerate(rows):
            line = '|' + ' '.join(
                f" {str(r[j]).rjust(widths[j])} " if j in [1, 3, 5] else f" {str(r[j]).ljust(widths[j])} "
                for j in range(len(headers))
            ) + '|'
            print(line)
            next_gpu = rows[i+1][0] if i+1 < len(rows) else None
            if next_gpu:
                print(sep)

        print(sep)
    except Exception as e:
        print(f"Error: {e}")


def print_vram_usage(mem_thresh=10):
    info = get_gpu_uuid_to_info()
    outstr = ""
    # tmp = 0
    for uuid, (idx, name, used_mb, total_mb) in info.items():
        pct = (used_mb / total_mb) * 100 if total_mb else 0
        # pct = (tmp +1)/ 4 * 100
        # tmp += 1
        pct = max(0, min(round(pct), 100))

        if pct < mem_thresh:
            # pure green background (R=0, G=5, B=0 → index=16+36*0+6*5+0=46)
            bg = 46
        else:
            # normalize between [0..1] over the 15–100% range
            norm = (pct - mem_thresh) / (100 - mem_thresh)
            # linearly ramp G from 5→0
            g_level = int(round((1 - norm) * 5))
            # keep R=5, B=0 → index=16 + 36*R + 6*G + B
            bg = 16 + 36*5 + 6*g_level

        # black text (38;5;0) on our bg
        outstr += f"\033[38;5;0m\033[48;5;{bg}m{pct:02d}\033[0m "

    print(outstr)


if __name__ == '__main__':
    if '--ram' in sys.argv:
        print_vram_usage()
    else:
        get_gpu_processes()

