import pandas as pd

from src.transform.ownership import _norm_link, filtrar_nettius


def test_link_normalization_strips_tracking_case_and_slash():
    assert _norm_link("https://WWW.Instagram.com/P/ABC/?utm_source=x") == "instagram.com/p/abc"


def test_youtube_short_and_watch_urls_match():
    assert _norm_link("https://youtu.be/AbC123?t=10") == _norm_link("https://youtube.com/watch?v=abc123&utm=x")


def test_only_monday_links_are_kept_on_same_date(publicaciones, monday_links):
    result = filtrar_nettius(publicaciones, monday_links)
    assert result["titulo"].tolist() == ["A", "C"]
    assert set(result["ownership_match"]) == {"link"}


def test_empty_monday_is_fail_closed(publicaciones):
    result = filtrar_nettius(publicaciones, pd.DataFrame(columns=["link", "fecha", "red"]))
    assert result.empty
    assert list(result.columns) == list(publicaciones.columns)


def test_date_network_fallback_only_for_blank_monday_link(publicaciones):
    monday = pd.DataFrame([
        {"id": "m1", "link": "", "fecha": "2026-08-05", "red": "instagram"},
    ])
    result = filtrar_nettius(publicaciones, monday)
    assert result["titulo"].tolist() == ["A", "B"]
    assert set(result["ownership_match"]) == {"fecha_red"}


def test_nonmatching_monday_link_does_not_enable_date_fallback(publicaciones):
    monday = pd.DataFrame([
        {"id": "m1", "link": "https://instagram.com/p/no-coincide", "fecha": "2026-08-05", "red": "instagram"},
    ])
    assert filtrar_nettius(publicaciones, monday).empty


def test_direct_fecha_red_mode_is_explicit(publicaciones):
    monday = pd.DataFrame([{"link": "x", "fecha": "2026-08-05", "red": "instagram"}])
    result = filtrar_nettius(publicaciones, monday, clave="fecha_red")
    assert result["titulo"].tolist() == ["A", "B"]
