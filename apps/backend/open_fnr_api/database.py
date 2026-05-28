from collections.abc import Callable
from contextlib import contextmanager
from typing import Any

from .config import Settings, settings


DbConnectionFactory = Callable[[], Any]


def make_pg8000_connection_factory(app_settings: Settings = settings) -> DbConnectionFactory:
    def factory() -> Any:
        from pg8000 import dbapi

        return dbapi.connect(
            host=app_settings.service_host,
            port=app_settings.postgres_port,
            database=app_settings.postgres_database,
            user=app_settings.postgres_user,
            password=app_settings.postgres_password,
        )

    return factory


@contextmanager
def managed_connection(connection_factory: DbConnectionFactory):
    connection = connection_factory()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
