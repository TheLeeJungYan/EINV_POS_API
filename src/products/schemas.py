from pydantic import BaseModel

class Product(BaseModel):
    ID:int
    NAME:str
    CATEGORY:str
    PRICE:int