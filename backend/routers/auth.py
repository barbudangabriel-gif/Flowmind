"""
Authentication router for FlowMind
Single-user login with JWT tokens
"""
import os
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Single user credentials (Gabriel)
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "gabriel@flowmind.ai")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "FlowMind2025!")
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "flowmind-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user: dict


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Login endpoint - single user authentication
    
    Credentials:
    - Email: gabriel@flowmind.ai (or env ADMIN_EMAIL)
    - Password: FlowMind2025! (or env ADMIN_PASSWORD)
    """
    if request.email != ADMIN_EMAIL or request.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create JWT token
    access_token = create_access_token(
        data={"sub": request.email, "name": "Gabriel", "role": "admin"}
    )
    
    return {
        "token": access_token,
        "user": {
            "email": request.email,
            "name": "Gabriel",
            "role": "admin"
        }
    }


@router.post("/verify")
async def verify_token_endpoint(authorization: str = Header(None)):
    """Verify JWT token validity"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    
    return {
        "valid": True,
        "user": {
            "email": payload.get("sub"),
            "name": payload.get("name"),
            "role": payload.get("role")
        }
    }


@router.post("/logout")
async def logout():
    """Logout endpoint (client-side token removal)"""
    return {"message": "Logged out successfully"}


# Dependency for protected routes
async def get_current_user(authorization: str = Header(None)) -> dict:
    """Dependency to verify JWT token in protected routes"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    
    return {
        "email": payload.get("sub"),
        "name": payload.get("name"),
        "role": payload.get("role")
    }
