Unicode True
!include "MUI2.nsh"
!ifndef PACKAGE_DIR
!error "PACKAGE_DIR must identify the verified portable payload"
!endif
!ifndef OUTPUT_EXE
!error "OUTPUT_EXE must identify the output installer"
!endif
Name "Minecataclysm"
OutFile "${OUTPUT_EXE}"
InstallDir "$LOCALAPPDATA\Programs\Minecataclysm"
RequestExecutionLevel user
SetCompressor /SOLID lzma
ShowInstDetails nevershow
ShowUninstDetails nevershow
!define MUI_ABORTWARNING
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"
Section "Minecataclysm"
 SetShellVarContext current
 SetOutPath "$INSTDIR"
 File /r "${PACKAGE_DIR}\*"
 CreateDirectory "$SMPROGRAMS\Minecataclysm"
 CreateShortCut "$DESKTOP\Minecataclysm.lnk" "$INSTDIR\Minecataclysm.exe" "" "$INSTDIR\Minecataclysm.exe"
 CreateShortCut "$SMPROGRAMS\Minecataclysm\Minecataclysm.lnk" "$INSTDIR\Minecataclysm.exe"
 WriteUninstaller "$INSTDIR\Uninstall.exe"
 WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Minecataclysm" "DisplayName" "Minecataclysm"
 WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Minecataclysm" "DisplayVersion" "0.1 prototype"
 WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Minecataclysm" "UninstallString" '$"$INSTDIR\Uninstall.exe$"'
 WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Minecataclysm" "InstallLocation" "$INSTDIR"
 WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Minecataclysm" "NoModify" 1
 WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Minecataclysm" "NoRepair" 1
SectionEnd
Function .onInstSuccess
 ExecShell "open" "$INSTDIR\Minecataclysm.exe"
FunctionEnd
Section "Uninstall"
 SetShellVarContext current
 Delete "$DESKTOP\Minecataclysm.lnk"
 RMDir /r "$SMPROGRAMS\Minecataclysm"
 DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Minecataclysm"
 RMDir /r "$INSTDIR\runtime"
 RMDir /r "$INSTDIR\licenses"
 Delete "$INSTDIR\Minecataclysm.exe"
 Delete "$INSTDIR\README.txt"
 Delete "$INSTDIR\BUILD-INFO.json"
 Delete "$INSTDIR\Uninstall.exe"
 RMDir "$INSTDIR"
 ; LocalAppData\Minecataclysm holds user-owned saves and is deliberately retained.
SectionEnd
