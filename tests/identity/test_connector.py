from unittest.mock import MagicMock, Mock

import pytest
from pytest import MonkeyPatch
from sqlalchemy.exc import SQLAlchemyError

from mex.common.exceptions import MExError
from mex.common.identity.connector import IdentityConnector
from mex.common.settings import BaseSettings


def test_db_connection() -> None:
    connector = IdentityConnector.get()
    assert connector.engine.execute("SELECT 1;").scalar_one() == 1


def test_service_unavailable_init(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(IdentityConnector, "_is_service_available", lambda _: False)
    settings = BaseSettings.get()
    with pytest.raises(MExError):
        IdentityConnector(settings)


def test_connector_is_service_available(monkeypatch: MonkeyPatch) -> None:
    connector = IdentityConnector.get()
    assert connector._is_service_available() is True

    faulty_engine = Mock()
    faulty_engine.execute = MagicMock(side_effect=SQLAlchemyError)
    monkeypatch.setattr(connector, "engine", faulty_engine)
    assert connector._is_service_available() is False


def test_upsert_identitfication() -> None:
    connector = IdentityConnector.get()
    identity_after_insert = connector.upsert(
        "system-a", "thing-1", "old-target", "type-x"
    )

    identity_after_update = connector.upsert(
        "system-a", "thing-1", "new-target", "type-x"
    )
    assert identity_after_update != identity_after_insert

    assert (
        identity_after_insert.platform_id
        == identity_after_update.platform_id
        == "system-a"
    )
    assert (
        identity_after_insert.original_id
        == identity_after_update.original_id
        == "thing-1"
    )
    assert identity_after_insert.fragment_id == identity_after_update.fragment_id
    assert identity_after_insert.merged_id != identity_after_update.merged_id
    assert (
        identity_after_insert.entity_type
        == identity_after_update.entity_type
        == "type-x"
    )


def test_fetch_identity() -> None:
    connector = IdentityConnector.get()

    result = connector.fetch()
    assert result is None

    identity = connector.upsert("system-a", "thing-1", "entity-1", "type-x")

    result = connector.fetch(
        had_primary_source=str(identity.platform_id),
        identifier_in_primary_source=str(identity.original_id),
        stable_target_id=str(identity.merged_id),
    )
    assert result == identity

    result = connector.fetch(
        had_primary_source="no-such",
        identifier_in_primary_source="no-such",
        stable_target_id="no-such",
    )
    assert result is None
