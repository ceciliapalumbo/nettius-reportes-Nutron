from src.extract import metricool


def test_demo_exports_are_normalized():
    import yaml
    from pathlib import Path
    cfg = yaml.safe_load((Path(__file__).parents[1] / "examples" / "config.demo.yaml").read_text())
    posts = metricool.fetch_posts(cfg, "2026-08")
    assert set(posts["red"]) == {"instagram", "linkedin"}
    assert posts.loc[0, "alcance"] == 1250
    assert posts.loc[0, "fecha"] == "2026-08-05"
    assert metricool.fetch_account_kpis(cfg, "2026-08")["instagram"]["seguidores"] == 10000
    assert metricool.fetch_youtube(cfg, "2026-08").loc[0, "tipo"] == "video"
    assert metricool.fetch_meta_ads(cfg, "2026-08")["seguidores"].sum() == 18
