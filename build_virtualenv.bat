@ECHO OFF
setlocal
set VIRTUALENV=C:\Python27\Scripts\virtualenv.exe

if not exist %VIRTUALENV% set VIRTUALENV=virtualenv

if not exist %VIRTUALENV% echo Virtualenv is not installed


set CS_PYTHON="c:\Program Files (x86)\QualiSystems\CloudShell\Server\python\2.7.10\python.exe"
::--python="c:\Program Files (x86)\QualiSystems\CloudShell\Server\python\2.7.10\python.exe" --always-copy .--always-copy
endlocal