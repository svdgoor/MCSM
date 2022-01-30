# Starts the minecraft server
# 
# Get the amount of MB ram from the system arguments, default to 1024
# 
# If the purpur.jar file does not exist, download it from 
# https://api.purpurmc.org/v2/purpur/1.18.1/latest/download
# and rename the file to purpur.jar
#
# If the eula.txt file does not exist, create it and add the following text:
# eula=true
#
# If the run.bat file does not exist, create it and let it run this file with the ram argument
# 
# If the plugins/Iris.jar file does not exist and there is not a jar of the regex (Iris-).*(\.jar),
# Ask the user to choose between:
# 1. download the git repository from https://github.com/VolmitSoftware/Iris and run the gradlew setup task and then the gradlew Iris task
# 2. download the jar from https://www.spigotmc.org/resources/iris-world-gen-custom-biome-colors.84586/
# 3. skip downloading Iris (do it manually)
# 
# If the plugins/Rift.jar file does not exist,
# Ask the user to choose between:
# 1. download the jar from https://github.com/VolmitSoftware/Rift/releases/download/1.0.1/Rift-1.0.1.jar
# 2. skip downloading Rift (do it manually)
#
# Run the server with the following command:
# java -Xmx<ram>M -Xms<ram>M -jar purpur.jar nogui


import os
import time
import subprocess
import requests
import sys
from git import Repo
import regex
import os, shutil, json

iris_regex = regex.compile(r'Iris-?.*\.jar')

rift_regex = regex.compile(r'Rift-?.*\.jar')

default_settings = {
    "clean": False,
    "cleanfolders": [
        "./crash-reports",
        "./logs",
        "./w",
        "./v",
        "./x",
        "./y",
        "./z",
        "./k",
        "./l",
        "./o",
        "./world/advancements",
        "./world/data",
        "./world/entities",
        "./world/playerdata",
        "./world/poi",
        "./world/region",
        "./world/stats"
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
        "usercache.json",
        "./world/level.dat",
        "./world/level.dat_old",
        "./world/session.lock",
        "./world/uid.dat"
    ],
    "rift": True,
    "iris": True,
    "irisRepoDir": "plugins/Iris/repo"
}


# Resets the config file
def getConfig(configFile: str):
    
    # Config path exists
    if not os.path.exists("./" + configFile):
        with open(configFile, "w") as f:
            f.write(json.dumps(default_settings, indent=4))
            return default_settings
    config = None
    with open(configFile, "r") as file:
        configJson = json.load(file)
        for dataTag in ["clean", "flags", "javaPaths", "cleanfolders", "cleanfiles"]:
            if not dataTag in configJson:
                file.close()
                with open(configFile, "w") as f:
                    f.write(json.dumps(default_settings, indent=4))
                return default_settings
        config = json.load(file)

    print("Loaded config")
    return config

def check_iris(iris_repo_dir: str):
    for file in os.listdir("plugins"):
        if iris_regex.match(file):
            print("Found " + file + " in plugins folder")
            return

    print("Iris is not installed. Please enter how you wish to install Iris:")
    print("1. Download the git repository and setup (~5 to 10 minutes first time, ~1 minute after)")
    print("2. Download the jar file from spigot (~1 minute)")
    print("3. Install Iris manually (skip)")
    choice = input("Choice: ")

    if choice == "2":
        # Open https://www.spigotmc.org/resources/iris-world-gen-custom-biome-colors.84586/
        # and download the jar file
        print("Download the jar file from https://www.spigotmc.org/resources/iris-world-gen-custom-biome-colors.84586/")
        print("and move it to the plugins folder")
        print("and run this script again")
        # Open the webbrowser with the website
        time.sleep(1)
        os.system("start https://www.spigotmc.org/resources/iris-world-gen-custom-biome-colors.84586/")
        exit(0)

    if choice != "1":
        print("Skipping Iris")
        return

    print("Cloning Iris from github")
    
    print("Using repodir: " + iris_repo_dir)

    # Check if the repo exists
    if not os.path.isdir(iris_repo_dir):
        os.makedirs(iris_repo_dir)
        print("Setting up Iris repo")
        repo = Repo.clone_from("https://github.com/VolmitSoftware/Iris.git", iris_repo_dir)
        print("Cloned repository")
        repo.git.checkout("master")
        print("Checked out master")
        repo.git.pull()
        print("Pulled latest changes")

    # Run the gradlew setup task
    if (not os.path.isdir(iris_repo_dir + "/build/buildtools/CraftBukkit")):
        print("Please make sure you have the CraftBukkit buildtools installed and setup") 
        input("Press enter to run the gradlew setup task. This script thinks it's not installed.")
        subprocess.run("cd " + iris_repo_dir + " && gradlew setup", shell=True)
    
    # Run the gradlew Iris task
    subprocess.run("cd " + iris_repo_dir + " && gradlew Iris", shell=True)

    # Move the jar file that appeared in the build/libs directory to the plugins folder and rename it to Iris.jar
    if (not os.path.isdir(iris_repo_dir + "/build/libs")):
        print("Could not find the Iris.jar file in the build/libs directory")
        print("Please make sure the build task was successful")
        exit(1)

    for file in os.listdir(iris_repo_dir + "/build/libs"):
        if file.endswith(".jar"):
            os.rename(iris_repo_dir + "/build/libs/" + file, "plugins/" + file)
            print("Moved " + file + " to plugins folder")
            break

# Check if the rift jar exists
# Use regex to find the jar file, with pattern: Rift-?.*\.jar
# If the jar file is not found, ask the user to download it from 
# https://github.com/VolmitSoftware/Rift/releases/download/1.0.1/Rift-1.0.1.jar
# and move it to the plugins folder
# or to skip downloading the jar file altogether
def check_rift():
    rift_regex = regex.compile(r'Rift-?.*\.jar')
    for file in os.listdir("plugins"):
        if rift_regex.match(file):
            print("Found " + file + " in plugins folder")
            return

    print("Rift is not installed. Please enter how you wish to install Rift:")
    print("1. Download the jar file from github (fast, ~1 minute)")
    print("2. Do not install rift (skip)")
    choice = input("Choice: ")
    if choice == "1":
        print("Downloading Rift from github")
        open("plugins/Rift.jar", "wb").write(requests.get("https://github.com/VolmitSoftware/Rift/releases/download/1.0.1/Rift-1.0.1.jar").content)
        print("Downloaded rift from github")

# Check to make sure purpur is installed
def check_purpur():
    if not os.path.isfile("purpur.jar"):
        print("Downloading purpur.jar from https://api.purpurmc.org/v2/purpur/1.18.1/latest/download")
        open("purpur.jar", "wb").write(requests.get("https://api.purpurmc.org/v2/purpur/1.18.1/latest/download").content)
    else:
        print("purpur.jar found")

# Run the main server loop
def boot_loop(cmd: str):
        
    # Run the server
    while (True):
        print("Starting the server: " + str(cmd))
        subprocess.run(cmd, shell=True)
        print("Server stopped. Rebooting in 5 seconds. Press CTRL+C to cancel.")
        time.sleep(5)

# Run the server
def run():
    config = getConfig("servermanager.json")

    # Cleanup
    if config["clean"]: 
        for folder in config["cleanfolders"]:
            shutil.rmtree(folder, True)
        for file in config["cleanfiles"]:
            if os.path.exists(file):
                os.remove(file)

    # Check if the jar file exists
    check_purpur()

    # Check if the eula.txt file exists
    if not os.path.isfile("eula.txt"):
        print("Creating eula.txt")
        with open("eula.txt", "w") as f:
            f.write("eula=true")
    else:
        print("eula.txt found")

    # Check if the run.bat file exists
    if not os.path.isfile("run.bat"):
        print("Creating run.bat")
        with open("run.bat", "w") as f:
            f.write("python run.py")
    else:
        print("run.bat found")

    if not os.path.isdir("plugins"):
        os.mkdir("plugins/")

    # Check if there is a jar of the regex (Iris-).*(\.jar)
    if config["iris"]:
        check_iris(config["irisRepoDir"])

    # Check if there is a jar of the regex (Rift-).*(\.jar)
    if config["rift"]:
        check_rift()

    cmd = ["java"] + sys.argv[1:] + ["-jar", "purpur.jar", "nogui"]

    # Run the main server loop
    boot_loop(cmd)

if __name__ == "__main__":
    run()