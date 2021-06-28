# Server Manager
 A manager for using many different server versions

## Install
To install, just unzip this in your main server directory
Your java paths may be different, so open `s.py` and replace the paths at the top.
Make sure to use double `\\` for directories.

__Add server jar
You put any server `.jar` in the `*/versions` folder and it'll show up after running the startup `x.bat`.
You do not have to rename them.

__Wiping__
By default, it wipes your server clean every time you launch
Wiping clean means removing any temporary file (worlds, logs, crashlogs, etc.)
it keeps your plugin configs, `eula`, `spigot/bukkit/paper/etc.yml`
You can disable that easily by going into `s.py`, and replacing `autoClean = True` with `autoClean = False`, which will then instead prompt you to clean.

__Flags__
This uses the following flags: `-Xms4G -Xmx4G` which you can change on line `170`

__Running__
You can run this by either running the `x.bat` file, or by opening command prompt and using `x` or `py s.py`.
You will be prompted to select a version
Upon selection, the server will run
