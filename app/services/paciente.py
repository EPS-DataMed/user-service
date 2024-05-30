from sqlalchemy.orm import Session
from ..models.paciente import Paciente
from ..schemas import PacienteCreate

def get_paciente_by_id(db: Session, id_usuario: int):
    return db.query(Paciente).filter(Paciente.id_usuario == id_usuario).first()

def get_paciente_by_email(db: Session, email: str):
    return db.query(Paciente).filter(Paciente.email == email).first()

def create_paciente(db: Session, paciente: PacienteCreate):
    db_paciente = Paciente(**paciente.dict())
    db.add(db_paciente)
    db.commit()
    db.refresh(db_paciente)
    return db_paciente

def update_paciente(db: Session, id_usuario: int, paciente: PacienteCreate):
    db_paciente = get_paciente_by_id(db, id_usuario)
    if not db_paciente:
        return None
    for key, value in paciente.dict().items():
        setattr(db_paciente, key, value)
    db.commit()
    db.refresh(db_paciente)
    return db_paciente

def delete_paciente(db: Session, id_usuario: int):
    db_paciente = get_paciente_by_id(db, id_usuario)
    if not db_paciente:
        return None
    db.delete(db_paciente)
    db.commit()
    return db_paciente
