from fastapi import APIRouter, status, Depends, Form, File, UploadFile, HTTPException, Security, Response
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import List, Optional
from sqlalchemy.orm import Session
from src.database.models import PRODUCTS, PRODUCT_OPTIONS, PRODUCT_OPTIONS_GROUPS, USERS
from src.database.seeder import SECRET_KEY
from src.login.security import SecurityManager
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

security = HTTPBearer()
product_router = APIRouter()
security_manager = SecurityManager(SECRET_KEY)

def get_current_user(token: str, db: Session):
    """Verify JWT token and return user"""
    try:
        # Verify token and get payload
        payload = security_manager.verify_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        # Get user from database
        user = db.query(USERS).filter(USERS.ID == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        return user

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@product_router.post('/product/create', status_code=status.HTTP_201_CREATED)
async def create_product(
    name: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    file: UploadFile = File(...),
    optionGroups: List[str] = Form(...),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        # Get current user
        current_user = get_current_user(credentials.credentials, db)
       
        # Input validation
        if price <= 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"status": "error", "message": "Price must be greater than 0"}
            )

        if not file.filename:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"status": "error", "message": "No file provided"}
            )

        try:
            # Upload image to Cloudinary
            contents = await file.read()
            upload_result = cloudinary.uploader.upload(contents)
            image_url = upload_result['secure_url']
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"status": "error", "message": f"Failed to upload image: {str(e)}"}
            )

        try:
            # Create the product
            new_product = PRODUCTS(
                COMPANY_ID=current_user.COMPANY_ID,
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

            # Process option groups
            for group_json in optionGroups:
                try:
                    group = OptionGroup.parse_raw(group_json)
                except Exception as e:
                    db.rollback()
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={"status": "error", "message": f"Invalid option group format: {str(e)}"}
                    )

                # Create option group
                option_group = PRODUCT_OPTIONS_GROUPS(
                    PRODUCT_ID=new_product.ID,
                    OPTION_GROUP=group.name,
                    CREATED_AT=datetime.utcnow(),
                    UPDATED_AT=datetime.utcnow()
                )
                db.add(option_group)
                db.flush()

                # Process each value in the group
                has_default = False
                for index,option in enumerate(group.options):
                    if index==group.default:
                        default = True
                        has_default = True
                    else:
                        default = False
                    if option.price < 0:
                        db.rollback()
                        return JSONResponse(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            content={"status": "error", "message": f"Price cannot be negative for option '{option.option}'"}
                        )

                    option = PRODUCT_OPTIONS(
                        PRODUCT_OPTION_GROUP_ID=option_group.ID,
                        OPTION=option.option,
                        DESCRIPTION=option.desc,
                        PRICE=int(option.price * 100),
                        DEFAULT=default,
                        CREATED_AT=datetime.utcnow(),
                        UPDATED_AT=datetime.utcnow()
                    )
                    db.add(option)

                if not has_default:
                    db.rollback()
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={"status": "error", "message": f"Option group '{group.name}' must have at least one default value"}
                    )

            db.commit()
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "status": "success",
                    "message": "Product created successfully",
                    "data": {
                        "product_id": new_product.ID,
                        "name": name,
                        "image_url": image_url
                    }
                }
            )

        except Exception as e:
            db.rollback()
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"status": "error", "message": f"Database error: {str(e)}"}
            )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": f"Unexpected error: {str(e)}"}
        )

@product_router.get('/product/{product_id}', status_code=status.HTTP_200_OK)
async def get_product(
    product_id: int,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        product = db.query(PRODUCTS).filter(
            PRODUCTS.ID == product_id,
            PRODUCTS.DELETED_AT.is_(None)
        ).first()
        
        if not product:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"status": "error", "message": "Product not found"}
            )

        # Get options for this product
        option_groups = db.query(PRODUCT_OPTIONS_GROUPS).filter(
            PRODUCT_OPTIONS_GROUPS.PRODUCT_ID == product_id,
            PRODUCT_OPTIONS_GROUPS.DELETED_AT.is_(None)
        ).all()
        
        option_data = []
        for group in option_groups:
            options = db.query(PRODUCT_OPTIONS).filter(
                PRODUCT_OPTIONS.PRODUCT_OPTION_GROUP_ID == group.ID,
                PRODUCT_OPTIONS.DELETED_AT.is_(None)
            ).all()
            
            option_data.append({
                "name": group.OPTION_GROUP,
                "options": [{
                    "option": option.OPTION,
                    "description": option.DESCRIPTION,
                    "price": option.PRICE / 100,
                    "default": option.DEFAULT
                } for option in options]
            })

        # Check if user is owner of the product
        is_owner = False
        if credentials:
            current_user = get_current_user(credentials.credentials, db)
            is_owner = (product.COMPANY_ID == current_user.COMPANY_ID)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "data": {
                    "product": {
                        "id": product.ID,
                        "name": product.NAME,
                        "description": product.DESCRIPTION,
                        "category": product.CATEGORY,
                        "price": product.PRICE / 100,
                        "image_url": product.IMAGE,
                        "created_at": str(product.CREATED_AT),
                        "is_owner": is_owner
                    },
                    "options": option_data
                }
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": f"Error retrieving product: {str(e)}"}
        )
    

@product_router.get('/products', status_code=status.HTTP_200_OK)
async def get_products(
    response: Response,
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    try:
        if credentials:
            # If authenticated, show user's company products
            current_user = get_current_user(credentials.credentials, db)
            products = db.query(PRODUCTS).filter(
                PRODUCTS.COMPANY_ID == current_user.COMPANY_ID,
                PRODUCTS.DELETED_AT.is_(None)
            ).all()
        else:
            # If not authenticated, show all active products
            products = db.query(PRODUCTS).filter(PRODUCTS.DELETED_AT.is_(None)).all()
        
        products_data = [{
            "id": product.ID,
            "name": product.NAME,
            "category": product.CATEGORY,
            "description": product.DESCRIPTION,
            "price": product.PRICE / 100,
            "image_url": product.IMAGE,
            "created_at": str(product.CREATED_AT)
        } for product in products]
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "success", "data": products_data}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": str(e)}
        )

@product_router.put('/product/{product_id}', status_code=status.HTTP_200_OK)
async def update_product(
    product_id: int,
    credentials: HTTPAuthorizationCredentials = Security(security),
    name: str = Form(None),
    description: str = Form(None),
    category: str = Form(None),
    price: float = Form(None),
    file: UploadFile = File(None),
    optionGroups: List[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        # Get current user
        current_user = get_current_user(credentials.credentials, db)
        
        # Check if product exists
        product = db.query(PRODUCTS).filter(
            PRODUCTS.ID == product_id,
            PRODUCTS.DELETED_AT.is_(None)
        ).first()
        
        if not product:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"status": "error", "message": "Product not found"}
            )

        # Check if user has permission
        if product.COMPANY_ID != current_user.COMPANY_ID:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"status": "error", "message": "You don't have permission to modify this product"}
            )

        # Update image if new file is provided
        if file and file.filename:
            try:
                contents = await file.read()
                upload_result = cloudinary.uploader.upload(contents)
                product.IMAGE = upload_result['secure_url']
            except Exception as e:
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"status": "error", "message": f"Failed to upload image: {str(e)}"}
                )

        # Update basic product details if provided
        if name is not None:
            product.NAME = name
        if description is not None:
            product.DESCRIPTION = description
        if category is not None:
            product.CATEGORY = category
        if price is not None:
            if price <= 0:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"status": "error", "message": "Price must be greater than 0"}
                )
            product.PRICE = int(price * 100)

        product.UPDATED_AT = datetime.utcnow()

        # Update option groups if provided
        if optionGroups is not None:
            # Soft delete existing options and their values
            current_time = datetime.utcnow()
            
            # Get all existing option groups
            existing_groups = db.query(PRODUCT_OPTIONS_GROUPS).filter(
                PRODUCT_OPTIONS_GROUPS.PRODUCT_ID == product_id,
                PRODUCT_OPTIONS_GROUPS.DELETED_AT.is_(None)
            ).all()
            
            for group in existing_groups:
                # Soft delete options
                db.query(PRODUCT_OPTIONS).filter(
                    PRODUCT_OPTIONS.PRODUCT_OPTION_GROUP_ID == group.ID,
                    PRODUCT_OPTIONS.DELETED_AT.is_(None)
                ).update({PRODUCT_OPTIONS.DELETED_AT: current_time})
                
                # Soft delete option group
                group.DELETED_AT = current_time

            # Create new option groups
            for group_json in optionGroups:
                try:
                    group = OptionGroup.parse_raw(group_json)
                except Exception as e:
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={"status": "error", "message": f"Invalid option group format: {str(e)}"}
                    )

                # Create option group
                option_group = PRODUCT_OPTIONS_GROUPS(
                    PRODUCT_ID=product_id,
                    OPTION_GROUP=group.name,
                    CREATED_AT=datetime.utcnow(),
                    UPDATED_AT=datetime.utcnow()
                )
                db.add(option_group)
                db.flush()

                # Process options within the group
                default_index = int(group.default)
                for index, option_value in enumerate(group.options):
                    if option_value.price < 0:
                        return JSONResponse(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            content={"status": "error", "message": f"Price cannot be negative for option '{option_value.option}'"}
                        )

                    option = PRODUCT_OPTIONS(
                        PRODUCT_OPTION_GROUP_ID=option_group.ID,
                        OPTION=option_value.option,
                        DESCRIPTION=option_value.desc,
                        PRICE=int(option_value.price * 100),
                        DEFAULT=(index == default_index),
                        CREATED_AT=datetime.utcnow(),
                        UPDATED_AT=datetime.utcnow()
                    )
                    db.add(option)

        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "message": "Product updated successfully",
                "data": {
                    "product_id": product_id,
                    "name": product.NAME,
                    "image_url": product.IMAGE
                }
            }
        )

    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": f"Error updating product: {str(e)}"}
        )

@product_router.delete('/product/{product_id}', status_code=status.HTTP_200_OK)
async def delete_product(
    product_id: int,
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
):
    try:
        # Get current user
        current_user = get_current_user(credentials.credentials, db)
        
        # Check if product exists
        product = db.query(PRODUCTS).filter(
            PRODUCTS.ID == product_id,
            PRODUCTS.DELETED_AT.is_(None)
        ).first()
        
        if not product:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"status": "error", "message": "Product not found"}
            )

        # Check if user has permission
        if product.COMPANY_ID != current_user.COMPANY_ID:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"status": "error", "message": "You don't have permission to delete this product"}
            )

        # Soft delete the product and its options
        current_time = datetime.utcnow()
        
        # Get all option groups
        option_groups = db.query(PRODUCT_OPTIONS_GROUPS).filter(
            PRODUCT_OPTIONS_GROUPS.PRODUCT_ID == product_id,
            PRODUCT_OPTIONS_GROUPS.DELETED_AT.is_(None)
        ).all()
        
        for group in option_groups:
            # Soft delete options
            db.query(PRODUCT_OPTIONS).filter(
                PRODUCT_OPTIONS.PRODUCT_OPTION_GROUP_ID == group.ID,
                PRODUCT_OPTIONS.DELETED_AT.is_(None)
            ).update({PRODUCT_OPTIONS.DELETED_AT: current_time})
            
            # Soft delete option group
            group.DELETED_AT = current_time

        # Soft delete the product
        product.DELETED_AT = current_time
        
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "message": "Product deleted successfully",
                "data": {"product_id": product_id}
            }
        )

    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": f"Error deleting product: {str(e)}"}
        )