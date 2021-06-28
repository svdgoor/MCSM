import os, shutil, json
from versionCollection import VersionCollection
from version import Version
from java import Java

# These are the folders and (below) the files
# that are wiped when the clean() task is ran
# This is the file location and default configuration for the config file
config = "SM/config.json"
dConfig = {
    "clean": True,
    "flags": "-Xms4G -Xmx4G",
    "javaPaths": {
        11: "C:\Program Files\Java\jdk-11.0.10\\bin\java.exe",
        16: "C:\Program Files\Java\jdk-16.0.1\\bin\java.exe"
    },
    "cleanfolders": [
        "./crash-reports",
        "./logs",
        "./w",
        "./v",
        "./x",
        "./y",
        "./z",
        "./world",
        "./world_nether",
        "./world_the_end"
    ],
    "cleanfiles": [
        "version_history.json",
        ".console_history",
        "banned-ips.json",
        "banned-players.json",
        "commands.yml",
        "help.yml",
        "permissions.yml",
        "wepif.yml",
        "whitelist.json",
        "usercache.json"
    ]
}

"""
Runs the manager from a config file
"""
def runConfig(config: dict):
    defaultRun(config[0], config[1], config[2], config[3], config[4])

"""
Runs the manager
"""
def defaultRun(
        javaPaths = {
            11: "C:\Program Files\Java\jdk-11.0.10\\bin\java.exe",
            16: "C:\Program Files\Java\jdk-16.0.1\\bin\java.exe"
        }, 
        flags = "-Xms4G -Xmx4G", 
        clean = False,
        cleanFolders = [
            "./crash-reports",
            "./logs",
            "./w",
            "./v",
            "./x",
            "./y",
            "./z",
            "./world",
            "./world_nether",
            "./world_the_end"
        ],
        cleanFiles = [
            "version_history.json",
            ".console_history",
            "banned-ips.json",
            "banned-players.json",
            "commands.yml",
            "help.yml",
            "permissions.yml",
            "wepif.yml",
            "whitelist.json",
            "usercache.json"
        ]
    ):

    # Clean if clean is enabled
    if clean: cleanServer(cleanFolders, cleanFiles)

    # Store the java paths
    Java.javaPaths = javaPaths

    # Create versions object
    versions = VersionCollection()

    # Reset previously active jar
    versions.resetActiveVersion(False)

    # Index jars
    versions.addAll(indexVersions())

    # Ask for selecting and run a jar
    versions.askSelect(True).run(flags)

"""
Retrieve the configuration and set a default if the file does not yet exist

Returns:
    An array with the javaPath, flags, clean, cleanFolders, and cleanFiles values in order
"""
def getResetConfig():
    if not os.path.exists(config):
        with open(config, "w") as f:
            json.dump(dConfig, f)
        print("Created default config at " + config + ".")

    with open(config) as f:
        data = json.load(f)

    return [data["javaPath"], data["flags"], data["clean"], data["cleanFolders"], data["cleanFiles"]]

"""
Cleans the server directory
"""
def cleanServer(cleanfolders: list, cleanfiles: list):
    for folder in cleanfolders:
        shutil.rmtree(folder, True)
    for file in cleanfiles:
        if os.path.exists(file):
            os.remove(file)

"""
Retrieves all jar file names from <working-directory>/versions

Returns:
    Array of filenames
"""
def getJarFiles(prefixPath = False, checkVersionsFolder = True):

    # Retrieve the versions directory path
    path = "\\".join(__file__.split("\\")[:-1]) + ("\\versions" if checkVersionsFolder else "")

    # Store jarfiles
    if not prefixPath:
        return os.listdir(path)
    else:
        jars = []
        for jar in os.listdir(path):
            jars.append(path + "\\" + jar)
        return jars

"""
Checks all jar files and makes versions for them

Returns:
    All server versions (jar files) found in the specified dir
"""
def indexVersions():

    # Retrieve the versions directory path
    path = "\\".join(__file__.split("\\")[:-1]) + "\\versions"

    # Make an array of versions
    v = []

    # Loop over all jarfiles found
    for jarFile in getJarFiles():

        # Split the jarfile name
        jarSplit = jarFile.split("-")

        # Retrieve the version
        version = int(jarSplit[1].split(".")[1])

        # If the jarfile is 1.16, also add a java 11 version
        if version == 16:
            v.append(Version(jarSplit[0], version, path + "\\" + jarFile, Java(11)))

        # Add a java 16 version
        v.append(Version(jarSplit[0], version, path + "\\" + jarFile, Java(16)))

    return v
 