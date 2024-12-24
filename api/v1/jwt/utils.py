import jwt
from config import jwt_settings
from datetime import timedelta, datetime, UTC
from typing import Any


def encode_jwt(
    payload: dict,
    expire_timedelta: timedelta,
    private_key: str = jwt_settings.private_key_path.read_text(),
    algorithm: str = jwt_settings.algorithm,
) -> str:
    to_encode = payload.copy()
    now = datetime.now(UTC)
    expire = now + expire_timedelta
    to_encode.update(iat=now, exp=expire)
    encoded_jwt = jwt.encode(payload=to_encode, key=private_key, algorithm=algorithm)

    return encoded_jwt


def decode_jwt(
    token: str | bytes,
    public_key: str = jwt_settings.public_key_path.read_text(),
    algorithm: str = jwt_settings.algorithm
) -> Any:
    decoded_jwt = jwt.decode(jwt=token, key=public_key, algorithm=algorithm)

    return decoded_jwt


