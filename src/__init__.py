from fastapi import FastAPI,Depends
from src.database.main import engine,get_db
import src.database.models as models
from typing import Annotated
from fastapi.middleware.cors import CORSMiddleware
from src.products.routes import product_router
models.Base.metadata.create_all(bind=engine)
version = "v1"
app = FastAPI(
    title="Books Api",
    description="A REST API for books",
    version=version
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
get_db()

app.include_router(product_router,prefix="/api/{version}",tags=['products'])