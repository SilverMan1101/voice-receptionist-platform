import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
import sys
from dotenv import load_dotenv

load_dotenv(".env.local")

# Ensure shared_kernel is discoverable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../services')))
from shared_kernel.domain.schemas import TokenData

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 day

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8003/api/v1/auth/login")

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# def get_current_token_data(token: str = Depends(oauth2_scheme)) -> TokenData:
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_id_str: str = payload.get("sub")
#         org_id_str: str = payload.get("org_id")
#         role: str = payload.get("role")
#         if user_id_str is None or org_id_str is None:
#             raise credentials_exception
#         token_data = TokenData(user_id=user_id_str, organization_id=org_id_str, role=role)
#     except (JWTError, ValidationError):
#         raise credentials_exception
#     return token_data


def get_current_token_data(credentials: HTTPAuthorizationCredentials = Depends(security),) -> TokenData:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("sub")
        org_id = payload.get("org_id")
        role = payload.get("role")

        if user_id is None or org_id is None:
            raise credentials_exception

        return TokenData(
            user_id=user_id,
            organization_id=org_id,
            role=role,
        )

    except (JWTError, ValidationError):
        raise credentials_exception