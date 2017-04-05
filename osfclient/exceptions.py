class OSFException(Exception):
    pass


class UnauthorizedException(OSFException):
    pass


class FolderExistsException(OSFException):
    def __init__(self, name):
        self.args = ('Folder %s already exists.' % name,)
