@echo off

rem CK installation script for QCK package
rem
rem Developer(s):
rem  * Grigori Fursin, dividiti/cTuning foundation
rem

rem ######################################################################################
echo Installing CK package to '%INSTALL_DIR%\build' ...

%CK_ENV_COMPILER_PYTHON_FILE% -m pip install %PYTHON_PACKAGE_NAME1% -t %INSTALL_DIR%\build %PIP_INSTALL_OPTIONS%

if %errorlevel% neq 0 (
 echo.
 echo Error: Failed installing pyQuil ...
 exit /b 1
)

rem picking up above installation in the next one
set PYTHONPATH=%INSTALL_DIR%\build;%PYTHONPATH%

%CK_ENV_COMPILER_PYTHON_FILE% -m pip install %PYTHON_PACKAGE_NAME2% -t %INSTALL_DIR%\build %PIP_INSTALL_OPTIONS%

if %errorlevel% neq 0 (
 echo.
 echo Error: Failed installing pyQuil ...
 exit /b 1
)


exit /b 0
