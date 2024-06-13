from sqlalchemy import Column, Integer, ForeignKey, Boolean
from app.database import Base

class Dependent(Base):
    __tablename__ = "dependents"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    dependent_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    confirmed = Column(Boolean, default=False)
