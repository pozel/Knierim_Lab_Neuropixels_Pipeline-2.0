@ECHO off

mkdir "%~1\A"
set "filename="%~1\A\csc_A"

set /a count = 1

for %%f in (%~1\*.ncs) do (
    echo %%f
  set /a count += 1
  echo %%count%%
)