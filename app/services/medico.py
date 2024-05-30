from sqlalchemy.orm import Session
from ..models.medico import Medico
from ..schemas import MedicoCreate

def get_medico_by_id(db: Session, id_usuario: int):
    return db.query(Medico).filter(Medico.id_usuario == id_usuario).first()

def create_medico(db: Session, medico: MedicoCreate):
    db_medico = Medico(**medico.dict())
    db.add(db_medico)
    db.commit()
    db.refresh(db_medico)
    return db_medico

def update_medico(db: Session, id_usuario: int, medico: MedicoCreate):
    db_medico = get_medico_by_id(db, id_usuario)
    if not db_medico:
        return None
    for key, value in medico.dict().items():
        setattr(db_medico, key, value)
    db.commit()
    db.refresh(db_medico)
    return db_medico

def delete_medico(db: Session, id_usuario: int):
    db_medico = get_medico_by_id(db, id_usuario)
    if not db_medico:
        return None
    db.delete(db_medico)
    db.commit()
    return db_medico
