from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app import models, schemas
from app.core import security
from app.api import deps

# Import limiter from main is tricky due to circular imports if main imports auth.
# Better pattern: create a separate RateLimit config or import from a centralized place.
# For simplicity in this stack, we can access it via Request.app.state.limiter but the decorator needs the instance.
# We will cheat slightly and import limiter from main inside the function OR move limiter creation to a core file?
# Moving limiter to core/security.py or new core/config.py is cleaner.
# adhering to "Simple code" rule: I'll create app/core/ratelimit.py.

from app.core.ratelimit import limiter

router = APIRouter()

@router.post("/register", response_model=schemas.User)
@limiter.limit("5/minute")
def register(request: Request, user: schemas.UserCreate, db: Session = Depends(deps.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = security.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=schemas.Token)
@limiter.limit("5/minute")
def login(request: Request, user: schemas.UserLogin, db: Session = Depends(deps.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not security.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(deps.get_current_user)):
    return current_user
