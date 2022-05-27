# ValueError https://docs.python.org/3/library/exceptions.html

from path import EXFOR_ALL_PATH


class Incorrectx4Number:
    def __init__(self, value=""):
        self.value = "Incorrect EXFOR entry number " + repr(value)
        raise IOError(self.value)


class x4NoBody:
    def __init__(self, value=""):
        self.value = "no entry body read, possible file reading error" + repr(value)
        raise IOError(self.value)


class NoPickelExistenceError:
    def __init__(self, value=""):
        self.value = "No pickel file at " + repr(value)
        raise IOError(self.value)


class Nox4AllDirExistenceError:
    def __init__(self, value=""):
        self.value = "No x4all dirctory at " + repr(value)
        raise IOError(self.value)


class Nox4FilesExistenceError:
    def __init__(self, value=""):
        self.value = "No files in " + repr(value)
        raise IOError(self.value)


class x4FileOpenError:
    def __init__(self, value=""):
        self.value = (
            "Entry file " + repr(value) + " cannot be opened from" + EXFOR_ALL_PATH
        )
        raise IOError(self.value)
