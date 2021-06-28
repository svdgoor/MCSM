from SM.util import defaultRun

autoClean = True
flags = "-Xms4G -Xmx4G"
javaPaths = {
    11: "C:\Program Files\Java\jdk-11.0.10\\bin\java.exe",
    16: "C:\Program Files\Java\jdk-16.0.1\\bin\java.exe"
}

if __name__ == "__main__":
    defaultRun(javaPaths, flags, autoClean)