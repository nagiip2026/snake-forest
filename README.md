<p align="center">
  <img src="assets/images/readme-hero.gif" alt="Snake Forest — forest snake game" width="900" />
</p>

<h1 align="center">🐍 Snake Forest 🌿</h1>

<p align="center">
  <img src="assets/images/logo.png" alt="Snake Forest logo" width="560" />
</p>

<p align="center">
  <strong>A desktop snake game set in a beautiful forest — collect fruit, score points, and don't crash!</strong>
</p>

<p align="center">
  <img alt="Windows 10/11 x64" src="https://img.shields.io/badge/Windows-10%20%2F%2011%20x64-3978b8?style=for-the-badge&logo=windows&logoColor=white" />
  <img alt="Python 3.11–3.13" src="https://img.shields.io/badge/Python-3.11--3.13-3776ab?style=for-the-badge&logo=python&logoColor=white" />
  <img alt="Open source MIT" src="https://img.shields.io/badge/Open%20Source-MIT-3b7d54?style=for-the-badge" />
  <img alt="Offline game" src="https://img.shields.io/badge/Playable-Offline-244f36?style=for-the-badge&logo=leaflet&logoColor=white" />
</p>

<p align="center">
  <a href="https://t.me/Nagiip_Star"><img alt="Telegram @Nagiip_Star" src="https://img.shields.io/badge/Telegram-%40Nagiip__Star-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" /></a>
  <a href="https://wa.me/252672339792"><img alt="WhatsApp +252672339792" src="https://img.shields.io/badge/WhatsApp-%2B252%20672%20339792-25D366?style=for-the-badge&logo=whatsapp&logoColor=white" /></a>
</p>

---

## 🌲 The game

**Snake Forest** is a Windows desktop snake game. Guide the snake through the forest, eat glowing fruit to grow and score points, and avoid the forest walls and your own body. The package includes forest scenery, artwork, and in-game sound effects; the game does not need an internet connection once installed.

It is built with **Python**, **PySide6**, and **Pygame**. Settings and game results are stored locally in SQLite on your computer.

## ✨ Features

- 🌄 Animated splash screen and menu with forest visuals and a loading animation.
- 🐍 Grid-based snake movement; each fruit adds **10 points**.
- 🏆 Best score, last score, total games, and player level.
- 🎚️ Three difficulty levels: **Easy, Normal, Hard**; and three speeds: **Slow, Normal, Fast**.
- ⏸️ Pause, resume, restart, and return to the menu.
- 🔊 In-game sound effects, adjustable volume, and an option to turn sound off.
- 🖥️ Full-screen mode, board grid, and reduced visual effects.
- 💾 Scores and settings are saved locally; no account or internet connection is required.
- 📦 A portable single-file Windows EXE and an optional offline installer.

## 🎮 How to play

| Action | Keys |
|---|---|
| Up | `↑` or `W` |
| Down | `↓` or `S` |
| Left | `←` or `A` |
| Right | `→` or `D` |
| Pause / resume | `Space` or `P` |
| Full screen | `F11` |

Eat fruit to earn **10 points per fruit** and grow the snake. Avoid the forest walls and your own body; the snake cannot immediately reverse into the opposite direction. If the game feels too difficult or you want a different speed, change it in **Settings**.

## 🚀 Run from source

You need **64-bit Python 3.11, 3.12, or 3.13**. First, open a terminal in the project folder, then run:

```bat
py -3.13 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python tools\prepare_assets.py
python main.py
```

`build_exe.bat` prepares the assets automatically; the `prepare_assets.py` step above is optional when running only from source. You can run the game-logic and data-persistence tests with:

```bat
python -m pytest -q tests
```

## 🪟 Build a Windows EXE

The project already includes a Windows build process. **This ZIP contains the source code; it does not include a prebuilt EXE.** The Windows EXE must be built on Windows 10/11 x64:

1. Install **64-bit Python 3.11, 3.12, or 3.13**. Python 3.13 is recommended.
2. If you want the installer, install **Inno Setup 6**. This is optional; the portable EXE does not need it.
3. Open the `snake-forest` folder extracted from the ZIP, then double-click `build.bat` or run it from Command Prompt:

   ```bat
   build.bat
   ```

`build.bat` calls `build_exe.bat`. The build checks Python and dependencies, prepares the assets, runs the tests, packages the game and runtime into a single EXE with PyInstaller, then runs `--verify-bundle` from `%TEMP%` to check that the bundled resources are present. If Inno Setup 6 is found, it creates an offline installer; otherwise, the script clearly reports that the installer was skipped. Missing dependencies may need to be downloaded over the internet on the **build computer**; the finished EXE does not need internet to install or play.

### Build outputs

- `dist\SnakeForest.exe` — a portable single-file application; send this to someone who wants to play without installing. The recipient needs Windows 10/11 x64, but does not need Python or the source folder.
- `installer-output\SnakeForest-Setup.exe` — the offline installer; it is created **only** when Inno Setup 6 is installed on the build computer. It installs to `%LOCALAPPDATA%\Programs\Snake Forest` and adds a Start Menu shortcut plus an optional desktop shortcut.

Scores, settings, and logs are stored outside the installation folder, in `%LOCALAPPDATA%\SnakeForest` within the user's profile.

### EXE build prompt

This prompt is a Snake Forest-specific version of the prompt provided, with the project details filled in. The full prompt is also available in [`PROMPT_WINDOWS_EXE.md`](PROMPT_WINDOWS_EXE.md); the original prompt is [`PROMPT_FOR_REAL_EXE_ORIGINAL.txt`](PROMPT_FOR_REAL_EXE_ORIGINAL.txt).

<details>
<summary>🧩 Click to view the full build prompt</summary>

```text
I want you to complete and correctly package this Snake Forest desktop project so that it runs on Windows 10/11 x64.

SOFTWARE DESCRIPTION:
Snake Forest is a desktop game written in Python. It uses PySide6 for the interface, Pygame for movement and the game board, and SQLite to store settings and scores locally. The player guides a snake through a forest, collects fruit (10 points per fruit), and avoids the walls and the snake's own body. The game has Easy/Normal/Hard difficulty, Slow/Normal/Fast speed, pause/resume, restart, sound effects, full-screen, grid, and reduced-effects settings. Image, icon, font, and WAV assets are in assets/.

IMPORTANT REQUIREMENTS:

1. First inspect the existing project, build scripts, `SnakeForest.spec`, `SnakeForest.iss`, dependencies, and tests. Fix anything missing while preserving the UI, game logic, saved data, and assets. Do not delete or rewrite anything unnecessarily. Do not claim that something was tested unless it actually was.

2. Prepare these two outputs:
   - Portable single-file application: `dist\SnakeForest.exe`
   - Offline installer: `installer-output\SnakeForest-Setup.exe`

3. The portable EXE must include the app, Python runtime, dependencies, and all runtime assets. The Windows computer used to play it must not need Python, development tools, the source folder, or internet. The EXE must not depend on the current working directory; resolve bundled assets in a way that works with PyInstaller one-file.

4. This project uses Python, so use PyInstaller one-file and `SnakeForest.spec` (or deliberately update the spec if needed). Include the images, icons, fonts, sounds, hidden imports, and dependencies that are actually required. Do not switch to an unsuitable packaging method.

5. Maintain or improve `build.bat` and `build_exe.bat` so they:
   - Check for 64-bit Python 3.11, 3.12, or 3.13 and the build dependencies.
   - Prepare the assets, run `python -m pytest -q tests`, and build the one-file EXE.
   - Check that `dist\SnakeForest.exe` was created.
   - Run `SnakeForest.exe --verify-bundle` with the working directory set to `%TEMP%`, to check that the resources are in the bundle and are not being read from the source folder.
   - If Inno Setup 6 (`ISCC.exe`) is available, build `installer-output\SnakeForest-Setup.exe`. If it is not available, clearly report that the portable EXE is ready and the installer was skipped; do not claim that an installer was created.
   - If the build or a check fails, show the error and return a non-success exit code.

6. The installer must be x64 and install offline. Install to a user-writable folder such as `%LOCALAPPDATA%\Programs\Snake Forest`, add a Start Menu shortcut and an optional desktop shortcut. Shortcuts must point to the installed EXE, not to the EXE in `dist` or the source folder. Keep settings, saves, and logs in `%LOCALAPPDATA%\SnakeForest`, not in the installation folder.

7. Make sure the installer includes the portable EXE and everything else the runtime requires; installation and gameplay must not require internet. At the end, state the exact output locations and which file can be sent to another computer:
   - `dist\SnakeForest.exe`
   - `installer-output\SnakeForest-Setup.exe` (only if Inno Setup 6 is available)

8. Run the checks the current environment allows. Distinguish what was verified from what was not tested. Do not say that the Windows EXE worked on Windows or a clean computer if you did not test it there. If your environment is not Windows or cannot build a Windows EXE, say so clearly; prepare or fix the build scripts and provide the steps to run on Windows.

Finish the task by editing the project files directly; do not stop at an explanation or sample code.
```

</details>

## 🗂️ Project structure

The list below shows every folder and file in the repository. Image, sound, and icon files are in `assets/` and are bundled into the EXE using `SnakeForest.spec`.

<details>
<summary>📁 Show the complete folder structure</summary>

```text
snake-forest/
├── app/
│   ├── __init__.py
│   ├── audio.py
│   ├── config.py
│   ├── database.py
│   ├── game_engine.py
│   └── resources.py
├── assets/
│   ├── fonts/
│   │   ├── DejaVuSans-Bold.ttf
│   │   ├── DejaVuSerif-Bold.ttf
│   │   └── LICENSE.txt
│   ├── icons/
│   │   └── fontawesome/
│   │       ├── apple-whole.svg
│   │       ├── arrow-down.svg
│   │       ├── arrow-left.svg
│   │       ├── arrow-right.svg
│   │       ├── arrow-up.svg
│   │       ├── bolt.svg
│   │       ├── bullseye.svg
│   │       ├── chart-bar.svg
│   │       ├── circle-check.svg
│   │       ├── circle-question.svg
│   │       ├── clock.svg
│   │       ├── expand.svg
│   │       ├── gamepad.svg
│   │       ├── gear.svg
│   │       ├── house.svg
│   │       ├── keyboard.svg
│   │       ├── LICENSE.txt
│   │       ├── medal.svg
│   │       ├── pause.svg
│   │       ├── play.svg
│   │       ├── rotate-right.svg
│   │       ├── trophy.svg
│   │       ├── volume-high.svg
│   │       ├── volume-xmark.svg
│   │       └── xmark.svg
│   ├── images/
│   │   ├── app_icon.ico
│   │   ├── app_icon.png
│   │   ├── developer-contact.gif
│   │   ├── forest-background.jpg
│   │   ├── forest-background.png
│   │   ├── forest-fruit.png
│   │   ├── logo.png
│   │   ├── readme-hero.gif
│   │   ├── snake-body.png
│   │   ├── snake-head.png
│   │   ├── snake-mascot.png
│   │   ├── snake-spritesheet.png
│   │   └── snake-tail.png
│   └── sounds/
│       ├── collect.wav
│       ├── game-over.wav
│       ├── game-start.wav
│       ├── high-score.wav
│       ├── pause.wav
│       └── ui-click.wav
├── installer-assets/
│   ├── wizard-image.bmp
│   └── wizard-small.bmp
├── tests/
│   ├── test_database.py
│   └── test_game_engine.py
├── tools/
│   └── prepare_assets.py
├── ui/
│   ├── __init__.py
│   ├── application.py
│   ├── common.py
│   ├── dashboard.py
│   ├── game_screen.py
│   ├── secondary_screens.py
│   └── splash.py
├── .gitignore
├── build.bat
├── build_exe.bat
├── INSTALLATION_NOTICE.txt
├── LICENSE
├── main.py
├── PROMPT_FOR_REAL_EXE_ORIGINAL.txt
├── PROMPT_WINDOWS_EXE.md
├── README.md
├── requirements.txt
├── SnakeForest.iss
└── SnakeForest.spec
```

</details>

| Folder / file | Purpose |
|---|---|
| `app/` | Game engine, settings, SQLite database, audio, and resource management. |
| `ui/` | Splash, menu/dashboard, gameplay, settings, and game guide screens. |
| `assets/images/` | Logo, app icons, forest backgrounds, fruit, and snake sprites. |
| `assets/sounds/` | Six local WAV sound effects. |
| `assets/icons/fontawesome/` | SVG icons and their license/attribution. |
| `assets/fonts/` | Bundled fonts and their license. |
| `installer-assets/` | Inno Setup wizard images. |
| `tests/` | Game-engine and data-storage tests. |
| `tools/` | Script that prepares/generates the game assets. |
| `build.bat`, `build_exe.bat` | Windows build entry point and EXE/installer creation. |
| `SnakeForest.spec` | PyInstaller one-file bundle configuration. |
| `SnakeForest.iss` | Inno Setup offline installer configuration. |
| `PROMPT_WINDOWS_EXE.md` | Windows EXE prompt tailored for Snake Forest. |
| `PROMPT_FOR_REAL_EXE_ORIGINAL.txt` | The original submitted prompt. |

## 🧰 Technology

- **Python 3.11–3.13** — language and runtime.
- **PySide6** — desktop interface.
- **Pygame** — gameplay movement and board rendering.
- **SQLite** — local settings, scores, and history.
- **PyInstaller** — portable one-file EXE.
- **Inno Setup 6** — optional Windows installer.

## 👨‍💻 Developer

**Nagiip Star** · 19 years old · lives in Somaliland

<p align="center">
  <img src="assets/images/developer-contact.gif" alt="Animated developer and contact banner: Nagiip Star, Somaliland, Telegram and WhatsApp" width="860" />
</p>

<p align="center">
  <a href="https://t.me/Nagiip_Star"><img alt="Telegram: @Nagiip_Star" src="https://img.shields.io/badge/Telegram-%40Nagiip__Star-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" /></a>
  <a href="https://wa.me/252672339792"><img alt="WhatsApp: +252672339792" src="https://img.shields.io/badge/WhatsApp-%2B252%20672%20339792-25D366?style=for-the-badge&logo=whatsapp&logoColor=white" /></a>
</p>

## 📜 Open source & licenses

The Snake Forest code is **open source** and released under the **MIT License** — see [`LICENSE`](LICENSE) for details. Notices and licenses for third-party components have been preserved: see [`assets/icons/fontawesome/LICENSE.txt`](assets/icons/fontawesome/LICENSE.txt) and [`assets/fonts/LICENSE.txt`](assets/fonts/LICENSE.txt). Those components remain under their own licenses; the project's MIT license does not replace them.

---

<p align="center"><sub>Built with 🌿 in Somaliland · Snake Forest © 2026 Nagiip Star</sub></p>
