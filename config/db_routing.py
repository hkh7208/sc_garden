import os
from contextvars import ContextVar
from typing import Optional, Set

_current_db_alias: ContextVar[Optional[str]] = ContextVar('current_db_alias', default=None)


def _parse_env_list(value: str) -> Set[str]:
    return {item.strip().lower() for item in value.split(',') if item.strip()}


LOCAL_HOSTS = _parse_env_list(
    os.environ.get('LOCAL_DB_HOSTNAMES', 'localhost,127.0.0.1,192.168.0.107,local')
)
NAS_HOSTS = _parse_env_list(
    os.environ.get('NAS_DB_HOSTNAMES', 'jakesto.synology.me,192.168.0.250')
)


def get_current_db_alias() -> str:
    alias = _current_db_alias.get()
    if alias:
        return alias

    mode = os.environ.get('DB_HOST_MODE', '').strip().lower()
    if mode in {'local', 'nas'}:
        return mode

    return os.environ.get('DEFAULT_REQUEST_DB_ALIAS', 'nas').strip().lower() or 'nas'


class HostDatabaseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        hostname = request.get_host().split(':', 1)[0].strip().lower()

        if hostname in LOCAL_HOSTS:
            alias = 'local'
        elif hostname in NAS_HOSTS:
            alias = 'nas'
        else:
            alias = os.environ.get('DEFAULT_REQUEST_DB_ALIAS', 'nas').strip().lower() or 'nas'

        token = _current_db_alias.set(alias)
        try:
            return self.get_response(request)
        finally:
            _current_db_alias.reset(token)


class HostDatabaseRouter:
    def db_for_read(self, model, **hints):
        return get_current_db_alias()

    def db_for_write(self, model, **hints):
        return get_current_db_alias()

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return None
