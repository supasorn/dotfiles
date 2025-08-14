import commands
import inspect
import functools

def confirm(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return "@confirm\n" + func(*args, **kwargs)
    return wrapper


def get_comment(func):
    lines, start_line = inspect.getsourcelines(func)
    file_path = inspect.getsourcefile(func)

    with open(file_path, "r", encoding="utf-8") as f:
        all_lines = f.readlines()

    # Walk upward from the line before the function
    comments = []
    i = start_line - 2  # -1 for zero-index, another -1 to go above def line
    while i >= 0:
        line = all_lines[i].rstrip("\n")
        if line.strip().startswith("#"):
            comments.insert(0, line.strip("# ").strip())
            i -= 1
        elif line.strip() == "":
            i -= 1
        else:
            break

    return "\n".join(comments) if comments else None


def get_functions_and_args(module):
    funcs_info = []
    for name, obj in inspect.getmembers(module, inspect.isfunction):
        sig = inspect.signature(obj)
        funcs_info.append((name, str(sig)))  # store name and argument string
    return funcs_info

def clean_command(command):
    # remove leading tab in each line and remove empty lines and remove trailing or leading whitespace
    return "\n".join(line.lstrip().rstrip() for line in command.strip().splitlines() if line.strip()) 

if __name__ == "__main__":
    for name, args in get_functions_and_args(commands):
        print(f"{name}{args}")

    result = clean_command(getattr(commands, "dwui")())
    print(result)
    print(get_comment(commands.download))
