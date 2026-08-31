from sqlalchemy import func

from database import SessionLocal
from models.alerta import Alerta


def obter_metricas():

    db = SessionLocal()

    try:

        total = db.query(Alerta).count()

        empresas = (
            db.query(Alerta.empresa)
            .distinct()
            .count()
        )

        ranking = (
            db.query(
                Alerta.empresa,
                func.count(Alerta.id).label("total")
            )
            .group_by(Alerta.empresa)
            .order_by(func.count(Alerta.id).desc())
            .all()
        )

        empresa_lider = ranking[0][0] if ranking else "Nenhuma"

        ultimas = (
            db.query(Alerta)
            .order_by(Alerta.criado_em.desc())
            .limit(5)
            .all()
        )

        return {
            "total": total,
            "empresas": empresas,
            "lider": empresa_lider,
            "ranking": ranking,
            "ultimas": ultimas
        }

    finally:
        db.close()
