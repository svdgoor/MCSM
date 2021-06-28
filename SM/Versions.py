from Version import Version
from Java import Java
from util import getJarFiles
import os
class Versions:
    versions = []
    def __init__(self, versions = [], flags = "-Xms4G -Xmx4G"):
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