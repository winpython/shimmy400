import sys
import base64
import argparse

#keep "max_limit = 1 0 0" unchanged for a dynamic adaptation per build.py script 
max_limit = 100 #100 is classic, till 240 is new attempt

#use keyword [doublequote] in the command_line if you need to get a doublequote, [simplequote] otherwise
# example:
# python mkshim240.py -f my_IDLE_ps.exe -c "Powershell.exe start-process -WindowStyle Hidden [simplequote]./scripts/winidle.bat[simplequote]"

def parse_args():
    parser = argparse.ArgumentParser(description="Create executable shims") # re-add wording change of 2014-08-01
    parser.add_argument("-f", "--filename", default="shim.exe",
            help="The filename of the generated shim")
    parser.add_argument("-c", "--command",
            help="The command to run (use %s for where the args should go)")
    parser.add_argument("--stub",
            help="The name of the stub executable")
    args = parser.parse_args()
    if len(args.command) >= max_limit:
        raise ValueError("The command cannot be over {max_limit} characters long")
    return args

def main():
    args = parse_args()
    if args.stub:
        with open(args.stub, "rb") as f:
            stub_bytes = f.read()
    else:
        stub_bytes = base64.b64decode(stub)
    marker = ('X' * max_limit).encode('utf-16le')
    cmd_pre = args.command.replace('[doublequote]', '"') #trick for [doublequote]
    cmd_pre = cmd_pre.replace('[simplequote]', '"') #trick for [simplequote]
    cmd = (cmd_pre + ('\0' * max_limit))[:max_limit]
    i = stub_bytes.index(marker)
    cmd_bytes = cmd.encode('utf-16le')
    with open(args.filename, "wb") as f:
        f.write(stub_bytes[:i])
        f.write(cmd_bytes)
        f.write(stub_bytes[i+len(marker):])

stub = """\
%%STUB%%
"""

if __name__ == '__main__':
    main()
