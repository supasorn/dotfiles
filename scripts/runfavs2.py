#!/usr/bin/env python3

import subprocess
import sys
import os
import tempfile
import readline
import re
import argparse
import commands
import commands_helper
import inspect

SHELL_OUTPUT_FILE = "/tmp/runfavs_result.sh"

ORANGE = "\033[38;5;214m"
RED = "\033[38;5;203m"
GREEN = "\033[32m"
BLUE = "\033[38;5;39m"
RESET = "\033[0m"
C_CMD = BLUE

def dry_run(func_name, arguments=[], argument_mode=False, sing=False):
    func = getattr(commands, func_name)
    if func is None:
        raise ValueError(f"Function '{func_name}' not found in commands module.")
    
    sig = inspect.signature(func)
    kwargs = {}
    # TODO: print the functoin out for user to see first
    prompt_for_value = False
    for name, param in sig.parameters.items():
        if param.default is not inspect.Parameter.empty:
            kwargs[name] = param.default
        else:
            kwargs[name] = ""
            prompt_for_value = True

    if prompt_for_value or argument_mode:
        print_command(func_name)
        print(f"\n{GREEN}Please provide values for the following arguments{RESET}:")
        for name, value in kwargs.items():
            if value == "":
                value = input(f"  {RED}{name}{RESET}: ") 
                kwargs[name] = value
            elif argument_mode:
                value = input(f"  {RED}{name}{RESET} (default: {value}): ") or value
                kwargs[name] = value


    out = commands_helper.clean_command(func(**kwargs))
    for line in out.splitlines():
        if line.startswith('@confirm'):
            ans = input(f"{ORANGE}Do you want to run this command? (y/n): {RESET}")
            if ans.lower() != 'y':
                print(f"{RED}Command execution cancelled.{RESET}")
                sys.exit(1)
            # remove the @confirm line
            out = '\n'.join([l for l in out.splitlines() if not l.startswith('@confirm')])

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

def print_command(func_name):
    func = getattr(commands, func_name)
    sig = inspect.signature(func)
    kwargs = {name: f"{RED}{{{name}}}{RESET}" for name in sig.parameters}  # {'a': 'a', 'b': 'b'}
    if kwargs:
        result = commands_helper.clean_command(func(**kwargs))
    else:
        result = commands_helper.clean_command(func())

    comment = commands_helper.get_comment(getattr(commands, func_name))
    print(f"{C_CMD}{func_name}{RED}{sig}{RESET}")
    if comment:
        print(f"{BLUE}# {comment}{RESET}")
    print(result)

def main():
    parser = argparse.ArgumentParser(description="Run commands with fzf.")
    parser.add_argument("--sing", action="store_true", help="Enable sing mode.")
    parser.add_argument("--show", action="store_true", help="Enable sing mode.")
    parser.add_argument("item", nargs="*", help="Command and optionally its arguments")
    args = parser.parse_args()

    if args.show:
        if args.item and len(args.item) > 0:
            print_command(args.item[0])
        exit()
            
    sing = args.sing

    results = commands_helper.get_functions_and_args(commands)                          
    candidates = ""
    for result in results:
        if result[0] == "confirm": continue
        candidates += f"{result[0]}\0"

    # if argument is provide, use it as item
    if args.item and False: # disable this for now
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
             '--preview=' + os.path.abspath(__file__) + ' --show {}',
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
        cmd_output = dry_run(item, recipe_args, argument_mode=True, sing=sing)
    else:
        cmd_output = dry_run(item, recipe_args, sing=sing)

    if fzf_selected_key == 'ctrl-e':
        print("HERE" + cmd_output)
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

