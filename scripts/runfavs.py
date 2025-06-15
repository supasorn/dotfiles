import subprocess
import sys
import os
import tempfile
import readline
import re
import argparse

SHELL_OUTPUT_FILE = "/tmp/runfavs_result.sh"

def run_just_dry_run(item, arguments=[], sing=False):
    result = subprocess.run(['just', '--dry-run', '--yes', item] + arguments, capture_output=True, text=True)
    out = result.stderr.strip()
    if sing:
        out = f'sg --cmd "{out}"'
    return out

def write_shell_command(cmd: str, eval=True, save_history=True, edit=False, display=True):
    cmd_str = ""
    if edit:
        cmd_str += f"print -z -- {cmd!r}"
    else:
        if save_history:
            cmd_str += f"print -s -- {cmd!r}"
        if eval:
            if cmd_str != "":
                cmd_str += " && "
            cmd_str += cmd

    with open(SHELL_OUTPUT_FILE, 'w') as f:
        f.write(cmd_str + '\n')

    # if display is boolean true, print the cmd
    # if it's a string, print it
    if display == True:
        print(cmd)
    elif display != None:
        print(display)

def argument_mode(recipe):
    result = subprocess.run(['just', '--show', recipe], capture_output=True, text=True)
    lines = result.stdout.strip().splitlines()
    args = [] 
    for line in lines:
        if line.startswith('#'):
            continue
        if not line.strip():
            continue
        if line[-1] == ':':
            sp = line[:-1].split()[1:]
            for arg in sp:
                if '=' in arg:
                    arg_name, default_value = arg.split('=', 1)
                    args.append((arg_name, default_value))
                else:
                    args.append((arg, None))

    cmd_output = run_just_dry_run(recipe, ['\033[31m{{'+arg[0]+'}}\033[0m' for arg in args])
    if len(args) > 0:
        print(cmd_output)

        arg_vals = [val for _, val in args]
        idx = 0  # current argument index
        for i, arg in enumerate(args):
            try:
                inp = input(f"{arg[0]}{' (' + arg[1] + ')' if arg[1] else ''}: ")
            except KeyboardInterrupt:
                print("\n\033[31mCancelled by user.\033[0m")
                return
            
            args[i] = (arg[0], inp if inp else arg[1])  # Use input or default value

        cmd_output = run_just_dry_run(recipe, [a[1] for a in args])

    write_shell_command(cmd_output)
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="Run Justfile recipes with fzf.")
    parser.add_argument("--sing", action="store_true", help="Enable sing mode.")
    parser.add_argument("item", nargs="*", help="The Justfile recipe to run, and its arguments.")
    args = parser.parse_args()

    sing = args.sing

    result = subprocess.run(['just', '--summary'], capture_output=True, text=True)
    candidates = result.stdout.strip().replace(' ', '\0')

    # if argument is provide, use it as item
    if args.item:
        item = args.item[0]
        recipe_args = args.item[1:]

        if item not in candidates:
            print(f"Item '{item}' not found in just recipes.")
            sys.exit(1)
        fzf_selected_key = 'enter'
    else:
        recipe_args = [] # No arguments if fzf is used
        fzf = subprocess.run(
            ['fzf', '--read0', '--layout=reverse',
             '--tiebreak=begin,length', '--algo=v1',
             # '--preview=just --dry-run --yes {}',
             '--preview=just --show {}',
             '--preview-window=right:50%:wrap',
             # '--preview-window=bottom:30%:wrap',
             '--height=20%', '--expect=ctrl-e,ctrl-x,ctrl-s,ctrl-a,enter',
             '--prompt=Run: '],
            input=candidates.encode('utf-8'),
            capture_output=True
        )

        if fzf.returncode != 0 or not fzf.stdout:
            sys.exit(1)

        output = fzf.stdout.decode('utf-8').split('\n')
        fzf_selected_key = output[0]
        item = output[1].strip()

    if fzf_selected_key == 'ctrl-a':
        argument_mode(item)

    cmd_output = run_just_dry_run(item, recipe_args, sing=sing)

    if "error:" in cmd_output: # right now, if we get this, we assume the function needs arguments
        just_args = cmd_output.split("usage:")[1].strip().split(" ")[2:]
        #print(cmd_outputjj
        #print(f"Number of required arguments: {num_required_args}")
        #just_args = []
        #for i in range(num_required_args):
            # ask for the argument
            #arg = input(f"Argument {i+1}: ")
            #just_args.append(arg)
        cmd_output = run_just_dry_run(item, [f"[{x}]" for x in just_args], sing=sing)
        full = cmd_output
        for arg in just_args:
            cmd_output = cmd_output.replace(f"[{arg}]", "")
        write_shell_command(cmd_output, edit=True, display=full)
        return


    if fzf_selected_key == 'ctrl-e':
        write_shell_command(cmd_output, edit=True, display=None)
    elif fzf_selected_key == 'ctrl-x':
        with tempfile.NamedTemporaryFile(delete=False, suffix='.sh', mode='w') as tmp:
            tmp.write(cmd_output + '\n')
            tmp_path = tmp.name

        subprocess.run(['nvim', tmp_path])

        with open(tmp_path) as f:
            edited_cmd = f.read().strip()
        os.unlink(tmp_path)

        write_shell_command(edited_cmd)
    elif fzf_selected_key == 'ctrl-s':
        if not sing: # if sing is enabled, the command is already wrapped in sg
            cmd_output = f'sg --cmd "{cmd_output}"'
        write_shell_command(cmd_output, edit=True, display=None)
    else:
        write_shell_command(cmd_output)

if __name__ == '__main__':
    main()

