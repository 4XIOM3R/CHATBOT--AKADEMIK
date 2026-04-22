from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt

from config import SECRET_KEY, ALGORITHM

security = HTTPBearer()

def get_current_user(token=Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]  # ini user_id
    except:
        raise HTTPException(status_code=401, detail="Invalid token")