import pandas as pd
import pytest


@pytest.fixture
def publicaciones():
    return pd.DataFrame([
        {"id": "p1", "link": "https://www.instagram.com/p/ABC/?utm_source=x", "fecha": "2026-08-05 10:00", "red": "Instagram", "titulo": "A", "alcance": 100, "interacciones": 20},
        {"id": "p2", "link": "https://instagram.com/p/externo", "fecha": "2026-08-05", "red": "instagram", "titulo": "B", "alcance": 300, "interacciones": 10},
        {"id": "p3", "link": "https://linkedin.com/feed/update/123", "fecha": "2026-08-07", "red": "linkedin", "titulo": "C", "alcance": 150, "interacciones": 20},
    ])


@pytest.fixture
def monday_links():
    return pd.DataFrame([
        {"id": "m1", "link": "instagram.com/p/abc", "fecha": "2026-08-05", "red": "instagram"},
        {"id": "m2", "link": "https://linkedin.com/feed/update/123/", "fecha": "2026-08-07", "red": "linkedin"},
    ])
