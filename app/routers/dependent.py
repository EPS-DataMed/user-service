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

    db_user = db.query(userModel.User).filter(userModel.User.id == db_dependent.dependent_id).first()
    form_status = db.query(formModel.Form.form_status).filter(formModel.Form.user_id == db_dependent.dependent_id).first()
    
    return dependentSchema.Dependent(
        user_id=db_dependent.user_id,
        dependent_id=db_dependent.dependent_id,
        confirmed=db_dependent.confirmed,
        user_full_name=db_user.full_name if db_user else None,
        user_birth_date=db_user.birth_date.isoformat() if db_user and db_user.birth_date else None,
        user_email=db_user.email if db_user else None,
        form_status=form_status[0] if form_status else None
    )

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
        dependentModel.Dependent.user_id == user_id,
        dependentModel.Dependent.confirmed == True
    ).all()

    if not dependents:
        raise HTTPException(status_code=404, detail="No confirmed dependents found")

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

@router.post("/confirm")
def confirm_dependent(body: dependentSchema.ConfirmDependentBody, db: Session = Depends(get_db)):
    db_user = db.query(userModel.User).filter(userModel.User.email == body.email).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User with the specified email not found")
    
    # Lógica de envio de e-mail será implementada aqui futuramente
    # Por enquanto, vamos apenas retornar uma mensagem de confirmação
    return {"message": "Email verification sent successfully"}
