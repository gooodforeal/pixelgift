from fastapi import FastAPI
from sqladmin import Admin, I18nConfig

from src.infrastructure.database import get_engine, get_session_factory
from src.presentation.admin.auth import AdminAuth
from src.presentation.admin.views import ADMIN_VIEWS


def setup_admin(app: FastAPI) -> Admin:
    admin = Admin(
        app,
        engine=get_engine(),
        session_maker=get_session_factory(),
        base_url="/admin",
        title="Pixelgift",
        authentication_backend=AdminAuth(),
        i18n_config=I18nConfig(default_locale="ru"),
    )
    for view in ADMIN_VIEWS:
        admin.add_view(view)
    return admin
