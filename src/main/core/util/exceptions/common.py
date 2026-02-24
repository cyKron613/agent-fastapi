class BizException(Exception):
    """
    Throw an handler when the service handler.
    """

    def __init__(self, code: int, message: str):
        self.message = message
        self.code = code
