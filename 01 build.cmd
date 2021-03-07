@echo off
set path=%path%;C:\Python27\
set PYTHONPATH=C:\Python27;C:\Python27\Lib
set LOGIC_ID=14107
set LOGIC_NAME=NibeWP

echo ^<head^> > .\release\log%LOGIC_ID%.html
echo ^<link rel="stylesheet" href="style.css"^> >> .\release\log%LOGIC_ID%.html
echo ^<title^>Logik - %LOGIC_NAME% (%LOGIC_ID%)^</title^> >> .\release\log%LOGIC_ID%.html
echo ^<style^> >> .\release\log%LOGIC_ID%.html
echo body { background: none; } >> .\release\log%LOGIC_ID%.html
echo ^</style^> >> .\release\log%LOGIC_ID%.html
echo ^<meta http-equiv="Content-Type" content="text/html;charset=UTF-8"^> >> .\release\log%LOGIC_ID%.html
echo ^</head^> >> .\release\log%LOGIC_ID%.html

@echo on

type .\README.md | C:\Python27\python -m markdown -x tables >> .\release\log%LOGIC_ID%.html

cd ..\..
C:\Python27\python generator.pyc "14107_NibeWP" UTF-8

xcopy .\projects\14107_NibeWP\src .\projects\14107_NibeWP\release /exclude:.\projects\14107_NibeWP\src\exclude.txt

@echo Fertig.

@pause
