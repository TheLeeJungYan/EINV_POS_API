from pydantic import BaseModel, EmailStr, StringConstraints, UUID4, ConfigDict
from typing import Optional, Annotated, Dict
from datetime import date
import re

class LoginRequest(BaseModel):
    username_or_email: str
    password: str

class UserType(BaseModel):
    id: int
    name: str

class UserInfo(BaseModel):
    id: UUID4
    username: str
    email: str
    type_id: int
    user_type: UserType

class CompanyInfo(BaseModel):
    id: UUID4
    owner_name: str
    business_reg_number: str

class LoginData(BaseModel):
    user: UserInfo
    company: Optional[CompanyInfo] = None
    access_token: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    data: Optional[LoginData] = None

class RegistrationRequest(BaseModel):
    email: EmailStr
    username: Annotated[str, StringConstraints(min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')]
    password: Annotated[str, StringConstraints(min_length=8, max_length=128)]  
    owner_full_name: str
    owner_ic_number: Annotated[str, StringConstraints(pattern=r'^\d{6}-\d{2}-\d{4}$')]  
    owner_birth_date: date
    phone_number: Annotated[str, StringConstraints(pattern=r'^\+?[\d\s-]{8,20}$')]
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: Annotated[str, StringConstraints(pattern=r'^\d{5}$')]
    country: str
    business_reg_number: Annotated[str, StringConstraints(min_length=5, max_length=50)]
    tax_reg_number: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "user123",
                "password": "SecurePass123!",
                "owner_full_name": "John Doe",
                "owner_ic_number": "123456-78-9012",
                "owner_birth_date": "1990-01-01",
                "phone_number": "+60123456789",
                "address_line1": "123 Main Street",
                "address_line2": "Suite 45",
                "city": "Kuala Lumpur",
                "state": "Federal Territory",
                "postal_code": "50000",
                "country": "Malaysia",
                "business_reg_number": "ABC12345",
                "tax_reg_number": "TAX123456"
            }
        }
    )

class RegistrationResponse(BaseModel):
    success: bool
    message: str