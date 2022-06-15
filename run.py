# Starts the minecraft server and a couple programs to run

import os, subprocess, sys, shutil, json, time, cgi
from urllib.request import urlopen, urlretrieve, build_opener, install_opener

try:
    import regex
except ImportError:
    print("Trying to Install required module: regex\n")
    subprocess.run(["python", "-m", "pip", "install", "regex", "--user"])
    try:
        import regex
    except ImportError:
        print("Failed to install Regex. Please install manually by running: pip install regex")
        print("In a terminal, run: python -m pip install regex")

try:
    from git import Repo
except ImportError:
    print("Trying to Install required module: git\n")
    subprocess.run(["python", "-m", "pip", "install", "gitpython", "--user"])
    try:
        from git import Repo
    except ImportError:
        print("Failed to install git. Please install manually by running: pip install gitpython")
        print("In a terminal, run: python -m pip install gitpython")

default_settings = {
    "run_regex": "purpur.*\.jar",
    "clean": {
        "enabled": False,
        "enabled_on_reboot": False,
        "folders": [
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
        "files": [
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
        ]
    },
    "do_download": True,
    "download": [
        {
            "name": "Iris",
            "use": True,
            "url": "https://www.spigotmc.org/resources/iris-world-gen-custom-biome-colors.84586/",
            "dir": "plugins",
            "regex": "Iris-?.*\.jar",
            "mode": 1,

            "git_url": "https://github.com/VolmitSoftware/Iris.git",
            "git_branch": "master",
            "git_repo_dir": "Iris"
        },
        {
            "name": "Rift",
            "use": True,
            "url": "https://github.com/VolmitSoftware/Rift/releases/download/1.0.1/Rift-1.0.1.jar",
            "dir": "plugins",
            "regex": "Rift-?.*\.jar",
            "mode": 1
        },
        {
            "name": "Purpur",
            "use": True,
            "url": "https://api.purpurmc.org/v2/purpur/1.18.2/latest/download",
            "dir": "",
            "regex": "Purpur-?.*\.jar",
            "mode": 1
        },
        {
            "name": "BileTools",
            "use": True,
            "url": "https://github.com/VolmitSoftware/BileTools/releases/download/2/BileTools-2.jar",
            "dir": "plugins",
            "regex": "BileTools-?.*\.jar",
            "mode": 1
        },
        {
            "name": "WorldEdit",
            "use": True,
            "url": "https://dev.bukkit.org/projects/worldedit/files/latest",
            "dir": "plugins",
            "regex": "WorldEdit-Bukkit?.*\.jar",
            "mode": 1
        },
        {
            "name": "EssentialsX",
            "use": True,
            "url": "https://github.com/EssentialsX/Essentials/releases/download/2.19.2/EssentialsX-2.19.2.jar",
            "dir": "plugins",
            "regex": "EssentialsX-?.*\.jar",
            "mode": 1
        }
    ],
    "reboot_delay": 0
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

# Download file from url to directory with original filename
def download_file(url: str, directory: str, backupname: str):

    # Create the build opener
    opener = build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    install_opener(opener)

    # Get the headers
    header_details = urlopen(url).info()['Content-Disposition']
    filename = ""
    if not header_details:
        print("Failed to get file name from header from: " + url)
        print("Using backup name: " + backupname)
        filename = backupname
    else:
        value, params = cgi.parse_header(header_details)
        filename = params['filename']

    # Get the file
    urlretrieve(url, directory + "/" + filename)

# Check if the @program_name is installed in @program_dir
# Use regex to find the jar file, with pattern: @regex_match
# If @update is true, remove the jar file from @program_dir
# If the jar file is not found, ask the user for input or use: @download_mode
# If the jar file is found, print a message saying so
# If it is not found, ask the user to:
# 1. Have it automatically downloaded from @program_url
# 2. Send the @program_url to the user with a small tutorial and shutdown the program
# 3. Do not install the program (skip)
def install_program(
    program_name: str,
    program_mode: int,
    program_url: str,
    program_dir: str,
    program_regex: str,
    update: bool
):
    # Add cwd to program_dir
    program_dir = os.path.join(os.getcwd(), program_dir)

    # Create the compiled regex from the regex_match string
    regex_compiled = regex.compile(program_regex)

    # Check if the directory exists
    if not os.path.isdir(program_dir):
        os.makedirs(os.getcwd() + program_dir)

    # Check if the program is installed using regex
    for file in os.listdir(program_dir):
        if regex_compiled.match(file):
            if update:
                os.remove(program_dir + "/" + file)
                print("Removed " + file + " from " + program_dir + " to update")
            else:
                print("Found " + file + " in plugins folder for program: " + program_name)
                return

    # Check if the download mode is -1, meaning the user provides a choice
    if program_mode == -1:
        print("{} is not installed. Please enter how you wish to install {}:".format(program_name, program_name))
        print("1. Download the jar file from {} (fast, ~1 minute)".format(program_url))
        print("2. Download the jar file manually from the website (manual, ~2 minutes")
        print("3. Do not install {} (skip)".format(program_name))
        program_mode = input("Choice: ")

    # Check if the download mode is 1, meaning the jar file should be downloaded from the download_url
    if program_mode == 1:
        print("Downloading {} from {}".format(program_name, program_url))
        download_file(program_url, program_dir, program_name + ".jar")
        print("Downloaded {} from {}".format(program_name, program_url))

    # Check if the download mode is 2, meaning the jar file should be downloaded from the website manually
    elif program_mode == 2:
        print("Download the jar file from {}".format(program_url))
        print("Then, move it to the correct folder ({}), and run this script again".format(program_dir))
        time.sleep(1)
        os.system("start " + program_url)
        exit(0)

    # Check if the download mode is something else, meaning the jar file should not be installed
    else:
        print("Skipping {}".format(program_name))

# Iris installation
def install_iris(program: dict, update: bool):

    program_mode = program["mode"]
    program_name = program["name"]
    program_dir = os.path.join(os.getcwd(), program["dir"])
    program_regex = program["regex"]
    program_url = program["url"]
    program_git_url = program["git_url"]
    program_git_branch = program["git_branch"]
    program_git_repo_dir = program["git_repo_dir"]

    # Create the compiled regex from the regex_match string
    regex_compiled = regex.compile(program_regex)

    # Check if the directory exists
    if not os.path.isdir(program_dir):
        os.makedirs(program_dir)

    # Check if the program is installed using regex
    for file in os.listdir(program_dir):
        if regex_compiled.match(file):
            if update:
                os.remove(program_dir + "/" + file)
                print("Removed " + file + " from " + program_dir + " to update")
            else:
                print("Found " + file + " in plugins folder for program: " + program_name)
                return

    # Check if the download mode is -1, meaning the user provides a choice
    if program_mode == -1:
        print("{} is not installed. Please enter how you wish to install {}:".format(program_name, program_name))
        print("1. Clone the jar file from {} (~10 minutes the first time / ~1 minute after)".format(program_git_url))
        print("2. Download the jar file manually from the website (manual, ~2 minutes)")
        print("3. Do not install {} (skip)".format(program_name))
        program_mode = input("Choice: ")

    # Run normal install unless the user selected option 1
    if program_mode != 1:
        install_program(program_name, program_mode, program_url, program_dir, program_regex, update)
        return

    # Check if the directory exists
    print("Cloning Iris from github, using repodir: " + program_git_repo_dir)

    # Check if the repo exists
    if not os.path.isdir(program_git_repo_dir):
        os.makedirs(program_git_repo_dir)
        print("Setting up Iris repo")
        repo = Repo.clone_from(program_git_url, program_git_repo_dir)
        print("Cloned repository")
        repo.git.checkout(program_git_branch)
        print("Checked out " + program_git_branch)
        repo.git.pull()
        print("Pulled latest changes")

    # Run the gradlew Setup task unless already (seemingly) setup
    # Warning: This check is pretty shallow but does the job 99% of the time
    if (not os.path.isdir(program_git_repo_dir + "/build/buildtools/CraftBukkit")):
        print("Please make sure you have the CraftBukkit buildtools installed and setup") 
        input("Press enter to run the gradlew setup task. This script thinks it's not installed.")
        subprocess.run("cd " + program_git_repo_dir + " && gradlew setup", shell=True)
    
    # Run the gradlew Iris task
    subprocess.run("cd " + program_git_repo_dir + " && gradlew Iris", shell=True)

    # Move the jar file that appeared in the build/libs directory to the plugins folder and rename it to Iris.jar
    if (not os.path.isdir(program_git_repo_dir + "/build")):
        print("Could not find the Iris.jar file in the build/libs directory")
        print("Please make sure the build task was successful")
        exit(1)

    # Move the jar file that appeared in build to the program directory
    for file in os.listdir(program_git_repo_dir + "/build"):
        if file.endswith(".jar"):
            os.rename(program_git_repo_dir + "/build/" + file, program_dir + "/" + file)
            print("Moved " + file + " to plugins folder")
            break

# Install all programs in the "download" list in the config file
def install_programs(config: dict, update: bool):
    for program in config["download"]:
        if program["use"]:
            if program["name"] == "Iris":
                install_iris(program, update)
            else:
                install_program(program["name"], program["mode"], program["url"], program["dir"], program["regex"], update)

# If the file is missing, create it and add the content
def install_file(filename: str, directory: str, content: str):
    if directory != "":
        directory = directory + "/"
    if not os.path.isfile(directory + filename):
        print("Creating " + filename + " in " + directory)
        with open(directory + filename, "w") as file:
            print("Writing " + content + " to " + filename)
            file.write(content)
    else:
        print("Found " + filename + " in " + directory)

# Install eula.txt, run.bat and update.bat
def install_files():

    # Check for eula.txt with the content "eula=true"
    install_file("eula.txt", "", "eula=true")

    # Check for run.bat with the content "python " + this_file + " -Xmx1G -Xms1G\nPAUSE"
    install_file("run.bat", "", "python " + os.path.basename(__file__) + " -Xmx8G -Xms8G\nPAUSE")

    # Check for update.bat with the content "python " + this_file + " -u\nPAUSE"
    install_file("update.bat", "", "python " + os.path.basename(__file__) + " -u\nPAUSE")

# Cleanup directories
def clean(clean_config: dict):
    if not clean_config["enabled"]:
        print("Skipping cleanup")
        return

    # Cleanup the directory
    print("Cleaning up directories")
    for folder in clean_config["folders"]:
        shutil.rmtree(folder, True)
    for file in clean_config["files"]:
        if os.path.exists(file):
            os.remove(file)

# Run the server
if __name__ == "__main__":

    # If the current working directory is a user directory, matching regex "[ABCDEFGHIJK]:\*Users\*[a-z]*"
    # Confirm with the user that they want to run the server
    main_dir_regex = regex.compile("[ABCDEFGHIJK]:\\*Users\\*[a-z]*")
    if main_dir_regex.match(os.getcwd()):
        print("This script is not meant to be run from a user directory. Please run it from the root directory.")
        input("Press enter to confirm if you're sure to run it in the root directory.")

    # Get config
    config = get_config("servermanager.json")

    # Clean
    clean(config["clean"])
    
    # Install programs
    update_programs = len(sys.argv) > 1 and sys.argv[1] == "-u"
    if config["do_download"]:
        install_programs(config, update_programs)

    # Setup required files
    install_files()

    # Find the server jar using regex in config["run_regex"]
    server_jar = ""
    server_jar_regex = regex.compile(config["run_regex"])
    for file in os.listdir(os.getcwd()):
        if server_jar_regex.match(file):
            server_jar = file
            print("Found server jar: " + server_jar)
            break

    # Create the command
    flags = [flag for flag in sys.argv[1:] if flag != "-u"]
    cmd = ["java"] + flags + ["-jar", server_jar, "nogui"]

    # Run the server
    while (True):
        print("Starting the server: " + str(cmd))
        subprocess.run(cmd, shell=True)
        print("Server stopped. Rebooting in " + str(config["reboot_delay"]) + " seconds. Press CTRL+C to cancel.")
        if config["clean"]["enabled_on_reboot"]:
            clean(config["clean"])
        time.sleep(config["reboot_delay"])