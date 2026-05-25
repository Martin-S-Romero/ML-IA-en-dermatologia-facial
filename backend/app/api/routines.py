from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import db_scheme as models, schemas
from app.api import deps
from app.core.logger import logger

router = APIRouter()


@router.get("/active", response_model=schemas.RoutineOut)
def get_active_routine(
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Devuelve la rutina activa del usuario con sus pasos y productos."""
    routine = (
        db.query(models.Routine)
        .filter(
            models.Routine.user_id  == current_user.id,
            models.Routine.is_active == True,
        )
        .order_by(models.Routine.created_at.desc())
        .first()
    )
    if not routine:
        raise HTTPException(status_code=404, detail="No hay rutina activa. Realiza un análisis primero.")
    return routine


@router.post("/", response_model=schemas.RoutineOut, status_code=status.HTTP_201_CREATED)
def create_routine(
    body: schemas.RoutineCreate,
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """
    Crea una nueva rutina para el usuario.
    Desactiva la anterior si existe.
    Recibe los pasos generados (por IA o por el frontend).
    """
    # Desactivar rutina anterior
    db.query(models.Routine).filter(
        models.Routine.user_id  == current_user.id,
        models.Routine.is_active == True,
    ).update({"is_active": False})

    routine = models.Routine(
        user_id     = current_user.id,
        analysis_id = body.analysis_id,
        is_active   = True,
    )
    db.add(routine)
    db.flush()  # para obtener routine.id antes del commit

    for step_data in body.steps:
        step = models.RoutineStep(
            routine_id       = routine.id,
            step_order       = step_data.get("step_order", 0),
            time_of_day      = step_data.get("time_of_day", "am"),
            product_name     = step_data.get("product_name", ""),
            product_category = step_data.get("product_category"),
            reason           = step_data.get("reason"),
            is_active        = True,
        )
        db.add(step)

    db.commit()
    db.refresh(routine)
    logger.info(f"Routine {routine.id} created for user {current_user.id}")
    return routine


@router.patch("/active/steps", response_model=schemas.RoutineOut)
def update_routine_steps(
    body: schemas.RoutineStepsUpdate,
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Actualiza productos de pasos específicos en la rutina activa."""
    routine = (
        db.query(models.Routine)
        .filter(
            models.Routine.user_id  == current_user.id,
            models.Routine.is_active == True,
        )
        .first()
    )
    if not routine:
        raise HTTPException(status_code=404, detail="No hay rutina activa.")

    step_map = {step.id: step for step in routine.steps}

    for update in body.steps:
        step = step_map.get(update.step_id)
        if not step:
            raise HTTPException(
                status_code=404,
                detail=f"Paso {update.step_id} no pertenece a la rutina activa.",
            )
        step.product_name = update.product_name

    db.commit()
    db.refresh(routine)
    logger.info(f"Routine {routine.id} steps updated by user {current_user.id}")
    return routine


@router.post("/check", response_model=schemas.SkinCheckOut, status_code=status.HTTP_201_CREATED)
def register_skin_check(
    body: schemas.SkinCheckCreate,
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Registra si el usuario siguió o no su rutina activa antes de un análisis."""
    routine = (
        db.query(models.Routine)
        .filter(
            models.Routine.user_id  == current_user.id,
            models.Routine.is_active == True,
        )
        .first()
    )
    if not routine:
        raise HTTPException(status_code=404, detail="No hay rutina activa para registrar el check.")

    check = models.SkinCheck(
        user_id          = current_user.id,
        routine_id       = routine.id,
        followed_routine = body.followed_routine,
        notes            = body.notes,
    )
    db.add(check)
    db.commit()
    db.refresh(check)
    logger.info(f"Skin check registered for user {current_user.id} — followed: {body.followed_routine}")
    return check
