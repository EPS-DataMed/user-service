from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas import MedicoCreate
from ..services import medico as medico_service
from ..database import get_db

router = APIRouter()

@router.post("/medicos/", response_model=MedicoCreate)
def create_medico(medico: MedicoCreate, db: Session = Depends(get_db)):
    db_medico = medico_service.get_medico_by_email(db, email=medico.email)
    if db_medico:
        raise HTTPException(status_code=400, detail="Email já registrado")
    return medico_service.create_medico(db=db, medico=medico)

@router.get("/medicos/{id_usuario}", response_model=MedicoCreate)
def read_medico(id_usuario: int, db: Session = Depends(get_db)):
    db_medico = medico_service.get_medico_by_id(db, id_usuario=id_usuario)
    if db_medico is None:
        raise HTTPException(status_code=404, detail="Medico não encontrado")
    return db_medico

@router.put("/medicos/{id_usuario}", response_model=MedicoCreate)
def update_medico(id_usuario: int, medico: MedicoCreate, db: Session = Depends(get_db)):
    db_medico = medico_service.update_medico(db, id_usuario=id_usuario, medico=medico)
    if db_medico is None:
        raise HTTPException(status_code=404, detail="Medico não encontrado")
    return db_medico

@router.delete("/medicos/{id_usuario}", response_model=MedicoCreate)
def delete_medico(id_usuario: int, db: Session = Depends(get_db)):
    db_medico = medico_service.delete_medico(db, id_usuario=id_usuario)
    if db_medico is None:
        raise HTTPException(status_code=404, detail="Medico não encontrado")
    return db_medico
