from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from .schemas import LoginRequest, RegistrationRequest, LoginResponse, RegistrationResponse
from .main import LoginSystem
from .security import SecurityManager, get_current_user
from src.database.main import get_db
from src.database.models import USERS, USER_TYPES
from typing import Dict, List
from src.database.seeder import SECRET_KEY
from .exceptions import AuthorizationError, InternalServerError
from sqlalchemy import select

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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )

@authentication_router.post("/register", response_model=RegistrationResponse)
async def register(
    request: RegistrationRequest,
    current_user: USERS = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> RegistrationResponse:
    """Handle registration endpoint"""
    try:
        # Check if current user has permission to register new users
        if current_user and current_user.USER_TYPE_ID != 1:  # Assuming 1 is SUPERADMIN
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can register new users"
            )
            
        login_system = LoginSystem(db, security_manager)
        return await login_system.register(request, current_user.ID if current_user else None)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@authentication_router.get('/users', response_model=List[Dict])
async def get_users(
    current_user: USERS = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of users with their types"""
    try:
        # Check user permissions
        if current_user.USER_TYPE_ID not in [1, 2]:  # Assuming 1 is SUPERADMIN, 2 is ADMIN
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view user list"
            )

        # Build the query based on user type
        stmt = select(
            USERS,
            USER_TYPES.NAME.label('user_type_name')
        ).join(
            USER_TYPES,
            USERS.USER_TYPE_ID == USER_TYPES.ID,
            isouter=True
        )

        # If not superadmin, only show users from same company
        if current_user.USER_TYPE_ID == 2:  # ADMIN
            stmt = stmt.where(USERS.COMPANY_ID == current_user.COMPANY_ID)

        users = db.execute(stmt).all()
        
        return [{
            "id": str(user.USERS.ID),  # Convert UUID to string
            "username": user.USERS.USERNAME,
            "email": user.USERS.EMAIL,
            "user_type": user.user_type_name,
            "company_id": str(user.USERS.COMPANY_ID) if user.USERS.COMPANY_ID else None,  # Convert UUID to string
            "created_at": user.USERS.CREATED_AT,
            "created_by": str(user.USERS.CREATED_BY) if hasattr(user.USERS, 'CREATED_BY') else None,
            "updated_at": user.USERS.UPDATED_AT,
            "updated_by": str(user.USERS.UPDATED_BY) if hasattr(user.USERS, 'UPDATED_BY') else None
        } for user in users]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user list"
        )