"""Carga de configuración: config.yaml (por cliente) + .env (credenciales)."""
from __future__ import annotations
import os
from pathlib import Path
import yaml
try:
    from dotenv import load_dotenv
except ImportError:  # la demo no requiere .env; producción instala python-dotenv.
    def load_dotenv() -> bool:
        return False

load_dotenv()


def load_config(cliente: str) -> dict:
    """Devuelve el dict de config para un cliente.

    Busca config.yaml en la raíz del repo. Para multi-cliente, usar
    config.<cliente>.yaml (ej: config.nutron.yaml) y este loader lo resuelve.
    """
    root = Path(__file__).resolve().parents[1]
    candidatos = [root / f"config.{cliente}.yaml", root / "config.yaml"]
    for p in candidatos:
        if p.exists():
            cfg = yaml.safe_load(p.read_text(encoding="utf-8"))
            if cfg.get("cliente") not in (None, cliente):
                # config.yaml genérico pero para otro cliente
                continue
            _validate_config(cfg, cliente)
            return cfg
    raise FileNotFoundError(
        f"No encontré config para '{cliente}'. Copiá config.example.yaml a "
        f"config.{cliente}.yaml y completalo."
    )


def env(nombre: str, requerido: bool = True) -> str | None:
    v = os.environ.get(nombre)
    if requerido and not v:
        raise RuntimeError(f"Falta la variable de entorno {nombre} (ponela en .env)")
    return v


def _validate_config(cfg: dict, cliente: str) -> None:
    required = ("google_sheet", "metricool", "monday", "narrativa")
    missing = [key for key in required if key not in cfg]
    if missing:
        raise ValueError(f"Config de '{cliente}' incompleta; faltan: {', '.join(missing)}")
