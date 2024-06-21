from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class DerivedHealthData(Base):
    __tablename__ = "DerivedHealthData"

    id = Column(Integer, primary_key=True, index=True)
    form_id = Column(Integer, ForeignKey("Forms.id"), nullable=False)
    test_id = Column(Integer, ForeignKey("Tests.id"), nullable=False)
    name = Column(String(255), nullable=False)
    value = Column(String(255), nullable=False)

    form = relationship("Form", back_populates="derived_health_data")
    test = relationship("Test", back_populates="derived_health_data")
