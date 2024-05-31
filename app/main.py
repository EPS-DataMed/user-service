from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
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

@app.post("/usuarios", response_model=schemas.Usuario)
def create_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
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

@app.post("/medicos", response_model=schemas.Medico)
def create_medico(medico: schemas.MedicoCreate, db: Session = Depends(get_db)):
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

@app.get("/")
def read_root():
    return {"message": "Welcome to the Usuarios API"}
