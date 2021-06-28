class Java:
    javaPaths = None
    def __init__(self, java: int, javaPaths: dict):
        if java not in javaPaths:
            print("Java {} is not in the java path list!".format(java))
            return
        self.path = Java.javaPaths[java]
        self.version = java