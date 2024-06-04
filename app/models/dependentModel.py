from sqlalchemy import Column, Integer, ForeignKey, Boolean
from ..database import Base

class Dependente(Base):
    __tablename__ = "dependentes"

    id_usuario = Column(Integer, ForeignKey("usuarios.id"), primary_key=True)
    id_dependente = Column(Integer, ForeignKey("usuarios.id"), primary_key=True)
    confirmado = Column(Boolean, default=False)