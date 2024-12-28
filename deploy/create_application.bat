:: activate virtual environment
cd "C:\Users\Admiin\anaconda3\condabin"
call activate screen_time_env
cd "C:\Ali\Learning\Software\On My Own\python projects\Desktop_Screen_Time_Tracker"
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
pause
:: move executables to curr dir
move ".\dist\*" "deploy/"
echo "Executables Moved"
:: move chrome extension to curr dir
xcopy /E /Y ".\extension" "deploy\extension\"
echo "Extension Moved"
pause
:: remove unnecessary files
rmdir /s /q "./dist"
rmdir /s /q "./build"
:: remove unnecessary files
del "./main.spec"
del "./recorder.spec"
del "./browser_recorder.spec"
echo "Unnecessary Files Removed"
pause
:: create installer
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "deploy/setup.iss"
echo "Installer Created"
pause