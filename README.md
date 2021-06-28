# Minecraft Server Manager
 A manager for using many different server versions
 
## Benefits & features
- No need to rename jarfiles
- No need to change startup batches for a jarfile
- No need to have multiple batch files for different versions
- No more hassle with switching java versions
- Full server wiping options & configurability
- Startup flag support
- Easy configurability

## Install
To install, just unzip [this](https://github.com/CocoTheOwner/Server-Manager/archive/refs/heads/main.zip) in your main server directory.
You will also need a version of [Python](https://www.python.org/). To make this, I used [Python 3.9.5](https://www.python.org/ftp/python/3.9.5/python-3.9.5-amd64.exe).

## Configuration
There are 3 parts to confiugure

#### Java
By default, Server Manager uses the following paths:
```
    11: "C:\Program Files\Java\jdk-11.0.10\\bin\java.exe",
    16: "C:\Program Files\Java\jdk-16.0.1\\bin\java.exe"
```
You can modify these in `s.py` by modifying the paths in the `javaPaths` dictionary. Ensure to use `\\` for directories.

#### Wiping
By default, Server Manager wipes your server clean every time you launch.
Wiping clean means removing any temporary file (worlds, logs, crashlogs, etc.).
it keeps your plugin configs, `eula`, `spigot/bukkit/paper/etc.yml`.
You can disable that easily by going into `s.py`, and replacing `clean = True` with `clean = False`.
You can there also remove and add files from the blacklists (the files that are removed), right below, under `cleanfolders` and `cleanfiles`.

#### Flags
By default, Server Manager uses the following flags: `-Xms4G -Xmx4G`. You can modify these by editing the `flags` variable in `s.py`

## Add server jar
To add a new server version, add any server `.jar` to the `*/versions` folder. 
It will then show up after running the startup `x.bat`.
You do not have to rename server jars.

## Running
You can run Server Manager by either running the `x.bat` file.
You can also open the command prompt and use `x`, `./x` or `py s.py`.
You will be prompted to select a version.
Upon selection, the server will run.
