class ApiBusinessException(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message

    @classmethod
    def from_code(cls, error_code: tuple):
        return cls(code=error_code[0], message=error_code[1])
