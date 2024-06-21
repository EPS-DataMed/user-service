from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models.userModel import User
from app.models.doctorModel import Doctor
from app.models.dependentModel import Dependent
from app.models.testModel import Test
from app.models.derivedHealthDataModel import DerivedHealthData
from app.models.formModel import Form
from app.schemas.userSchema import User as UserSchema, UserWithDoctor as UserWithDoctorSchema
from app.database import get_db
from app import utils

router = APIRouter(
    prefix="/user/users",
    tags=["usuarios"]
)

class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str

@router.get("/{user_id}", response_model=UserSchema)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/", response_model=List[UserSchema])
def read_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@router.patch("/{user_id}/password", response_model=UserSchema)
def update_user_password(user_id: int, password_update: PasswordUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    decrypted_password = utils.decrypt_password(db_user.password)
    if not utils.verify_password(password_update.old_password, decrypted_password):
        raise HTTPException(status_code=400, detail="Old password does not match")
    
    encrypted_password = utils.encrypt_password(password_update.new_password)
    db_user.password = encrypted_password
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_doctor = db.query(Doctor).filter(Doctor.user_id == user_id).first()
    if db_doctor:
        db.delete(db_doctor)
    
    db_dependents = db.query(Dependent).filter((Dependent.user_id == user_id) | (Dependent.dependent_id == user_id)).all()
    for db_dependent in db_dependents:
        db.delete(db_dependent)

    db_tests = db.query(Test).filter(Test.user_id == user_id).all()
    for db_test in db_tests:
        db_derived_health_data = db.query(DerivedHealthData).filter(DerivedHealthData.test_id == db_test.id).all()
        for db_data in db_derived_health_data:
            db.delete(db_data)
        db.delete(db_test)

    db_forms = db.query(Form).filter(Form.user_id == user_id).all()
    for db_form in db_forms:
        db_derived_health_data = db.query(DerivedHealthData).filter(DerivedHealthData.form_id == db_form.id).all()
        for db_data in db_derived_health_data:
            db.delete(db_data)
        db.delete(db_form)

    db.delete(db_user)
    db.commit()
    return {"ok": True}

@router.get("/with-doctor/{user_id}", response_model=UserWithDoctorSchema)
def get_user_with_doctor(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_doctor = db.query(Doctor).filter(Doctor.user_id == user_id).first()
    user_data = db_user.__dict__
    if db_doctor:
        user_data["doctor"] = db_doctor

    return user_data
