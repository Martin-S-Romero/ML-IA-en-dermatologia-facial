from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime


# ── AUTH ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    gdpr_accepted: bool

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

class TokenData(BaseModel):
    email: Optional[str] = None


# ── USERS / PERFIL DE PIEL ────────────────────────────────────────────────────

class SkinProfileCreate(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    fitzpatrick: Optional[str] = None
    skin_type: Optional[str] = None
    skin_conditions: Optional[List[str]] = []
    allergies: Optional[List[str]] = []
    country: Optional[str] = None
    city: Optional[str] = None

class SkinProfileOut(BaseModel):
    id: int
    user_id: int
    age: Optional[int] = None
    gender: Optional[str] = None
    fitzpatrick: Optional[str] = None
    skin_type: Optional[str] = None
    skin_conditions: Optional[List[str]] = []  # JSONB → ya llega como lista
    allergies: Optional[List[str]] = []         # JSONB → ya llega como lista
    country: Optional[str] = None
    city: Optional[str] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None


# ── ANALYSIS ──────────────────────────────────────────────────────────────────

class AnalysisCreated(BaseModel):
    analysis_id: int
    status: str

class AnalysisStatusOut(BaseModel):
    analysis_id: int
    status: str
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class AnalysisOut(BaseModel):
    id: int
    status: str
    original_filename: str
    censored_filename: Optional[str] = None
    result: Optional[Any] = None        # JSONB → llega como dict, no como str
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AnalysisSnapshot(BaseModel):
    id: int
    status: str
    censored_filename: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── ROUTINES ──────────────────────────────────────────────────────────────────

class RoutineStepCreate(BaseModel):
    step_order: int
    time_of_day: str               # am / pm / both
    product_name: str
    product_category: Optional[str] = None
    reason: Optional[str] = None

class RoutineStepOut(BaseModel):
    id: int
    step_order: int
    time_of_day: str
    product_name: str
    product_category: Optional[str] = None
    reason: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class RoutineOut(BaseModel):
    id: int
    analysis_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    steps: List[RoutineStepOut]

    class Config:
        from_attributes = True

class RoutineStepCreate(BaseModel):
    step_order: int
    time_of_day: str
    product_name: str
    product_category: Optional[str] = None
    reason: Optional[str] = None

class RoutineCreate(BaseModel):
    analysis_id: Optional[int] = None
    steps: List[RoutineStepCreate]

class StepUpdate(BaseModel):
    step_id: int
    product_name: str

class RoutineStepsUpdate(BaseModel):
    steps: List[StepUpdate]

class SkinCheckCreate(BaseModel):
    followed_routine: bool
    notes: Optional[str] = None

class SkinCheckOut(BaseModel):
    id: int
    routine_id: int
    followed_routine: bool
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── PRODUCTS ──────────────────────────────────────────────────────────────────

class ProductOut(BaseModel):
    id: int
    name: str
    brand: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True

class IngredientOut(BaseModel):
    id: int
    inci_name: str
    function: Optional[str] = None
    rating: Optional[str] = None

    class Config:
        from_attributes = True

class ProductIngredientOut(BaseModel):
    position: int
    irr_com: Optional[str] = None
    ingredient: IngredientOut

    class Config:
        from_attributes = True

class ProductDetailOut(ProductOut):
    highlights: Optional[Any] = None   # JSONB → llega como lista, no como str
    source_url: str
    product_ingredients: List[ProductIngredientOut]
