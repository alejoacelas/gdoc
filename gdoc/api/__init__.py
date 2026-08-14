"""API service factories, cached per account.

Each factory keys its cache on the *resolved* account (`resolve_account()`),
so a long-lived multi-account process (`gdoc mcp`, a hosted server) never
hands one account another account's service object, and an unpinned call
picks up a default-account change at call time. For the one-shot CLI this
degenerates to the old one-service-per-process behavior.
"""

from functools import lru_cache

from googleapiclient.discovery import build

from gdoc.util import resolve_account

# How many accounts keep a warm service object at once; an evicted account
# is just rebuilt on its next call.
ACCOUNT_CACHE_SIZE = 8


@lru_cache(maxsize=ACCOUNT_CACHE_SIZE)
def _drive_service(account: str | None):
    from gdoc.auth import get_credentials

    return build("drive", "v3", credentials=get_credentials(account))


def get_drive_service():
    """Build or reuse the Drive API v3 service for the current account.

    Lazy-imports get_credentials to avoid import errors when Google
    libraries are not available (e.g., during ``gdoc --help``).
    """
    return _drive_service(resolve_account())


@lru_cache(maxsize=ACCOUNT_CACHE_SIZE)
def _sheets_service(account: str | None):
    from gdoc.auth import get_credentials

    return build("sheets", "v4", credentials=get_credentials(account))


def get_sheets_service():
    """Build or reuse the Sheets API v4 service for the current account.

    The existing ``drive`` OAuth scope covers the Sheets API, so no
    re-authentication is needed.
    """
    return _sheets_service(resolve_account())


def clear_service_caches() -> None:
    """Forget every cached, account-specific service object.

    Caches are keyed per account, so routine account switches never need
    this; it exists for the rare full reset (re-authentication in-process,
    test isolation). Keep it in sync with any new cached service.
    """
    from gdoc.api.docs import _docs_service
    from gdoc.api.revisions import _session_for

    _drive_service.cache_clear()
    _sheets_service.cache_clear()
    _docs_service.cache_clear()
    _session_for.cache_clear()
