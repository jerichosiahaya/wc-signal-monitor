from wcprob.config import Settings


def test_default_settings_use_local_sqlite():
    settings = Settings()
    assert settings.database_path.name == "wcprob.sqlite"
    assert settings.refresh_seconds == 900
