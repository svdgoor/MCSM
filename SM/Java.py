javaPaths = {
    11: "C:\Program Files\Java\jdk-11.0.10\\bin\java.exe",
    16: "C:\Program Files\Java\jdk-16.0.1\\bin\java.exe"
}

class Java:
    def __init__(self, java: int, javaPaths: dict):
        if java not in javaPaths:
            print("Java {} is not in the java path list!".format(java))
            return
        self.path = javaPaths[java]
        self.version = java