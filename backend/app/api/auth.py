from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app import models, schemas
from app.core import security
from app.api import deps
from app.core.ratelimit import limiter
from app.core.logger import logger

router = APIRouter()


@router.post("/register", response_model=schemas.TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, user: schemas.UserCreate, db: Session = Depends(deps.get_db)):
    if not user.gdpr_accepted:
        raise HTTPException(status_code=400, detail="Debes aceptar los términos para continuar.")

    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="El correo ya está registrado.")

    new_user = models.User(
        email=user.email,
        hashed_password=security.get_password_hash(user.password),
        full_name=user.full_name,
        gdpr_accepted=user.gdpr_accepted,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = security.create_access_token(
        data={"sub": new_user.email},
        expires_delta=timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    logger.info(f"New user registered: {new_user.email}")
    return {"access_token": access_token, "token_type": "bearer", "user": new_user}


@router.post("/login", response_model=schemas.TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, user: schemas.UserLogin, db: Session = Depends(deps.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not security.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = security.create_access_token(
        data={"sub": db_user.email},
        expires_delta=timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    logger.info(f"User logged in: {db_user.email}")
    return {"access_token": access_token, "token_type": "bearer", "user": db_user}


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(current_user: models.User = Depends(deps.get_current_user)):
    # JWT es stateless: el cliente elimina el token.
    # Extensible a blacklist en Redis si se requiere en el futuro.
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Sesión cerrada correctamente."}


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
@limiter.limit("3/minute")
def forgot_password(request: Request, body: dict, db: Session = Depends(deps.get_db)):
    email = body.get("email", "").strip()
    if not email:
        raise HTTPException(status_code=400, detail="El correo es requerido.")

    # No revelar si el correo existe o no (buena práctica de seguridad)
    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        # TODO: enviar email con enlace de recuperación cuando haya servidor de correo configurado
        logger.info(f"Password reset requested for: {email}")

    return {"message": "Si el correo está registrado, recibirás un enlace en los próximos minutos."}
