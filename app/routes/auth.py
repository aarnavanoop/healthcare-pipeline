from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
from app.db.deps import get_db
from app.db.models import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import get_password_hash

logger = logging.getLogger("api_engine.auth")

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Registers a new user. 
    Requires a unique username and a password.
    """
    logger.info(f"Attempting to register new user: {user_in.username}")


    stmt = select(User).where(User.username == user_in.username)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        logger.warning(f"Registration failed: Username {user_in.username} already exists.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    hashed_pw = get_password_hash(user_in.password)

    new_user = User(
        username=user_in.username,
        hashed_password=hashed_pw
    )


    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    logger.info(f"Successfully registered user: {new_user.username}")
    

    return new_user

@router.post("/login")
async def login_user():
    """
    Sends passwords through
    """

    logger.info("Sends password")
    return{"message": "login endpoint"}
