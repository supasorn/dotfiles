import subprocess

def get_gpu_uuid_to_info():
    """
    Returns a dict mapping GPU UUIDs to (index, name, used_mem_MB, total_mem_MB).
    """
    uuid_to_info = {}
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=index,uuid,name,memory.used,memory.total', '--format=csv,noheader,nounits'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        lines = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        for line in lines:
            parts = [p.strip() for p in line.split(',')]
            if len(parts) == 5:
                index, uuid, name, mem_used, mem_total = parts
                uuid_to_info[uuid] = (index, name, int(mem_used), int(mem_total))
            else:
                print(f"[Warning] Unexpected format in line: '{line}' (skipping)")
    except Exception as e:
        print(f"[Error] Failed to get GPU uuid to memory mapping: {e}")
    return uuid_to_info

def color_bar(used, total, bar_width=20):
    """
    Returns a colored bar string showing usage percentage.
    """
    ratio = used / total if total > 0 else 0
    filled_length = int(bar_width * ratio)
    empty_length = bar_width - filled_length
    percent_display = f"{ratio * 100:.1f}%"

    if ratio < 0.4:
        color = "\033[92m"  # Green
    elif ratio < 0.8:
        color = "\033[93m"  # Yellow
    else:
        color = "\033[91m"  # Red
    reset = "\033[0m"

    bar = f"{percent_display} {color}{'█' * filled_length}{' ' * empty_length}{reset}"
    return bar

def strip_ansi(s):
    """
    Removes ANSI color codes to calculate visible length.
    """
    import re
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', s)

def get_gpu_processes():
    uuid_to_info = get_gpu_uuid_to_info()
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-compute-apps=gpu_uuid,pid,process_name', '--format=csv,noheader'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        lines = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]

        table_rows = []
        headers = ['GPU', 'PID', 'User', 'Process Name', 'Used', 'Total', 'Usage']
        table_rows.append(headers)

        # Track which GPUs we've already shown usage for
        shown_gpu_indices = set()

        for line in lines:
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 3 and parts[1].isdigit():
                gpu_uuid, pid, pname = parts[0], parts[1], ','.join(parts[2:])
                gpu_info = uuid_to_info.get(gpu_uuid, ('Unknown', 'Unknown', 0, 0))
                gpu_index, gpu_name, mem_used_mb, mem_total_mb = gpu_info
                ps_result = subprocess.run(
                    ['ps', '-o', 'user=', '-p', pid],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                user = ps_result.stdout.strip()

                # Convert MiB to GB
                mem_used_gb = mem_used_mb / 1024
                mem_total_gb = mem_total_mb / 1024
                used_display = f"{mem_used_gb:.1f}"
                total_display = f"{mem_total_gb:.1f}"

                # GPU # column: format as "0: NVIDIA ..."
                gpu_display = f"{gpu_index}: {gpu_name.replace('NVIDIA ', '').replace('GeForce ', '')}"

                # Only show RAM/bar once per GPU
                if gpu_index not in shown_gpu_indices:
                    bar = color_bar(mem_used_mb, mem_total_mb)
                    shown_gpu_indices.add(gpu_index)
                else:
                    used_display = ''
                    total_display = ''
                    bar = ''

                table_rows.append([gpu_display, pid, user, pname, used_display, total_display, bar])

        if len(table_rows) > 1:
            # Calculate max width for each column (including bar)
            col_widths = [0] * len(headers)
            for row in table_rows:
                for i, cell in enumerate(row):
                    # For bar: strip ANSI color codes for length
                    visible_len = len(strip_ansi(str(cell)))
                    col_widths[i] = max(col_widths[i], visible_len)

            # Print table with borders
            separator = '+'.join('-' * (w + 2) for w in col_widths)
            print(f"+{separator}+")
            for i, row in enumerate(table_rows):
                row_str = '|'.join(
                    f" {str(cell).rjust(col_widths[j]) if j in [4,5] else str(cell).ljust(col_widths[j])} " for j, cell in enumerate(row)
                )
                print(f"|{row_str}|")
                if i == 0:
                    print(f"+{separator}+")
            print(f"+{separator}+")
        else:
            print("No GPU processes found.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_gpu_processes()

