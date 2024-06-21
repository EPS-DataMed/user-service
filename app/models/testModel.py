from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Test(Base):
    __tablename__ = "Tests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("Users.id"), nullable=False)
    test_name = Column(String(255), nullable=False)
    url = Column(String(400), nullable=False)
    test_date = Column(TIMESTAMP)
    submission_date = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")

    user = relationship("User", back_populates="tests")
    derived_health_data = relationship("DerivedHealthData", back_populates="test")
