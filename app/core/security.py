from functools import lru_cache
from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

from app.core.config import get_settings

settings = get_settings()
bearer_scheme = HTTPBearer(auto_error=True)


@lru_cache
def get_jwk_client() -> PyJWKClient:
    return PyJWKClient(settings.keycloak_jwks_url)


def validate_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict[str, Any]:
    token = credentials.credentials

    try:
        signing_key = get_jwk_client().get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256", "RS384", "RS512"],
            audience=settings.keycloak_audience,
            issuer=settings.keycloak_issuer,
            options={"require": ["exp", "iat", "iss"]},
        )
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=401,
            detail=f"Token expirado: {exc}",
        ) from exc
    
    except jwt.InvalidAudienceError as exc:
        raise HTTPException(
            status_code=401,
            detail=f"Audience inválida: {exc}",
        ) from exc
    
    except jwt.InvalidIssuerError as exc:
        raise HTTPException(
            status_code=401,
            detail=f"Issuer inválido: {exc}",
        ) from exc
    
    except jwt.InvalidSignatureError as exc:
        raise HTTPException(
            status_code=401,
            detail=f"Firma inválida: {exc}",
        ) from exc
    
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=401,
            detail=f"{type(exc).__name__}: {exc}",
        ) from exc

    allowed_username = settings.keycloak_allowed_username
    if allowed_username:
        token_username = payload.get("preferred_username")
        if token_username != allowed_username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario no autorizado para esta API",
            )

    return payload
