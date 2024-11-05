from fastapi import APIRouter, status, Depends, Form, File, UploadFile, HTTPException
from typing import List
from sqlalchemy.orm import Session
from src.database.models import PRODUCTS, PRODUCT_OPTIONS, PRODUCT_OPTION_VALUES
from src.database.main import get_db
from src.products.schemas import OptionGroup
from datetime import datetime
import cloudinary
import cloudinary.uploader

# Configure Cloudinary
cloudinary.config( 
    cloud_name = "dhlzptfdd", 
    api_key = "422561542944353", 
    api_secret = "ONEWzA6SG4RnVKtqGvOaoCDIvQo" 
)

product_router = APIRouter()

@product_router.get('/products')
async def get_products(db:Session = Depends(get_db)):
    products = db.query(PRODUCTS).all()
    return products

@product_router.post('/create_transaction')
async def create_transaction(db:Session = Depends(get_db)):
    return 'success'

@product_router.post('/product/create')
async def create_product(
    name: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    file: UploadFile = File(...),
    optionGroups: List[str] = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # Input validation
        if price <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Price must be greater than 0"
            )

        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )

        try:
            # Upload image to Cloudinary
            contents = await file.read()
            upload_result = cloudinary.uploader.upload(contents)
            image_url = upload_result['secure_url']
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload image: {str(e)}"
            )

        try:
            # Create the product
            new_product = PRODUCTS(
                COMPANY_ID=3,  # Hardcoded company ID
                NAME=name,
                DESCRIPTION=description,
                CATEGORY=category,
                PRICE=int(price * 100),
                IMAGE=image_url,
                CREATED_AT=datetime.utcnow(),
                UPDATED_AT=datetime.utcnow()
            )
            db.add(new_product)
            db.flush()
            
            # If no option groups provided, commit and return
            if not optionGroups:
                db.commit()
                return {
                    "status": "success",
                    "message": "Product created successfully without options",
                    "data": {
                        "product_id": new_product.ID,
                        "name": name,
                        "image_url": image_url
                    }
                }

            # Process option groups
            for group_json in optionGroups:
                try:
                    group = OptionGroup.parse_raw(group_json)
                except Exception as e:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid option group format: {str(e)}"
                    )

                # Create option group
                option = PRODUCT_OPTIONS(
                    PRODUCT_ID=new_product.ID,
                    OPTION=group.name,
                    CREATED_AT=datetime.utcnow(),
                    UPDATED_AT=datetime.utcnow()
                )
                db.add(option)
                db.flush()

                # Validate option values
                has_default = False
                for value in group.values:
                    if value.default:
                        has_default = True
                    if value.price < 0:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Price cannot be negative for option '{value.name}'"
                        )

                    # Create option value
                    option_value = PRODUCT_OPTION_VALUES(
                        OPTION_ID=option.ID,
                        VALUE=value.name,
                        PRICE=int(value.price * 100),
                        DEFAULT=value.default,
                        CREATED_AT=datetime.utcnow(),
                        UPDATED_AT=datetime.utcnow()
                    )
                    db.add(option_value)

                if not has_default:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Option group '{group.name}' must have at least one default value"
                    )

            db.commit()

            return {
                "status": "success",
                "message": "Product created successfully with options",
                "data": {
                    "product_id": new_product.ID,
                    "name": name,
                    "image_url": image_url
                }
            }

        except HTTPException as he:
            db.rollback()
            raise he
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )
    

@product_router.get('/product/{product_id}')
async def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(PRODUCTS).filter(PRODUCTS.ID == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Get the options for this product
    options = db.query(PRODUCT_OPTIONS).filter(PRODUCT_OPTIONS.PRODUCT_ID == product_id).all()
    
    option_data = []
    for option in options:
        values = db.query(PRODUCT_OPTION_VALUES).filter(PRODUCT_OPTION_VALUES.OPTION_ID == option.ID).all()
        option_data.append({
            "name": option.OPTION,
            "values": [{
                "name": value.VALUE,
                "price": value.PRICE / 100,
                "default": value.DEFAULT
            } for value in values]
        })

    return {
        "product": {
            "id": product.ID,
            "name": product.NAME,
            "description": product.DESCRIPTION,
            "category": product.CATEGORY,
            "price": product.PRICE / 100,
            "image_url": product.IMAGE,
            "created_at": product.CREATED_AT
        },
        "options": option_data
    }