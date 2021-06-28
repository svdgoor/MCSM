import os, shutil
autoClean = True
flags = "-Xms4G -Xmx4G"
javaPaths = {
    11: "C:\Program Files\Java\jdk-11.0.10\\bin\java.exe",
    16: "C:\Program Files\Java\jdk-16.0.1\\bin\java.exe"
}
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


"""
Cleans the server directory
"""
def clean():
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
    jars = []
    for file in os.listdir(path):
        if file.endswith(".jar"):
            if prefixPath:
                jars.append(path + "\\" + file)
            else:
                jars.append(file)
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
    

class Java:
    paths = javaPaths
    def __init__(self, java: int):
        if java not in self.paths:
            print("Java {} is not in the java path list!".format(java))
            return
        self.path = self.paths[java]
        self.version = java

class Version:
    def __init__(self, title: str, mcversion: int, path: str, java: Java):
        self.title = title.capitalize()
        self.version = mcversion
        self.path = path
        self.java = java

    """
    Prepares the jar to be ran
    """
    def prepareRun(self):
        invf = self.isInVersionFolder()
        if not invf and self.isInMainFolder():
            print("Already prepared version!")
            return None
        elif not invf:
            print("File not in main and not in version folder!")
            return None
        self.moveToMain()
        if not self.isInMainFolder():
            print("Moving self to main failed!")
            return None
        return self.path

    """
    Checks if this version is still in the versions folder
    
    Returns:
        True if this version is still in the versions folder
    """
    def isInVersionFolder(self):
        # print("Checking if in server folder: " + self.path)
        return self.path in getJarFiles(True)

    """
    Checks if this version is in the main server directory

    Returns:
        True if this version is in the main server directory
    """
    def isInMainFolder(self):
        # print("Checking if in main directory: " + self.path.replace("\\versions", ""))
        return self.path.replace("versions\\", "active-") in getJarFiles(True, False)

    """
    Moves this version to the main directory
    """
    def moveToMain(self):
        # print("Moving to main: " + self.path)
        os.rename(self.path, self.path.replace("versions\\", "active-"))

    """
    Moves this version to the versions directory
    """
    def moveToVersions(self):
        # print("Moving to versions: " + self.path.replace("\\versions", ""))
        os.rename(self.path.replace("versions\\", "active-"), self.path)

    """
    Builds a server run command

    Returns:
        The built command
    """
    def buildRunCommand(self, inMainDir = True):
        return 'cmd /k ""' + self.java.path + '" ' + flags + ' -jar active-' + self.path.split("\\")[-1] + ' nogui"'
    
    """
    Runs this version
    """
    def run(self):
        self.prepareRun()
        command = self.buildRunCommand()
        print("Delegating command: " + command)
        os.system(command)
    

    """
    Prints information about this version    
    """
    def print(self):
        print(self.getInfo())

    """
    Gets information about this version
    """
    def getInfo(self, simplified: False):
        if simplified:
            return "1." + str(self.version) + " " + self.title + " / Java " + str(self.java.version) 
        else:
            return "V: 1." + str(self.version) + " " + self.title + " / Java (" + str(self.java.version) + "): " + self.java.path + " / Path: " + self.path

class Versions:
    versions = []
    def __init__(self, versions = []):
        self.addAll(versions)

    """
    Add a version
    """
    def add(self, version: Version):
        self.versions.append(version)

    """
    Add a list of versions
    """
    def addAll(self, versions: list):
        for version in versions:
            if not type(version) is Version:
                print(str(version) + " is not a version object")
            else:
                self.versions.append(version) 

    """
    Prints the version options
    """
    def print(self):
        for i, version in enumerate(self.versions):
            print(str(i) + ": " + version.getInfo(True))
            
    """
    Checks if there is an active jarfile present

    Returns:
        True if there is an active jar. If returnFile is true, returns the file instead (can return none)
    """
    def existsActiveVersion(self, returnFile = False):
        for jar in getJarFiles(True, False):
            if jar.split("\\")[-1].startswith("active-"):
                return (True if not returnFile else jar)
        return (False if not returnFile else None)

    """
    Resets and adds back active versions

    If addVersionToList is false, the version found here will not be added
    """
    def resetActiveVersion(self, addVersionToList = True):
        version = self.existsActiveVersion(True)
        if not version == None:
            # This renames the active jarfile to its normal name, inside the versions folder
            # Version looks like this: `<working directory>/active-jarfile-version.jar`
            # The target location is: `<working directory>/versions/jarfile.jar`
            target = "\\".join(version.split("\\")[:-1]) + "\\versions\\" + version.split("\\")[-1].replace("active-", "")
            os.rename(version, target)
            if addVersionToList:
                if int(target.split("\\")[-1].split("-")[1].split(".")[1]) == 16:
                    self.add(Version(
                        target.split("\\")[-1].split("-")[0],
                        int(target.split("\\")[-1].split("-")[1].split(".")[1]),
                        target,
                        Java(11)
                    ))   
                self.add(Version(
                    target.split("\\")[-1].split("-")[0],
                    int(target.split("\\")[-1].split("-")[1].split(".")[1]),
                    target,
                    Java(16)
                ))

    """
    Ask for a version selection

    Returns:
        The selected version
    """
    def askSelect(self, includeVersions = False):

        # If requested, print versions
        if includeVersions: self.print()

        # Ask to select a version
        print("Please select a version from the list above")

        # Get selection input
        selection = input()

        # Try again until a valid number was input
        while not selection.isnumeric() or not self.getValidSelection(int(selection)):
            if not selection.isnumeric():
                print("You entered a non-numerical value")
            else:
                print("You selected a number out of bounds: " + str(self.getSelectionBounds()))
            print("Please try again to select a version from the list above")
            selection = input()
        return self.versions[int(selection)]

    """
    Asks to toggle looping on or off

    Returns:
        True if selected as such
    """
    def askLoop():

        # The yes/no definitions
        yes = ["Y", "y", "Yes", "yes"]
        no = ["N", "n", "No", "no"]

        # Ask for the yes/no input
        print("Would you like to loop this version? (" + ", ".join(yes) + " or " + ", ".join(no) + ")")

        # Retrieve yes/no input
        loop = input()

        # Loop until the entry is valid
        while not loop in yes and not loop in no:
            print("You did not select one of these options: " + ", ".join(yes) + " or " + ", ".join(no) + ". Please try again")
            loop = input()

        # Return the boolean value
        return loop in yes

    """
    Asks to select a version and for a loop

    Returns:
        Array with [loop (bool), version (Version)]
    """
    def askSelectLoop(self):
        version = self.askSelect(True)
        loop = Versions.askLoop()
        return [loop, version]

    """ 
    Checks the inputted selection

    Returns:
        True if valid
    """
    def getValidSelection(self, selection: int):
        return selection > 0 and selection < len(self.versions)

    """
    Get the selection bounds

    Returns:
        The possible selection bounds
    """
    def getSelectionBounds(self):
        return [0, len(self.versions) - 1]

if __name__ == "__main__":
    if autoClean or input("Would you like to clean? [Y, y, Yes, yes]") in ["Y", "y", "Yes", "yes"]:
        clean()
    versions = Versions([])
    versions.resetActiveVersion(False)
    versions.addAll(indexVersions())
    versions.askSelect(True).run()