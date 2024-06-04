from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import dependentModel, userModel
from ..schemas import dependentSchema
from ..database import get_db

router = APIRouter(
    prefix="/user/dependents",
    tags=["dependentes"]
)

@router.post("/", response_model=dependentSchema.Dependente)
def create_dependente(dependente: dependentSchema.DependenteCreate, db: Session = Depends(get_db)):
    db_usuario = db.query(userModel.Usuario).filter(userModel.Usuario.id == dependente.id_usuario).first()
    db_dependente_usuario = db.query(userModel.Usuario).filter(userModel.Usuario.id == dependente.id_dependente).first()
    if not db_usuario or not db_dependente_usuario:
        raise HTTPException(status_code=400, detail="Usuario or Dependente Usuario not found")
    existing_dependente = db.query(dependentModel.Dependente).filter(
        dependentModel.Dependente.id_usuario == dependente.id_usuario,
        dependentModel.Dependente.id_dependente == dependente.id_dependente
    ).first()
    if existing_dependente:
        raise HTTPException(status_code=400, detail="Dependente already registered")
    db_dependente = dependentModel.Dependente(**dependente.dict())
    db.add(db_dependente)
    db.commit()
    db.refresh(db_dependente)
    return db_dependente

@router.get("/{id_usuario}/{id_dependente}", response_model=dependentSchema.Dependente)
def read_dependente(id_usuario: int, id_dependente: int, db: Session = Depends(get_db)):
    db_dependente = db.query(dependentModel.Dependente).filter(
        dependentModel.Dependente.id_usuario == id_usuario,
        dependentModel.Dependente.id_dependente == id_dependente
    ).first()
    if db_dependente is None:
        raise HTTPException(status_code=404, detail="Dependente not found")
    return db_dependente

@router.get("/", response_model=List[dependentSchema.Dependente])
def read_dependentes(db: Session = Depends(get_db)):
    dependentes = db.query(dependentModel.Dependente).all()
    return dependentes

@router.put("/{id_usuario}/{id_dependente}", response_model=dependentSchema.Dependente)
def update_dependente(id_usuario: int, id_dependente: int, dependente: dependentSchema.DependenteBase, db: Session = Depends(get_db)):
    db_dependente = db.query(dependentModel.Dependente).filter(
        dependentModel.Dependente.id_usuario == id_usuario,
        dependentModel.Dependente.id_dependente == id_dependente
    ).first()
    if db_dependente is None:
        raise HTTPException(status_code=404, detail="Dependente not found")
    for key, value in dependente.dict().items():
        setattr(db_dependente, key, value)
    db.commit()
    db.refresh(db_dependente)
    return db_dependente

@router.delete("/{id_usuario}/{id_dependente}")
def delete_dependente(id_usuario: int, id_dependente: int, db: Session = Depends(get_db)):
    db_dependente = db.query(dependentModel.Dependente).filter(
        dependentModel.Dependente.id_usuario == id_usuario,
        dependentModel.Dependente.id_dependente == id_dependente
    ).first()
    if db_dependente is None:
        raise HTTPException(status_code=404, detail="Dependente not found")
    db.delete(db_dependente)
    db.commit()
    return {"ok": True}
