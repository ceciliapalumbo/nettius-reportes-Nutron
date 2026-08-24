"""Orquestador mensual: ``python -m src.run_month --cliente nutron --mes 2026-08``."""
from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path

import yaml

from .config import load_config
from .extract import meta_ads, metricool, monday, youtube
from .narrative import generate
from .sheets import writer
from .transform import metrics, ownership

LOGGER = logging.getLogger("nettius_reportes")


class MissingManualData(RuntimeError):
    pass


def _validate_month(mes: str) -> None:
    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", mes):
        raise ValueError("--mes debe tener formato YYYY-MM")


def _validate_metrics(payload: dict) -> None:
    schema_path = Path(__file__).resolve().parents[1] / "schemas" / "metrics.schema.json"
    schema = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
    try:
        import jsonschema
    except ImportError:  # permite la demo en entornos mínimos; producción lo instala.
        required = set(schema["required"])
        missing = required - set(payload)
        if missing or not re.fullmatch(r"\d{4}-\d{2}", str(payload.get("mes", ""))):
            raise ValueError(f"metrics.json no cumple el contrato; faltan {sorted(missing)}")
    else:
        jsonschema.validate(payload, schema)


def run(cliente: str, mes: str, cfg: dict | None = None) -> dict:
    _validate_month(mes)
    cfg = cfg or load_config(cliente)
    LOGGER.info("Reporte %s — %s", cfg.get("nombre_cliente", cliente), mes)

    LOGGER.info("1/5 Extrayendo exports de Sheets y propiedad de Monday")
    posts_all = metricool.fetch_posts(cfg, mes)
    kpis_cuenta = metricool.fetch_account_kpis(cfg, mes)
    yt_all = youtube.fetch(cfg, mes)
    ads = meta_ads.fetch(cfg, mes)
    lista_monday = monday.fetch_publicaciones_nettius(cfg, mes)

    LOGGER.info("2/5 Aplicando ownership determinístico")
    clave = cfg.get("monday", {}).get("clave_cruce", "link")
    contenido = ownership.filtrar_nettius(posts_all, lista_monday, clave=clave)
    networks = contenido.get("red", "").fillna("").astype(str).str.lower()
    ig = contenido[networks.eq("instagram")].reset_index(drop=True)
    li = contenido[networks.eq("linkedin")].reset_index(drop=True)
    yt = ownership.filtrar_nettius(yt_all, lista_monday, clave=clave)

    organicos = writer.leer_dato_manual_organicos(cfg, mes)
    if organicos is None:
        tab = cfg["google_sheet"]["tabs"]["dato_manual"]
        raise MissingManualData(
            f"Falta el dato manual de seguidores orgánicos para {mes}. "
            f"Cárgalo en '{tab}' (columnas: mes, organicos). No se escribió ningún resultado."
        )

    LOGGER.info("3/5 Calculando y validando consolidados")
    consolidados = metrics.construir_consolidados(
        cliente=cliente, mes=mes, kpis_cuenta=kpis_cuenta,
        contenido_nettius=contenido, youtube_nettius=yt,
        seguidores_campana=int(ads["seguidores"].sum()) if not ads.empty else 0,
        seguidores_organicos=organicos,
    )
    _validate_metrics(consolidados)

    LOGGER.info("4/5 Escribiendo tablas idempotentes")
    writer.escribir_reporte(
        cfg, consolidados=consolidados, ig_contenido=ig,
        li_contenido=li, youtube=yt, meta_ads=ads,
    )
    LOGGER.info("5/5 Generando los seis párrafos de narrativa")
    paragraphs = generate.generar_parrafos(cfg, consolidados)
    writer.escribir_analisis(cfg, paragraphs)
    _notify(cfg, mes)
    LOGGER.info("Reporte finalizado; Looker puede refrescar la Sheet")
    return consolidados


def _notify(cfg: dict, mes: str) -> None:
    webhook = cfg.get("notificar", {}).get("slack_webhook")
    if not webhook:
        return
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    retry = Retry(total=3, backoff_factor=1, status_forcelist=(429, 500, 502, 503, 504), allowed_methods=None)
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    response = session.post(webhook, json={"text": f"Reporte {cfg['cliente']} {mes} listo en Looker."}, timeout=15)
    response.raise_for_status()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cliente", required=True)
    parser.add_argument("--mes", required=True, help="YYYY-MM")
    parser.add_argument("--demo", action="store_true", help="usa fixtures locales sin credenciales")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    try:
        demo_cfg = None
        if args.demo:
            path = Path(__file__).resolve().parents[1] / "examples" / "config.demo.yaml"
            demo_cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
        run(args.cliente, args.mes, cfg=demo_cfg)
    except MissingManualData as exc:
        LOGGER.error(str(exc))
        sys.exit(2)
    except Exception:
        LOGGER.exception("Falló el reporte")
        sys.exit(1)


if __name__ == "__main__":
    main()
