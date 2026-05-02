from app.core.security import create_token, decode_token


def test_create_and_decode_token():
    payload = {"user_id": 123}
    token = create_token(payload)
    decoded = decode_token(token)
    assert decoded["user_id"] == 123


def test_decode_invalid_token():
    result = decode_token("invalid-token")
    assert result is None
