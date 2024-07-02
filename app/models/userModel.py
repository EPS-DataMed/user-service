from sqlalchemy import Column, Integer, String, Date, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(2048), nullable=False)
    birth_date = Column(Date, nullable=False)
    biological_sex = Column(String(1), nullable=False)
    creation_date = Column(TIMESTAMP, server_default=func.now())

    doctors = relationship("Doctor", back_populates="user")
    dependents = relationship("Dependent", foreign_keys="[Dependent.user_id]")
    tests = relationship("Test", back_populates="user")
    forms = relationship("Form", back_populates="user")
