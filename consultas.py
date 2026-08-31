from database import SessionLocal
from models.alerta import Alerta
from sqlalchemy import func


def relatorio_geral():
    db = SessionLocal()

    try:
        # Total de campanhas
        total = db.query(Alerta).count()

        # Quantidade por empresa
        por_empresa = (
            db.query(
                Alerta.empresa,
                func.count(Alerta.id)
            )
            .group_by(Alerta.empresa)
            .all()
        )

        # Últimos alertas
        ultimos = (
            db.query(Alerta)
            .order_by(Alerta.criado_em.desc())
            .limit(3)
            .all()
        )

        print("\n" + "=" * 50)
        print("📊 RELATÓRIO CLOUDPULSE - VISÃO DE MERCADO")
        print("=" * 50)

        print(f"\nTotal de campanhas detectadas: {total}")

        print("\n🏢 Volume por concorrente:")

        for empresa, quantidade in por_empresa:
            print(f" • {empresa}: {quantidade} campanha(s)")

        print("\n🕒 Últimas movimentações:")

        for alerta in ultimos:
            print(f" • [{alerta.empresa}] {alerta.titulo}")

        print("\n" + "=" * 50)

    finally:
        db.close()


if __name__ == "__main__":
    relatorio_geral()
