"""
Authentication routes for user registration and login
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app.utils.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


class UserRegister(BaseModel):
    """User registration request"""
    email: str
    password: str


class UserLogin(BaseModel):
    """User login request"""
    email: str
    password: str


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User response"""
    id: int
    email: str


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserRegister):
    """
    Register a new user.
    
    - **email**: User email address (must be unique)
    - **password**: User password (will be hashed)
    """
    if not user.email or not user.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )
    
    # Hash the password
    password_hash = hash_password(user.password)
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE email = ?", (user.email,))
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Insert new user
            cursor.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (user.email, password_hash)
            )
            conn.commit()
            
            # Get the created user
            cursor.execute("SELECT id, email FROM users WHERE email = ?", (user.email,))
            row = cursor.fetchone()
            
            if row:
                return UserResponse(id=row["id"], email=row["email"])
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin):
    """
    Login a user and receive JWT access token.
    
    - **email**: User email address
    - **password**: User password
    """
    if not user.email or not user.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get user by email
            cursor.execute("SELECT id, email, password_hash FROM users WHERE email = ?", (user.email,))
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            user_id = row["id"]
            email = row["email"]
            password_hash = row["password_hash"]
            
            # Verify password
            if not verify_password(user.password, password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            # Create JWT token
            access_token = create_access_token(user_id, email)
            
            return TokenResponse(access_token=access_token, token_type="bearer")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
