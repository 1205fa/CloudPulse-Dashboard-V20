from database import Base, engine

import models.alerta

Base.metadata.create_all(bind=engine)

print("Banco criado com sucesso.")
