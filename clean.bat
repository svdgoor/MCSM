REM Print to console that the script is starting
echo Cleaning up the build directory...
echo If there is no executable at the location specified, run setup.bat first.
REM Run `./target/build/release/mcsm.exe` with the `-e` flag to clean up the build directory
./target/build/release/mcsm.exe -e