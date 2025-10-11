from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func
from src.database.db import Base

class Funcionario(Base):
    __tablename__ = 'relatorio_individual'

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    area = Column(String, nullable=False)
    salario = Column(Float, nullable=False)
    bonus_percentual = Column(Float, nullable=False)
    data_criacao = Column(DateTime, default=func.now())