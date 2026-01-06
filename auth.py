import time
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# this file hasesh and verifies passwords, creates JWT tokens, and extracts user ID
# to keep security logic separate from routes (professional structure)

# Realistically, this part should be kept secret in an environment variable
JWT_SECRET = "dev-only-change-me" # secret key to sign tokens
JWT_ALG = "HS256" # the alg used to sign the token (math formula)
JWT_EXPIRES_SECONDS = 60 * 60 # 1 hour token expiration

pwd_context = CryptContext(schemes=["bycrypt"], deprecated="auto") # handles hasing and verification
bearer_scheme = HTTPBearer() # validate tokens, password + hash --> verify 

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

# make a log in token to prove which user logged in
def create_access_token(user_id: int) -> str:
    now = int(time.time())
    payload = {     # token content
        "sub": str(user_id),
        "iat": now, # issued at time
        "exp": now + JWT_EXPIRES_SECONDS, # expiration time
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG) # signs payload and returns token

# reads token from request, verifies it, and returns logged-in user ID
def get_current_user_id(creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),) -> int:
    token = creds.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG]) # decode token
        return int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")