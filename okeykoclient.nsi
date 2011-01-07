; emesene.nsi

Name "okeykoclient"
Icon "okeykoclient.ico"
OutFile "okeykoclient-install.exe"
SetCompressor /SOLID lzma
InstallDir $PROGRAMFILES\okeykoclient

InstallDirRegKey HKLM "Software\okeykoclient" "Install_Dir"

Section "okeykoclient"

	SectionIn RO

	SetOutPath $INSTDIR

	File /r dist\*.*

	WriteRegStr HKLM SOFTWARE\okeykoclient "Install_Dir" "$INSTDIR"

SectionEnd

Section "Start Menu Shortcuts"

	CreateDirectory "$SMPROGRAMS\okeykoclient"
	CreateShortCut "$SMPROGRAMS\okeykoclient\okeykoclient.lnk" "$INSTDIR\okeykoclient.exe" "" "$INSTDIR\okeykoclient.exe" 0
	CreateShortCut "$SMPROGRAMS\okeykoclient\okeykoclient_debug.lnk" "$INSTDIR\okeykoclient_debug.exe" "" "$INSTDIR\okeykoclient.exe" 0

SectionEnd
