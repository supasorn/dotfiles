import curses
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

def build_user_data():
    """
    Fetches data for all logged-in users.
    """
    users = get_logged_in_users()
    user_data = []

    for user in users:
        processes, mem_kb = get_processes_for_user(user)
        mem_gb = mem_kb / (1024 * 1024)
        proc_data = []
        for pid, cmd, rss_kb in processes:
            proc_gb = rss_kb / (1024 * 1024)
            proc_data.append((pid, cmd, proc_gb))
        proc_data.sort(key=lambda x: x[2], reverse=True)
        user_data.append({'user': user, 'mem_gb': mem_gb, 'proc_count': len(proc_data), 'processes': proc_data[:50]})

    # Sort users by total memory descending
    user_data.sort(key=lambda x: x['mem_gb'], reverse=True)
    return user_data

def main(stdscr):
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(False)
    stdscr.keypad(True)

    user_data = build_user_data()
    current_idx = 0
    expanded = False

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if not expanded:
            stdscr.addstr(0, 0, "Logged-in Users (j/k to move, Enter to expand, q to quit):")
            for idx, ud in enumerate(user_data):
                line = f"{ud['user']:<15} - {ud['mem_gb']:.2f} GB total"
                if idx == current_idx:
                    stdscr.addstr(idx + 2, 0, line, curses.A_REVERSE)
                else:
                    stdscr.addstr(idx + 2, 0, line)
        else:
            ud = user_data[current_idx]
            stdscr.addstr(0, 0, f"User: {ud['user']} (Enter to collapse, q to quit)")
            stdscr.addstr(1, 0, f"Total Memory Usage: {ud['mem_gb']:.2f} GB")
            stdscr.addstr(2, 0, f"Number of Processes: {ud['proc_count']}")
            stdscr.addstr(4, 0, f"Top {len(ud['processes'])} Processes:")
            stdscr.addstr(5, 0, f"{'PID':<8} {'Process':<25} {'Mem (GB)':>10}")
            stdscr.addstr(6, 0, f"{'-'*8} {'-'*25} {'-'*10}")
            for idx_p, (pid, cmd, proc_gb) in enumerate(ud['processes']):
                stdscr.addstr(7 + idx_p, 0, f"{pid:<8} {cmd:<25} {proc_gb:>10.3f}")

        stdscr.refresh()
        key = stdscr.getch()

        if key == ord('q'):
            break
        elif key == ord('j') and not expanded:
            current_idx = (current_idx + 1) % len(user_data)
        elif key == ord('k') and not expanded:
            current_idx = (current_idx - 1) % len(user_data)
        elif key in (curses.KEY_ENTER, 10, 13):  # Enter key
            expanded = not expanded

if __name__ == "__main__":
    curses.wrapper(main)

