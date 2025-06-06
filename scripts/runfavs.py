#!/usr/bin/env python3

import subprocess
import sys
import os
import tempfile
import re

# Fixed temp output location (so Zsh can find it)
SHELL_OUTPUT_FILE = "/tmp/runfavs_result.sh"

def run_just_dry_run(item):
    result = subprocess.run(['just', '--dry-run', '--yes', item], capture_output=True, text=True)
    return result.stderr.strip()

def append_to_history(cmd):
    hist_file = os.path.expanduser('~/.just_history')
    with open(hist_file, 'a') as f:
        f.write(cmd + '\n')

def write_shell_command(cmd: str):
    with open(SHELL_OUTPUT_FILE, 'w') as f:
        f.write(cmd + '\n')
    print(cmd)

def list_variables(cmd: str):
    """Finds all shell variables like $VAR or ${VAR} in a command."""
    pattern = r'\$(?:\{(\w+)\}|(\w+))'
    matches = re.findall(pattern, cmd)
    return [v for group in matches for v in group if v]

def main():
    if len(sys.argv) > 1:
        item = sys.argv[1]
        cmd_output = run_just_dry_run(item)
        append_to_history(cmd_output)
        write_shell_command(cmd_output)
        return


    result = subprocess.run(['just', '--summary'], capture_output=True, text=True)
    candidates = result.stdout.strip().replace(' ', '\0')

    fzf = subprocess.run(
        ['fzf', '--read0', '--layout=reverse',
         '--tiebreak=begin,length', '--algo=v1',
         '--preview=just --dry-run --yes {}',
         '--preview-window=right:70%:wrap',
         '--height=20%', '--expect=ctrl-e,ctrl-x,ctrl-r,enter',
         '--prompt=Run: '],
        input=candidates.encode('utf-8'),
        capture_output=True
    )

    if fzf.returncode != 0 or not fzf.stdout:
        sys.exit(1)

    output = fzf.stdout.decode('utf-8').split('\n')
    fzf_selected_key = output[0]
    item = output[1].strip()
    cmd_output = run_just_dry_run(item)
    variables = list_variables(cmd_output)

    if variables:
        # Haven't finished implementing this yet
        env_vars = {}
        # check that each variable is defined in the environment
        for var in variables:
            if var not in os.environ:
                if var == 'cuda_devices':
                    env_vars['cuda_devices'] = '0'
                else:
                    print(f"Variable {var} is not defined in the environment and not default value")
                    sys.exit(1)
            else:
                env_vars[var] = os.environ[var]
            cmd_output = cmd_output.replace(f'${var}', f'{env_vars[var]}')
        

    if fzf_selected_key == 'ctrl-e':
        write_shell_command(f'print -z -- {cmd_output!r}')
    elif fzf_selected_key == 'ctrl-x':
        with tempfile.NamedTemporaryFile(delete=False, suffix='.sh', mode='w') as tmp:
            tmp.write(cmd_output + '\n')
            tmp_path = tmp.name

        subprocess.run(['nvim', tmp_path])

        with open(tmp_path) as f:
            edited_cmd = f.read().strip()
        os.unlink(tmp_path)

        append_to_history(edited_cmd)
        write_shell_command(edited_cmd)
    elif fzf_selected_key == 'ctrl-r':
        # Haven't finished implementing this yet
        for var in variables:
            # prompt the user for the value of the variable
            value = input(f"{var}: ")
            cmd_output = cmd_output.replace(f'${var}', value)
            
        print(cmd_output)
        sys.exit(1)
    else:
        append_to_history(f"r {item}")
        write_shell_command(cmd_output)

if __name__ == '__main__':
    main()

