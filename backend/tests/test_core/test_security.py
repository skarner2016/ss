from app.core.security import hash_password, verify_password, create_token, decode_token


def test_hash_and_verify_password():
    password = "test123456"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)


def test_verify_wrong_password():
    hashed = hash_password("correct-password")
    assert not verify_password("wrong-password", hashed)


def test_create_and_decode_token():
    payload = {"user_id": 123}
    token = create_token(payload)
    decoded = decode_token(token)
    assert decoded["user_id"] == 123


def test_decode_invalid_token():
    result = decode_token("invalid-token")
    assert result is None
