; InnoSetupScript for PELD
; See Inno Setup documentation for explanation of these settings

; I'm not happy with the AppVersion here.  I'm just using a generic 1.0 for now.
; Sadly, there isn't a great way for us to automatically populate this value.
; Inno Setup does allow us to use a preprocessor GetFileVersion function,
; but PyInstaller's .exe versioning utility doesn't support Python 3.x!
; There are other ways we could hack it in, but really it's just not worth it.

[Setup]
AppName=PELD
AppVersion=1.0
DefaultDirName={pf}\PELD
DefaultGroupName=PELD
UninstallDisplayIcon={app}\PELD.exe
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x86 x64
ArchitecturesInstallIn64BitMode=x64
SetupIconFile=app.ico
OutputDir=dist
OutputBaseFilename=PELD-installer

[InstallDelete]
Type: files; Name: "{app}\api-ms-win*.dll"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\PELD\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "README.md"; DestDir: "{app}"; Flags: isreadme
Source: "LICENSE"; DestDir: "{app}"

[Icons]
Name: "{group}\PELD"; Filename: "{app}\PELD.exe"; WorkingDir: "{app}"
Name: "{group}\Uninstall PELD"; Filename: "{uninstallexe}"
Name: "{userdesktop}\PELD"; Filename: "{app}\PELD.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\PELD.exe"; Description: "Run PELD"; WorkingDir: "{app}"; Flags: postinstall