[Setup]
AppName=Screen_Time_Tracker
AppVersion=0.3
DefaultDirName={commonpf}\Screen_Time_Tracker
DefaultGroupName=Screen_Time_Tracker
OutputDir=.
OutputBaseFilename=Screen_Time_Tracker_Installer
Compression=lzma2/max
SolidCompression=yes
PrivilegesRequired=Admin
ArchitecturesInstallIn64BitMode=x64os


[Files]
Source: "main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "recorder.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "browser_recorder.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "readme.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "extension\*"; DestDir: "{app}\extension"; Flags: ignoreversion recursesubdirs

[Icons]
; Create shortcuts for launching the dashboard
Name: "{group}\Screen Time Dashboard"; Filename: "{app}\main.exe"
Name: "{userdesktop}\Screen Time Dashboard"; Filename: "{app}\main.exe";
; Create shortcuts for the tracker in startup folder, so it runs automatically
Name: "{userstartup}\Screen Tracker"; Filename: "{app}\recorder.exe"; WorkingDir: "{app}"
Name: "{userstartup}\Browser Tracker"; Filename: "{app}\browser_recorder.exe"; WorkingDir: "{app}"

[Run]
Filename: "{app}\recorder.exe"; Description: "Launch Screen Time Tracker"; Flags: nowait postinstall skipifsilent
Filename: "{app}\browser_recorder.exe"; Description: "Launch Browser Time Tracker"; Flags: nowait postinstall skipifsilent
