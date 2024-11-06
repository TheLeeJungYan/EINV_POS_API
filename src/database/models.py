from sqlalchemy import Boolean, String, Integer, TIMESTAMP, Column, ForeignKey, JSON, Table, Date,Text
from sqlalchemy.orm import relationship
from src.database.main import Base

class USER_TYPES(Base):
    __tablename__ = 'USER_TYPES'
    ID = Column(Integer, primary_key=True, index=True)
    NAME = Column(String(50), unique=True, nullable=False)  # 'SUPERADMIN', 'ADMIN', 'USER'
    CREATED_AT = Column(TIMESTAMP)
    UPDATED_AT = Column(TIMESTAMP)

class COMPANIES(Base):
    __tablename__ = 'COMPANIES'
    ID = Column(Integer, primary_key=True, index=True)
    # Owner Information
    OWNER_FULL_NAME = Column(String(255), nullable=False)
    OWNER_IC_NUMBER = Column(String(20), nullable=False, unique=True)
    OWNER_BIRTH_DATE = Column(Date, nullable=False)
    
    # Contact Information
    PHONE_NUMBER = Column(String(20))
    ADDRESS_LINE1 = Column(String(255), nullable=False)
    ADDRESS_LINE2 = Column(String(255))
    CITY = Column(String(100))
    STATE = Column(String(100))
    POSTAL_CODE = Column(String(20))
    COUNTRY = Column(String(100))
    
    # Business Information
    BUSINESS_REG_NUMBER = Column(String(50), unique=True)
    TAX_REG_NUMBER = Column(String(50), unique=True)
    
    # Subscription and Login Info
    SUBSCRIPTION_ID = Column(Integer)
    SUBSCRIPTION_END_AT = Column(TIMESTAMP)
    LAST_LOGIN_IP = Column(String(255))
    LAST_LOGIN_AT = Column(TIMESTAMP)
    
    # Timestamps
    CREATED_AT = Column(TIMESTAMP)
    UPDATED_AT = Column(TIMESTAMP)

class USERS(Base):
    __tablename__ = 'USERS'
    ID = Column(Integer, primary_key=True, index=True)
    USERNAME = Column(String(255), unique=True)
    EMAIL = Column(String(255), unique=True)
    PASSWORD = Column(String(255))
    USER_TYPE_ID = Column(Integer, ForeignKey('USER_TYPES.ID'))  # Changed to match seeder
    COMPANY_ID = Column(Integer, ForeignKey('COMPANIES.ID'), nullable=True)
    CREATED_AT = Column(TIMESTAMP)
    UPDATED_AT = Column(TIMESTAMP)

class CATEGORIES(Base):
    __tablename__ = 'CATEGORIES'
    ID = Column(Integer, primary_key=True, index=True)
    NAME = Column(String(255))
    ICON = Column(String(255))
    CREATED_AT = Column(TIMESTAMP)
    UPDATED_AT = Column(TIMESTAMP)
    DELETED_AT = Column(TIMESTAMP)

class PRODUCTS(Base):
    __tablename__ = 'PRODUCTS'
    ID = Column(Integer, primary_key=True, index=True)
    COMPANY_ID = Column(Integer, ForeignKey('COMPANIES.ID'))
    NAME = Column(String(255))
    CATEGORY = Column(String(255))
    DESCRIPTION = Column(Text)
    PRICE = Column(Integer)
    IMAGE = Column(String(255))
    CREATED_AT = Column(TIMESTAMP)
    UPDATED_AT = Column(TIMESTAMP)
    DELETED_AT = Column(TIMESTAMP)

class PAYMENT_TYPES(Base):  # Renamed from TRANSACTION_TYPES
    __tablename__ = 'PAYMENT_TYPES'
    ID = Column(Integer, primary_key=True, index=True)
    NAME = Column(String(50), unique=True, nullable=False)  # 'CASH', 'TNG', 'CREDIT_CARD', etc.
    IS_ACTIVE = Column(Boolean, default=True)  # To enable/disable payment methods
    CREATED_AT = Column(TIMESTAMP)
    UPDATED_AT = Column(TIMESTAMP)

class TRANSACTIONS(Base):
    __tablename__ = 'TRANSACTIONS'
    ID = Column(Integer, primary_key=True, index=True)
    COMPANY_ID = Column(Integer, ForeignKey('COMPANIES.ID'))
    PRODUCT_ID = Column(Integer, ForeignKey('PRODUCTS.ID'))
    PAYMENT_TYPE_ID = Column(Integer, ForeignKey('PAYMENT_TYPES.ID'))  # Changed from TRANSACTION_TYPE_ID
    AMOUNT = Column(Integer)
    SELECTED_OPTIONS = Column(JSON)
    PAYMENT_REFERENCE = Column(String(255), nullable=True)  # For payment references/receipts
    CREATED_AT = Column(TIMESTAMP)

class PRODUCT_OPTIONS_GROUPS(Base):
    __tablename__ = 'PRODUCT_OPTIONS_GROUPS'
    ID = Column(Integer, primary_key=True, index=True)
    PRODUCT_ID = Column(Integer, ForeignKey('PRODUCTS.ID'))
    OPTION_GROUP = Column(String(255), nullable=False)
    CREATED_AT = Column(TIMESTAMP)
    UPDATED_AT = Column(TIMESTAMP)
    DELETED_AT = Column(TIMESTAMP)

class PRODUCT_OPTIONS(Base):
    __tablename__ = "PRODUCT_OPTION"
    ID = Column(Integer, primary_key=True, index=True)
    PRODUCT_OPTION_GROUP_ID= Column(Integer, ForeignKey('PRODUCT_OPTIONS_GROUPS.ID'))
    OPTION = Column(String(255),nullable=False)
    DESCRIPTION = Column(Text)
    PRICE = Column(Integer,nullable=False)
    DEFAULT = Column(Boolean,nullable=False)
    CREATED_AT = Column(TIMESTAMP)
    UPDATED_AT = Column(TIMESTAMP)
    DELETED_AT = Column(TIMESTAMP)