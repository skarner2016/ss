from app.core.error_codes import ErrorCode
from app.core.exceptions import ApiBusinessException


def test_error_code_tuple_format():
    code, message = ErrorCode.PASSWORD_ERROR
    assert isinstance(code, int)
    assert isinstance(message, str)
    assert code == 2002


def test_api_business_exception_from_tuple():
    exc = ApiBusinessException(*ErrorCode.PASSWORD_ERROR)
    assert exc.code == 2002
    assert exc.message == "密码错误"


def test_api_business_exception_from_code():
    exc = ApiBusinessException.from_code(ErrorCode.POST_NOT_FOUND)
    assert exc.code == 3001
    assert exc.message == "帖子不存在"
