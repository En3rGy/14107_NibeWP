@echo off
set path=%path%;C:\Python27\
set PYTHONPATH=C:\Python27;C:\Python27\Lib
@echo on

cd ..\..
C:\Python27\python generator.pyc "14107_NibeWP" UTF-8

xcopy .\projects\14107_NibeWP\src .\projects\14107_NibeWP\release

@echo Fertig.

@pause
