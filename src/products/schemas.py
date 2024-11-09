from pydantic import BaseModel
from typing import List, Optional  # Add Optional import

# For basic product response
class Product(BaseModel):
    ID: int
    NAME: str
    CATEGORY: str
    PRICE: int

# For option values
class OptionValue(BaseModel):
    option: str
    desc: Optional[str] = "" 
    price: float

# For option groups
class OptionGroup(BaseModel):
    name: str
    default: int
    options: List[OptionValue]

# For product creation request
class ProductCreateRequest(BaseModel):
    name: str
    description: str
    category: str
    price: float
    optionGroups: List[OptionGroup] = []