from sqlalchemy import Boolean, String, Integer, TIMESTAMP, Column, ForeignKey, JSON, Table
from sqlalchemy.orm import relationship
from src.database.main import Base

# Association table for PRODUCTS and PRODUCT_OPTIONS
product_options_association = Table('product_options_association', Base.metadata,
    Column('product_id', Integer, ForeignKey('PRODUCTS.ID')),
    Column('option_id', Integer, ForeignKey('PRODUCT_OPTIONS.ID'))
)

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

    products = relationship("PRODUCTS", back_populates="company")

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

    company = relationship("COMPANIES", back_populates="products")
    options = relationship("PRODUCT_OPTIONS", secondary=product_options_association, back_populates="products")
    transactions = relationship("TRANSACTIONS", back_populates="product")

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

    company = relationship("COMPANIES")
    product = relationship("PRODUCTS", back_populates="transactions")

class PRODUCT_OPTIONS(Base):
    __tablename__ = 'PRODUCT_OPTIONS'
    ID = Column(Integer, primary_key=True, index=True)
    NAME = Column(String(255), nullable=False)
    CREATED_AT = Column(TIMESTAMP)
    UPDATED_AT = Column(TIMESTAMP)
    DELETED_AT = Column(TIMESTAMP)

    products = relationship("PRODUCTS", secondary=product_options_association, back_populates="options")
    option_values = relationship("PRODUCT_OPTION_VALUES", back_populates="option")

class PRODUCT_OPTION_VALUES(Base):
    __tablename__ = 'PRODUCT_OPTION_VALUES'
    ID = Column(Integer, primary_key=True, index=True)
    OPTION_ID = Column(Integer, ForeignKey('PRODUCT_OPTIONS.ID'))
    VALUE = Column(String(255), nullable=False)
    CREATED_AT = Column(TIMESTAMP)
    UPDATED_AT = Column(TIMESTAMP)
    DELETED_AT = Column(TIMESTAMP)

    option = relationship("PRODUCT_OPTIONS", back_populates="option_values")