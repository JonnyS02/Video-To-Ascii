pip install pyinstaller
pyinstaller --noconfirm --onefile --distpath "" --console --icon "cover.ico"  "Video-To-Ascii.py"
cd %~dp0
rmdir /s /q "build"
del "Video-To-Ascii.spec"