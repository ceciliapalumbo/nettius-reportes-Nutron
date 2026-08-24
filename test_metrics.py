import json
from pathlib import Path

import jsonschema
import pandas as pd

from src.transform.metrics import construir_consolidados


def test_metrics_preserve_account_kpis_and_filter_content(publicaciones):
    content = publicaciones.iloc[[0, 2]].copy()
    youtube = pd.DataFrame([{"red": "youtube", "visualizaciones": 1234}])
    result = construir_consolidados(
        cliente="nutron", mes="2026-08",
        kpis_cuenta={
            "Instagram": {"seguidores": 100, "alcance": 1000, "impresiones": 2000, "interacciones": 50},
            "linkedin": {"seguidores": 50, "alcance": 500, "impresiones": 700, "interacciones": 20},
            "youtube": {"seguidores": 25, "alcance": 10, "impresiones": 30, "interacciones": 5},
        },
        contenido_nettius=content, youtube_nettius=youtube,
        seguidores_campana=4, seguidores_organicos=6,
    )
    assert result["comunidad_total"] == 175
    assert result["alcance_total"] == 1510
    assert result["nuevos_seguidores"] == {"organicos": 6, "por_campana": 4, "total": 10}
    assert result["pct_crecimiento_nettius"] == 60.0
    assert result["por_red"]["instagram"]["posts_nettius"] == 1
    assert result["por_red"]["youtube"]["alcance"] == 10
    assert result["por_red"]["youtube"]["visualizaciones"] == 1234


def test_top_uses_reach_as_tiebreaker(publicaciones):
    result = construir_consolidados(
        cliente="nutron", mes="2026-08", kpis_cuenta={},
        contenido_nettius=publicaciones.iloc[[0, 2]],
        youtube_nettius=pd.DataFrame(), seguidores_campana=0, seguidores_organicos=0,
    )
    assert result["top_contenido"][0]["titulo"] == "C"


def test_output_conforms_to_schema(publicaciones):
    result = construir_consolidados(
        cliente="nutron", mes="2026-08", kpis_cuenta={},
        contenido_nettius=publicaciones.iloc[0:0], youtube_nettius=pd.DataFrame(),
        seguidores_campana=0, seguidores_organicos=0,
    )
    schema = json.loads((Path(__file__).parents[1] / "schemas" / "metrics.schema.json").read_text())
    jsonschema.validate(result, schema)
