:: File name: start_server_debug.bat
@echo off
setlocal
pushd %~dp0

echo === Current working directory ===
cd
echo.

echo === Trying to launch with Python launcher (py) ===
where py 2>nul
if %errorlevel%==0 (
  echo Found py launcher: & where py
  echo.
  py -3 serve_index.py
  goto :PAUSE_AND_END
)

echo === Trying python / pythonw ===
for %%P in (python.exe pythonw.exe) do (
  where %%P >nul 2>nul
  if not errorlevel 1 (
    echo Found %%P: & where %%P
    echo.
    %%P serve_index.py
    goto :PAUSE_AND_END
  )
)

echo [ERROR] Python was not found.
echo Please install Python from https://www.python.org/downloads/
echo or check your PATH / py launcher settings.

:PAUSE_AND_END
echo.
echo === Script finished. Check any error messages above. ===
pause
