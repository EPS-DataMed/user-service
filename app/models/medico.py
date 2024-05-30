from sqlalchemy import Column, Integer, String, Date
from .base import Base

class Medico(Base):
    __tablename__ = "medicos"
    id_usuario = Column(Integer, primary_key=True, index=True)
    crm = Column(String, unique=True, nullable=False)
    especialidade = Column(String, nullable=False)
    email = Column(String, nullable=False)
    senha = Column(String, nullable=False)
    nome = Column(String, nullable=False)
    dt_nascimento = Column(Date, nullable=False)
    criado_em = Column(Date, nullable=False)
