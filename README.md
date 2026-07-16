# Orbit: Daily Expense Tracker

> [!TIP]
> **Live Demo:** Try the deployed application online at [orbit-the-expenses-tracker.onrender.com](https://orbit-the-expenses-tracker.onrender.com/).

Orbit is a web-based Daily Expense Tracker designed to help users log their daily spending, categorize expenses under the **50/30/20 budget rule** (Needs, Wants, Savings/Investments), set monthly budget limits, receive automatic budget alerts, and generate monthly reports.

The project is built with a **FastAPI backend** (Python) and a **Vanilla HTML/CSS/JavaScript frontend**.

---

## Features

- **User Authentication**: Secure register, login, and token-based JWT authentication.
- **Expense Management**: Log, edit, delete, and categorize daily expenses.
- **Budget Rule Integration**: Automatically tracks expenses against custom category breakdowns (e.g. Needs, Wants, Savings/Investments).
- **Monthly Limit Alerts**: Set a monthly budget and receive automatic emails (via SendGrid) when spending hits 60%, 75%, or 90% threshold.
- **Automated Monthly Reports**: Background jobs generate and dispatch monthly financial summaries on the 1st of every month.
- **Interactive Dashboard**: Modern responsive UI with visual spending breakdowns and clean styling.

---

## Tech Stack

### Backend
- **Core**: Python & FastAPI
- **Database**: SQLite (default for local setup) or PostgreSQL (ready for production) with SQLAlchemy ORM
- **Authentication**: JWT tokens (via `python-jose`) and password hashing (via `bcrypt` & `passlib`)
- **Background Jobs**: `APScheduler` (handles limit monitoring and email triggers)
- **Emails**: SendGrid API

### Frontend
- **Structure**: Semantic HTML5
- **Style**: Custom Vanilla CSS (Modern aesthetic)
- **Logic**: Vanilla JavaScript utilizing Fetch API for backend communication

---

## Project Structure

```text
├── app/
│   ├── database/     # SQLAlchemy engine, session maker, and DB base model
│   ├── models/       # Database tables schemas (User, Expense, Limit)
│   ├── routes/       # API router controllers (Auth, Expenses, Insights, Summary)
│   ├── scheduler/    # APScheduler configuration & email background jobs
│   ├── schemas/      # Pydantic validation schemas
│   ├── utils/        # Helper utilities
│   └── main.py       # Main API entrypoint and app setup
├── frontend/
│   ├── index.html    # Login / Register page
│   ├── dashboard.html# User dashboard
│   ├── app.js        # Frontend logic & API handlers
│   └── style.css     # CSS Stylesheet
├── requirements.txt  # Python package dependencies
├── start.bat         # Windows batch file to start backend server
└── Procfile          # Production deployment process file
```

---

## Getting Started

### Prerequisites
- Python 3.8+ installed on your system.

### Backend Setup
1. **Clone the repository** and navigate to the project directory.
2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```
3. **Activate the virtual environment**:
   - **Windows (PowerShell)**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **Windows (CMD)**:
     ```cmd
     .\venv\Scripts\activate.bat
     ```
   - **macOS / Linux**:
     ```bash
     source venv/bin/activate
     ```
4. **Install backend dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Configure environment variables**:
   Create a `.env` file in the root directory and copy the contents from `.env.example`:
   ```bash
   cp .env.example .env
   ```
   Modify `.env` to include your unique `SECRET_KEY` and your `SENDGRID_API_KEY` (if you wish to enable emails).

6. **Start the FastAPI server**:
   You can either run the batch script:
   ```cmd
   start.bat
   ```
   Or launch it manually:
   ```bash
   uvicorn app.main:app --reload
   ```
   Once started, the backend API will run at `http://127.0.0.1:8000`. You can visit the interactive documentation at `http://127.0.0.1:8000/docs`.

### Frontend Setup
1. Since the frontend is composed of static assets, you can run them directly by opening `frontend/index.html` in your browser.
2. For the best user experience and to avoid CORS issues in some strict browser environments, serve the frontend folder using a simple HTTP server:
   - Using Python:
     ```bash
     cd frontend
     python -m http.server 8080
     ```
   - Then open `http://localhost:8080` in your web browser.

---

## License

This project is licensed under the MIT License.
