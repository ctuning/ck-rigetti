@echo off

rem CK installation script for pyQuil
rem
rem Developer(s):
rem  * Grigori Fursin, dividiti/cTuning foundation
rem  * Leo Gordon, dividiti
rem


echo **************************************************************
echo Installing pyQuil package and its dependencies ...

set GIT_SRC_DIR=%INSTALL_DIR%\src
set EXTRA_PYTHON_SITE=%INSTALL_DIR%\build

echo **************************************************************
echo.
echo Cleanup: removing %EXTRA_PYTHON_SITE% and %GIT_SRC_DIR%
if exist "%EXTRA_PYTHON_SITE%" (
 rmdir /S /Q "%EXTRA_PYTHON_SITE%"
)
if exist "%GIT_SRC_DIR%" (
 rmdir /S /Q "%GIT_SRC_DIR%"
)

rem ######################################################################################
IF DEFINED PACKAGE_VERSION (
    SET PACKAGE_COMMIT=v%PACKAGE_VERSION%
) ELSE (
    SET PACKAGE_COMMIT=master
)

echo Cloning %PACKAGE_COMMIT% @ %PYTHON_PACKAGE_NAME% into %GIT_SRC_DIR% from %GIT_SRC_URL% ...
git clone -b %PACKAGE_COMMIT% %GIT_SRC_URL% %GIT_SRC_DIR%

rem ######################################################################################
echo Installing %PYTHON_PACKAGE_NAME% requirements to '%EXTRA_PYTHON_SITE%' ...

%CK_ENV_COMPILER_PYTHON_FILE% -m pip install %GIT_SRC_DIR% -r %GIT_SRC_DIR%\examples\requirements.txt -t %EXTRA_PYTHON_SITE% %PIP_INSTALL_OPTIONS%

if %errorlevel% neq 0 (
 echo.
 echo Error: Failed installing requirements ...
 exit /b 1
)

exit /b 0
