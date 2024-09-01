#include <stdio.h> //needed
#include <ctype.h>
#include <stdlib.h>

#define WIN32_LEAN_AND_MEAN
#include <windows.h> //needed

/* play with the default directory */
//#include <direct.h>
#include <shlwapi.h>
#include <wchar.h>

/* feature:
 400 = max command line size
 force working directory to .\scripts
 */
static wchar_t MARKER[] = L"XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX";
static wchar_t SUBDIR[] = L"\\scripts"; // to hack in the future
/* remark: cl /arch:IA32 for ia32 */

/* Skip a quoted string: on entry, p points just after the opening quote.
 * Return value: pointer to the character after the terminating quote.
 */
wchar_t *skipquoted(wchar_t *p) {
    while (*p) {
        if (*p == '"')
            return p+1;

        /* Skip a backslash-escaped quote */
        if (*p == '\\' && p[1] == '"')
            p += 2;
        else
            ++p;
    }

    /* We didn't find a terminating quote - return the end of string */
    return p;
}

wchar_t *skipargv0(wchar_t *p) {
    while (isspace(*p))
        ++p;
    if (*p == '"')
        p = skipquoted(p+1);
    else {
        while (*p && !isspace(*p))
            ++p;
    }
    while (isspace(*p))
        ++p;

    return p;
}

int run_process(wchar_t *args) {
    BOOL ret = FALSE;
    STARTUPINFOW si;
    PROCESS_INFORMATION pi;
    int exit = 0;
    wchar_t *placeholder;
    size_t len = wcslen(MARKER) + wcslen(args) + 2;
    wchar_t *cmdline = malloc(len * sizeof(wchar_t));

    if (cmdline == 0) {
        fwprintf(stderr, L"Cannot allocate %zd bytes of memory for command line\n", len * sizeof(wchar_t));
        return 1;
    }

    placeholder = wcsstr(MARKER, L"%s");
    if (placeholder) {
        swprintf(cmdline, len, L"%.*s%s%s",
            (placeholder-MARKER), MARKER, args, placeholder+2);
    } else {
        swprintf(cmdline, len, L"%s %s", MARKER, args);
    }


    /* switching directory to have .\scripts working*/
    wchar_t path[MAX_PATH];
    wchar_t *lastSlash;

    // get full path to the current C program that is running (aka the launcher icon)
    GetModuleFileNameW(NULL, path, MAX_PATH);
    //printf("Current exec program is: %ls\n", path);
    

    // Find the last backslash in the path
    lastSlash = wcsrchr(path, L'\\');
    if (lastSlash != NULL) {
        // Terminate the string at the last backslash to get the directory
        *lastSlash = L'\0';
    }

    // Set an environment variable WINPYDIRICONS to make things easier for launcher
        /** UTF-16LE encoded string (example)
    wchar_t envVarName[] = L"MY_ENV_VAR";
    wchar_t envVarValue[] = L"Hello, 世界"; */
    wchar_t envVarName[] = L"WINPYDIRICONS";
    if (SetEnvironmentVariableW(envVarName, path)) {
        //wprintf(L"Environment variable %s set to %s\n", envVarName, path);
    } else {
        fwprintf(stderr, L"Failed to set environment variable. Error code: %d\n", GetLastError());
    }

    // Append the "scripts" subdirectory: only the 400s
    //wcscat(path, L"\\scripts");
    /*
    wcscat(path, SUBDIR);
    if (_wchdir(path) == 0) {
       //printf("Current directory changed to: %ls\n", path);
    }
   /**/


    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi));
    fwprintf(stderr, L"Command line: %ls\n", cmdline);
    ret = CreateProcessW(0, cmdline, 0, 0, FALSE, 0, 0, 0, &si, &pi);
    free(cmdline);

    if (!ret) {
        fwprintf(stderr, L"CreateProcess failed: %d\n", GetLastError());
        return 1;
    }
    
    WaitForSingleObject(pi.hProcess, INFINITE);
    GetExitCodeProcess(pi.hProcess, &exit);
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);
    return exit;
}

int main(int argc, char *argv[]) {
    wchar_t *cmdline = GetCommandLineW();
    cmdline = skipargv0(cmdline);
    //fwprintf(stderr, L"Command line: %ls\n", cmdline);
    return run_process(cmdline);
}
