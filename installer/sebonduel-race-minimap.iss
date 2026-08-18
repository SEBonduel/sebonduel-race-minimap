; Installeur SEBonduel Race Minimap - Inno Setup (https://jrsoftware.org/isdl.php)
; Compile ce script SUR WINDOWS avec Inno Setup après avoir lancé build.py.
; Il dépose dist\sebonduel-race-minimap.wotmod dans World_of_Tanks\mods\<version>\.

#define MyName "SEBonduel Race Minimap"
#define MyVersion "0.1.0"
#define WotMod "sebonduel-race-minimap.wotmod"

[Setup]
AppId={{B7E2B0C0-6A2E-4E7B-9A1E-0F1A2B3C4D5E}
AppName={#MyName}
AppVersion={#MyVersion}
AppPublisher=SEBonduel
DefaultDirName={code:GetWotDir}
DisableDirPage=no
DirExistsWarning=no
AppendDefaultDirName=no
DefaultGroupName={#MyName}
DisableProgramGroupPage=yes
OutputBaseFilename=SEBonduel-Race-Minimap-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayName={#MyName}

[Languages]
Name: "fr"; MessagesFile: "compiler:Languages\French.isl"

[Messages]
fr.SelectDirLabel3=Sélectionne le dossier d'installation de World of Tanks (celui qui contient le dossier « mods »).

[Tasks]
Name: "modeclean"; Description: "Installation propre - dossier mods\ (recommandé : n'écrase rien, désinstallation facile)"; GroupDescription: "Mode d'installation :"; Flags: exclusive
Name: "modeoverride"; Description: "Mode écraser - dossier res_mods\ (passe devant les minimaps HD / Aslain)"; GroupDescription: "Mode d'installation :"; Flags: exclusive unchecked

[Files]
; Cible PROPRE : le .wotmod dans mods\<version>\ (n'écrase rien).
Source: "..\dist\{#WotMod}"; DestDir: "{code:GetVersionDir|mods}"; Flags: ignoreversion; Tasks: modeclean
; Cible ÉCRASER : les textures brutes dans res_mods\<version>\ (prime sur les autres).
Source: "..\dist\res_mods_payload\*"; DestDir: "{code:GetVersionDir|res_mods}"; Flags: ignoreversion recursesubdirs createallsubdirs; Tasks: modeoverride

[Run]
Filename: "{code:GetOpenDir}"; Description: "Ouvrir le dossier installé"; Flags: postinstall shellexec skipifsilent

[Code]
{ --- Détection du dossier WoT (registre WGC, sinon valeur par défaut) --- }
function GetWotDir(Param: String): String;
var p: String;
begin
  Result := 'C:\Games\World_of_Tanks_EU';
  if RegQueryStringValue(HKLM,
      'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Wargaming.net World Of Tanks EU',
      'InstallLocation', p) and (p <> '') then
    Result := p
  else if RegQueryStringValue(HKLM,
      'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Wargaming.net World Of Tanks EU',
      'InstallLocation', p) and (p <> '') then
    Result := p;
end;

{ Normalise une version « 1.27.0.0 » en segments zéro-remplis pour comparaison. }
function NormVer(v: String): String;
var i: Integer; seg: String;
begin
  Result := '';
  v := v + '.';
  seg := '';
  for i := 1 to Length(v) do
  begin
    if v[i] = '.' then
    begin
      while Length(seg) < 6 do seg := '0' + seg;
      Result := Result + seg + '.';
      seg := '';
    end
    else
      seg := seg + v[i];
  end;
end;

{ Renvoie <app>\<Param>\<version la plus récente>, où Param = 'mods' ou 'res_mods'.
  Si aucun dossier version, renvoie <app>\<Param> (le jeu doit avoir été lancé
  au moins une fois pour créer le dossier de version). }
function GetVersionDir(Param: String): String;
var base, best: String; rec: TFindRec;
begin
  base := AddBackslash(ExpandConstant('{app}')) + Param;
  best := '';
  if FindFirst(base + '\*', rec) then
  begin
    try
      repeat
        if (rec.Attributes and FILE_ATTRIBUTE_DIRECTORY <> 0)
           and (rec.Name <> '.') and (rec.Name <> '..') then
          if (best = '') or (NormVer(rec.Name) > NormVer(best)) then
            best := rec.Name;
      until not FindNext(rec);
    finally
      FindClose(rec);
    end;
  end;
  if best = '' then
    Result := base
  else
    Result := base + '\' + best;
end;

{ Dossier à ouvrir en fin d'install, selon le mode choisi. }
function GetOpenDir(Param: String): String;
begin
  if IsTaskSelected('modeoverride') then
    Result := GetVersionDir('res_mods')
  else
    Result := GetVersionDir('mods');
end;

{ Vérifie à la validation de la page dossier que « mods » existe bien. }
function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = wpSelectDir then
    if not DirExists(AddBackslash(ExpandConstant('{app}')) + 'mods') then
      Result := (MsgBox('Le dossier « mods » est introuvable ici. Es-tu sûr que c''est '
        + 'bien le dossier de World of Tanks ? (Lance le jeu une fois s''il n''existe pas.)',
        mbConfirmation, MB_YESNO) = IDYES);
end;
