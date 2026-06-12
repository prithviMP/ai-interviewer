from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from models.auth import UserResponse
from services.auth_service import AuthService

security = HTTPBearer(auto_error=False)
auth_service = AuthService()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> UserResponse:
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = auth_service.decode_token(credentials.credentials)
    return auth_service.get_user(user_id)
