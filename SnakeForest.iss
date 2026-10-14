#define AppName "Snake Forest"
#define AppVersion "1.0.0"
#define AppPublisher "Snake Forest Studio"

[Setup]
AppId={{D4E62BB0-6DB7-4F82-91E1-7AAE7F2851A9}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppComments=An offline forest-themed snake game.
DefaultDirName={localappdata}\Programs\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
LicenseFile=INSTALLATION_NOTICE.txt
SetupIconFile=assets\images\app_icon.ico
UninstallDisplayName={#AppName}
UninstallDisplayIcon={app}\SnakeForest.exe
WizardStyle=modern
WizardImageFile=installer-assets\wizard-image.bmp
WizardSmallImageFile=installer-assets\wizard-small.bmp
Compression=lzma2/ultra64
SolidCompression=yes
OutputDir=installer-output
OutputBaseFilename=SnakeForest-Setup
SetupLogging=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Files]
Source: "dist\SnakeForest.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#AppName}\{#AppName}"; Filename: "{app}\SnakeForest.exe"; WorkingDir: "{app}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\SnakeForest.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\SnakeForest.exe"; Description: "Launch Snake Forest"; Flags: nowait postinstall skipifsilent

[Code]
var
  AgreementCheckBox: TNewCheckBox;

procedure AgreementCheckBoxClick(Sender: TObject);
begin
  WizardForm.LicenseAcceptedRadio.Checked := AgreementCheckBox.Checked;
  WizardForm.LicenseNotAcceptedRadio.Checked := not AgreementCheckBox.Checked;
end;

procedure InitializeWizard();
begin
  WizardForm.WelcomeLabel1.Caption := 'Welcome to Snake Forest Setup';
  WizardForm.WelcomeLabel2.Caption :=
    'Install the forest-themed snake game. All game files are included, and no internet connection is needed to install or play.';
  WizardForm.WelcomeLabel2.WordWrap := True;

  WizardForm.LicenseAcceptedRadio.Visible := False;
  WizardForm.LicenseNotAcceptedRadio.Visible := False;
  AgreementCheckBox := TNewCheckBox.Create(WizardForm);
  AgreementCheckBox.Parent := WizardForm.LicenseAcceptedRadio.Parent;
  AgreementCheckBox.Left := WizardForm.LicenseAcceptedRadio.Left;
  AgreementCheckBox.Top := WizardForm.LicenseAcceptedRadio.Top;
  AgreementCheckBox.Width := WizardForm.LicenseAcceptedRadio.Width;
  AgreementCheckBox.Height := WizardForm.LicenseAcceptedRadio.Height;
  AgreementCheckBox.Caption := 'I agree to the installation notice';
  AgreementCheckBox.Checked := False;
  AgreementCheckBox.OnClick := @AgreementCheckBoxClick;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = wpLicense then
  begin
    Result := AgreementCheckBox.Checked;
    if not Result then
      MsgBox('Please check "I agree to the installation notice" before continuing.',
        mbInformation, MB_OK);
  end;
end;
