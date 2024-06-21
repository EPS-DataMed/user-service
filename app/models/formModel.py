from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Form(Base):
    __tablename__ = "Forms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("Users.id"), nullable=False)
    weight = Column(String(255))
    height = Column(String(255))
    bmi = Column(String(255))
    blood_type = Column(String(255))
    abdominal_circumference = Column(String(255))
    allergies = Column(String(255))
    diseases = Column(String(255))
    medications = Column(String(255))
    family_history = Column(String(255))
    important_notes = Column(String(255))
    images_reports = Column(String(255))
    form_status = Column(String(20), nullable=False, default="Not started")
    latest_red_blood_cell = Column(String(255))
    latest_hemoglobin = Column(String(255))
    latest_hematocrit = Column(String(255))
    latest_glycated_hemoglobin = Column(String(255))
    latest_ast = Column(String(255))
    latest_alt = Column(String(255))
    latest_urea = Column(String(255))
    latest_creatinine = Column(String(255))

    user = relationship("User", back_populates="forms")
    derived_health_data = relationship("DerivedHealthData", back_populates="form")
