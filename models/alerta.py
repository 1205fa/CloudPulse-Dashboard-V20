from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.sql import func

from database import Base


class Alerta(Base):

    __tablename__ = "alertas"

    id = Column(Integer, primary_key=True)

    empresa = Column(String(120))

    titulo = Column(String(300))

    url = Column(String(600))

    criado_em = Column(DateTime(timezone=True), server_default=func.now())
