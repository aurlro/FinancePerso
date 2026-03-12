"""
Authentication Router - JWT-based authentication for FinancePerso API.

Provides endpoints for:
- User registration
- User login
- Token refresh
- User profile retrieval
- Password change
"""

import os
import sqlite3
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

import sys
from pathlib import Path
# Add FinancePerso root to path for importing modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from modules.db.connection import get_db_connection
from modules.logger import logger

from models.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
    RefreshTokenRequest,
    ChangePasswordRequest,
    ErrorResponse,
)

router = APIRouter(tags=["Authentication"])

# Security configuration - Load from environment variable
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    logger.warning("JWT_SECRET_KEY not set, using fallback (INSECURE for production)")
    SECRET_KEY = "dev-secret-key-change-immediately"

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day
REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7 days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def init_auth_tables():
    """Initialize authentication tables if they don't exist."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                household_id INTEGER,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Refresh tokens table (for token revocation)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS refresh_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token_hash TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                revoked_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES api_users(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        logger.info("Authentication tables initialized")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: int) -> str:
    """Create a JWT refresh token and store it in database."""
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    token_data = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
        "jti": f"{user_id}-{datetime.utcnow().timestamp()}"
    }
    
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    # Store token hash in database
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO refresh_tokens (user_id, token_hash, expires_at)
            VALUES (?, ?, ?)
            """,
            (user_id, token, expire.isoformat())
        )
        conn.commit()
    
    return token


async def get_current_user(token: Annotated[str | None, Depends(oauth2_scheme)]) -> UserResponse:
    """Dependency to get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if token is None:
        raise credentials_exception
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "access":
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, email, name, household_id, created_at
            FROM api_users
            WHERE id = ? AND is_active = 1
            """,
            (int(user_id),)
        )
        user = cursor.fetchone()
        
        if user is None:
            raise credentials_exception
        
        return UserResponse(
            id=user[0],
            email=user[1],
            name=user[2],
            household_id=user[3],
            created_at=user[4]
        )


# Optional authentication - returns None if not authenticated
async def get_optional_user(token: Annotated[str | None, Depends(oauth2_scheme)]) -> UserResponse | None:
    """Dependency for optional authentication."""
    try:
        return await get_current_user(token)
    except HTTPException:
        return None


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with email and password.",
    responses={
        400: {"model": ErrorResponse, "description": "Email already registered"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    }
)
async def register(request: UserRegisterRequest) -> UserResponse:
    """
    Register a new user.
    
    Args:
        request: User registration data (email, password, name)
    
    Returns:
        Created user information (without password)
    
    Raises:
        HTTPException: 400 if email already exists
    """
    init_auth_tables()  # Ensure tables exist
    
    # Hash password
    password_hash = get_password_hash(request.password)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                INSERT INTO api_users (email, password_hash, name)
                VALUES (?, ?, ?)
                """,
                (request.email, password_hash, request.name)
            )
            conn.commit()
            user_id = cursor.lastrowid
            
            logger.info(f"New user registered: {request.email} (ID: {user_id})")
            
            return UserResponse(
                id=user_id,
                email=request.email,
                name=request.name,
                household_id=None,
                created_at=datetime.now().isoformat()
            )
            
        except sqlite3.IntegrityError:
            logger.warning(f"Registration failed: email already exists - {request.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate user and return access/refresh tokens.",
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
    }
)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> TokenResponse:
    """
    Authenticate user and return JWT tokens.
    
    Args:
        form_data: OAuth2 form with username (email) and password
    
    Returns:
        Access token, refresh token, and user information
    
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    init_auth_tables()
    
    # Find user by email
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, email, password_hash, name, household_id, created_at
            FROM api_users
            WHERE email = ? AND is_active = 1
            """,
            (form_data.username,)
        )
        user = cursor.fetchone()
    
    # Verify credentials
    if user is None or not verify_password(form_data.password, user[2]):
        logger.warning(f"Login failed for email: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = user[0]
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user_id)})
    refresh_token = create_refresh_token(user_id)
    
    logger.info(f"User logged in: {user[1]} (ID: {user_id})")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(
            id=user_id,
            email=user[1],
            name=user[3],
            household_id=user[4],
            created_at=user[5]
        )
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Get a new access token using a valid refresh token.",
    responses={
        401: {"model": ErrorResponse, "description": "Invalid refresh token"},
    }
)
async def refresh_token(request: RefreshTokenRequest) -> TokenResponse:
    """
    Refresh access token using refresh token.
    
    Args:
        request: Refresh token
    
    Returns:
        New access and refresh tokens
    
    Raises:
        HTTPException: 401 if refresh token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "refresh":
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Check if token exists and is not revoked
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT user_id, expires_at, revoked_at
            FROM refresh_tokens
            WHERE token_hash = ?
            """,
            (request.refresh_token,)
        )
        token_record = cursor.fetchone()
        
        if token_record is None or token_record[2] is not None:
            raise credentials_exception
        
        # Check expiration
        expires_at = datetime.fromisoformat(token_record[1])
        if datetime.utcnow() > expires_at:
            raise credentials_exception
        
        # Get user data
        cursor.execute(
            """
            SELECT id, email, name, household_id, created_at
            FROM api_users
            WHERE id = ? AND is_active = 1
            """,
            (int(user_id),)
        )
        user = cursor.fetchone()
        
        if user is None:
            raise credentials_exception
        
        # Revoke old refresh token
        cursor.execute(
            "UPDATE refresh_tokens SET revoked_at = ? WHERE token_hash = ?",
            (datetime.utcnow().isoformat(), request.refresh_token)
        )
        conn.commit()
    
    # Create new tokens
    access_token = create_access_token(data={"sub": str(user_id)})
    new_refresh_token = create_refresh_token(int(user_id))
    
    logger.info(f"Token refreshed for user ID: {user_id}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(
            id=user[0],
            email=user[1],
            name=user[2],
            household_id=user[3],
            created_at=user[4]
        )
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Retrieve current authenticated user's profile.",
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    }
)
async def get_me(current_user: Annotated[UserResponse, Depends(get_current_user)]) -> UserResponse:
    """
    Get current authenticated user profile.
    
    Returns:
        Current user information
    """
    return current_user


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change password",
    description="Change current user's password.",
    responses={
        401: {"model": ErrorResponse, "description": "Invalid current password"},
        400: {"model": ErrorResponse, "description": "Validation error"},
    }
)
async def change_password(
    request: ChangePasswordRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)]
) -> dict:
    """
    Change user password.
    
    Args:
        request: Current and new password
        current_user: Authenticated user
    
    Returns:
        Success message
    
    Raises:
        HTTPException: 401 if current password is wrong
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get current password hash
        cursor.execute(
            "SELECT password_hash FROM api_users WHERE id = ?",
            (current_user.id,)
        )
        result = cursor.fetchone()
        
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not verify_password(request.current_password, result[0]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )
        
        # Update password
        new_hash = get_password_hash(request.new_password)
        cursor.execute(
            "UPDATE api_users SET password_hash = ?, updated_at = ? WHERE id = ?",
            (new_hash, datetime.utcnow().isoformat(), current_user.id)
        )
        conn.commit()
    
    logger.info(f"Password changed for user ID: {current_user.id}")
    
    return {"message": "Password changed successfully"}


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout",
    description="Revoke current refresh token.",
)
async def logout(
    request: RefreshTokenRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)]
) -> dict:
    """
    Logout user by revoking refresh token.
    
    Args:
        request: Refresh token to revoke
        current_user: Authenticated user
    
    Returns:
        Success message
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE refresh_tokens
            SET revoked_at = ?
            WHERE token_hash = ? AND user_id = ?
            """,
            (datetime.utcnow().isoformat(), request.refresh_token, current_user.id)
        )
        conn.commit()
    
    logger.info(f"User logged out: {current_user.email}")
    
    return {"message": "Logged out successfully"}
