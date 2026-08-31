from database import SessionLocal
from models.alerta import Alerta

import traceback


def salvar_alerta(empresa, titulo, url):
    db = SessionLocal()

    try:

        existe = (
            db.query(Alerta)
            .filter(Alerta.url == url)
            .first()
        )

        if existe:
            return False

        alerta = Alerta(
            empresa=empresa,
            titulo=titulo,
            url=url
        )

        db.add(alerta)

        db.commit()

        return True

    except Exception as e:

        db.rollback()

        print("\n================ ERRO DO BANCO ================\n")
        traceback.print_exc()
        print("\n===============================================\n")

        raise

    finally:

        db.close()
