from app.db.session import AsyncSessionLocal


async def get_db():
    """
    Provides an asynchronous database session for each request.
    """
    async with AsyncSessionLocal() as session:
        yield session