from fastapi import APIRouter
import logging

logger = logging.getLogger("api_engine.auth")

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/login")
async def login_user():
    """
    Sends passwords through
    """

    logger.info("Sends password")
    return{"message": "login endpoint"}
