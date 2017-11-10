@ECHO OFF
setlocal
set DRIVERS_FOLDER=C:\Program Files (x86)\QualiSystems\CloudShell\Server\Drivers
set DRIVER_NAME=%~n0
set LOGS_PATH=C:\Program Files (x86)\QualiSystems\CloudShell\Server\Logs\%DRIVER_NAME%
set DRIVER_ENV=%DRIVERS_FOLDER%\%DRIVER_NAME%
::set DRIVER_FOLDER=MRV
::call %cd%\%DRIVER_FOLDER%\Scripts\activate.bat
set PYTHON="%DRIVER_ENV%\Scripts\python"
set EXE=%PYTHON% "%DRIVER_ENV%\main.py"
set port=%1
if not defined port set port=4000
echo Starting driver %DRIVER_NAME%
echo Log Path %LOGS_PATH%
%EXE% %port% %LOGS_PATH%
::echo %PYTHONPATH%
::echo %DRIVER_ENV%\cloudshell
::echo %EXE%
::%PYTHON%
endlocal