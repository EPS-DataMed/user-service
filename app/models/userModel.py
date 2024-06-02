from sqlalchemy import Column, Integer, String, Date, DateTime, JSON, CheckConstraint
from sqlalchemy.sql import func
from ..database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome_completo = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    senha = Column(String, nullable=False)
    data_nascimento = Column(Date, nullable=False)
    sexo_biologico = Column(String(1), CheckConstraint("sexo_biologico IN ('M', 'F')"), nullable=False)
    data_criacao = Column(DateTime, default=func.now())
    formulario = Column(JSON)
    status_formulario = Column(String(20), CheckConstraint("status_formulario IN ('Preenchido', 'Em andamento', 'Não iniciado')"), default='Não iniciado')