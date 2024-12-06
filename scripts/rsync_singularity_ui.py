import curses
import socket
import psutil
import os

def is_localhost(alias):
    try:
        ip_address = socket.gethostbyname(alias)
        local_ips = {addr.address for iface in psutil.net_if_addrs().values() for addr in iface}
        return ip_address in local_ips
    except socket.gaierror:
        # If the alias cannot be resolved, return False
        return False

# Identify the path belonging to the current machine
paths = [
    "v1:/home2/supasorn/singularity/",
    "pure-c2:/mnt/data/supasorn/singularity/",
    "v21:/home2/supasorn/singularity/",
    "v23:/home2/supasorn/singularity/",
    "_:/ist-nas/users/supasorn/singularity/",
    "_:/ist/users/supasorn/singularity/"
]

selected_path = None
for path in paths:
    if is_localhost(path.split(":")[0]):
        selected_path = path.split(":", 1)[1]
        break

if not selected_path:
    print("Could not find a matching path for this hostname.")
    exit(1)

print(f"Local path detected: {selected_path}")

def toggle_menu(screen, paths):
    sel = [0] * len(paths)  # 0: not selected, 1: download, 2: upload, 3: download and upload
    ci = 0

    while True:
        screen.clear()
        screen.addstr("'d' for download, 'u' for upload, capital for --delete, and press ENTER when done (ESC to exit):\n\n")

        for idx, path in enumerate(paths):
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

            screen.addstr(f"{marker} {path}\n")

            if idx == ci:
                screen.attroff(curses.A_REVERSE)

        key = screen.getch()

        if key == ord('k') and ci > 0:
            ci -= 1
        elif key == ord('j') and ci < len(paths) - 1:
            ci += 1
        elif key == ord('d'):
            sel[ci] = (sel[ci] & ~3) | ((sel[ci] & 1)^1)
        elif key == ord('D'):
            sel[ci] = (sel[ci] & ~3) | ((sel[ci] & 2)^2)
        elif key == ord('u'):
            sel[ci] = (sel[ci] & ~12) | ((sel[ci] & 4)^4)
        elif key == ord('U'):
            sel[ci] = (sel[ci] & ~12) | ((sel[ci] & 8)^8)
        # elif key == ord(' '):
            # if sel[ci] != 3:
                # sel[ci] = 3
            # else:
                # sel[ci] = 0
        elif key == ord('\n') or key == 10:
            break
        elif key == 27:  # ESC key
            return []

    return [(path, sel[idx]) for idx, path in enumerate(paths) if sel[idx] != 0]

def main(paths):
    global selected_path
    # Exclude the current machine's path from the list of choices
    filtered_paths = [path for path in paths if not is_localhost(path.split(":")[0])]
    selected_paths = curses.wrapper(toggle_menu, filtered_paths)
    print("\nSelected Paths:")
    for path, selection in selected_paths:
        host, target_path = path.split(":", 1)
        if host == '_':
            host = ""
        else:
            host += ":"
        if selection & 3:
            rsync_extra_args = "--delete" if selection & 2 else ""
            command = f"rsync -avh {rsync_extra_args} {host}{target_path} {selected_path}"
            print(command)
            os.system(command)

    for path, selection in selected_paths:
        host, target_path = path.split(":", 1)
        if host == '_':
            host = ""
        else:
            host += ":"
        if selection & 12:
            rsync_extra_args = "--delete" if selection & 8 else ""
            command = f"rsync -avh {rsync_extra_args} {selected_path} {host}{target_path}"
            print(command)
            os.system(command)


if __name__ == "__main__":
    main(paths)

