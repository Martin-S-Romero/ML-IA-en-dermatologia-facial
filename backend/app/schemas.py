import json as _json
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime


# ── AUTH ──────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    gdpr_accepted: bool

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    is_active: bool
    created_at: Optional[datetime]

    class Config:
        orm_mode = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

class TokenData(BaseModel):
    email: Optional[str] = None


# ── USERS / PROFILE ───────────────────────────────────────────────────────

class SkinProfileCreate(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    fitzpatrick: Optional[str] = None
    skin_type: Optional[str] = None
    skin_conditions: Optional[List[str]] = []
    allergies: Optional[List[str]] = []
    country: Optional[str] = None
    city: Optional[str] = None

class SkinProfileOut(SkinProfileCreate):
    id: int
    user_id: int
    updated_at: Optional[datetime]

    @validator('skin_conditions', 'allergies', pre=True, always=True)
    def parse_json_list(cls, v):
        if isinstance(v, str):
            try:
                return _json.loads(v)
            except Exception:
                return []
        return v or []

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    fitzpatrick: Optional[str] = None
    skin_type: Optional[str] = None
    skin_conditions: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    country: Optional[str] = None
    city: Optional[str] = None


# ── ANALYSIS ──────────────────────────────────────────────────────────────

class AnalysisCreated(BaseModel):
    analysis_id: int
    status: str

class AnalysisStatusOut(BaseModel):
    analysis_id: int
    status: str

    class Config:
        orm_mode = True

class AnalysisOut(BaseModel):
    id: int
    status: str
    original_filename: str
    censored_filename: Optional[str]
    result: Optional[str]       # JSON string con metadata del resultado
    error_message: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

class AnalysisSnapshot(BaseModel):
    id: int
    status: str
    censored_filename: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True


# ── ROUTINES ──────────────────────────────────────────────────────────────

class RoutineStepOut(BaseModel):
    id: int
    step_order: int
    time_of_day: str
    product_name: str
    product_category: Optional[str]
    reason: Optional[str]
    is_active: bool

    class Config:
        orm_mode = True

class RoutineOut(BaseModel):
    id: int
    analysis_id: Optional[int]
    is_active: bool
    created_at: datetime
    steps: List[RoutineStepOut]

    class Config:
        orm_mode = True

class RoutineCreate(BaseModel):
    analysis_id: Optional[int] = None
    steps: List[dict]           # [{ step_order, time_of_day, product_name, product_category, reason }]

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
    notes: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True


# ── PRODUCTS ──────────────────────────────────────────────────────────────

class ProductOut(BaseModel):
    id: int
    name: str
    brand: str
    category: str
    description: str

    class Config:
        orm_mode = True


class IngredientOut(BaseModel):
    id: int
    inci_name: str
    function: str
    rating: str

    class Config:
        orm_mode = True


class ProductIngredientOut(BaseModel):
    position: int
    irr_com: Optional[str]
    ingredient: IngredientOut

    class Config:
        orm_mode = True


class ProductDetailOut(ProductOut):
    highlights: Optional[str]    # JSON string con la lista de #tags
    source_url: str
    product_ingredients: List[ProductIngredientOut]

    class Config:
        orm_mode = True
