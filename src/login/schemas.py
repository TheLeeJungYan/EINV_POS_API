from pydantic import BaseModel, EmailStr, StringConstraints
from typing import Optional, Annotated
from datetime import date
import re

class LoginRequest(BaseModel):
    username_or_email: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

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
    business_reg_number: str
    tax_reg_number: Optional[str] = None

class RegistrationResponse(BaseModel):
    success: bool
    message: str