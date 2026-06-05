from pydantic import BaseModel, EmailStr, validator, root_validator
from typing import Optional, List, Any
from datetime import date, datetime


# ── AUTH ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    full_name:       str
    email:           EmailStr
    password:        str
    gdpr_accepted:   bool
    data_processing: bool = False
    image_storage:   bool = False
    ai_analysis:     bool = False

class UserLogin(BaseModel):
    email:    EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class UserOut(BaseModel):
    id:          int
    email:       EmailStr
    full_name:   Optional[str]
    is_active:   bool
    created_at:  Optional[datetime]
    has_profile: bool = False

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type:   str
    user:         UserOut

class TokenData(BaseModel):
    email: Optional[str] = None

class ChangePassword(BaseModel):
    current_password: str
    new_password:     str

class ResetPasswordRequest(BaseModel):
    token:        str
    new_password: str


# ── CONSENTS ──────────────────────────────────────────────────────────────────

class ConsentOut(BaseModel):
    id:              int
    gdpr_accepted:   bool
    data_processing: bool
    image_storage:   bool
    ai_analysis:     bool
    accepted_at:     datetime

    class Config:
        orm_mode = True


# ── USERS / PROFILE ───────────────────────────────────────────────────────────

class SkinProfileCreate(BaseModel):
    birth_date:      Optional[date]      = None
    gender:          Optional[str]       = None
    fitzpatrick:     Optional[str]       = None
    skin_type:       Optional[str]       = None
    skin_conditions: Optional[List[str]] = []
    allergies:       Optional[List[str]] = []
    country:         Optional[str]       = None
    city:            Optional[str]       = None

    @root_validator(pre=True)
    def accept_age_field(cls, values):
        age = values.pop('age', None)
        if age is not None and values.get('birth_date') is None:
            values['birth_date'] = date(date.today().year - int(age), 1, 1)
        return values

class SkinProfileOut(SkinProfileCreate):
    id:         int
    user_id:    int
    updated_at: Optional[datetime]
    age:        Optional[int] = None

    @validator('age', always=True)
    def compute_age(cls, v, values):
        bd = values.get('birth_date')
        return date.today().year - bd.year if bd else None

    class Config:
        from_attributes = True

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


# ── ANALYSIS ──────────────────────────────────────────────────────────────────

class AnalysisCreated(BaseModel):
    analysis_id: int
    status:      str

class AnalysisStatusOut(BaseModel):
    analysis_id: int
<<<<<<< HEAD
    status:      str
=======
    status: str

    class Config:
        from_attributes = True

class AnalysisOut(BaseModel):
    id:                int
    status:            str
    censored_filename: Optional[str]   = None
    face_censored:     bool            = False
    lighting:          Optional[str]   = None
    device:            Optional[str]   = None
    top1_label:        Optional[str]   = None
    top1_confidence:   Optional[float] = None
    model_version:     Optional[str]   = None
    result:            Optional[Any]   = None
    error_message:     Optional[str]   = None
    created_at:        datetime
    completed_at:      Optional[datetime] = None

    class Config:
        from_attributes = True

class AnalysisSnapshot(BaseModel):
    id:                int
    status:            str
    censored_filename: Optional[str]   = None
    top1_label:        Optional[str]   = None
    top1_confidence:   Optional[float] = None
    created_at:        datetime

    class Config:
        from_attributes = True


# ── ROUTINES ──────────────────────────────────────────────────────────────────

class RoutineStepOut(BaseModel):
    id:               int
    step_order:       int
    time_of_day:      str
    product_name:     str
    product_category: Optional[str] = None
    reason:           Optional[str] = None
    ai_suggested:     bool          = True
    user_replaced:    bool          = False
    replaced_with:    Optional[str] = None
    is_active:        bool

    class Config:
        from_attributes = True

class RoutineOut(BaseModel):
    id:          int
    analysis_id: Optional[int]
    is_active:   bool
    created_at:  datetime
    steps:       List[RoutineStepOut]

    class Config:
        from_attributes = True

class RoutineStepCreate(BaseModel):
    step_order: int
    time_of_day: str
    product_name: str
    product_category: Optional[str] = None
    reason: Optional[str] = None
    is_active: bool

    class Config:
        orm_mode = True

class RoutineOut(BaseModel):
    id: int
    analysis_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    steps: List[RoutineStepOut]

    class Config:
        orm_mode = True

class RoutineCreate(BaseModel):
    analysis_id: Optional[int] = None
    steps: List[RoutineStepCreate]  # tipado correctamente

class StepUpdate(BaseModel):
    step_id:      int
    product_name: str

class RoutineStepsUpdate(BaseModel):
    steps: List[StepUpdate]

class SkinCheckCreate(BaseModel):
    followed_routine: bool
    notes:            Optional[str] = None

class SkinCheckOut(BaseModel):
    id:               int
    routine_id:       int
    followed_routine: bool
    notes:            Optional[str]
    created_at:       datetime

    class Config:
        from_attributes = True


# ── PRODUCTS ──────────────────────────────────────────────────────────────────

class ProductOut(BaseModel):
    id:          int
    name:        str
    brand:       Optional[str]
    category:    Optional[str]
    description: Optional[str]

    class Config:
        from_attributes = True

class IngredientOut(BaseModel):
    id:        int
    inci_name: str
    function:  Optional[str]
    rating:    Optional[str]

    class Config:
        from_attributes = True

class ProductIngredientOut(BaseModel):
    position:   int
    irr_com:    Optional[str]
    ingredient: IngredientOut

    class Config:
        from_attributes = True

class ProductDetailOut(ProductOut):
    highlights:          Optional[Any]
    suitable_for:        Optional[Any]
    source_url:          str
    product_ingredients: List[ProductIngredientOut]
