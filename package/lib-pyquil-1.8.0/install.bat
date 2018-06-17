@echo off

rem CK installation script for pyQuil
rem
rem Developer(s):
rem  * Grigori Fursin, dividiti/cTuning foundation
rem


echo **************************************************************
echo Installing pyQuil package and its dependencies ...

set GIT_SRC_DIR=%INSTALL_DIR%\src

rem This is where pip will install the modules.
rem It has its own funny structure we don't control :
rem 

rem ######################################################################################
echo Cloning %PACKAGE_COMMIT% @ pyQuil into %GIT_SRC_DIR% ...
git clone -b %PACKAGE_COMMIT% https://github.com/rigetticomputing/pyquil %GIT_SRC_DIR%

rem ######################################################################################
echo Installing pyQuil requirements to '%INSTALL_DIR%\build' ...

cd /D %GIT_SRC_DIR%

%CK_ENV_COMPILER_PYTHON_FILE% -m pip install --upgrade -r %GIT_SRC_DIR%\examples\requirements.txt -t %INSTALL_DIR%\build

if %errorlevel% neq 0 (
 echo.
 echo Error: Failed installing requirements ...
 exit /b 1
)

rem ######################################################################################
echo Installing pyQuil to '%INSTALL_DIR%\build' ...

%CK_ENV_COMPILER_PYTHON_FILE% -m pip install --upgrade . -t %INSTALL_DIR%\build

if %errorlevel% neq 0 (
 echo.
 echo Error: Failed installing pyQuil ...
 exit /b 1
)

exit /b 0
