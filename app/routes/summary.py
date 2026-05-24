from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.database.database import get_db
from app.models.models import Expense, User
from app.utils.auth import get_current_user

router = APIRouter(prefix="/summary", tags=["Summary"])

def calculate_summary(db: Session, user_id: int, start_date: datetime, end_date: datetime):
    expenses = db.query(Expense.category, func.sum(Expense.amount).label("total")).\
        filter(Expense.user_id == user_id).\
        filter(Expense.date >= start_date).\
        filter(Expense.date <= end_date).\
        group_by(Expense.category).all()
    
    total_spending = sum(e.total for e in expenses)
    categories = {e.category.value: e.total for e in expenses}
    
    return {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "total_spending": total_spending,
        "categories": categories
    }

@router.get("/daily")
def get_daily_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    return calculate_summary(db, current_user.id, today_start, today_end)

@router.get("/monthly")
def get_monthly_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Aggregate last 30 days
    start_date = datetime.utcnow() - timedelta(days=30)
    return calculate_summary(db, current_user.id, start_date, datetime.utcnow())

@router.get("/custom")
def get_custom_summary(start_date: str, end_date: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Expected format: YYYY-MM-DD
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) # include end date fully
    return calculate_summary(db, current_user.id, start, end)
