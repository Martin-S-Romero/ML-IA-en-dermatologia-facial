import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas
from app.api import deps
from app.core.logger import logger

router = APIRouter()


@router.put("/profile", response_model=schemas.SkinProfileOut)
def update_profile(
    profile: schemas.SkinProfileCreate,
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Actualiza el perfil de piel del usuario."""
    existing = db.query(models.SkinProfile).filter(
        models.SkinProfile.user_id == current_user.id
    ).first()

    data = profile.dict()
    data["skin_conditions"] = json.dumps(data.get("skin_conditions") or [])
    data["allergies"]       = json.dumps(data.get("allergies") or [])

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
    """Actualiza campos editables del usuario (full_name)."""
    if body.full_name is not None:
        current_user.full_name = body.full_name

    db.commit()
    db.refresh(current_user)
    logger.info(f"User {current_user.id} updated their account.")
    return current_user


@router.delete("/me", status_code=status.HTTP_200_OK)
def delete_me(
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Elimina la cuenta y todos los datos del usuario (irreversible)."""
    user_id = current_user.id
    email   = current_user.email

    # Eliminar datos relacionados en orden para respetar FK
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

