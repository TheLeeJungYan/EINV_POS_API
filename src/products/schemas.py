from pydantic import BaseModel
from typing import List
from pydantic import BaseModel, Field
class Product(BaseModel):
    ID:int
    NAME:str
    CATEGORY:str
    PRICE:int

class Option(BaseModel):
    option: str
    desc: str
    price: str

class OptionGroup(BaseModel):
    name: str
    collapse: bool
    default: str
    options: List[Option]

class ProductCreateRequest(BaseModel):
    name: str
    description: str
    category: int
    price: float
    optionGroups: List[OptionGroup] = Field(default_factory=list)