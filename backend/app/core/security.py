from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Literal
from uuid import UUID

from jose import ExpiredSignatureError, JWTError, jwt
import bcrypt as _bcrypt

from app.core.exceptions import InvalidTokenError, TokenExpiredError

# =============================================================================
# Password hashing  (bcrypt direct — passlib dropped, incompatible with bcrypt 4.x)
# =============================================================================

_BCRYPT_ROUNDS = 12


def _pre_hash(plain: str) -> bytes:
    """SHA-256 the plain password so bcrypt always receives exactly 32 bytes.

    bcrypt truncates inputs > 72 bytes; pre-hashing eliminates that limit.
    """
    return hashlib.sha256(plain.encode()).digest()


def hash_password(plain: str) -> str:
    return _bcrypt.hashpw(_pre_hash(plain), _bcrypt.gensalt(_BCRYPT_ROUNDS)).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return _bcrypt.checkpw(_pre_hash(plain), hashed.encode())


# =============================================================================
# JWT
# =============================================================================

TokenType = Literal["access", "refresh"]


def _build_payload(
    user_id: UUID,
    tenant_id: UUID,
    role: str,
    token_type: TokenType,
    expire_delta: timedelta,
    jti: str,
) -> dict:
    now = datetime.now(tz=timezone.utc)
    return {
        "sub": str(user_id),
        "tenant_id": str(tenant_id),
        "role": role,
        "type": token_type,
        "jti": jti,
        "iat": int(now.timestamp()),
        "exp": int((now + expire_delta).timestamp()),
    }


def create_access_token(
    user_id: UUID,
    tenant_id: UUID,
    role: str,
    private_key: str,
    algorithm: str,
    expire_minutes: int,
) -> str:
    jti = str(uuid.uuid4())
    payload = _build_payload(
        user_id=user_id,
        tenant_id=tenant_id,
        role=role,
        token_type="access",
        expire_delta=timedelta(minutes=expire_minutes),
        jti=jti,
    )
    return jwt.encode(payload, private_key, algorithm=algorithm)


def create_refresh_token(
    user_id: UUID,
    tenant_id: UUID,
    role: str,
    private_key: str,
    algorithm: str,
    expire_days: int,
) -> tuple[str, str]:
    """Returns (signed_jwt, jti). Caller stores hash_jti(jti) in DB."""
    jti = str(uuid.uuid4())
    payload = _build_payload(
        user_id=user_id,
        tenant_id=tenant_id,
        role=role,
        token_type="refresh",
        expire_delta=timedelta(days=expire_days),
        jti=jti,
    )
    token = jwt.encode(payload, private_key, algorithm=algorithm)
    return token, jti


def decode_token(token: str, public_key: str, algorithm: str) -> dict:
    """
    Decode and verify a JWT. Raises domain exceptions (never raw jose errors).
    Returns the full payload dict.
    """
    try:
        payload = jwt.decode(token, public_key, algorithms=[algorithm])
        return payload
    except ExpiredSignatureError:
        raise TokenExpiredError()
    except JWTError:
        raise InvalidTokenError()


def hash_jti(jti: str) -> str:
    """SHA-256 hex digest of the JTI. This is what gets stored in the DB."""
    return hashlib.sha256(jti.encode()).hexdigest()
