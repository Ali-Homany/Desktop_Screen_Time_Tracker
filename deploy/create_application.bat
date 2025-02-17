:: activate virtual environment
:: replace the directory below by the actual directory of condabin\activate on your device
call "C:\Users\Admiin\anaconda3\condabin\activate" screen_time_env
cd "src"
echo "Environment Activated"
pause
:: create executables
echo "Creating App Executable"
pyinstaller --onefile --noupx --add-data "static;static" --add-data "templates;templates" main.py
pause
echo "Creating Recorder Executable"
pyinstaller --onefile --noconsole --noupx recorder.py
pause
echo "Creating Browser Recorder Executable"
pyinstaller --onefile --noconsole --noupx browser_recorder.py
pause
:: deactivate environment
call conda deactivate
echo "Environment Deactivated"
cd ".."
pause
:: move executables to curr dir
move "src\dist\*" "deploy\"
echo "Executables Moved"
pause
:: move chrome extension to curr dir
xcopy /E /Y "src\extension" "deploy\extension\"
echo "Extension Moved"
pause
:: remove unnecessary files
rmdir /s /q "src\dist"
rmdir /s /q "src\build"
pause
:: remove unnecessary files
del "src\main.spec"
del "src\recorder.spec"
del "src\browser_recorder.spec"
echo "Unnecessary Files Removed"
pause
:: create installer
:: replace the directory below by the actual directory of inno setup on your device
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "deploy\setup.iss"
echo "Installer Created"
pause