from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, crud
from ..database import get_db

router = APIRouter()

@router.post("/medicos/", response_model=schemas.MedicoCreate)
def create_medico(medico: schemas.MedicoCreate, db: Session = Depends(get_db)):
    db_medico = crud.get_paciente_by_email(db, email=medico.email)
    if db_medico:
        raise HTTPException(status_code=400, detail="Email já registrado")
    return crud.create_medico(db=db, medico=medico)
