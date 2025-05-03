import subprocess

def get_logged_in_users():
    """
    Returns a set of currently logged-in users.
    """
    result = subprocess.run(['who'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    users = set()
    for line in result.stdout.strip().split('\n'):
        if line:
            parts = line.split()
            if len(parts) >= 1:
                users.add(parts[0])
    return users

def get_processes_for_user(user):
    """
    Returns a list of (PID, process name, memory usage in KB) for the given user,
    and the total memory usage in KB.
    """
    result = subprocess.run(
        ['ps', '-u', user, '-o', 'pid,comm,rss='],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    processes = []
    total_kb = 0
    for line in result.stdout.strip().split('\n'):
        if line.strip():
            parts = line.strip().split(None, 2)
            if len(parts) == 3:
                pid, cmd, rss = parts
                if rss.strip().isdigit():
                    rss_kb = int(rss.strip())
                    total_kb += rss_kb
                    processes.append((pid, cmd, rss_kb))
    return processes, total_kb

def main():
    users = get_logged_in_users()
    user_data = []

    for user in users:
        processes, mem_kb = get_processes_for_user(user)
        mem_gb = mem_kb / (1024 * 1024)
        proc_data = []
        for pid, cmd, rss_kb in processes:
            proc_gb = rss_kb / (1024 * 1024)
            proc_data.append((pid, cmd, proc_gb))
        # Sort processes by memory descending
        proc_data.sort(key=lambda x: x[2], reverse=True)
        user_data.append((user, mem_gb, len(proc_data), proc_data[:20]))  # Only keep top 20

    # Sort users by total memory descending
    user_data.sort(key=lambda x: x[1], reverse=True)

    # Print detailed summary for each user first
    for user, mem_gb, proc_count, processes in user_data:
        print(f"User: {user}")
        print(f"Total Memory Usage: {mem_gb:.2f} GB")
        print(f"Number of Processes: {proc_count}")
        if processes:
            print(f"Top {len(processes)} Processes:")
            print(f"  {'PID':<8} {'Process':<25} {'Mem (GB)':>10}")
            print(f"  {'-'*8} {'-'*25} {'-'*10}")
            for pid, cmd, proc_gb in processes:
                print(f"  {pid:<8} {cmd:<25} {proc_gb:>10.3f}")
            print()
        else:
            print("  No processes found.\n")

    # Print the user summary table at the end
    print("\nSummary Table:")
    print(f"{'User':<15} {'Total Memory (GB)':>20}")
    print('-' * 38)
    for user, mem_gb, proc_count, _ in user_data:
        print(f"{user:<15} {mem_gb:>20.2f}")

if __name__ == "__main__":
    main()

