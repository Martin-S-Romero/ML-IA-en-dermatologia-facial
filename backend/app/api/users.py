from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import db_scheme as models, schemas
from app.api import deps
from app.core.logger import logger

router = APIRouter()


@router.post("/profile", response_model=schemas.SkinProfileOut, status_code=status.HTTP_201_CREATED)
def save_profile(
    profile: schemas.SkinProfileCreate,
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Guarda o reemplaza el perfil de piel del usuario tras el registro."""
    existing = db.query(models.SkinProfile).filter(
        models.SkinProfile.user_id == current_user.id
    ).first()

    # Con JSONB, SQLAlchemy serializa listas directamente — sin json.dumps
    data = profile.dict()

    if existing:
        for key, value in data.items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        logger.info(f"Skin profile updated for user {current_user.id}")
        return existing

    new_profile = models.SkinProfile(user_id=current_user.id, **data)
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    logger.info(f"Skin profile created for user {current_user.id}")
    return new_profile


@router.get("/me", response_model=schemas.UserOut)
def get_me(current_user: models.User = Depends(deps.get_current_user)):
    """Devuelve los datos del usuario autenticado."""
    return current_user


@router.get("/profile", response_model=schemas.SkinProfileOut)
def get_profile(
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Devuelve el perfil de piel del usuario autenticado."""
    profile = db.query(models.SkinProfile).filter(
        models.SkinProfile.user_id == current_user.id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil de piel no encontrado.")
    return profile


@router.put("/me", response_model=schemas.UserOut)
def update_me(
    body: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Actualiza campos editables del usuario y su perfil de piel."""
    if body.full_name is not None:
        current_user.full_name = body.full_name

    profile_fields = ["age", "gender", "fitzpatrick", "skin_type",
                      "skin_conditions", "allergies", "country", "city"]
    profile_data = {k: getattr(body, k) for k in profile_fields if getattr(body, k) is not None}

    if profile_data:
        profile = db.query(models.SkinProfile).filter(
            models.SkinProfile.user_id == current_user.id
        ).first()

        if not profile:
            profile = models.SkinProfile(user_id=current_user.id)
            db.add(profile)

        # Con JSONB, las listas se asignan directamente — sin json.dumps
        for key, value in profile_data.items():
            setattr(profile, key, value)

    db.commit()
    db.refresh(current_user)
    logger.info(f"User {current_user.id} updated their profile.")
    return current_user


@router.delete("/me", status_code=status.HTTP_200_OK)
def delete_me(
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Elimina la cuenta y todos los datos del usuario (irreversible)."""
    user_id = current_user.id
    email   = current_user.email

    db.query(models.SkinCheck).filter(models.SkinCheck.user_id == user_id).delete()
    db.query(models.RoutineStep).filter(
        models.RoutineStep.routine_id.in_(
            db.query(models.Routine.id).filter(models.Routine.user_id == user_id)
        )
    ).delete(synchronize_session=False)
    db.query(models.Routine).filter(models.Routine.user_id == user_id).delete()
    db.query(models.Analysis).filter(models.Analysis.user_id == user_id).delete()
    db.query(models.SkinProfile).filter(models.SkinProfile.user_id == user_id).delete()
    db.delete(current_user)
    db.commit()

    logger.info(f"Account deleted: {email} (id={user_id})")
    return {"message": "Cuenta eliminada correctamente."}
