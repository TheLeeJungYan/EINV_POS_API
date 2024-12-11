from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from enum import Enum

class ProductStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DRAFT = "DRAFT"
    ARCHIVED = "ARCHIVED"

class Product(BaseModel):
    ID: UUID
    NAME: str
    CATEGORY: str
    PRICE: int
    STATUS: ProductStatus
    COMPANY_ID: UUID
    CREATED_BY: Optional[UUID] = None
    UPDATED_BY: Optional[UUID] = None
    CREATED_AT: Optional[datetime] = None
    UPDATED_AT: Optional[datetime] = None

class OptionValue(BaseModel):
    option: str
    desc: Optional[str] = "" 
    price: float = Field(..., gt=0)  # Ensure price is greater than 0

    class Config:
        json_schema_extra = {
            "example": {
                "option": "Large",
                "desc": "Large size option",
                "price": 2.50
            }
        }

class OptionGroup(BaseModel):
    name: str
    default: int
    options: List[OptionValue]

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Size",
                "default": 0,
                "options": [
                    {"option": "Small", "desc": "Small size", "price": 0},
                    {"option": "Medium", "desc": "Medium size", "price": 1.50},
                    {"option": "Large", "desc": "Large size", "price": 2.50}
                ]
            }
        }

class ProductCreateRequest(BaseModel):
    name: str
    description: str
    category: str
    price: float = Field(..., gt=0)  # Ensure price is greater than 0
    optionGroups: List[OptionGroup] = []
    status: ProductStatus = ProductStatus.DRAFT  # Default status is DRAFT

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Classic Burger",
                "description": "A delicious classic burger",
                "category": "Burgers",
                "price": 9.99,
                "status": "DRAFT",
                "optionGroups": [
                    {
                        "name": "Size",
                        "default": 0,
                        "options": [
                            {"option": "Regular", "desc": "Regular size", "price": 0},
                            {"option": "Large", "desc": "Large size", "price": 2.00}
                        ]
                    }
                ]
            }
        }

class ProductResponse(BaseModel):
    id: UUID
    name: str
    description: str
    category: str
    price: float
    image_url: str
    status: ProductStatus
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ProductOptionResponse(BaseModel):
    option: str
    description: Optional[str]
    price: float
    default: bool

class ProductOptionGroupResponse(BaseModel):
    name: str
    options: List[ProductOptionResponse]

class ProductDetailResponse(BaseModel):
    product: ProductResponse
    options: List[ProductOptionGroupResponse]
    is_owner: bool = False

class ProductListResponse(BaseModel):
    status: str
    data: List[ProductResponse]

class ProductUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    status: Optional[ProductStatus] = None
    optionGroups: Optional[List[OptionGroup]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated Burger",
                "description": "Updated description",
                "category": "Premium Burgers",
                "price": 11.99,
                "status": "ACTIVE",
                "optionGroups": [
                    {
                        "name": "Size",
                        "default": 0,
                        "options": [
                            {"option": "Regular", "desc": "Regular size", "price": 0},
                            {"option": "Large", "desc": "Large size", "price": 2.50}
                        ]
                    }
                ]
            }
        }