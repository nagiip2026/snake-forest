@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "PY_CMD="
py -3.13 --version >nul 2>&1
if not errorlevel 1 set "PY_CMD=py -3.13"

if not defined PY_CMD (
    py -3.12 --version >nul 2>&1
    if not errorlevel 1 set "PY_CMD=py -3.12"
)

if not defined PY_CMD (
    py -3.11 --version >nul 2>&1
    if not errorlevel 1 set "PY_CMD=py -3.11"
)

if not defined PY_CMD (
    python -c "import sys; sys.exit(0 if (3, 11) <= sys.version_info[:2] < (3, 14) else 1)" >nul 2>&1
    if not errorlevel 1 set "PY_CMD=python"
)

if not defined PY_CMD (
    echo [ERROR] Python 3.11, 3.12, or 3.13 was not found.
    echo Pygame 2.6.1 has no prebuilt wheel for Python 3.14 and would fail to compile.
    echo Install 64-bit Python 3.13 from python.org, then run this file again.
    goto :failed
)

echo [1/7] Preparing a reusable build environment...
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import sys; sys.exit(0 if (3, 11) <= sys.version_info[:2] < (3, 14) else 1)" >nul 2>&1
    if errorlevel 1 (
        echo Removing an old virtual environment made with an unsupported Python version...
        rmdir /s /q ".venv"
        if exist ".venv\Scripts\python.exe" goto :failed
    )
)
if not exist ".venv\Scripts\python.exe" (
    call %PY_CMD% -m venv --system-site-packages ".venv"
    if errorlevel 1 goto :failed
)

findstr /i /c:"include-system-site-packages = true" ".venv\pyvenv.cfg" >nul
if not errorlevel 1 goto :system_packages_enabled
echo Enabling reuse of packages already installed for Python...
call %PY_CMD% -c "from pathlib import Path; p=Path('.venv/pyvenv.cfg'); s=p.read_text(); p.write_text(s.replace('include-system-site-packages = false', 'include-system-site-packages = true'))"
if errorlevel 1 goto :failed
:system_packages_enabled
set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"

echo [2/7] Checking for already-installed game and packaging dependencies...
"%PYTHON_EXE%" -m pip install --disable-pip-version-check --no-index --only-binary=pygame -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo Some requirements are missing. Installing only missing or incompatible packages...
    "%PYTHON_EXE%" -m pip install --disable-pip-version-check --only-binary=pygame -r requirements.txt
    if errorlevel 1 goto :failed
) else (
    echo Existing packages satisfy the requirements; no download is needed.
)

echo [3/7] Preparing bundled artwork and offline sound effects...
"%PYTHON_EXE%" tools\prepare_assets.py
if errorlevel 1 goto :failed

echo [4/7] Running the automated game and save-data checks...
"%PYTHON_EXE%" -m pytest -q tests
if errorlevel 1 goto :failed

echo [5/7] Building the single-file Windows application...
"%PYTHON_EXE%" -m PyInstaller --noconfirm --clean SnakeForest.spec
if errorlevel 1 goto :failed

if not exist "dist\SnakeForest.exe" (
    echo [ERROR] PyInstaller finished without creating dist\SnakeForest.exe.
    goto :failed
)

echo [6/7] Verifying the self-contained EXE outside the source folder...
pushd "%TEMP%"
if errorlevel 1 goto :failed
"%~dp0dist\SnakeForest.exe" --verify-bundle
if errorlevel 1 (
    popd
    echo [ERROR] The one-file EXE failed its out-of-project resource/import check.
    echo Check "%LOCALAPPDATA%\SnakeForest\logs\snake-forest.log" for details.
    goto :failed
)
popd

set "ISCC="
where ISCC.exe >nul 2>&1
if not errorlevel 1 set "ISCC=ISCC.exe"
if not defined ISCC (
    if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
)
if not defined ISCC (
    if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
)
if not defined ISCC (
    echo.
    echo [SUCCESS] The portable one-file game was built and verified:
    echo %~dp0dist\SnakeForest.exe
    echo [NOTE] Inno Setup 6 was not found, so the optional setup installer was skipped.
    echo Install Inno Setup 6 and run this file again only if you also need the setup installer.
    pause
    exit /b 0
)

if not exist "installer-output" mkdir "installer-output"
if not exist "installer-output" goto :failed

echo [7/7] Creating the offline setup wizard and single-file installer...
"%ISCC%" /Qp "SnakeForest.iss"
if errorlevel 1 goto :failed

if not exist "installer-output\SnakeForest-Setup.exe" (
    echo [ERROR] Inno Setup finished without creating installer-output\SnakeForest-Setup.exe.
    goto :failed
)

echo.
echo [SUCCESS] Snake Forest is ready:
echo Portable one-file application: %~dp0dist\SnakeForest.exe
echo Offline installer: %~dp0installer-output\SnakeForest-Setup.exe
echo The installer includes the application, images, icons, sounds, and runtime dependencies.
echo The installed game works offline and creates Start Menu and optional desktop shortcuts.
pause
exit /b 0

:failed
echo.
echo [BUILD FAILED] Review the message above. No completed installer was confirmed.
echo Build output, when present, is in the build, dist, and installer-output folders.
pause
exit /b 1
