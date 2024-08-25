redone from project https://github.com/pfmoore/shimmy initial commit of 2024-01-26

change:
- we can create a bigger commande line than 100 characters
- we can use [doublequote] or [simplequote] in the command line given in parameter, they will be replaced per a  doublequote or a simplequote

typical use:

* creating a stub.exe
- launch Visual studio Tools in this directory,
- compile "cl stub240.c"
- ... generating a big nice stub240.exe

* creating a wrapper:
- do launch  "python buildNNN.py", it will :
  . read templateNNN.py
  . replace in its code:
       'max_limit = 100" per  'max_limit = 240"
        %%STUB%% per the stub204.exe program in base64
  . save the result as mkshim240.py

* example to create an executable launcher after:
 python mkshim240.py -f my_IDLE_python200.exe -c "./scripts/noshell.vbs ./python-3.13.0rc1.amd64/python.exe                                                      ./python-3.13.0rc1.amd64/Lib/idlelib/idle.pyw"
