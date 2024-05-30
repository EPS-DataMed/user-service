from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas import UsuarioCreate
from ..services import usuario as usuario_service
from ..database import get_db

router = APIRouter()

@router.post("/", response_model=UsuarioCreate)
def create_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = usuario_service.get_usuario_by_email(db, email=usuario.email)
    if db_usuario:
        raise HTTPException(status_code=400, detail="Email já registrado")
    return usuario_service.create_usuario(db=db, usuario=usuario)

@router.get("/{id}", response_model=UsuarioCreate)
def read_usuario(id: int, db: Session = Depends(get_db)):
    db_usuario = usuario_service.get_usuario_by_id(db, id=id)
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return db_usuario

@router.put("/{id}", response_model=UsuarioCreate)
def update_usuario(id: int, usuario: UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = usuario_service.update_usuario(db, id=id, usuario=usuario)
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return db_usuario

@router.delete("/{id}", response_model=UsuarioCreate)
def delete_usuario(id: int, db: Session = Depends(get_db)):
    db_usuario = usuario_service.delete_usuario(db, id=id)
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return db_usuario
