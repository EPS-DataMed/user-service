from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from .services.usuario import get_usuario_by_email

def get_current_usuario(email: str, db: Session = Depends(get_db)):
    usuario = get_usuario_by_email(db, email=email)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario
