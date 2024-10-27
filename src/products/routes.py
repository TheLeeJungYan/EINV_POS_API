from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from typing import List
from src.products.schemas import Product
from sqlalchemy.orm import Session
from src.database.models import PRODUCTS
from src.database.main import get_db
product_router = APIRouter()


@product_router.get('/products')
async def get_products(db:Session = Depends(get_db)):
    products = db.query(PRODUCTS).all()
    return products

