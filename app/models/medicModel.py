from sqlalchemy import Column, Integer, String, ForeignKey
from ..database import Base

class Medico(Base):
    __tablename__ = "medicos"

    id_usuario = Column(Integer, ForeignKey("usuarios.id"), primary_key=True)
    crm = Column(String(50), nullable=False)
    especialidade = Column(String(255), nullable=False)