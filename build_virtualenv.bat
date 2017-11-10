@ECHO OFF
setlocal
set PYTHON_PATH=C:\Python27
set DEFINED_PYTHON_PATH=%1
if defined %DEFINED_PYTHON_PATH% set PYTHON_PATH=%DEFINED_PYTHON_PATH%
if not exist %PYTHON_PATH% echo Python path is not correct or Python is not installed
set VIRTUALENV_EXE=%PYTHON_PATH%\Scripts\virtualenv.exe
if not exist %VIRTUALENV_EXE% (
    %PYTHON_PATH%\Scripts\pip.exe install virtualenv
)

::--python="c:\Program Files (x86)\QualiSystems\CloudShell\Server\python\2.7.10\python.exe" --always-copy .--always-copy
endlocal