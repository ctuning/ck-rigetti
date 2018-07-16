@echo off

rem
rem CK installation script
rem
rem See CK LICENSE for licensing details.
rem See CK COPYRIGHT for copyright details.
rem

cd %INSTALL_DIR%

del /F /Q %RIGETTI_LOGIN_FILE%

move %TMP_RIGETTI_LOGIN_FILE% %RIGETTI_LOGIN_FILE%

exit /b 0
