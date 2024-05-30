from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas import PacienteCreate
from ..services import paciente as paciente_service
from ..models.paciente import StatusEnum
from ..database import get_db

router = APIRouter()

@router.post("/pacientes/", response_model=PacienteCreate)
def create_paciente(paciente: PacienteCreate, db: Session = Depends(get_db)):
    db_paciente = paciente_service.get_paciente_by_email(db, email=paciente.email)
    if db_paciente:
        raise HTTPException(status_code=400, detail="Email já registrado")
    if paciente.status_formulario not in [status.value for status in StatusEnum]:
        raise HTTPException(status_code=400, detail="Status do formulário inválido")
    
    return paciente_service.create_paciente(db=db, paciente=paciente)

@router.get("/pacientes/{id_usuario}", response_model=PacienteCreate)
def read_paciente(id_usuario: int, db: Session = Depends(get_db)):
    db_paciente = paciente_service.get_paciente_by_id(db, id_usuario=id_usuario)
    if db_paciente is None:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return db_paciente

@router.put("/pacientes/{id_usuario}", response_model=PacienteCreate)
def update_paciente(id_usuario: int, paciente: PacienteCreate, db: Session = Depends(get_db)):
    db_paciente = paciente_service.update_paciente(db, id_usuario=id_usuario, paciente=paciente)
    if db_paciente is None:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return db_paciente

@router.delete("/pacientes/{id_usuario}", response_model=PacienteCreate)
def delete_paciente(id_usuario: int, db: Session = Depends(get_db)):
    db_paciente = paciente_service.delete_paciente(db, id_usuario=id_usuario)
    if db_paciente is None:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return db_paciente
