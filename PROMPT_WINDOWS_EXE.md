# Prompt: Snake Forest u diyaari Windows EXE dhab ah

Nuqul ka samee prompt-kan oo geli AI coding agent marka aad rabto inuu baaro, hagaajiyo, tijaabiyo ama dib u dhiso xirmada Windows ee mashruucan.

```text
Waxaan rabaa inaad dhamaystirto oo aad si sax ah u xirmayso project-kan desktop-ka ah ee Snake Forest, si uu ugu shaqeeyo Windows 10/11 x64.

SHARAXAADDA SOFTWARE-KA:
Snake Forest waa ciyaar desktop ah oo Python lagu qoray. Waxay isticmaashaa PySide6 interface-ka, Pygame dhaqdhaqaaqa iyo looxa ciyaarta, SQLite-na waxay ku kaydisaa settings-ka iyo dhibcaha maxalli ahaan. Ciyaaryahanku wuxuu maska ku hagaa kayn, miro ayuu ururiyaa (10 dhibcood midkiiba), wuxuuna iska ilaaliyaa darbiyada iyo jirka maska. Ciyaartu waxay leedahay Easy/Normal/Hard, Slow/Normal/Fast, pause/resume, restart, sound effects, fullscreen, grid iyo reduced-effects settings. Assets-ka sawirrada, icons-ka, font-yada iyo WAV-yada waxay ku jiraan assets/.

SHURUUDAHA MUHIIMKA AH:

1. Marka hore baar project-ka hadda jira, build scripts-ka, `SnakeForest.spec`, `SnakeForest.iss`, dependencies-ka iyo tests-ka. Hagaaji waxa maqan adigoo ilaalinaya UI-ga, game logic-ga, xogta kaydsan iyo assets-ka. Ha tirtirin ama dib ha u qorin wax aan loo baahnayn. Ha sheegan in wax la tijaabiyey haddii aan la tijaabin.

2. Diyaari labadan output:
   - Portable hal-fayl ah: `dist\SnakeForest.exe`
   - Installer offline ah: `installer-output\SnakeForest-Setup.exe`

3. Portable EXE-gu ha ku jiro app-ka, Python runtime-ka, dependencies-ka iyo dhammaan assets-ka runtime-ka looga baahan yahay. Kombiyuutarka Windows-ka lagu ciyaarayo looma baahna Python, development tools, source folder ama internet. EXE-gu yuusan ku tiirsanaan current working directory-ga; assets-ka ku xalliso habka ku habboon PyInstaller one-file.

4. Mashruucu waa Python, marka isticmaal PyInstaller one-file iyo `SnakeForest.spec` (ama si ula kac ah u cusboonaysii spec-ka haddii loo baahdo). Ku dar images, icons, fonts, sounds, hidden imports iyo dependencies dhab ahaan loo baahan yahay. Ha u beddelin hab packaging oo aan ku habboonayn stack-kan.

5. Hagaaji/ilaali `build.bat` iyo `build_exe.bat` si ay:
   - U hubiyaan 64-bit Python 3.11, 3.12 ama 3.13 iyo build dependencies-ka.
   - U diyaariyaan assets-ka, u ordiyaan `python -m pytest -q tests`, una dhisaan one-file EXE-ga.
   - U hubiyaan in `dist\SnakeForest.exe` la sameeyey.
   - U ordiyaan `SnakeForest.exe --verify-bundle` iyaga oo working directory-ga ka dhigaya `%TEMP%`, si loo hubiyo in resources-ku ku jiraan bundle-ka oo aan laga soo akhrinayn source folder-ka.
   - Haddii Inno Setup 6 (`ISCC.exe`) jiro, u dhisaan `installer-output\SnakeForest-Setup.exe`. Haddii aanu jirin, si cad u sheeg portable EXE-gu inuu diyaar yahay, installer-kana la booday; ha sheegin in installer la sameeyey.
   - Haddii build ama hubin fashilanto, muujiyaan qaladka oo exit code aan-guul ahayn bixiyaan.

6. Installer-ku ha noqdo x64 oo offline ku rakibma. Ku rakib user-ku qori karo folder sida `%LOCALAPPDATA%\Programs\Snake Forest`, ku dar Start Menu shortcut iyo desktop shortcut ikhtiyaari ah. Shortcuts-ku ha tilmaamaan EXE-ga la rakibay, ee yaanay tilmaamin `dist` ama source folder. Settings, saves iyo logs ku hay `%LOCALAPPDATA%\SnakeForest`, ee ha ku qorin install folder-ka.

7. Hubi in installer-ku xambaarsan yahay portable EXE-ga iyo wax kasta oo runtime-ka looga baahan yahay; rakibidda iyo ciyaartu yaanay u baahnayn internet. Dhammaadka sheeg meelaha saxda ah ee outputs-ka iyo midka loo diri karo kombiyuutar kale:
   - `dist\SnakeForest.exe`
   - `installer-output\SnakeForest-Setup.exe` (kaliya haddii Inno Setup 6 la heli karo)

8. Orod checks-ka environment-ku kuu oggol yahay. Kala saar waxa la xaqiijiyey iyo waxa aan la tijaabin. Ha odhan Windows EXE ayaa shaqeeyey kombiyuutar Windows/nadiif ah haddii aadan halkaas ku tijaabin. Haddii deegaankaagu aanu ahayn Windows ama aanu dhisi karin Windows EXE, si cad u sheeg xaddidaadda; diyaari ama sax build scripts-ka oo sii tilmaamaha Windows-ka lagu ordo.

Dhamee hawsha adigoo si toos ah u hagaajinaya faylasha project-ka; ha ku ekaan sharaxaad ama tusaale kood ah.
```
