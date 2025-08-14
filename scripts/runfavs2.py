import subprocess
import sys
import os
import tempfile
import readline
import re
import argparse
import commands
import test_commands
import inspect

SHELL_OUTPUT_FILE = "/tmp/runfavs_result.sh"

def run_just_dry_run(func_name, arguments=[], sing=False):
    func = getattr(commands, func_name)
    if func is None:
        raise ValueError(f"Function '{func_name}' not found in commands module.")
    
    sig = inspect.signature(func)
    kwargs = {}
    # TODO: print the functoin out for user to see first
    for name, param in sig.parameters.items():
        if param.default is not inspect.Parameter.empty:
            kwargs[name] = param.default
        else:
            value = input(f"{name}: ")
            kwargs[name] = value

            # kwargs[name] = f'{{{name}}}'
    print(kwargs)
    exit()
    # check if the arguments match the signature
    '''
    if len(arguments) > 0:
        if len(arguments) > len(sig.parameters):
            raise ValueError(f"Function '{func_name}' expects {len(sig.parameters)} arguments, but {len(arguments)} were provided.")
        elif len(arguments) < len(sig.parameters):

    elif len(sig.parameters) > 0:
        raise ValueError(f"Function '{func_name}' expects {len(sig.parameters)} arguments, but none were provided.")

    out = test_commands.clean_command(func(*arguments))

    if sing:
        out = f'sg --cmd "{out}"'
    return out
    '''

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



def main():
    parser = argparse.ArgumentParser(description="Run Justfile recipes with fzf.")
    parser.add_argument("--sing", action="store_true", help="Enable sing mode.")
    parser.add_argument("--show", action="store_true", help="Enable sing mode.")
    parser.add_argument("item", nargs="*", help="The Justfile recipe to run, and its arguments.")
    args = parser.parse_args()

    if args.show:
        if args.item and len(args.item) > 0:
            ORANGE = "\033[38;5;214m"
            RED = "\033[38;5;203m"
            GREEN = "\033[32m"
            BLUE = "\033[38;5;39m"
            RESET = "\033[0m"


            func = getattr(commands, args.item[0])
            sig = inspect.signature(func)
            kwargs = {name: f"{RED}{{{name}}}{RESET}" for name in sig.parameters}  # {'a': 'a', 'b': 'b'}
            if kwargs:
                result = test_commands.clean_command(func(**kwargs))
            else:
                result = test_commands.clean_command(func())

            comment = test_commands.get_comment(getattr(commands, args.item[0]))
            print(f"{ORANGE}{args.item[0]}{RED}{sig}{RESET}")
            if comment:
                print(f"{BLUE}# {comment}{RESET}")
            print(result)
        exit()
            
            

    sing = args.sing

    results = test_commands.get_functions_and_args(commands)                          
    candidates = ""
    for result in results:
        if result[0] == "confirm": continue
        candidates += f"{result[0]}\0"

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
             '--preview=python runfavs2.py --show {}',
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
        argument_mode(item, sing)

    cmd_output = run_just_dry_run(item, recipe_args, sing=sing)

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

