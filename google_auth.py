"""Autenticación compartida para Google Sheets."""
from __future__ import annotations

import json
from pathlib import Path

from .config import env


def gspread_client(scopes: list[str]):
    """Acepta GOOGLE_SERVICE_ACCOUNT_JSON como JSON o como ruta local."""
    raw = env("GOOGLE_SERVICE_ACCOUNT_JSON")
    import gspread
    from google.oauth2.service_account import Credentials
    assert raw is not None
    if raw.lstrip().startswith("{"):
        creds = Credentials.from_service_account_info(json.loads(raw), scopes=scopes)
    else:
        path = Path(raw).expanduser()
        if not path.is_file():
            raise RuntimeError(
                "GOOGLE_SERVICE_ACCOUNT_JSON debe contener el JSON completo o la ruta "
                f"a un archivo existente; no existe: {path}"
            )
        creds = Credentials.from_service_account_file(path, scopes=scopes)
    return gspread.authorize(creds)
