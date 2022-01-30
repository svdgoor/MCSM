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
from turtle import down
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
    "download": {
        "use_iris": True,
        "use_rift": True,
        "iris_repo": "plugins/Iris/repo",
        "iris_download_mode": -1,
        "rift_download_mode": -1
    }
}


# Resets the config file
def get_config(configFile: str):
    
    # Config path exists
    if not os.path.exists("./" + configFile):

        # Set the config file to the default settings
        with open(configFile, "w") as f:
            f.write(json.dumps(default_settings, indent=4))
            return default_settings

    # Read the config file
    with open(configFile, "r") as file:

        # Read the json
        configJson = json.load(file)

        for dataTag in default_settings.keys():
            if not dataTag in configJson:
                print("Missing tag: " + dataTag + ", resetting to default")
                file.close()
                with open(configFile, "w") as f:
                    f.write(json.dumps(default_settings, indent=4))
                return default_settings

    print("Loaded config")
    return configJson

def install_iris_github(repo_dir: str):
    print("Cloning Iris from github, using repodir: " + repo_dir)

    # Check if the repo exists
    if not os.path.isdir(repo_dir):
        os.makedirs(repo_dir)
        print("Setting up Iris repo")
        repo = Repo.clone_from("https://github.com/VolmitSoftware/Iris.git", repo_dir)
        print("Cloned repository")
        repo.git.checkout("master")
        print("Checked out master")
        repo.git.pull()
        print("Pulled latest changes")

    # Run the gradlew setup task
    if (not os.path.isdir(repo_dir + "/build/buildtools/CraftBukkit")):
        print("Please make sure you have the CraftBukkit buildtools installed and setup") 
        input("Press enter to run the gradlew setup task. This script thinks it's not installed.")
        subprocess.run("cd " + repo_dir + " && gradlew setup", shell=True)
    
    # Run the gradlew Iris task
    subprocess.run("cd " + repo_dir + " && gradlew Iris", shell=True)

    # Move the jar file that appeared in the build/libs directory to the plugins folder and rename it to Iris.jar
    if (not os.path.isdir(repo_dir + "/build/libs")):
        print("Could not find the Iris.jar file in the build/libs directory")
        print("Please make sure the build task was successful")
        exit(1)

    for file in os.listdir(repo_dir + "/build/libs"):
        if file.endswith(".jar"):
            os.rename(repo_dir + "/build/libs/" + file, "plugins/" + file)
            print("Moved " + file + " to plugins folder")
            break

def check_iris(download_mode: int, repo_dir: str, update: bool):
    for file in os.listdir("plugins"):
        if iris_regex.match(file):
            if update:
                os.remove(file)
                print("Removed " + file + " from plugins folder to update")
            else:
                print("Found " + file + " in plugins folder")
                return

    if (download_mode == -1):

        print("Iris is not installed. Please enter how you wish to install Iris:")
        print("1. Download the git repository and setup (~5 to 10 minutes first time, ~1 minute after)")
        print("2. Download the jar file from spigot (~1 minute)")
        print("3. Install Iris manually (skip)")
        download_mode = int(input("Choice: "))

    if download_mode == 2:
        # Open https://www.spigotmc.org/resources/iris-world-gen-custom-biome-colors.84586/
        # and download the jar file
        print("Download the jar file from https://www.spigotmc.org/resources/iris-world-gen-custom-biome-colors.84586/")
        print("and move it to the plugins folder")
        print("and run this script again")
        # Open the webbrowser with the website
        time.sleep(1)
        os.system("start https://www.spigotmc.org/resources/iris-world-gen-custom-biome-colors.84586/")
        exit(0)

    if download_mode != 1:
        print("Skipping Iris")
        return

    # Install Iris using the github repo
    install_iris_github(repo_dir)

# Check if the rift jar exists
# Use regex to find the jar file, with pattern: Rift-?.*\.jar
# If the jar file is not found, ask the user to download it from 
# https://github.com/VolmitSoftware/Rift/releases/download/1.0.1/Rift-1.0.1.jar
# and move it to the plugins folder
# or to skip downloading the jar file altogether
def check_rift(download_mode: int):
    rift_regex = regex.compile(r'Rift-?.*\.jar')
    for file in os.listdir("plugins"):
        if rift_regex.match(file):
            print("Found " + file + " in plugins folder")
            return

    if download_mode == -1:
        print("Rift is not installed. Please enter how you wish to install Rift:")
        print("1. Download the jar file from github (fast, ~1 minute)")
        print("2. Do not install rift (skip)")
        download_mode = input("Choice: ")
    if download_mode == 1:
        print("Downloading Rift from github")
        open("plugins/Rift.jar", "wb").write(requests.get("https://github.com/VolmitSoftware/Rift/releases/download/1.0.1/Rift-1.0.1.jar").content)
        print("Downloaded rift from github")
    else:
        print("Skipping Rift")

# Check to make sure purpur is installed
def check_purpur():
    if not os.path.isfile("purpur.jar"):
        print("Downloading purpur.jar from https://api.purpurmc.org/v2/purpur/1.18.1/latest/download")
        open("purpur.jar", "wb").write(requests.get("https://api.purpurmc.org/v2/purpur/1.18.1/latest/download").content)
    else:
        print("Found purpur.jar in the current directory")

# Run the main server loop
def boot_loop(cmd: str, config: dict):
        
    # Run the server
    while (True):
        print("Starting the server: " + str(cmd))
        subprocess.run(cmd, shell=True)
        print("Server stopped. Rebooting in 5 seconds. Press CTRL+C to cancel.")
        if config["clean"]:
            clean(config["cleanfolders"], config["cleanfiles"])
        time.sleep(5)

# Cleanup directories
def clean(folders, files):
    print("Cleaning up directories")
    for folder in folders:
        shutil.rmtree(folder, True)
    for file in files:
        if os.path.exists(file):
            os.remove(file)

# Run the server
def run():
    config = get_config("servermanager.json")

    # Cleanup
    if config["clean"]:
        clean(config["cleanfolders"], config["cleanfiles"])

    # Check if the jar file exists
    check_purpur()

    # Check if the eula.txt file exists
    if not os.path.isfile("eula.txt"):
        print("Creating eula.txt")
        with open("eula.txt", "w") as f:
            f.write("eula=true")
    else:
        print("Found eula.txt in server folder")

    # Check if the run.bat file exists
    if not os.path.isfile("run.bat"):
        print("Creating run.bat")
        with open("run.bat", "w") as f:
            # Write "python" with the name of this file and pause on a new line
            f.write("python " + os.path.basename(__file__) + "\nPAUSE")
    else:
        print("Found run.bat in server folder")

    # Check if the update.bat file exists
    if not os.path.isfile("update.bat"):
        print("Creating update.bat")
        with open("update.bat", "w") as f:
            # Write "python" with the name of this file and pause on a new line
            f.write("python " + os.path.basename(__file__) + " -u\nPAUSE")
    else:
        print("Found update.bat in server folder")

    if not os.path.isdir("plugins"):
        os.mkdir("plugins/")

    download = config["download"]

    # Check if there is a jar of the regex (Iris-).*(\.jar)
    if download["use_iris"]:
        check_iris(download["iris_download_mode"], download["iris_repo"], len(sys.argv) > 1 and sys.argv[1] == "-u")

    # Check if there is a jar of the regex (Rift-).*(\.jar)
    if download["use_rift"]:
        check_rift(download["rift_download_mode"])

    cmd = ["java"] + sys.argv[1:] + ["-jar", "purpur.jar", "nogui"]

    # Run the main server loop
    boot_loop(cmd, config)

if __name__ == "__main__":
    run()