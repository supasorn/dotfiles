#!/usr/bin/env python3

import subprocess
import sys
import os
import tempfile

# Fixed temp output location (so Zsh can find it)
SHELL_OUTPUT_FILE = "/tmp/runfavs_result.sh"

def run_just_dry_run(item):
    result = subprocess.run(['just', '--dry-run', '--yes', item], capture_output=True, text=True)
    return result.stderr.strip()

def extract_last_nonempty_line(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else ''

def append_to_history(cmd):
    hist_file = os.path.expanduser('~/.just_history')
    with open(hist_file, 'a') as f:
        f.write(cmd + '\n')

def write_shell_command(cmd: str):
    with open(SHELL_OUTPUT_FILE, 'w') as f:
        f.write(cmd + '\n')

def main():
    if len(sys.argv) > 1:
        item = sys.argv[1]
        cmd_output = run_just_dry_run(item)
        real_cmd = extract_last_nonempty_line(cmd_output)
        append_to_history(real_cmd)
        write_shell_command(real_cmd)
        return

    result = subprocess.run(['just', '--summary'], capture_output=True, text=True)
    candidates = result.stdout.replace(' ', '\0')

    fzf = subprocess.run(
        ['fzf', '--read0', '--layout=reverse',
         '--tiebreak=begin,length', '--algo=v1',
         '--preview=just --dry-run --yes {}',
         '--preview-window=right:70%:wrap',
         '--height=20%', '--expect=ctrl-e,ctrl-x,enter',
         '--prompt=Run: '],
        input=candidates.encode('utf-8'),
        capture_output=True
    )

    if fzf.returncode != 0 or not fzf.stdout:
        return

    output = fzf.stdout.decode('utf-8').split('\n')
    fzf_selected_key = output[0]
    item = output[1].strip()
    cmd_output = run_just_dry_run(item)
    real_cmd = extract_last_nonempty_line(cmd_output)

    if fzf_selected_key == 'ctrl-e':
        write_shell_command(f'print -z -- {real_cmd!r}')
    elif fzf_selected_key == 'ctrl-x':
        with tempfile.NamedTemporaryFile(delete=False, suffix='.sh', mode='w') as tmp:
            tmp.write(real_cmd + '\n')
            tmp_path = tmp.name

        subprocess.run(['nvim', tmp_path])

        with open(tmp_path) as f:
            edited_cmd = f.read().strip()
        os.unlink(tmp_path)

        append_to_history(edited_cmd)
        write_shell_command(edited_cmd)
    else:
        append_to_history(f"r {item}")
        write_shell_command(real_cmd)

if __name__ == '__main__':
    main()

