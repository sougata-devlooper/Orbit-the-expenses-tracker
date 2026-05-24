from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database.database import get_db
from app.schemas.schemas import ExpenseCreate, ExpenseResponse
from app.models.models import Expense, User
from app.utils.auth import get_current_user

router = APIRouter(prefix="/expenses", tags=["Expenses"])

@router.post("/", response_model=ExpenseResponse)
def add_expense(expense: ExpenseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_expense = Expense(
        user_id=current_user.id,
        amount=expense.amount,
        category=expense.category,
        note=expense.note,
        date=expense.date if expense.date else datetime.utcnow()
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

@router.get("/", response_model=List[ExpenseResponse])
def get_expenses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Expense).filter(Expense.user_id == current_user.id).order_by(Expense.date.desc()).all()
