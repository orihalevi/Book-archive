pyinstaller --onefile -w -i "dependence\images\Software icon.png" BookArchiveByOri.py
move dist\BookArchiveByOri.exe
rd /s /q build
rd /s /q dist
del BookArchiveByOri.spec
exit
