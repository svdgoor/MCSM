REM Print to console that the script is starting
echo Updating the server...
echo If there is no executable at the location specified, run setup.bat first.
REM Run `./target/build/release/mcsm.exe` with the `-u` flag to update the plugins and server software
./target/build/release/mcsm.exe -u