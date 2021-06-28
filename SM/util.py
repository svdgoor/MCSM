import os, shutil
from Versions import Versions
from Version import Version
from Java import Java

"""
Runs the manager
"""
def defaultRun(flags = "-Xms4G -Xmx4G", autoClean = False):
    if autoClean or input("Would you like to clean? [Y, y, Yes, yes]") in ["Y", "y", "Yes", "yes"]:
        clean()
    versions = Versions([])
    versions.resetActiveVersion(False)
    versions.addAll(indexVersions())
    versions.askSelect(True).run(flags)

"""
Cleans the server directory
"""
def clean():
    cleanfolders = [
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
    ]
    cleanfiles = [
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
 