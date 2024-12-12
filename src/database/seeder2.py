from .main import SessionLocal
from .models import (
    USER_TYPES, USERS, COMPANIES, CATEGORIES, PRODUCTS, 
    PAYMENT_TYPES, PRODUCT_OPTIONS_GROUPS, PRODUCT_OPTIONS,
    TRANSACTIONS
)
from .seed_data import products, options
from datetime import datetime, date
def seed():
    db = SessionLocal()
    try:
        for product in products:
            new_product = PRODUCTS(
                COMPANY_ID=2,
                NAME=product['NAME'],
                DESCRIPTION=product['DESCRIPTION'],
                CATEGORY=product['CATEGORY'],
                PRICE=float(product['PRICE']*100),
                IMAGE=product['IMAGE'],
                CREATED_AT=datetime.utcnow(),
                UPDATED_AT=datetime.utcnow()
            )
            db.add(new_product)
            db.flush()

            option_group = PRODUCT_OPTIONS_GROUPS(
                    PRODUCT_ID=new_product.ID,
                    OPTION_GROUP='SIZE',
                    CREATED_AT=datetime.utcnow(),
                    UPDATED_AT=datetime.utcnow()
            )
            db.add(option_group)
            db.flush()

            for option in options:
                option = PRODUCT_OPTIONS(
                        PRODUCT_OPTION_GROUP_ID=option_group.ID,
                        OPTION=option['NAME'],
                        DESCRIPTION=option['DESC'],
                        PRICE= 0,
                        DEFAULT=True if option['NAME'] == 'S' else False,
                        CREATED_AT=datetime.utcnow(),
                        UPDATED_AT=datetime.utcnow()
                )
                db.add(option)
                db.flush
        db.commit()
    finally:
        db.close()
        print('done')


if __name__ == "__main__":
    seed()