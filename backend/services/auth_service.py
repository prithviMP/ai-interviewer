import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from config import get_settings
from database import get_connection, row_to_dict
from models.auth import AuthResponse, LoginRequest, SignUpRequest, UserResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def signup(self, payload: SignUpRequest) -> AuthResponse:
        user_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        password_hash = pwd_context.hash(payload.password)

        try:
            with get_connection() as conn:
                conn.execute(
                    "INSERT INTO users (id, email, name, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
                    (user_id, payload.email.lower(), payload.name.strip(), password_hash, now),
                )
        except Exception as exc:
            if "UNIQUE constraint failed" in str(exc):
                raise HTTPException(status_code=400, detail="Email already registered") from exc
            raise

        user = UserResponse(id=user_id, name=payload.name.strip(), email=payload.email.lower())
        return AuthResponse(access_token=self._create_token(user_id), user=user)

    def login(self, payload: LoginRequest) -> AuthResponse:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE email = ?", (payload.email.lower(),)
            ).fetchone()

        user_row = row_to_dict(row)
        if not user_row or not pwd_context.verify(payload.password, user_row["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        user = UserResponse(id=user_row["id"], name=user_row["name"], email=user_row["email"])
        return AuthResponse(access_token=self._create_token(user_row["id"]), user=user)

    def get_user(self, user_id: str) -> UserResponse:
        with get_connection() as conn:
            row = conn.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,)).fetchone()
        user_row = row_to_dict(row)
        if not user_row:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse(**user_row)

    def decode_token(self, token: str) -> str:
        settings = get_settings()
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
            user_id: str | None = payload.get("sub")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token")
            return user_id
        except JWTError as exc:
            raise HTTPException(status_code=401, detail="Invalid or expired token") from exc

    def _create_token(self, user_id: str) -> str:
        settings = get_settings()
        expire = datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expire_hours)
        payload = {"sub": user_id, "exp": expire}
        return jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")
