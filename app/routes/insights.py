from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database.database import get_db
from app.models.models import User, Limit
from app.utils.auth import get_current_user
from app.routes.summary import calculate_summary
from app.schemas.schemas import LimitCreate

router = APIRouter(tags=["Insights & Limits"])

@router.get("/insights")
def get_insights(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    start_date = datetime.utcnow() - timedelta(days=30)
    summary = calculate_summary(db, current_user.id, start_date, datetime.utcnow())
    
    total = summary["total_spending"]
    if total == 0:
        return {"message": "No expenses in the last 30 days. Start logging!"}
        
    categories = summary["categories"]
    need_pct = (categories.get("Need", 0) / total) * 100
    want_pct = (categories.get("Want", 0) / total) * 100
    invest_pct = (categories.get("Invest", 0) / total) * 100
    
    insights = []
    
    if want_pct > 50:
        insights.append("High spending on Wants ⚠️")
    if invest_pct > 20:
        insights.append("Good investing habit 💪")
    if want_pct <= 50 and invest_pct >= 10:
        insights.append("Spending looks healthy 👍")
        
    # Check limit using the current month's expenses
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
    month_summary = calculate_summary(db, current_user.id, month_start, datetime.utcnow())
    month_total = month_summary["total_spending"]
    
    limit_obj = db.query(Limit).filter(Limit.user_id == current_user.id).first()
    limit_alert = None
    if limit_obj and limit_obj.monthly_limit > 0:
        usage = month_total / limit_obj.monthly_limit
        if usage >= 0.90:
            limit_alert = "Critical: 90% budget used"
        elif usage >= 0.75:
            limit_alert = "Warning: 75% budget used"
        elif usage >= 0.60:
            limit_alert = "You have used 60% of your budget"

    return {
        "total_last_30_days": total,
        "percentages": {
            "Need": round(need_pct, 2),
            "Want": round(want_pct, 2),
            "Invest": round(invest_pct, 2)
        },
        "insights": insights,
        "limit_alert": limit_alert
    }

@router.post("/limits")
def set_limit(limit: LimitCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing_limit = db.query(Limit).filter(Limit.user_id == current_user.id).first()
    if existing_limit:
        existing_limit.monthly_limit = limit.monthly_limit
    else:
        new_limit = Limit(user_id=current_user.id, monthly_limit=limit.monthly_limit)
        db.add(new_limit)
    db.commit()
    return {"message": f"Monthly limit updated successfully to {limit.monthly_limit}."}
