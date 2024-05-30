from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from .services.paciente import get_paciente_by_email

def get_current_paciente(email: str, db: Session = Depends(get_db)):
    paciente = get_paciente_by_email(db, email=email)
    if paciente is None:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return paciente
