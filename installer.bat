@echo off
title Installazione github_conn
cls
echo ====================================================
echo             INSTALLAZIONE COMPONENTE
echo ====================================================
echo.
echo Questo script installera la libreria 'github_conn'.
echo.
set /p scelta="Vuoi procedere con l'installazione? (S/N): "

if /I "%scelta%" EQU "S" goto :INSTALLA
if /I "%scelta%" EQU "N" goto :ANNULLA
goto :FINE

:INSTALLA
echo.
echo Installazione in corso...
python -m pip install github_conn
echo.
echo ====================================================
echo Operazione completata!
echo ====================================================
pause
exit

:ANNULLA
echo.
echo Operazione annullata dall'utente.
font>nul
exit

:FINE
