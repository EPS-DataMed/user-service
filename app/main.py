from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from . import database
from .database import Base
from fastapi.middleware.cors import CORSMiddleware
from .routers import user, medic, dependent

Base.metadata.create_all(bind=database.engine)

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas de serviço
app.include_router(user.router)
app.include_router(medic.router)
app.include_router(dependent.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Usuarios API"}


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred."}
    )

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=400,
        content={"message": "Integrity error occurred, likely due to duplicate entries or constraint violations."}
    )