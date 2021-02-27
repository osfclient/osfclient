class OSFException(Exception):
    pass


class UnauthorizedException(OSFException):
    pass


class FolderExistsException(OSFException):
    def __init__(self, name):
        self.args = ('Folder %s already exists.' % name,)


class ToManyRequests(OSFException):
    def __init__(self, msg='Too many requests have been sent. See '
                           'https://help.osf.io/hc/en-us/articles/360054528874-OSF-Storage-Caps'
                           'for details', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class NotFound(OSFException):
    def __init__(self, msg='The requested resource does not exist.', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class Gone(OSFException):
    def __init__(self, msg='The requested resource is no longer available,'
                           ' most likely because it was deleted.', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class ServerError(OSFException):
    def __init__(self, msg='The API server encountered an unexpected error.', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class BadRequest(OSFException):
    def __init__(self, msg='The request was unacceptable, often due to a'
                           ' missing required parameter or malformed data.', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


def raise_unexp_status(status_code, expected_code=200, msg=None):
    exc, msg = {
        400: (BadRequest, msg),
        401: (UnauthorizedException, msg),
        404: (NotFound, msg),
        410: (Gone, msg),
        429: (ToManyRequests, msg),
    }.get(status_code, (OSFException, "Response has status "
                                      "code {} not {}".format(status_code, expected_code)))
    if msg is not None:
        raise exc(msg=msg)
    else:
        raise exc
