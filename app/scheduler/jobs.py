from apscheduler.schedulers.background import BackgroundScheduler
import os
from datetime import datetime, timedelta
import sendgrid
# pyrefly: ignore [missing-import]
# pyrefly: ignore [missing-import]
from sendgrid.helpers.mail import Mail
from app.database.database import SessionLocal
from app.models.models import User, Limit
from app.routes.summary import calculate_summary

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

def send_email(to_email, subject, html_content):
    if not SENDGRID_API_KEY or SENDGRID_API_KEY == "your_sendgrid_api_key_here":
        print(f"[Mock Email] To: {to_email} | Subject: {subject}")
        return

    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    message = Mail(
        from_email=os.getenv("FROM_EMAIL", "noreply@expensetracker.com"),
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )
    try:
        response = sg.send(message)
        print(f"Email sent to {to_email} with status {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {e}")

def monthly_report_job():
    db = SessionLocal()
    users = db.query(User).all()
    start_date = datetime.utcnow() - timedelta(days=30)
    for user in users:
        summary = calculate_summary(db, user.id, start_date, datetime.utcnow())
        if summary["total_spending"] > 0:
            content = f"""
            <h3>Monthly Expense Report</h3>
            <p>Total Spending: ${summary['total_spending']}</p>
            <ul>
                <li>Need: ${summary['categories'].get('Need', 0)}</li>
                <li>Want: ${summary['categories'].get('Want', 0)}</li>
                <li>Invest: ${summary['categories'].get('Invest', 0)}</li>
            </ul>
            <p>Keep tracking your expenses to stay on top of your financial health!</p>
            """
            send_email(user.email, "Your Monthly Expense Report", content)
    db.close()

def daily_limit_check_job():
    db = SessionLocal()
    limits = db.query(Limit).all()
    start_date = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0) # start of current month
    for limit in limits:
        summary = calculate_summary(db, limit.user_id, start_date, datetime.utcnow())
        total = summary["total_spending"]
        if limit.monthly_limit > 0:
            usage = total / limit.monthly_limit
            alert = ""
            if usage >= 0.90:
                alert = "Critical: 90% budget used!"
            elif usage >= 0.75:
                alert = "Warning: 75% budget used."
            elif usage >= 0.60:
                alert = "Notice: You have used 60% of your budget."
            
            if alert:
                user = db.query(User).filter(User.id == limit.user_id).first()
                if user:
                    send_email(user.email, "Budget Alert", f"<p>{alert}</p><p>You have spent ${total} out of your ${limit.monthly_limit} monthly limit.</p>")
    db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Monthly report on the 1st of every month
    scheduler.add_job(monthly_report_job, 'cron', day=1, hour=8, minute=0)
    # Daily limit check at 9 AM
    scheduler.add_job(daily_limit_check_job, 'cron', hour=9, minute=0)
    
    scheduler.start()
    print("Background jobs scheduled.")
