from Java import Java
from util import getJarFiles
import os
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
    def buildRunCommand(self, flags = "-Xmx4G -Xms4G", inMainDir = True):
        return 'cmd /k ""' + self.java.path + '" ' + flags + ' -jar active-' + self.path.split("\\")[-1] + ' nogui"'
    
    """
    Runs this version
    """
    def run(self, flags):
        self.prepareRun()
        command = self.buildRunCommand(flags=flags)
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