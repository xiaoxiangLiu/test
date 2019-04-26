

class SyncException(Exception):
    """
    sync异常
    """
    def __init__(self, ErrorInfo):
        super().__init__()
        self.ErrorInfo = ErrorInfo

    def __repr__(self):
        return self.ErrorInfo


class LoginException(Exception):
    """
    登陆异常
    """
    def __init__(self, errorInfo):
        super().__init__()
        self.errorInfo = errorInfo

    def __repr__(self):
        return self.errorInfo


class HttpStatusException(Exception):
    """
    接口状态异常
    """
    def __init__(self, ErrorInfo):
        super().__init__()
        self.ErrorInfo = ErrorInfo

    def __repr__(self):
        return self.ErrorInfo


class TokenException(Exception):
    """
    token 异常
    """
    pass


class AuthorizationException(Exception):
    """
    Authorization 异常
    """
    pass


