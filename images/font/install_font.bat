echo off

pause
SET mypath=%~dp0
echo %mypath:~0,-1%
echo %cd%\Kbreindeergames-ra2O.ttf
Pause
ROBOCOPY %mypath% C:\Windows\Fonts\ Kbreindeergames-ra2O.ttf /r:2 /w:1
echo
Pause