from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Dependent(Base):
    __tablename__ = "Dependents"

    user_id = Column(Integer, ForeignKey("Users.id"), primary_key=True)
    dependent_id = Column(Integer, ForeignKey("Users.id"), primary_key=True)
    confirmed = Column(Boolean, default=False)

    user = relationship("User", foreign_keys=[user_id], back_populates="dependents")
    dependent_user = relationship("User", foreign_keys=[dependent_id])
