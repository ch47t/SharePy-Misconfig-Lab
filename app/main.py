import os
import shutil
from typing import Optional
from fastapi import Response

from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Request, Form
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Database imports (Keep your previous SQLAlchemy code here)
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import jwt 

# --- CONFIG & DB SETUP (Same as before) ---
SECRET_KEY = "secret123" # M15
DB_USER = os.getenv("POSTGRES_USER", "admin")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_NAME = os.getenv("POSTGRES_DB", "sharepy")
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

app = FastAPI(title="SharePy", debug=True) # M2

# M7: CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MOUNT STATIC & TEMPLATES ---
# Mount static for CSS and Images
app.mount("/static", StaticFiles(directory="static"), name="static")
# Mount uploads so we can see the uploaded pictures (M3 vulnerability enabled via Nginx usually, but this works too)
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

templates = Jinja2Templates(directory="templates")

# --- DB MODELS (Simplified for brevity) ---
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String) 
    role = Column(String, default="user")
    profile_pic = Column(String, default="/static/default.png")

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Pydantic Schemas ---
class UserAuth(BaseModel):
    username: str
    password: str

# ==========================
# 🖥️ FRONTEND ROUTES (HTML)
# ==========================

@app.get("/", response_class=HTMLResponse)
def view_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
    
@app.get("/search", response_class=HTMLResponse)
def search(q: str = ""):
    return f"""
    <html>
    <head><title>Search</title></head>
    <body style="background-color: #1a1a2e; color: white; text-align: center; font-family: monospace;">
        <h1>Search Results</h1>
        <p>No results found for: <b>{q}</b></p>
        <a href="/" style="color: cyan;">Back Home</a>
    </body>
    </html>
    """

@app.get("/register", response_class=HTMLResponse)
def view_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/profile", response_class=HTMLResponse)
def view_profile(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})

@app.get("/debug/info")
def debug_info():
    # On convertit en dict pour que FastAPI le sérialise en JSON proprement
    return dict(os.environ)
# ==========================
# ⚙️ API ROUTES (Logic)
# ==========================

"""@app.post("/api/register")
def api_register(user: UserAuth, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(400, "Username taken")
    
    role = "admin" if user.username == "admin" else "user"
    new_user = User(username=user.username, password=user.password, role=role)
    db.add(new_user); db.commit()
    return {"msg": "Created"}"""
    
# M2: Version réaliste (Crash sur erreur DB)
@app.post("/api/register")
def api_register(user: UserAuth, db: Session = Depends(get_db)):
    # ❌ ON ENLÈVE CE BLOC DE VÉRIFICATION PROPRE
    # if db.query(User).filter(User.username == user.username).first():
    #     raise HTTPException(400, "Username taken")
    
    # On force l'insertion directe. 
    # Si le user existe déjà, PostgreSQL va renvoyer une erreur "IntegrityError".
    # Comme on n'a pas de try/except ici, FastAPI va crasher en mode DEBUG.
    
    role = "admin" if user.username == "admin" else "user"
    new_user = User(username=user.username, password=user.password, role=role)
    db.add(new_user)
    db.commit() # <--- C'est ici que ça va exploser
    return {"msg": "Created"}
    

@app.post("/api/login")
def api_login(user: UserAuth, response: Response, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or db_user.password != user.password:
        raise HTTPException(401, "Bad credentials")
    
    token = jwt.encode({"sub": db_user.username, "role": db_user.role}, SECRET_KEY, algorithm="HS256")
    
    # 🍪 CRÉATION DU COOKIE VULNÉRABLE (M9)
    # HttpOnly=False permet au JavaScript (et donc au XSS) de le lire.
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=False,  # <--- C'est LA faille M9
        secure=False,
        samesite="lax"
    )
    
    return {"access_token": token}

@app.get("/api/users/me")
def api_me(request: Request, db: Session = Depends(get_db)):
    # M9: Vulnerability - Token logic should be robust, here it is manual for demo
    auth = request.headers.get("Authorization")
    if not auth: raise HTTPException(401)
    token = auth.split(" ")[1]
    data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    
    user = db.query(User).filter(User.username == data['sub']).first()
    return {"username": user.username, "role": user.role, "profile_pic": user.profile_pic}


@app.post("/api/upload")
async def api_upload(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Validate Token
    auth = request.headers.get("Authorization")
    if not auth: raise HTTPException(401)
    token = auth.split(" ")[1]
    data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    
    # M13: Save file (Vulnerable to path traversal and malicious types)
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Update DB
    user = db.query(User).filter(User.username == data['sub']).first()
    user.profile_pic = f"/uploads/{file.filename}"
    db.commit()
    
    return {"path": user.profile_pic}
