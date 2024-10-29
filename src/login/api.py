from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from src.login.routes import router as login_router
from src.database.main import get_db

app = FastAPI(title="POS System API")

# Include the router
app.include_router(login_router, prefix="/api/v1")