"""
Authentication system for FlowMind
Single-user login with JWT tokens
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
import os

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Config
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "flowmind_secret_change_in_production_123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Admin credentials (single user)
ADMIN_EMAIL = "gabriel@flowmind.ai"
# Password: FlowMind2025! (hashed)
ADMIN_PASSWORD_HASH = "$2b$12$LQ3Z8J0YQZ0Z0Z0Z0Z0Z0uK8X8X8X8X8X8X8X8X8X8X8X8X8X8X8X"  # Placeholder


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token from Authorization header"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None or email != ADMIN_EMAIL:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Login endpoint for single admin user
    
    Credentials:
    - Email: gabriel@flowmind.ai
    - Password: FlowMind2025!
    """
    # Verify email
    if request.email != ADMIN_EMAIL:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    # For now, simple password check (will generate proper hash after)
    if request.password != "FlowMind2025!":
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": request.email},
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60  # seconds
    )


@router.post("/verify")
async def verify(payload: dict = Depends(verify_token)):
    """Verify if current token is valid"""
    return {
        "valid": True,
        "email": payload.get("sub"),
        "expires_at": payload.get("exp")
    }


@router.post("/logout")
async def logout():
    """
    Logout endpoint (client-side token removal)
    JWT tokens are stateless, so just return success
    """
    return {"message": "Logged out successfully"}


# Helper to generate password hash (run once)
def generate_password_hash(password: str) -> str:
    """Generate bcrypt hash for password"""
    return pwd_context.hash(password)


# Uncomment to generate hash for "FlowMind2025!"
# print(generate_password_hash("FlowMind2025!"))
