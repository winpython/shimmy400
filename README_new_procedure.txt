redone from project https://github.com/pfmoore/shimmy initial commit of 2014-01-26
post-production icon Addition from https://gist.github.com/flyx/2965682 example

change: v03
- WIDER: we can create a command line of up to 400 characters
- EASIER: we can use [doublequote], [simplequote] and [percent] in the given command line given in parameter,
   they will be replaced per the  doublequote, simplequote or percent character when true execution
- variable $ENV:WINPYDIRICONS contains the icon directory, accessible when PowerShell.exe is used (not cmd.exe apparently)
- optional --subdir option allows to force a change of a subdirectory of the icon (or the icon directory itself if ".")

preparation of generator
* get  https://github.com/stonebig/shimmy/tree/shimmy240
* get native Tools for vs 2022
* creating generic launcher stub.exe (without icon, launching Nothing but the command 'XXXXXX...XXX')
- get launch Visual studio Tools in this directory,
- compile "cl stub400.c" ... generating a big nice stub400.exe
- remark: if ever for 32 bit "real", maybe shall we "cl /EHsc /Fe:stub400.exe /arch:IA32 stub400.c"
* creating generators:
- the generator will be a python program that generates a final binary launcher from the prepared generic launcher
- do launch  "python buildNNN.py -s stub400.exe -t templateNNN.py -o mkshim400.py", it will :
  . read templateNNN.py
  . replace in its code:
       'max_limit_string = 'NNN'" per  'max_limit_string = 400"
        %%STUB%% per the stub400.exe program in base64
  . save the result as mkshim400.py

typical build use for WinPython:
* copy the generators in make.py directory: mkshim400.py , mkshm400s.py
* example to create manually an executable launcher:
   python mkshim400.py -f my_IDLE_icon.exe -c "powershell.exe start-process -WindowStyle Hidden -FilePath ([dollar]ENV:WINPYDIRICONS + '\scripts\winidle.bat')"
   python mkshim400.py -f "my_ControlPanel_ICON.exe" -c ".\wpcp.bat" --subdir ".\scripts"
* the addition of an icon is now included, but requires pywin32:
   python mkshim400.py -f "my_ControlPanel_ICON.exe" -c ".\wpcp.bat" --subdir ".\scripts" -i "python.ico"