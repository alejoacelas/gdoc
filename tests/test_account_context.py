"""Per-request credential injection: the account is carried by the calling
context, and service caches are keyed by it — never process-global."""

import threading

import pytest

from gdoc import api, util


@pytest.fixture(autouse=True)
def _isolated(monkeypatch):
    """Fresh caches and no machine-configured default account."""
    api.clear_service_caches()
    monkeypatch.setattr("gdoc.util.get_default_account", lambda: None)
    yield
    api.clear_service_caches()


@pytest.fixture()
def _fake_services(mocker):
    """Mock credentials + build so services record the account they carry."""
    mocker.patch(
        "gdoc.auth.get_credentials", side_effect=lambda account: f"creds:{account}"
    )
    built = {}

    def fake_build(api_name, version, credentials):
        service = object()
        built[service] = credentials
        return service

    mocker.patch("gdoc.api.build", side_effect=fake_build)
    mocker.patch("gdoc.api.docs.build", side_effect=fake_build)
    return built


def test_concurrent_accounts_see_only_their_own_credentials(_fake_services):
    """Two accounts used concurrently in one process must not see each
    other's credentials or cached services."""
    barrier = threading.Barrier(2, timeout=5)
    results = {}

    def use(account):
        with util.account_context(account):
            barrier.wait()  # both threads hold their contexts at once
            results[account] = api.get_drive_service()

    threads = [
        threading.Thread(target=use, args=(name,)) for name in ("alice", "bob")
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert _fake_services[results["alice"]] == "creds:alice"
    assert _fake_services[results["bob"]] == "creds:bob"
    assert results["alice"] is not results["bob"]


def test_services_are_cached_per_account(_fake_services):
    with util.account_context("alice"):
        first = api.get_drive_service()
    with util.account_context("bob"):
        other = api.get_drive_service()
    with util.account_context("alice"):
        again = api.get_drive_service()

    assert first is again
    assert first is not other


def test_default_account_change_is_picked_up_unpinned(mocker, _fake_services):
    """An unpinned call resolves the configured default at call time."""
    default = mocker.patch("gdoc.util.get_default_account", return_value="a")

    first = api.get_drive_service()
    assert api.get_drive_service() is first  # unchanged default: cache kept

    default.return_value = "b"
    switched = api.get_drive_service()
    assert switched is not first
    assert _fake_services[switched] == "creds:b"


def test_every_factory_keys_on_the_account(mocker, _fake_services):
    """Docs service and the revisions session isolate accounts too."""
    from gdoc.api import docs, revisions

    sessions = {}

    def fake_session(credentials):
        session = object()
        sessions[session] = credentials
        return session

    mocker.patch(
        "google.auth.transport.requests.AuthorizedSession",
        side_effect=fake_session,
    )

    with util.account_context("alice"):
        docs_a = docs.get_docs_service()
        session_a = revisions._get_session()
    with util.account_context("bob"):
        docs_b = docs.get_docs_service()
        session_b = revisions._get_session()

    assert _fake_services[docs_a] == "creds:alice"
    assert _fake_services[docs_b] == "creds:bob"
    assert sessions[session_a] == "creds:alice"
    assert sessions[session_b] == "creds:bob"


def test_account_context_restores_previous_value():
    """The pre-call account survives even a set_active_account inside the
    block (run_argv sets it when argv carries --account)."""
    assert util.get_active_account() is None
    with util.account_context("work"):
        assert util.get_active_account() == "work"
        util.set_active_account("other")
    assert util.get_active_account() is None


def test_account_context_validates_the_name():
    from gdoc.util import GdocError

    with pytest.raises(GdocError), util.account_context("../evil"):
        pass  # pragma: no cover


def test_token_path_for_resolved_accounts():
    assert util.token_path_for(None) == util.TOKEN_PATH
    assert (
        util.token_path_for("work")
        == util.CONFIG_DIR / "accounts" / "work" / "token.json"
    )
