from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.database.models import COMPANIES, USERS, USER_TYPES
from sqlalchemy import select, or_
from .schemas import LoginRequest, RegistrationRequest, LoginResponse, RegistrationResponse
from .validators import DataValidator
from .security import SecurityManager
from fastapi import HTTPException
from typing import Dict, Any

class LoginSystem:
    def __init__(self, db_session: Session, security_manager: SecurityManager):
        self.db = db_session
        self.security = security_manager
        self.validator = DataValidator()

    async def login(self, request: LoginRequest, ip_address: str) -> LoginResponse:
        """Handle login request"""
        try:
            # Query for user with join to USER_TYPES
            stmt = select(USERS, USER_TYPES).join(
                USER_TYPES,
                USERS.USER_TYPE_ID == USER_TYPES.ID
            ).where(
                or_(
                    USERS.USERNAME == request.username_or_email,
                    USERS.EMAIL == request.username_or_email
                )
            )
            result = self.db.execute(stmt).first()

            if not result:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid username or password"
                )

            user, user_type = result
            if not self.security.verify_password(request.password, user.PASSWORD):
                raise HTTPException(
                    status_code=401,
                    detail="Invalid username or password"
                )

            # Get company info if user has company_id
            company_info = None
            if user.COMPANY_ID:
                company_stmt = select(COMPANIES).where(COMPANIES.ID == user.COMPANY_ID)
                company_result = self.db.execute(company_stmt).first()
                if company_result:
                    company = company_result[0]
                    company_info = {
                        "id": company.ID,
                        "owner_name": company.OWNER_FULL_NAME,
                        "business_reg_number": company.BUSINESS_REG_NUMBER
                    }

            # Create access token
            access_token = self.security.create_access_token(
                data={"sub": str(user.ID), "username": user.USERNAME},
                expires_delta=timedelta(hours=24)
            )

            return LoginResponse(
                success=True,
                message="Login successful",
                data={
                    "user": {
                        "id": user.ID,
                        "username": user.USERNAME,
                        "email": user.EMAIL,
                        "type_id": user.USER_TYPE_ID,
                        "user_type": {
                            "id": user_type.ID,
                            "name": user_type.NAME
                        }
                    },
                    "company": company_info,
                    "access_token": access_token
                }
            )

        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"An internal error occurred: {str(e)}"
            )

    async def register(self, request: RegistrationRequest) -> RegistrationResponse:
        """Handle registration request"""
        try:
            # Validate fields
            if not self.validator.validate_email(request.email):
                raise HTTPException(
                    status_code=422,
                    detail="Invalid email format"
                )

            if not self.validator.validate_ic_number(request.owner_ic_number):
                raise HTTPException(
                    status_code=422,
                    detail="Invalid IC number format"
                )

            if not self.validator.validate_phone_number(request.phone_number):
                raise HTTPException(
                    status_code=422,
                    detail="Invalid phone number format"
                )

            if not self.validator.validate_postal_code(request.postal_code):
                raise HTTPException(
                    status_code=422,
                    detail="Invalid postal code format"
                )

            is_valid_password, password_message = self.validator.validate_password(request.password)
            if not is_valid_password:
                raise HTTPException(
                    status_code=422,
                    detail=password_message
                )

            # Check for existing records
            existing = self.db.execute(
                select(COMPANIES).where(
                    or_(
                        COMPANIES.OWNER_IC_NUMBER == request.owner_ic_number,
                        COMPANIES.BUSINESS_REG_NUMBER == request.business_reg_number
                    )
                )
            ).first()

            if existing:
                raise HTTPException(
                    status_code=409,
                    detail="IC number or business registration number already exists"
                )

            # Create new company record
            new_company = COMPANIES(
                OWNER_FULL_NAME=request.owner_full_name,
                OWNER_IC_NUMBER=request.owner_ic_number,
                OWNER_BIRTH_DATE=request.owner_birth_date,
                PHONE_NUMBER=request.phone_number,
                ADDRESS_LINE1=request.address_line1,
                ADDRESS_LINE2=request.address_line2,
                CITY=request.city,
                STATE=request.state,
                POSTAL_CODE=request.postal_code,
                COUNTRY=request.country,
                BUSINESS_REG_NUMBER=request.business_reg_number,
                TAX_REG_NUMBER=request.tax_reg_number,
                CREATED_AT=datetime.utcnow(),
                UPDATED_AT=datetime.utcnow()
            )

            self.db.add(new_company)
            self.db.flush()

            # Create new user record
            new_user = USERS(
                USERNAME=request.username,
                EMAIL=request.email,
                PASSWORD=self.security.hash_password(request.password),
                USER_TYPE_ID=2,  # Company user type
                COMPANY_ID=new_company.ID,
                CREATED_AT=datetime.utcnow(),
                UPDATED_AT=datetime.utcnow()
            )

            self.db.add(new_user)
            self.db.commit()

            return RegistrationResponse(
                success=True,
                message="Registration completed successfully"
            )

        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to complete registration: {str(e)}"
            )