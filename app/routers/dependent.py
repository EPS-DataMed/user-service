from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import dependentModel, userModel
from app.schemas import dependentSchema
from app.database import get_db

router = APIRouter(
    prefix="/user/dependents",
    tags=["dependentes"]
)

@router.post("/", response_model=dependentSchema.Dependent)
def create_dependent(dependent: dependentSchema.DependentCreate, db: Session = Depends(get_db)):
    db_user = db.query(userModel.User).filter(userModel.User.id == dependent.user_id).first()
    db_dependent_user = db.query(userModel.User).filter(userModel.User.id == dependent.dependent_id).first()
    if not db_user or not db_dependent_user:
        raise HTTPException(status_code=400, detail="User or Dependent User not found")
    existing_dependent = db.query(dependentModel.Dependent).filter(
        dependentModel.Dependent.user_id == dependent.user_id,
        dependentModel.Dependent.dependent_id == dependent.dependent_id
    ).first()
    if existing_dependent:
        raise HTTPException(status_code=400, detail="Dependent already registered")
    db_dependent = dependentModel.Dependent(**dependent.model_dump())
    db.add(db_dependent)
    db.commit()
    db.refresh(db_dependent)
    return db_dependent

@router.get("/{user_id}/{dependent_id}", response_model=dependentSchema.Dependent)
def read_dependent(user_id: int, dependent_id: int, db: Session = Depends(get_db)):
    db_dependent = db.query(dependentModel.Dependent).filter(
        dependentModel.Dependent.user_id == user_id,
        dependentModel.Dependent.dependent_id == dependent_id
    ).first()
    if db_dependent is None:
        raise HTTPException(status_code=404, detail="Dependent not found")
    return db_dependent

@router.get("/", response_model=List[dependentSchema.Dependent])
def read_dependents(db: Session = Depends(get_db)):
    dependents = db.query(dependentModel.Dependent).all()
    return dependents

@router.put("/{user_id}/{dependent_id}", response_model=dependentSchema.Dependent)
def update_dependent(user_id: int, dependent_id: int, dependent: dependentSchema.DependentBase, db: Session = Depends(get_db)):
    db_dependent = db.query(dependentModel.Dependent).filter(
        dependentModel.Dependent.user_id == user_id,
        dependentModel.Dependent.dependent_id == dependent_id
    ).first()
    if db_dependent is None:
        raise HTTPException(status_code=404, detail="Dependent not found")
    for key, value in dependent.model_dump().items():
        setattr(db_dependent, key, value)
    db.commit()
    db.refresh(db_dependent)
    return db_dependent

@router.delete("/{user_id}/{dependent_id}")
def delete_dependent(user_id: int, dependent_id: int, db: Session = Depends(get_db)):
    db_dependent = db.query(dependentModel.Dependent).filter(
        dependentModel.Dependent.user_id == user_id,
        dependentModel.Dependent.dependent_id == dependent_id
    ).first()
    if db_dependent is None:
        raise HTTPException(status_code=404, detail="Dependent not found")
    db.delete(db_dependent)
    db.commit()
    return {"ok": True}
