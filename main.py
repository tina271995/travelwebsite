from fastapi import FastAPI, Form, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import sqlite3
import hashlib

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Database Initialization
def init_db():
    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()
    
    # Create bookings table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destination TEXT,
            date TEXT,
            passengers INTEGER,
            class TEXT
        )
    """)
    
    # Create users table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Home route
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Bookings route
@app.get("/bookings", response_class=HTMLResponse)
async def render_bookings(request: Request):
    return templates.TemplateResponse("bookings.html", {"request": request})

# Signup Page
@app.get("/signup", response_class=HTMLResponse)
async def render_signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

# Login Page
@app.get("/login", response_class=HTMLResponse)
async def render_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Signup Functionality
@app.post("/signup/")
async def signup(request: Request, username: str = Form(...), password: str = Form(...)):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        conn = sqlite3.connect("bookings.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()
        return RedirectResponse(url="/login", status_code=303)
    except sqlite3.IntegrityError:
        return JSONResponse(content={"error": "Username already exists"}, status_code=400)

# Login Functionality
@app.post("/login/")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    user = cursor.fetchone()
    conn.close()

    if user:
        response = RedirectResponse(url="/bookings", status_code=303)
        response.set_cookie(key="logged_in_user", value=username)
        return response
    else:
        return JSONResponse(content={"error": "Invalid username or password"}, status_code=400)
