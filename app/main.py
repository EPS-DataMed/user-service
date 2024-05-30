from fastapi import FastAPI
from .database import engine
from .models.base import Base
from .routers import usuarios, medicos

# Cria todas as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Inclui os roteadores de usuários e médicos
app.include_router(usuarios.router, prefix="/usuarios", tags=["usuarios"])
app.include_router(medicos.router, prefix="/medicos", tags=["medicos"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}
