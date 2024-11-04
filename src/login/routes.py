from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from .schemas import LoginRequest, RegistrationRequest, LoginResponse, RegistrationResponse
from .main import LoginSystem
from .security import SecurityManager
from src.database.main import get_db
from typing import Dict
from src.database.seeder import SECRET_KEY  # Import the same secret key


app = FastAPI()

router = APIRouter()
security_manager = SecurityManager(SECRET_KEY)

@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    client_request: Request,
    db: Session = Depends(get_db)
) -> LoginResponse:
    """Handle login endpoint"""
    try:
        login_system = LoginSystem(db, security_manager)
        return await login_system.login(request, client_request.client.host)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/register", response_model=RegistrationResponse)
async def register(
    request: RegistrationRequest,
    db: Session = Depends(get_db)
) -> RegistrationResponse:
    """Handle registration endpoint"""
    try:
        login_system = LoginSystem(db, security_manager)
        return await login_system.register(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Include the router in the FastAPI app
app.include_router(router)