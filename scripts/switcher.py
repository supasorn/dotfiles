import os
import sys

def fos(command, p1, p2=None):
  ls1 = ["~/.config/nvim", "~/.local/share/nvim", "~/.cache/nvim"]
  ls2 = ls1
  if p2 is None:
    ls2 = ["", "", ""]
    p2 = ""
  for i in range(3):
    cmd = f"{command} {ls1[i]+p1} {ls2[i]+p2}"
    os.system(cmd)
    print(cmd)

# options = ["backup_mine", "backup_chad", "remove_current", "to_mine", "to_chad", "to_mynvim"]
options = ["backup", "backup_use", "remove_current"]
if len(sys.argv) != 1:
    print("please don't provide any argument")

option = int(input("Options: " + "".join([f"\n  {i}. {x}" for i, x in enumerate(options)]) + "\n:"))

prefix = ""
if option < 2:
    prefix = input("Type prefix: ")

if option == 0:
  print(options[option])
  fos("rm -rf", "_" + prefix)
  fos("cp -r", "", "_" + prefix)
elif option == 1:
  print(options[option])
  fos("rm -rf", "")
  fos("cp -r", "_" + prefix, "")
elif option == 2:
  fos("rm -rf", "")

