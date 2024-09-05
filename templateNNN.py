import sys
import base64
import argparse
import os
from pathlib import Path

max_limit_string = 'NNN' #100 is classic, till 400 is new attempt
max_limit = int(max_limit_string)
#use keyword [doublequote] in the command_line if you need to get a doublequote, [simplequote] otherwise
# example:
# python mkshim240.py -f my_IDLE_ps.exe -c "Powershell.exe start-process -WindowStyle Hidden [simplequote]./scripts/winidle.bat[simplequote]"
# python mkshim240.py -f "C:\WinP\bd312\bu\WPy64-31250b6\IDLEtest4.exe" -c "Powershell.exe start-process  -FilePath (Join-Path (Get-Location).Path  -ChildPath 'scripts\winidletest.bat')"

# 2024-08-25 v01
# - fork from initial https://github.com/pfmoore/shimmy commit
# 2024-09-01 v03
# the new ICONS :
# - do create a WINPYDIRICONS environment variable with the location of the launcher,
# - and do not play anymore with a workingdir to set it to .\scripts
# - so we have a similar behavior by double-clicking the icon or Drag&Droping something on it 
# python mkshim400.py -f "IDLE_test_v02.exe" -c "Powershell.exe start-process  -FilePath (Join-Path -Path $ENV:WINPYDIRICONS -ChildPath 'scripts\winidletest.bat')"
# python mkshim400.py -f "IDLE_test_v02b.exe" -c "Powershell.exe start-process -WindowStyle Hidden  -FilePath ([dollar]ENV:WINPYDIRICONS + '\scripts\winidle.bat')"
# 
# 2024-09-03 v04: same stub can also optionnaly change the working-directory
# python mkshim400.py -f "ControlPannel_test_v03.exe" -c ".\wpcp.bat" --subdir ".\scripts"
#
# 2024-09-05 v05: -i icon_filename to add the icon 
# python mkshim400.py -f "ControlPannel_test_v03.exe" -c ".\wpcp.bat" --subdir ".\scripts" -i "python.ico"


def parse_args():
    parser = argparse.ArgumentParser(description="Create executable shims") # re-add wording change of 2014-08-01
    parser.add_argument("-f", "--filename", default="shim.exe",
            help="The filename of the generated shim")
    parser.add_argument("-c", "--command",
            help="The command to run (use %s for where the args should go)")
    parser.add_argument("--stub",
            help="The name of the stub executable")
    parser.add_argument("-d", "--subdir", default="",
            help="swith working directory to this subdirectory from there for the running executable")
    parser.add_argument("-i", "--icon", default="",
            help="the filename of the icon file '.ico' to add")
    args = parser.parse_args()
    if len(args.command) >= max_limit:
        raise ValueError("The command cannot be over {max_limit} characters long")
    if len(args.subdir)>1 and not args.subdir[:2] in [".\\" , "."]:
        raise ValueError(f"sub-directory '{args.subdir}' from icon position must start per '.\\' or  '.', not '{args.subdir[:2]}' ")
    return args

def checkPath(path, mode):
    """ from https://gist.github.com/flyx/2965682 """ 
    import os, os.path
    if not os.path.exists(path) or not os.path.isfile(path):
        raise ValueError("{0} does not exist or isn't a file.".format(path))
    if not os.access(path, mode):
        raise ValueError("Insufficient permissions: {0}".format(path))
    
def updateExecutableIcon(executablePath, iconPath):
    """ from https://gist.github.com/flyx/2965682 """ 
    import win32api, win32con
    import struct
    import math
    """
    Updates the icon of a Windows executable file.
    """
    
    checkPath(executablePath, os.W_OK)
    checkPath(iconPath, os.R_OK)
    
    handle = win32api.BeginUpdateResource(executablePath, False)
    
    icon = open(iconPath, "rb")
    
    fileheader = icon.read(6)
    
    # Read icon data
    image_type, image_count = struct.unpack("xxHH", fileheader)
    print ("Icon file has type {0} and contains {1} images.".format(image_type, image_count))
    
    icon_group_desc = struct.pack("<HHH", 0, image_type, image_count)
    icon_sizes = []
    icon_offsets = []
    
    # Read data of all included icons
    for i in range(1, image_count + 1):
        imageheader = icon.read(16)
        width, height, colors, panes, bits_per_pixel, image_size, offset =\
            struct.unpack("BBBxHHLL", imageheader)
        print ("Image is {0}x{1}, has {2} colors in the palette, {3} planes, {4} bits per pixel.".format(
            width, height, colors, panes, bits_per_pixel));
        print ("Image size is {0}, the image content has an offset of {1}".format(image_size, offset));
        
        icon_group_desc = icon_group_desc + struct.pack("<BBBBHHIH",
            width,          # Icon width
            height,         # Icon height
            colors,         # Colors (0 for 256 colors)
            0,              # Reserved2 (must be 0)
            panes,          # Color planes
            bits_per_pixel, # Bits per pixel
            image_size,     # ImageSize
            i               # Resource ID
        )
        icon_sizes.append(image_size)
        icon_offsets.append(offset)
    
    # Read icon content and write it to executable file
    for i in range(1, image_count + 1):
        icon_content = icon.read(icon_sizes[i - 1])
        print ("Read {0} bytes for image #{1}".format(len(icon_content), i))
        win32api.UpdateResource(handle, win32con.RT_ICON, i, icon_content)
        
    win32api.UpdateResource(handle, win32con.RT_GROUP_ICON, "MAINICON", icon_group_desc)
    
    win32api.EndUpdateResource(handle, False)

def main():
    args = parse_args()
    if args.stub:
        with open(args.stub, "rb") as f:
            stub_bytes = f.read()
    else:
        stub_bytes = base64.b64decode(stub)


    cmd_pre = args.command.replace('[doublequote]', '"') #trick for [doublequote]
    cmd_pre = cmd_pre.replace('[simplequote]', '"') #trick for [simplequote]
    cmd_pre = cmd_pre.replace('[percent]', '%') #trick for [percent]
    cmd_pre = cmd_pre.replace('[dollar]', '$') #trick for [dollar]

    # v03-20240903: same stub can optionnaly change the working-directory
    if len(args.subdir) >= 1:
        print("SHIMMY THIS:", cmd_pre, "subdirectory:", args.subdir)
    else:
        print("SHIMMY THIS:", cmd_pre)
    
    # v03-20240903: same stub can optionnaly change the working-directory
    if len(args.subdir) >= 1:
        marker = ('Y' * max_limit).encode('utf-16le')
        i = stub_bytes.index(marker)
        cmd = (args.subdir+('\0' * max_limit))[:max_limit]
        cmd_bytes = cmd.encode('utf-16le')
        stub_bytes= b"".join([ stub_bytes[:i] , cmd_bytes , stub_bytes[i+len(marker):] ])

    marker = ('X' * max_limit).encode('utf-16le')
    cmd = (cmd_pre + ('\0' * max_limit))[:max_limit]
    i = stub_bytes.index(marker)
    cmd_bytes = cmd.encode('utf-16le')
    with open(args.filename, "wb") as f:
        f.write(stub_bytes[:i])
        f.write(cmd_bytes)
        f.write(stub_bytes[i+len(marker):])

    # Embed the icon with pywin32, if provided
    if Path(args.icon).is_file():
        updateExecutableIcon(args.filename, args.icon)

stub = """\
%%STUB%%
"""

if __name__ == '__main__':
    main()
