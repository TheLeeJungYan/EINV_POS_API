from sqlalchemy import Boolean, String, Integer, TIMESTAMP, Column, ForeignKey
from sqlalchemy.orm import relationship
from src.database.main import Base

class COMPANIES(Base):
    __tablename__ = 'COMPANIES'
    ID = Column(Integer, primary_key=True, index=True)
    NAME = Column(String(255), unique=True)
    USERNAME = Column(String(255))
    PASSWORD = Column(String(255))
    SUBSCRIPTION_ID = Column(Integer)
    SUBSCRIPTION_END_AT = Column(TIMESTAMP)
    LAST_LOGIN_IP = Column(String(255))
    LAST_LOGIN_AT = Column(TIMESTAMP)
    CREATED_AT = Column(TIMESTAMP)

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

    company = relationship("COMPANIES")
    option_mappings = relationship("PRODUCT_OPTION_MAPPINGS")

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
    CREATED_AT = Column(TIMESTAMP)

    company = relationship("COMPANIES")
    product = relationship("PRODUCTS")
    option_selections = relationship("TRANSACTION_OPTION_SELECTIONS")

class PRODUCT_OPTIONS(Base):
    __tablename__ = 'PRODUCT_OPTIONS'
    ID = Column(Integer, primary_key=True, index=True)
    NAME = Column(String(255), nullable=False)
    CREATED_AT = Column(TIMESTAMP)
    UPDATED_AT = Column(TIMESTAMP)
    DELETED_AT = Column(TIMESTAMP)

    option_values = relationship("PRODUCT_OPTION_VALUES")
    product_mappings = relationship("PRODUCT_OPTION_MAPPINGS")

class PRODUCT_OPTION_VALUES(Base):
    __tablename__ = 'PRODUCT_OPTION_VALUES'
    ID = Column(Integer, primary_key=True, index=True)
    OPTION_ID = Column(Integer, ForeignKey('PRODUCT_OPTIONS.ID'))
    VALUE = Column(String(255), nullable=False)
    CREATED_AT = Column(TIMESTAMP)
    UPDATED_AT = Column(TIMESTAMP)
    DELETED_AT = Column(TIMESTAMP)

    option = relationship("PRODUCT_OPTIONS")

class PRODUCT_OPTION_MAPPINGS(Base):
    __tablename__ = 'PRODUCT_OPTION_MAPPINGS'
    ID = Column(Integer, primary_key=True, index=True)
    PRODUCT_ID = Column(Integer, ForeignKey('PRODUCTS.ID'))
    OPTION_ID = Column(Integer, ForeignKey('PRODUCT_OPTIONS.ID'))
    CREATED_AT = Column(TIMESTAMP)
    UPDATED_AT = Column(TIMESTAMP)
    DELETED_AT = Column(TIMESTAMP)

    product = relationship("PRODUCTS")
    option = relationship("PRODUCT_OPTIONS")

class TRANSACTION_OPTION_SELECTIONS(Base):
    __tablename__ = 'TRANSACTION_OPTION_SELECTIONS'
    ID = Column(Integer, primary_key=True, index=True)
    TRANSACTION_ID = Column(Integer, ForeignKey('TRANSACTIONS.ID'))
    OPTION_ID = Column(Integer, ForeignKey('PRODUCT_OPTIONS.ID'))
    OPTION_VALUE_ID = Column(Integer, ForeignKey('PRODUCT_OPTION_VALUES.ID'))
    CREATED_AT = Column(TIMESTAMP)

    transaction = relationship("TRANSACTIONS")
    option = relationship("PRODUCT_OPTIONS")
    option_value = relationship("PRODUCT_OPTION_VALUES")