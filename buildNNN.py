import base64
import argparse


#max_limit = 400 # may be a parameter later


def parse_args():
    parser = argparse.ArgumentParser(description="Create mkshimNNN.py")
    parser.add_argument("-s", "--stub", default="stub400.exe",
            help="The template launcher, default: stub400.exe")
    parser.add_argument("-t", "--templatefile", default="templateNNN.py",
            help="The template launcher transformer , default: templateNNN.py")
    parser.add_argument("-o", "--generatorfile", default="mkshim400.py",
            help="The generated tranformer progem, default: mkshim400.py")
    parser.add_argument("-m", "--max_limit", default="400",
            help="The maximum size of the command, default: 400")
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    with open(args.stub, 'rb') as f:
        stub = f.read()
    max_limit = int(args.max_limit)
    
    # define string, whose presence in the binary blob is mandatory
    MARKER = ('X' * max_limit).encode('utf-16le')
    if MARKER not in stub:
        raise ValueError(f"Invalid stub: no marker bytes of size {args.max_limit}")
    stub_txt = base64.b64encode(stub).decode('ASCII')
    with open(args.templatefile) as template:
        script = template.read()
        script = script.replace('%%STUB%%', stub_txt)
        script = script.replace("max_limit_string = 'NNN'", f"max_limit_string = '{max_limit}'")
    with open(f'{args.generatorfile}', 'w') as scriptfile:
        scriptfile.write(script)

if __name__ == '__main__':
    main()
