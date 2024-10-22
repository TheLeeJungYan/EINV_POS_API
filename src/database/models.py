from sqlalchemy import Boolean,String,Integer,TIMESTAMP,Column
from src.database.main import Base

class COMPANIES(Base):
    __tablename__='COMPANIES'
    ID = Column(Integer,primary_key=True,index=True)
    NAME = Column(String(255),unique=True)
    USERNAME = Column(String(255))
    PASSWORD = Column(String(255))
    SUBSCRIPTION_ID = Column(Integer)
    SUBSCRIPTION_END_AT = Column(TIMESTAMP)
    LAST_LOGIN_IP = Column(String(255))
    LAST_LOGIN_AT = Column(TIMESTAMP)
    CREATED_AT = Column(TIMESTAMP)

class PRODUCTS(Base):
    __tablename__ = 'PRODUCTS'
    ID = Column(Integer,primary_key=True,index=True)
    COMPANY_ID = Column(Integer)
    NAME = Column(String(255))
    CATEGORY = Column(String(255))
    PRICE = Column(Integer)
    IMAGE = Column(String(255))
    CREATED_AT = Column(TIMESTAMP)
    UPDATED_AT = Column(TIMESTAMP)
    DELETED_AT = Column(TIMESTAMP)

class CATEGORIES(Base):
    __tablename__ = 'CATEGORIES'
    ID = Column(Integer,primary_key=True,index=True)
    NAME = Column(String(255))
    ICON = Column(String(255))
    CREATED_AT = Column(TIMESTAMP)
    UPDATED_AT = Column(TIMESTAMP)
    DELETED_AT = Column(TIMESTAMP)



class TRANSACTIONS(Base):
    __tablename__ = 'TRANSACTIONS'
    ID = Column(Integer,primary_key=True,index=True)
    COMPANY_ID = Column(Integer)
    PRODUCT_ID = Column(Integer)
    AMOUNT = Column(Integer)
    CREATED_AT = Column(TIMESTAMP)
