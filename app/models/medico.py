from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Medico(Base):
    __tablename__ = "medicos"
    id_usuario = Column(Integer, ForeignKey('usuarios.id'), primary_key=True, index=True)
    crm = Column(String, nullable=False)
    especialidade = Column(String, nullable=False)

    usuario = relationship("Usuario", back_populates="medico")
