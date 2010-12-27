SetCompressor 'lzma'

Name 'okeykoclient-portable.exe'
Icon "okeykoclient.ico"
OutFile 'okeykoclient-portable.exe'
SilentInstall silent

Section
	SetOutPath '$EXEDIR\Portable'
	File /r dist\*.*
	SetOutPath '$EXEDIR\Portable'
	nsExec::Exec $EXEDIR\Portable\okeykoclient.exe
SectionEnd
