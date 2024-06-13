from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import doctorModel, userModel
from app.schemas import doctorSchema
from app.database import get_db

router = APIRouter(
    prefix="/user/doctors",
    tags=["medicos"]
)

@router.post("/", response_model=doctorSchema.Doctor)
def create_doctor(doctor: doctorSchema.DoctorCreate, db: Session = Depends(get_db)):
    db_user = db.query(userModel.User).filter(userModel.User.id == doctor.user_id).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Associated user not found")
    existing_doctor = db.query(doctorModel.Doctor).filter(doctorModel.Doctor.user_id == doctor.user_id).first()
    if existing_doctor:
        raise HTTPException(status_code=400, detail="Doctor already registered")
    db_doctor = doctorModel.Doctor(**doctor.model_dump())
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor

@router.get("/{doctor_id}", response_model=doctorSchema.Doctor)
def read_doctor(doctor_id: int, db: Session = Depends(get_db)):
    db_doctor = db.query(doctorModel.Doctor).filter(doctorModel.Doctor.user_id == doctor_id).first()
    if db_doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return db_doctor

@router.get("/", response_model=List[doctorSchema.Doctor])
def read_doctors(db: Session = Depends(get_db)):
    doctors = db.query(doctorModel.Doctor).all()
    return doctors

@router.put("/{doctor_id}", response_model=doctorSchema.Doctor)
def update_doctor(doctor_id: int, doctor: doctorSchema.DoctorBase, db: Session = Depends(get_db)):
    db_doctor = db.query(doctorModel.Doctor).filter(doctorModel.Doctor.user_id == doctor_id).first()
    if db_doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    for key, value in doctor.model_dump().items():
        setattr(db_doctor, key, value)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor

@router.delete("/{doctor_id}")
def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    db_doctor = db.query(doctorModel.Doctor).filter(doctorModel.Doctor.user_id == doctor_id).first()
    if db_doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    db.delete(db_doctor)
    db.commit()
    return {"ok": True}
