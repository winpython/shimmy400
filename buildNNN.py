import base64

max_limit = 240 # may be a parameter later
MARKER = ('X' * max_limit).encode('utf-16le')

def main():
    with open(f'stub{max_limit}.exe', 'rb') as f:
        stub = f.read()
    if MARKER not in stub:
        raise ValueError("Invalid stub: no marker bytes")
    stub_txt = base64.b64encode(stub).decode('ASCII')
    with open(f'templateNNN.py') as template:
        script = template.read()
        script = script.replace('%%STUB%%', stub_txt)
        script = script.replace('max_limit = 100', f'max_limit = {max_limit}')
    with open(f'mkshim{max_limit}.py', 'w') as scriptfile:
        scriptfile.write(script)

if __name__ == '__main__':
    main()
