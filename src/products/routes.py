from fastapi import APIRouter, status, Depends, Form, File, UploadFile
from fastapi.exceptions import HTTPException
from typing import List
from src.products.schemas import Product
from sqlalchemy.orm import Session
from src.database.models import PRODUCTS
from src.database.main import get_db
from sqlalchemy.orm import Session
import os
from src.products.schemas import OptionGroup 
product_router = APIRouter()


@product_router.get('/products')
async def get_products(db:Session = Depends(get_db)):
    products = db.query(PRODUCTS).all()
    return products

@product_router.post('/create_transaction')
async def create_transaction(db:Session = Depends(get_db)):
    return 'success'

@product_router.post('/product/create')
async def create_product(name: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    file: UploadFile = File(...),
    optionGroups: List[str] = Form(...),
    db: Session = Depends(get_db)):
    # save_path = os.path.join(os.getcwd(), file.filename) 
    # with open(save_path, "wb") as f:
    #     contents = await file.read()  # Read the file contents
    #     f.write(contents)  # Write contents to the file
    option_groups = [OptionGroup.parse_raw(group) for group in optionGroups]
    return option_groups
    # return {
    #     "status": "success",
    #     "name": name,
    #     "description": description,
    #     "category": category,
    #     "price": price,
    #     "optionGroups": optionGroups
    # }

