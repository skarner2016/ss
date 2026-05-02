from app.core.error_codes import ErrorCode
from app.core.exceptions import ApiBusinessException


def test_code_invalid_error():
    code, message = ErrorCode.CODE_INVALID
    assert code == 1003
    assert message == "验证码错误或已过期"


def test_code_send_failed_error():
    code, message = ErrorCode.CODE_SEND_FAILED
    assert code == 1004
    assert message == "邮件发送失败，请稍后重试"


def test_api_business_exception_from_code():
    exc = ApiBusinessException.from_code(ErrorCode.POST_NOT_FOUND)
    assert exc.code == 3001
    assert exc.message == "帖子不存在"
