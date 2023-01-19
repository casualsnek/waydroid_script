class Logger:

    @staticmethod
    def error(str):
        print("\033[31m"+"ERROR: "+str+"\033[0m")

    @staticmethod
    def info(str):
        print("\033[32m"+"INFO: "+"\033[0m"+str)

    @staticmethod
    def warning(str):
        print("\033[33m"+"WARN: "+str+"\033[0m")
