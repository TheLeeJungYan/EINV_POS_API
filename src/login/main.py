from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from src.database.models import COMPANIES
from .schemas import LoginRequest, RegistrationRequest, LoginResponse, RegistrationResponse
from .exceptions import LoginError, ValidationError, AuthenticationError, RegistrationError
from .validators import DataValidator
from .security import SecurityManager
from typing import Dict, Any

class LoginSystem:
    def __init__(self, db_session: Session, security_manager: SecurityManager):
        """Initialize login system with database session and security manager"""
        self.db = db_session
        self.security = security_manager
        self.validator = DataValidator()

    async def login(self, request: LoginRequest, ip_address: str) -> LoginResponse:
        """Handle login request"""
        try:
            # Query for user
            stmt = select(COMPANIES).where(
                or_(
                    COMPANIES.USERNAME == request.username_or_email,
                    COMPANIES.EMAIL == request.username_or_email
                )
            )
            result = self.db.execute(stmt).first()

            if not result:
                return LoginResponse(
                    success=False,
                    message="User not found. Would you like to register?",
                    data=None
                )

            company = result[0]
            if not self.security.verify_password(request.password, company.PASSWORD):
                return LoginResponse(
                    success=False,
                    message="Invalid password",
                    data=None
                )

            # Update last login info
            company.LAST_LOGIN_IP = ip_address
            company.LAST_LOGIN_AT = datetime.utcnow()
            self.db.commit()

            # Create access token
            access_token = self.security.create_access_token(
                data={"sub": str(company.ID), "username": company.USERNAME}
            )

            return LoginResponse(
                success=True,
                message="Login successful",
                data={
                    "id": company.ID,
                    "name": company.NAME,
                    "username": company.USERNAME,
                    "email": company.EMAIL,
                    "owner_name": company.OWNER_FULL_NAME,
                    "phone_number": company.PHONE_NUMBER,
                    "business_reg_number": company.BUSINESS_REG_NUMBER,
                    "access_token": access_token
                }
            )

        except Exception as e:
            self.db.rollback()
            raise LoginError(f"Login failed: {str(e)}")

    async def register(self, request: RegistrationRequest) -> RegistrationResponse:
        """Handle registration request"""
        try:
            # Validate fields
            if not self.validator.validate_email(request.email):
                raise ValidationError("Invalid email format")

            if not self.validator.validate_ic_number(request.owner_ic_number):
                raise ValidationError("Invalid IC number format")

            if not self.validator.validate_phone_number(request.phone_number):
                raise ValidationError("Invalid phone number format")

            if not self.validator.validate_postal_code(request.postal_code):
                raise ValidationError("Invalid postal code format")

            is_valid_password, password_message = self.validator.validate_password(request.password)
            if not is_valid_password:
                raise ValidationError(password_message)

            # Check for existing records
            existing = self.db.execute(
                select(COMPANIES).where(
                    or_(
                        COMPANIES.EMAIL == request.email,
                        COMPANIES.USERNAME == request.username,
                        COMPANIES.OWNER_IC_NUMBER == request.owner_ic_number,
                        COMPANIES.BUSINESS_REG_NUMBER == request.business_reg_number
                    )
                )
            ).first()

            if existing:
                raise RegistrationError(
                    "Email, username, IC number, or business registration number already exists"
                )

            # Create new company record
            new_company = COMPANIES(
                NAME=request.company_name,
                USERNAME=request.username,
                EMAIL=request.email,
                PASSWORD=self.security.hash_password(request.password),
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
            self.db.commit()

            return RegistrationResponse(
                success=True,
                message="Registration completed successfully"
            )

        except ValidationError as e:
            self.db.rollback()
            return RegistrationResponse(success=False, message=str(e))
        except RegistrationError as e:
            self.db.rollback()
            return RegistrationResponse(success=False, message=str(e))
        except Exception as e:
            self.db.rollback()
            raise RegistrationError(f"Failed to complete registration: {str(e)}")