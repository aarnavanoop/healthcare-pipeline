from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Takes a plain-text password and returns a securely hashed version.
    bcrypt automatically generates and includes a unique salt for every hash.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against the hashed version in the database.
    Used during the login flow.
    """
    return pwd_context.verify(plain_password, hashed_password)