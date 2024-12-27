import curses
import os

def generate_commands(host, selection, current_directory):
    commands = []
    if selection & 3:
        rsync_extra_args = "--delete" if selection & 2 else ""
        commands.append(f"ssh {host} 'mkdir -p {current_directory}'")
        commands.append(f"rsync -avh {rsync_extra_args} {host}:{current_directory} {current_directory}")
    if selection & 12:
        rsync_extra_args = "--delete" if selection & 8 else ""
        commands.append(f"ssh {host} 'mkdir -p {current_directory}'")
        commands.append(f"rsync -avh {rsync_extra_args} {current_directory} {host}:{current_directory}")
    return commands

def toggle_menu(screen, hosts):
    sel = [0] * len(hosts)  # 0: not selected, 1: download, 2: upload, 3: download and upload
    ci = 0

    while True:
        screen.clear()
        screen.addstr("'d' for download, 'u' for upload, capital for --delete, and press ENTER when done (ESC to exit):\n\n")

        for idx, host in enumerate(hosts):
            if idx == ci:
                screen.attron(curses.A_REVERSE)

            status = list("[ / ]")
            if sel[idx] & 2:
                status[3] = "D"
            elif sel[idx] & 1:
                status[3] = "d"
            if sel[idx] & 8:
                status[1] = "U"
            elif sel[idx] & 4:
                status[1] = "u"
            marker = "".join(status)

            screen.addstr(f"{marker} {host}\n")

            if idx == ci:
                screen.attroff(curses.A_REVERSE)

        key = screen.getch()

        if key == ord('k') and ci > 0:
            ci -= 1
        elif key == ord('j') and ci < len(hosts) - 1:
            ci += 1
        elif key == ord('d'):
            sel[ci] = (sel[ci] & ~3) | ((sel[ci] & 1)^1)
        elif key == ord('D'):
            sel[ci] = (sel[ci] & ~3) | ((sel[ci] & 2)^2)
        elif key == ord('u'):
            sel[ci] = (sel[ci] & ~12) | ((sel[ci] & 4)^4)
        elif key == ord('U'):
            sel[ci] = (sel[ci] & ~12) | ((sel[ci] & 8)^8)
        elif key == ord('\n') or key == 10:
            break
        elif key == 27:  # ESC key
            return []

    return [(host, sel[idx]) for idx, host in enumerate(hosts) if sel[idx] != 0]

def main(hosts):
    current_directory = os.getcwd()

    selected_hosts = curses.wrapper(toggle_menu, hosts)
    commands = []

    for host, selection in selected_hosts:
        commands.extend(generate_commands(host, selection, current_directory))

    print("\nCommands to be executed:")
    for command in commands:
        print(command)

    confirm = input("\nDo you want to execute these commands? (y/n): ").strip().lower()
    if confirm == 'y':
        for command in commands:
            os.system(command)

if __name__ == "__main__":
    hosts = [
        "v1",
        "pure-c2",
        "v21",
        "v23",
        "10.204.100.61"
    ]
    main(hosts)

