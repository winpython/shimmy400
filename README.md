Windows Executable Link Stubs
=============================

This project allows the creation of Windows "executable stubs" - exe files
that when run, execute a defined command, passing the command line arguments
on to the subcommand, and optionally forcing a sub-directory from where the icon is located.

It is derived from initial commit of project //github.com/pfmoore/shimmy of Paul Moore
to replace Nullsoft in WinPython project as the creator of icon launchers.


Usage
-----

Compile a typical generic launcher, with VS tools

   cl stub400.c
  
Generate a Python Launcher generator mkshim400.py from this executable and templateNNN.py model, via:

   python buildNNN.py -s stub400.exe -t templateNNN.py -o mkshim400.py

Create a final launcher as follow:

    mkshim400.py -f filename.exe -c "a command"
    mkshim400.py -f filename.exe -c "a command" --subdir ".\s_sub-directory_of_the_launcher"


This will generate an executable, `filename.exe`, which when run, will execute
`a command`. So, for example:

    filename a b c

runs

    a command a b c

Note that there is no requirement for the command to be just an executable
name. A common usage might be to run `py C:\Some\Python\Script.py`.


Complement
----------
The strings `[dollar]`, `[simplequote]`, and `[doublequote]` will be replaced per their respective character in the command line
The environment variable `$ENV:WINPYDIRICONS` is created per the launcher, with current launcher location, but this work only for powershell.exe, on Windows11.

example:

    mkshim400.py -f my_IDLE_icon.exe -c "powershell.exe start-process -WindowStyle Hidden -FilePath ([dollar]ENV:WINPYDIRICONS + '\scripts\winidle.bat')"

An icon can ba added (if you have pywin32)

example:

    mkshim400.py -f my_IDLE_icon.exe -c "powershell.exe start-process -WindowStyle Hidden -FilePath ([dollar]ENV:WINPYDIRICONS + '\scripts\winidle.bat')" -i "python.ico"

It is possible to have the supplied arguments inserted somewhere other than
at the end of the line, by including `%s` in the command string. The arguments
will be inserted in place of the `%s`.

Technical Details
-----------------

The command is executed using the Windows `CreateProcess` API, so file
associations will not be considered when running the subcommand.

The stub executable is built from the `stub400.c` source. The compile command is
simply `cl stub400.c`. The script is built from `templateNNN.py` and the
stub.exe using `buildNNN.py`, variable %%STUB%% of templateNNN.Py being replaced per stub400.exe coded in Base64.

If you want to use a different stub when building a link (for example, when
testing a change to the stub code) you can use the `--stub` argument to
specify the name of the sub exe directly. Otherwise, it will be the embedded
`stub400.exe`

Command Line and Sub-Directory are arbitrary limited to 400 characters long.

Future Possibilities
--------------------

1. Include the icon addition, currently in sister project winpython/winpython make.py, with:

   updateExecutableIcon(launcher_name, icon_path)

2.  if ever for 32 bit "real", maybe shall we use "cl /EHsc /Fe:stub400.exe /arch:IA32 stub400.c"
