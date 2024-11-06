from datetime import datetime, date
from src.database.main import SessionLocal
from src.database.models import (
    USER_TYPES, USERS, COMPANIES, CATEGORIES, PRODUCTS, 
    PAYMENT_TYPES, PRODUCT_OPTIONS_GROUPS, PRODUCT_OPTIONS,
    TRANSACTIONS
)
from src.login.security import SecurityManager

# Use this secret key across your application
SECRET_KEY = "vn8K9pZ2Rj4Mx5Ly3Qw7"  # 20 characters, mix of letters and numbers
security_manager = SecurityManager(SECRET_KEY)

def seed_database():
    db = SessionLocal()
    try:
        # Clear existing data (optional, but helps prevent duplicates)
        db.query(TRANSACTIONS).delete()
        db.query(PRODUCT_OPTIONS).delete()
        db.query(PRODUCT_OPTIONS_GROUPS).delete()
        db.query(PRODUCTS).delete()
        db.query(CATEGORIES).delete()
        db.query(USERS).delete()
        db.query(COMPANIES).delete()
        db.query(PAYMENT_TYPES).delete()
        db.query(USER_TYPES).delete()
        
        # 1. Seed User Types
        print("Seeding user types...")
        user_types = [
            USER_TYPES(
                NAME="SUPERADMIN",
                CREATED_AT=datetime.now(),
                UPDATED_AT=datetime.now()
            ),
            USER_TYPES(
                NAME="ADMIN",
                CREATED_AT=datetime.now(),
                UPDATED_AT=datetime.now()
            ),
            USER_TYPES(
                NAME="USER",
                CREATED_AT=datetime.now(),
                UPDATED_AT=datetime.now()
            )
        ]
        db.add_all(user_types)
        db.flush()

        # 2. Seed Payment Types
        print("Seeding payment types...")
        payment_types = [
            PAYMENT_TYPES(
                NAME="CASH",
                IS_ACTIVE=True,
                CREATED_AT=datetime.now(),
                UPDATED_AT=datetime.now()
            ),
            PAYMENT_TYPES(
                NAME="TOUCH_N_GO",
                IS_ACTIVE=True,
                CREATED_AT=datetime.now(),
                UPDATED_AT=datetime.now()
            ),
            PAYMENT_TYPES(
                NAME="CREDIT_CARD",
                IS_ACTIVE=True,
                CREATED_AT=datetime.now(),
                UPDATED_AT=datetime.now()
            ),
            PAYMENT_TYPES(
                NAME="DEBIT_CARD",
                IS_ACTIVE=True,
                CREATED_AT=datetime.now(),
                UPDATED_AT=datetime.now()
            ),
            PAYMENT_TYPES(
                NAME="GRAB_PAY",
                IS_ACTIVE=True,
                CREATED_AT=datetime.now(),
                UPDATED_AT=datetime.now()
            ),
            PAYMENT_TYPES(
                NAME="BOOST",
                IS_ACTIVE=True,
                CREATED_AT=datetime.now(),
                UPDATED_AT=datetime.now()
            ),
            PAYMENT_TYPES(
                NAME="SHOPEE_PAY",
                IS_ACTIVE=True,
                CREATED_AT=datetime.now(),
                UPDATED_AT=datetime.now()
            ),
            PAYMENT_TYPES(
                NAME="MAE",
                IS_ACTIVE=True,
                CREATED_AT=datetime.now(),
                UPDATED_AT=datetime.now()
            ),
            PAYMENT_TYPES(
                NAME="DuitNow_QR",
                IS_ACTIVE=True,
                CREATED_AT=datetime.now(),
                UPDATED_AT=datetime.now()
            )
        ]
        db.add_all(payment_types)
        db.flush()

        # 3. Create Superadmin (not associated with any company)
        print("Creating superadmin...")
        superadmin = USERS(
            USERNAME="superadmin",
            EMAIL="superadmin@example.com",
            PASSWORD=security_manager.hash_password("SuperAdmin123!"),
            USER_TYPE_ID=user_types[0].ID,  # SUPERADMIN type
            CREATED_AT=datetime.now(),
            UPDATED_AT=datetime.now()
        )
        db.add(superadmin)
        db.flush()

        # 4. Seed Company
        print("Seeding company...")
        company = COMPANIES(
            OWNER_FULL_NAME="John Doe",
            OWNER_IC_NUMBER="123456-78-9012",  # Updated to match format
            OWNER_BIRTH_DATE=date(1990, 1, 1),
            PHONE_NUMBER="+60123456789",
            ADDRESS_LINE1="123 Main Street",
            CITY="Kuala Lumpur",
            STATE="Federal Territory",
            POSTAL_CODE="50000",
            COUNTRY="Malaysia",
            BUSINESS_REG_NUMBER="BRN123456",
            TAX_REG_NUMBER="TRN123456",
            CREATED_AT=datetime.now(),
            UPDATED_AT=datetime.now()
        )
        db.add(company)
        db.flush()

        # 5. Seed Company Admin and User
        print("Creating admin and regular user...")
        admin = USERS(
            USERNAME="admin",
            EMAIL="admin@example.com",
            PASSWORD=security_manager.hash_password("Admin123!"),
            USER_TYPE_ID=user_types[1].ID,  # ADMIN type
            COMPANY_ID=company.ID,
            CREATED_AT=datetime.now(),
            UPDATED_AT=datetime.now()
        )
        db.add(admin)

        user = USERS(
            USERNAME="user",
            EMAIL="user@example.com",
            PASSWORD=security_manager.hash_password("User123!"),
            USER_TYPE_ID=user_types[2].ID,  # USER type
            COMPANY_ID=company.ID,
            CREATED_AT=datetime.now(),
            UPDATED_AT=datetime.now()
        )
        db.add(user)
        db.flush()

        # 6. Seed Categories
        print("Seeding categories...")
        categories = [
            CATEGORIES(
                NAME="Food",
                ICON="🍔",
                CREATED_AT=datetime.now(),
                UPDATED_AT=datetime.now()
            ),
            CATEGORIES(
                NAME="Drinks",
                ICON="🥤",
                CREATED_AT=datetime.now(),
                UPDATED_AT=datetime.now()
            ),
            CATEGORIES(
                NAME="Desserts",
                ICON="🍰",
                CREATED_AT=datetime.now(),
                UPDATED_AT=datetime.now()
            )
        ]
        db.add_all(categories)
        db.flush()

        # 7. Seed Products
        print("Seeding products...")
        products = [
            PRODUCTS(
                COMPANY_ID=company.ID,
                NAME="Burger",
                CATEGORY="Food",
                PRICE=1000,  # RM10.00
                IMAGE="burger.jpg",
                CREATED_AT=datetime.now(),
                UPDATED_AT=datetime.now()
            ),
            PRODUCTS(
                COMPANY_ID=company.ID,
                NAME="Coca Cola",
                CATEGORY="Drinks",
                PRICE=300,  # RM3.00
                IMAGE="coke.jpg",
                CREATED_AT=datetime.now(),
                UPDATED_AT=datetime.now()
            )
        ]
        db.add_all(products)
        db.flush()

        # 8. Seed Product Options
        print("Seeding product options...")
        for product in products:
            size_option = PRODUCT_OPTIONS_GROUPS(
                PRODUCT_ID=product.ID,
                OPTION="Size",
                CREATED_AT=datetime.now(),
                UPDATED_AT=datetime.now()
            )
            db.add(size_option)
            db.flush()

            # 9. Seed Product Option Values
            option_values = [
                PRODUCT_OPTIONS(
                    OPTION_ID=size_option.ID,
                    VALUE="Small",
                    PRICE=0,
                    DEFAULT=True,
                    CREATED_AT=datetime.now(),
                    UPDATED_AT=datetime.now()
                ),
                PRODUCT_OPTIONS(
                    OPTION_ID=size_option.ID,
                    VALUE="Large",
                    PRICE=200,  # RM2.00 extra
                    DEFAULT=False,
                    CREATED_AT=datetime.now(),
                    UPDATED_AT=datetime.now()
                )
            ]
            db.add_all(option_values)

        # 10. Create Sample Transaction
        print("Creating sample transaction...")
        sample_transaction = TRANSACTIONS(
            COMPANY_ID=company.ID,
            PRODUCT_ID=products[0].ID,  # Burger
            PAYMENT_TYPE_ID=payment_types[0].ID,  # CASH
            AMOUNT=1200,  # RM12.00 (Burger + Large size)
            SELECTED_OPTIONS={"size": "Large"},
            PAYMENT_REFERENCE="CASH-001",
            CREATED_AT=datetime.now()
        )
        db.add(sample_transaction)

        # Commit all changes
        db.commit()
        print("Database seeded successfully!")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise  # Re-raise the exception to see the full error
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()