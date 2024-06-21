from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import dependentModel, userModel, formModel
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
    db_dependent = dependentModel.Dependent(**dependent.dict())
    db.add(db_dependent)
    db.commit()
    db.refresh(db_dependent)
    return db_dependent

@router.get("/{user_id}/{dependent_id}", response_model=dependentSchema.Dependent)
def read_dependent(user_id: int, dependent_id: int, db: Session = Depends(get_db)):
    db_dependent = db.query(
        dependentModel.Dependent,
        userModel.User.full_name.label("user_full_name"),
        userModel.User.birth_date.label("user_birth_date"),
        userModel.User.email.label("user_email"),
        formModel.Form.form_status.label("form_status")
    ).join(
        userModel.User, userModel.User.id == dependentModel.Dependent.dependent_id
    ).outerjoin(
        formModel.Form, formModel.Form.user_id == dependentModel.Dependent.dependent_id
    ).filter(
        dependentModel.Dependent.user_id == user_id,
        dependentModel.Dependent.dependent_id == dependent_id
    ).first()

    if db_dependent is None:
        raise HTTPException(status_code=404, detail="Dependent not found")

    dependent, full_name, birth_date, email, form_status = db_dependent
    dependent_data = dependent.__dict__
    dependent_data.update({
        "user_full_name": full_name,
        "user_birth_date": birth_date.isoformat() if birth_date else None,
        "user_email": email,
        "form_status": form_status
    })

    return dependentSchema.Dependent(**dependent_data)


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
    for key, value in dependent.dict().items():
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

@router.get("/{user_id}", response_model=List[dependentSchema.Dependent])
def read_user_dependents(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(userModel.User).filter(userModel.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    dependents = db.query(
        dependentModel.Dependent,
        userModel.User.full_name.label("user_full_name"),
        userModel.User.birth_date.label("user_birth_date"),
        userModel.User.email.label("user_email"),
        formModel.Form.form_status.label("form_status")
    ).join(
        userModel.User, userModel.User.id == dependentModel.Dependent.dependent_id
    ).outerjoin(
        formModel.Form, formModel.Form.user_id == dependentModel.Dependent.dependent_id
    ).filter(
        dependentModel.Dependent.user_id == user_id
    ).all()

    results = []
    for dep, full_name, birth_date, email, form_status in dependents:
        dep_data = dep.__dict__
        dep_data.update({
            "user_full_name": full_name,
            "user_birth_date": birth_date.isoformat() if birth_date else None,
            "user_email": email,
            "form_status": form_status
        })
        results.append(dep_data)
    
    return results
