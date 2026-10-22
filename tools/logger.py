import os


class Logger:
    _log_file = None

    @classmethod
    def set_log_file(cls, path):
        if not path:
            return
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        cls._log_file = open(path, "a", encoding="utf-8")

    @classmethod
    def _write(cls, level, msg):
        line = "{}: {}".format(level, msg)
        if cls._log_file:
            cls._log_file.write(line + "\n")
            cls._log_file.flush()

    @staticmethod
    def error(str):
        print("\033[31m"+"ERROR: "+str+"\033[0m")
        Logger._write("ERROR", str)

    @staticmethod
    def info(str):
        print("\033[32m"+"INFO: "+"\033[0m"+str)
        Logger._write("INFO", str)

    @staticmethod
    def warning(str):
        print("\033[33m"+"WARN: "+str+"\033[0m")
        Logger._write("WARN", str)
