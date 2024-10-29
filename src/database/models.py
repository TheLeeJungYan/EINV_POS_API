from sqlalchemy import Boolean, String, Integer, TIMESTAMP, Column, ForeignKey, JSON, Table, Date
from sqlalchemy.orm import relationship
from src.database.main import Base


class COMPANIES(Base):
    __tablename__ = 'COMPANIES'
    ID = Column(Integer, primary_key=True, index=True)
    NAME = Column(String(255), unique=True)
    USERNAME = Column(String(255), unique=True)
    EMAIL = Column(String(255), unique=True)
    PASSWORD = Column(String(255))
    
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

class PRODUCTS(Base):
    __tablename__ = 'PRODUCTS'
    ID = Column(Integer, primary_key=True, index=True)
    COMPANY_ID = Column(Integer, ForeignKey('COMPANIES.ID'))
    NAME = Column(String(255))
    CATEGORY = Column(String(255))
    PRICE = Column(Integer)
    IMAGE = Column(String(255))
    CREATED_AT = Column(TIMESTAMP)
    UPDATED_AT = Column(TIMESTAMP)
    DELETED_AT = Column(TIMESTAMP)


class CATEGORIES(Base):
    __tablename__ = 'CATEGORIES'
    ID = Column(Integer, primary_key=True, index=True)
    NAME = Column(String(255))
    ICON = Column(String(255))
    CREATED_AT = Column(TIMESTAMP)
    UPDATED_AT = Column(TIMESTAMP)
    DELETED_AT = Column(TIMESTAMP)

class TRANSACTIONS(Base):
    __tablename__ = 'TRANSACTIONS'
    ID = Column(Integer, primary_key=True, index=True)
    COMPANY_ID = Column(Integer, ForeignKey('COMPANIES.ID'))
    PRODUCT_ID = Column(Integer, ForeignKey('PRODUCTS.ID'))
    AMOUNT = Column(Integer)
    SELECTED_OPTIONS = Column(JSON)
    CREATED_AT = Column(TIMESTAMP)


class PRODUCT_OPTIONS(Base):
    __tablename__ = 'PRODUCT_OPTIONS'
    ID = Column(Integer, primary_key=True, index=True)
    PRODUCT_ID = Column(Integer, ForeignKey('PRODUCTS.ID'))
    OPTION = Column(String(255), nullable=False)
    CREATED_AT = Column(TIMESTAMP)
    UPDATED_AT = Column(TIMESTAMP)
    DELETED_AT = Column(TIMESTAMP)

class PRODUCT_OPTION_VALUES(Base):
    __tablename__ = "PRODUCT_OPTION_VALUES"
    ID = Column(Integer, primary_key=True, index=True)
    OPTION_ID= Column(Integer, ForeignKey('PRODUCT_OPTIONS.ID'))
    VALUE = Column(String(255),nullable=False)
    PRICE = Column(Integer,nullable=False)
    DEFAULT = Column(Boolean,nullable=False)
    CREATED_AT = Column(TIMESTAMP)
    UPDATED_AT = Column(TIMESTAMP)
    DELETED_AT = Column(TIMESTAMP)