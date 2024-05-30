from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, crud, models
from ..database import get_db

router = APIRouter()

@router.post("/pacientes/", response_model=schemas.PacienteCreate)
def create_paciente(paciente: schemas.PacienteCreate, db: Session = Depends(get_db)):
    db_paciente = crud.get_paciente_by_email(db, email=paciente.email)
    if db_paciente:
        raise HTTPException(status_code=400, detail="Email já registrado")
    if paciente.status_formulario not in [status.value for status in models.paciente.StatusEnum]:
        raise HTTPException(status_code=400, detail="Status do formulário inválido")
    
    return crud.create_paciente(db=db, paciente=paciente)
