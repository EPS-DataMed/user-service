from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from . import models, schemas, database
import bcrypt
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=database.engine)

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

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

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

@app.get("/")
def read_root():
    return {"message": "Welcome to the Usuarios API"}

# Usuários
@app.post("/usuarios", response_model=schemas.Usuario)
def create_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = hash_password(usuario.senha)
    db_usuario = models.Usuario(
        nome_completo=usuario.nome_completo,
        email=usuario.email,
        senha=hashed_password,
        data_nascimento=usuario.data_nascimento,
        sexo_biologico=usuario.sexo_biologico,
        formulario=usuario.formulario,
        status_formulario=usuario.status_formulario
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

@app.get("/usuarios/{usuario_id}", response_model=schemas.Usuario)
def read_usuario(usuario_id: int, db: Session = Depends(get_db)):
    db_usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario not found")
    return db_usuario

@app.get("/usuarios", response_model=List[schemas.Usuario])
def read_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(models.Usuario).all()
    return usuarios

@app.put("/usuarios/{usuario_id}", response_model=schemas.Usuario)
def update_usuario(usuario_id: int, usuario: schemas.UsuarioUpdate, db: Session = Depends(get_db)):
    db_usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario not found")
    for key, value in usuario.dict().items():
        setattr(db_usuario, key, value)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

@app.delete("/usuarios/{usuario_id}")
def delete_usuario(usuario_id: int, db: Session = Depends(get_db)):
    db_usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario not found")
    db.delete(db_usuario)
    db.commit()
    return {"ok": True}

# Médicos
@app.post("/medicos", response_model=schemas.Medico)
def create_medico(medico: schemas.MedicoCreate, db: Session = Depends(get_db)):
    db_usuario = db.query(models.Usuario).filter(models.Usuario.id == medico.id_usuario).first()
    if not db_usuario:
        raise HTTPException(status_code=400, detail="Associated usuario not found")
    existing_medico = db.query(models.Medico).filter(models.Medico.id_usuario == medico.id_usuario).first()
    if existing_medico:
        raise HTTPException(status_code=400, detail="Medico already registered")
    db_medico = models.Medico(**medico.dict())
    db.add(db_medico)
    db.commit()
    db.refresh(db_medico)
    return db_medico

@app.get("/medicos/{medico_id}", response_model=schemas.Medico)
def read_medico(medico_id: int, db: Session = Depends(get_db)):
    db_medico = db.query(models.Medico).filter(models.Medico.id_usuario == medico_id).first()
    if db_medico is None:
        raise HTTPException(status_code=404, detail="Medico not found")
    return db_medico

@app.get("/medicos", response_model=List[schemas.Medico])
def read_medicos(db: Session = Depends(get_db)):
    medicos = db.query(models.Medico).all()
    return medicos

@app.put("/medicos/{medico_id}", response_model=schemas.Medico)
def update_medico(medico_id: int, medico: schemas.MedicoBase, db: Session = Depends(get_db)):
    db_medico = db.query(models.Medico).filter(models.Medico.id_usuario == medico_id).first()
    if db_medico is None:
        raise HTTPException(status_code=404, detail="Medico not found")
    for key, value in medico.dict().items():
        setattr(db_medico, key, value)
    db.commit()
    db.refresh(db_medico)
    return db_medico

@app.delete("/medicos/{medico_id}")
def delete_medico(medico_id: int, db: Session = Depends(get_db)):
    db_medico = db.query(models.Medico).filter(models.Medico.id_usuario == medico_id).first()
    if db_medico is None:
        raise HTTPException(status_code=404, detail="Medico not found")
    db.delete(db_medico)
    db.commit()
    return {"ok": True}

# Dependentes
@app.post("/dependentes", response_model=schemas.Dependente)
def create_dependente(dependente: schemas.DependenteCreate, db: Session = Depends(get_db)):
    db_usuario = db.query(models.Usuario).filter(models.Usuario.id == dependente.id_usuario).first()
    db_dependente_usuario = db.query(models.Usuario).filter(models.Usuario.id == dependente.id_dependente).first()
    if not db_usuario or not db_dependente_usuario:
        raise HTTPException(status_code=400, detail="Usuario or Dependente Usuario not found")
    existing_dependente = db.query(models.Dependente).filter(
        models.Dependente.id_usuario == dependente.id_usuario,
        models.Dependente.id_dependente == dependente.id_dependente
    ).first()
    if existing_dependente:
        raise HTTPException(status_code=400, detail="Dependente already registered")
    db_dependente = models.Dependente(**dependente.dict())
    db.add(db_dependente)
    db.commit()
    db.refresh(db_dependente)
    return db_dependente

@app.get("/dependentes/{id_usuario}/{id_dependente}", response_model=schemas.Dependente)
def read_dependente(id_usuario: int, id_dependente: int, db: Session = Depends(get_db)):
    db_dependente = db.query(models.Dependente).filter(
        models.Dependente.id_usuario == id_usuario,
        models.Dependente.id_dependente == id_dependente
    ).first()
    if db_dependente is None:
        raise HTTPException(status_code=404, detail="Dependente not found")
    return db_dependente

@app.get("/dependentes", response_model=List[schemas.Dependente])
def read_dependentes(db: Session = Depends(get_db)):
    dependentes = db.query(models.Dependente).all()
    return dependentes

@app.put("/dependentes/{id_usuario}/{id_dependente}", response_model=schemas.Dependente)
def update_dependente(id_usuario: int, id_dependente: int, dependente: schemas.DependenteBase, db: Session = Depends(get_db)):
    db_dependente = db.query(models.Dependente).filter(
        models.Dependente.id_usuario == id_usuario,
        models.Dependente.id_dependente == id_dependente
    ).first()
    if db_dependente is None:
        raise HTTPException(status_code=404, detail="Dependente not found")
    for key, value in dependente.dict().items():
        setattr(db_dependente, key, value)
    db.commit()
    db.refresh(db_dependente)
    return db_dependente

@app.delete("/dependentes/{id_usuario}/{id_dependente}")
def delete_dependente(id_usuario: int, id_dependente: int, db: Session = Depends(get_db)):
    db_dependente = db.query(models.Dependente).filter(
        models.Dependente.id_usuario == id_usuario,
        models.Dependente.id_dependente == id_dependente
    ).first()
    if db_dependente is None:
        raise HTTPException(status_code=404, detail="Dependente not found")
    db.delete(db_dependente)
    db.commit()
    return {"ok": True}
