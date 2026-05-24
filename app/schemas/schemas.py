from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from app.models.models import CategoryEnum

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    class Config:
        from_attributes = True

class ExpenseCreate(BaseModel):
    amount: float
    category: CategoryEnum
    note: Optional[str] = None
    date: Optional[datetime] = None

class ExpenseResponse(BaseModel):
    id: int
    amount: float
    category: CategoryEnum
    note: Optional[str]
    date: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class LimitCreate(BaseModel):
    monthly_limit: float
