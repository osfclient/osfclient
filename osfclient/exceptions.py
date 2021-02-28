class OSFException(Exception):
    pass


class UnauthorizedException(OSFException):
    pass


class FolderExistsException(OSFException):
    def __init__(self, name):
        self.args = ('Folder %s already exists.' % name,)


class ToManyRequests(OSFException):
    def __init__(self, msg, *args, **kwargs):
        msg = msg + 'Too many requests have been sent. See '
        'https://help.osf.io/hc/en-us/articles/360054528874-OSF-Storage-Caps'
        'for details'
        super().__init__(msg, *args, **kwargs)


class NotFound(OSFException):
    def __init__(self, msg, *args, **kwargs):
        msg = msg + ' The requested resource does not exist.'
        super().__init__(msg, *args, **kwargs)


class Gone(OSFException):
    def __init__(self, msg, *args, **kwargs):
        msg = msg + ' The requested resource is no longer available,'
        ' most likely because it was deleted.'
        super().__init__(msg, *args, **kwargs)


class ServerError(OSFException):
    def __init__(self, msg, *args, **kwargs):
        msg = msg + ' The API server encountered an unexpected error.'
        super().__init__(msg, *args, **kwargs)


class BadRequest(OSFException):
    def __init__(self, msg, *args, **kwargs):
        msg = msg + 'The request was unacceptable, often due to a'
        ' missing required parameter or malformed data.'
        super().__init__(msg, *args, **kwargs)


def raise_unexp_status(status_code, expected_code=200, msg=None):
    msg = msg or "Response has status code {} not {}".format(status_code, expected_code)
    exc= {
        400: BadRequest,
        401: UnauthorizedException,
        404: NotFound,
        410: Gone,
        429: ToManyRequests,
    }.get(status_code, OSFException)
    raise exc(msg=msg)
