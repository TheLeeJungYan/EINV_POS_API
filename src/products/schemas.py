from pydantic import BaseModel
from typing import List

# For basic product response
class Product(BaseModel):
    ID: int
    NAME: str
    CATEGORY: str
    PRICE: int

# For option values
class OptionValue(BaseModel):
    name: str
    price: float
    default: bool = False

# For option groups
class OptionGroup(BaseModel):
    name: str
    values: List[OptionValue]

# For product creation request
class ProductCreateRequest(BaseModel):
    name: str
    description: str
    category: str
    price: float
    optionGroups: List[OptionGroup] = []