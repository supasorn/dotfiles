import subprocess
import sys
import os
import tempfile
import re
SHELL_OUTPUT_FILE = "/tmp/runfavs_result.sh"

def run_just_dry_run(item, args=[]):
    result = subprocess.run(['just', '--dry-run', '--yes', item] + args, capture_output=True, text=True)
    return result.stderr.strip()

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
         '--height=20%', '--expect=ctrl-e,ctrl-x,enter',
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

    if "error:" in cmd_output: # right now, if we get this, we assume the function needs arguments
        args = cmd_output.split("usage:")[1].strip().split(" ")[2:]
        #print(cmd_outputjj
        #print(f"Number of required arguments: {num_required_args}")
        #args = []
        #for i in range(num_required_args):
            # ask for the argument
            #arg = input(f"Argument {i+1}: ")
            #args.append(arg)
        cmd_output = run_just_dry_run(item, [f"[{x}]" for x in args])
        full = cmd_output
        for arg in args:
            cmd_output = cmd_output.replace(f"[{arg}]", "")
        write_shell_command(cmd_output, edit=True, display=full)
        return

        # write_shell_command(f'print -z -- {argstr!r}')
        #write_shell_command(f'print -z -- {cmd_output!r}')
    # variables = list_variables(cmd_output)


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
    else:
        write_shell_command(cmd_output)

if __name__ == '__main__':
    main()

