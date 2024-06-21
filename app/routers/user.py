from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.userModel import User
from app.models.doctorModel import Doctor
from app.schemas.userSchema import UserUpdate, User as UserSchema, UserWithDoctor as UserWithDoctorSchema
from app.database import get_db
from app import utils

router = APIRouter(
    prefix="/user/users",
    tags=["usuarios"]
)

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
def update_user_password(user_id: int, old_password: str, new_password: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    decrypted_password = utils.decrypt_password(db_user.password)
    if not utils.verify_password(old_password, decrypted_password):
        raise HTTPException(status_code=400, detail="Old password does not match")
    
    encrypted_password = utils.encrypt_password(new_password)
    db_user.password = encrypted_password
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
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
