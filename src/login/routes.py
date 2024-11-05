from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request,status
from sqlalchemy.orm import Session
from .schemas import LoginRequest, RegistrationRequest, LoginResponse, RegistrationResponse
from .main import LoginSystem
from .security import SecurityManager
from src.database.main import get_db
from src.database.models import USERS, USER_TYPES
from typing import Dict
from src.database.seeder import SECRET_KEY  # Import the same secret key
from .exceptions import AuthorizationError, InternalServerError


authentication_router = APIRouter()
security_manager = SecurityManager(SECRET_KEY)

@authentication_router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    client_request: Request,
    db: Session = Depends(get_db)
) -> LoginResponse:
    """Handle login endpoint"""
    try:
        login_system = LoginSystem(db, security_manager)
        return await login_system.login(request, client_request.client.host)
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@authentication_router.post("/register", response_model=RegistrationResponse)
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


@authentication_router.get('/users')
async def get_users(db: Session = Depends(get_db)):
    users = db.query(
        USERS,
        USER_TYPES.NAME.label('user_type_name')
    ).join(
        USER_TYPES,
        USERS.USER_TYPE_ID == USER_TYPES.ID,
        isouter=True  # This makes it a LEFT JOIN
    ).all()
    
    return [{
        "id": user.USERS.ID,
        "username": user.USERS.USERNAME,
        "email": user.USERS.EMAIL,
        "user_type": user.user_type_name,
        "created_at": user.USERS.CREATED_AT
    } for user in users]

