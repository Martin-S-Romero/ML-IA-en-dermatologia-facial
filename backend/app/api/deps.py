from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app import schemas, models
from app.core import database, security

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
        
    # Establecer la variable de contexto
    from app.core.context import current_user_id
    current_user_id.set(str(user.id))
    
    # Inyectar el ID en la sesión actual para RLS
    from sqlalchemy import text
    db.execute(text(f"SET app.current_user_id = '{user.id}';"))
    
    return user


async def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Dependency that optionally extracts the current authenticated user from
    either the 'Authorization' Bearer header or the 'token' query parameter.
    Uses Request internally so these parameters are NOT exposed in Swagger UI.
    If no valid token is provided, it sets the database RLS variable to empty and returns None.
    """
    actual_token = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        actual_token = auth_header.split(" ")[1]
    elif "token" in request.query_params:
        actual_token = request.query_params["token"]
        
    from sqlalchemy import text
    from app.core.context import current_user_id

    if not actual_token:
        # No token provided: ensure database RLS context is cleared/empty
        current_user_id.set("")
        db.execute(text("SET app.current_user_id = '';"))
        return None
        
    try:
        payload = jwt.decode(actual_token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            current_user_id.set("")
            db.execute(text("SET app.current_user_id = '';"))
            return None
        token_data = schemas.TokenData(email=email)
    except JWTError:
        current_user_id.set("")
        db.execute(text("SET app.current_user_id = '';"))
        return None
        
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        current_user_id.set("")
        db.execute(text("SET app.current_user_id = '';"))
        return None
        
    # Establecer la variable de contexto
    current_user_id.set(str(user.id))
    
    # Inyectar el ID en la sesión actual para RLS
    db.execute(text(f"SET app.current_user_id = '{user.id}';"))
    
    return user
