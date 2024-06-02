from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/medicos",
    tags=["medicos"]
)

@router.post("/", response_model=schemas.Medico)
def create_medico(medico: schemas.MedicoCreate, db: Session = Depends(get_db)):
    db_usuario = db.query(models.Usuario).filter(models.Usuario.id == medico.id_usuario).first()
    if not db_usuario:
        raise HTTPException(status_code=400, detail="Associated usuario not found")
    existing_medico = db.query(models.Medico).filter(models.Medico.id_usuario == medico.id_usuario).first()
    if existing_medico:
        raise HTTPException(status_code=400, detail="Medico already registered")
    db_medico = models.Medico(**medico.dict())
    db.add(db_medico)
    db.commit()
    db.refresh(db_medico)
    return db_medico

@router.get("/{medico_id}", response_model=schemas.Medico)
def read_medico(medico_id: int, db: Session = Depends(get_db)):
    db_medico = db.query(models.Medico).filter(models.Medico.id_usuario == medico_id).first()
    if db_medico is None:
        raise HTTPException(status_code=404, detail="Medico not found")
    return db_medico

@router.get("/", response_model=List[schemas.Medico])
def read_medicos(db: Session = Depends(get_db)):
    medicos = db.query(models.Medico).all()
    return medicos

@router.put("/{medico_id}", response_model=schemas.Medico)
def update_medico(medico_id: int, medico: schemas.MedicoBase, db: Session = Depends(get_db)):
    db_medico = db.query(models.Medico).filter(models.Medico.id_usuario == medico_id).first()
    if db_medico is None:
        raise HTTPException(status_code=404, detail="Medico not found")
    for key, value in medico.dict().items():
        setattr(db_medico, key, value)
    db.commit()
    db.refresh(db_medico)
    return db_medico

@router.delete("/{medico_id}")
def delete_medico(medico_id: int, db: Session = Depends(get_db)):
    db_medico = db.query(models.Medico).filter(models.Medico.id_usuario == medico_id).first()
    if db_medico is None:
        raise HTTPException(status_code=404, detail="Medico not found")
    db.delete(db_medico)
    db.commit()
    return {"ok": True}