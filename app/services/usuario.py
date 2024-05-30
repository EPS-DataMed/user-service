from sqlalchemy.orm import Session
from ..models.usuario import Usuario
from ..schemas import UsuarioCreate

def get_usuario_by_id(db: Session, id: int):
    return db.query(Usuario).filter(Usuario.id == id).first()

def get_usuario_by_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.email == email).first()

def create_usuario(db: Session, usuario: UsuarioCreate):
    db_usuario = Usuario(**usuario.dict())
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def update_usuario(db: Session, id: int, usuario: UsuarioCreate):
    db_usuario = get_usuario_by_id(db, id)
    if not db_usuario:
        return None
    for key, value in usuario.dict().items():
        setattr(db_usuario, key, value)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def delete_usuario(db: Session, id: int):
    db_usuario = get_usuario_by_id(db, id)
    if not db_usuario:
        return None
    db.delete(db_usuario)
    db.commit()
    return db_usuario
