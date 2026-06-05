import secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import db_scheme as models, schemas
from app.core import security
from app.core.email_service import send_password_reset_email
from app.api import deps
from app.core.ratelimit import limiter
from app.core.logger import logger

_RESET_TOKEN_EXPIRE_HOURS = 1

router = APIRouter()


@router.post("/register", response_model=schemas.TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
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
    db.flush()   # obtener new_user.id sin commit aún

    # Registro de consentimiento granular (GDPR)
    ip = request.client.host if request.client else None
    consent = models.Consent(
        user_id=new_user.id,
        gdpr_accepted=user.gdpr_accepted,
        data_processing=user.data_processing,
        image_storage=user.image_storage,
        ai_analysis=user.ai_analysis,
        ip_address=ip,
    )
    db.add(consent)
    db.commit()
    db.refresh(new_user)

    access_token = security.create_access_token(
        data={"sub": new_user.email},
        expires_delta=timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    logger.info(f"New user registered: {new_user.email}")
    return {"access_token": access_token, "token_type": "bearer", "user": new_user}


@router.post("/login", response_model=schemas.TokenResponse)
@limiter.limit("20/minute")
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

    has_profile = db.query(models.SkinProfile).filter(
        models.SkinProfile.user_id == db_user.id
    ).first() is not None

    user_data = {
        "id":          db_user.id,
        "email":       db_user.email,
        "full_name":   db_user.full_name,
        "is_active":   db_user.is_active,
        "created_at":  db_user.created_at,
        "has_profile": has_profile,
    }

    logger.info(f"User logged in: {db_user.email}")
    return {"access_token": access_token, "token_type": "bearer", "user": user_data}


@router.post("/token", response_model=schemas.TokenResponse)
@limiter.limit("20/minute")
def login_swagger(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(deps.get_db)
):
    db_user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not db_user or not security.verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = security.create_access_token(
        data={"sub": db_user.email},
        expires_delta=timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    logger.info(f"Swagger token request successful: {db_user.email}")
    return {"access_token": access_token, "token_type": "bearer", "user": db_user}



@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(current_user: models.User = Depends(deps.get_current_user)):
    # JWT es stateless: el cliente elimina el token.
    # Extensible a blacklist en Redis si se requiere en el futuro.
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Sesión cerrada correctamente."}


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
@limiter.limit("3/minute")
def forgot_password(request: Request, body: schemas.ForgotPasswordRequest, db: Session = Depends(deps.get_db)):
    email = body.email.strip()
    if not email:
        raise HTTPException(status_code=400, detail="El correo es requerido.")

    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        # Eliminar tokens previos no usados para este usuario
        db.query(models.PasswordResetToken).filter(
            models.PasswordResetToken.user_id == user.id,
            models.PasswordResetToken.used == False,  # noqa: E712
        ).delete()

        token_value = secrets.token_urlsafe(32)
        expires_at  = datetime.now(timezone.utc) + timedelta(hours=_RESET_TOKEN_EXPIRE_HOURS)

        reset_token = models.PasswordResetToken(
            user_id    = user.id,
            token      = token_value,
            expires_at = expires_at,
        )
        db.add(reset_token)
        db.commit()

        send_password_reset_email(user.email, token_value)
        logger.info(f"Password reset email sent to: {email}")

    return {"message": "Si el correo está registrado, recibirás un enlace en los próximos minutos."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
def reset_password(request: Request, body: schemas.ResetPasswordRequest, db: Session = Depends(deps.get_db)):
    now = datetime.now(timezone.utc)

    reset_token = (
        db.query(models.PasswordResetToken)
        .filter(
            models.PasswordResetToken.token      == body.token,
            models.PasswordResetToken.used       == False,  # noqa: E712
            models.PasswordResetToken.expires_at >  now,
        )
        .first()
    )

    if not reset_token:
        raise HTTPException(status_code=400, detail="El enlace es inválido o ha expirado.")

    if len(body.new_password) < 8:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 8 caracteres.")

    user = db.query(models.User).filter(models.User.id == reset_token.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    user.hashed_password = security.get_password_hash(body.new_password)
    reset_token.used     = True
    db.commit()

    logger.info(f"Password reset completed for: {user.email}")
    return {"message": "Contraseña actualizada correctamente. Ya puedes iniciar sesión."}
