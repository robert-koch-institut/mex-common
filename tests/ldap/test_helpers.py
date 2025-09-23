from unittest.mock import MagicMock, patch

import pytest

from mex.common.ldap.helpers import get_wikidata_rki_organization
from mex.common.types.identifier import MergedOrganizationIdentifier


@pytest.fixture(autouse=True)
def clear_cache() -> None:
    get_wikidata_rki_organization.cache_clear()


def test_returns_organization_id_when_found() -> None:
    mock_id = MergedOrganizationIdentifier("rki-123")
    mock_response = MagicMock(total=1, items=[MagicMock(stableTargetId=mock_id)])
    with patch("mex.common.ldap.helpers.BackendApiConnector.get") as mock_connector:
        mock_connector.return_value.fetch_extracted_items.return_value = mock_response
        result = get_wikidata_rki_organization()
        assert result == mock_id


def test_returns_none_when_not_found() -> None:
    mock_response = MagicMock(total=0, items=[])
    with (
        patch("mex.common.ldap.helpers.BackendApiConnector.get") as mock_connector,
        patch("mex.common.ldap.helpers.logger") as mock_logger,
    ):
        mock_connector.return_value.fetch_extracted_items.return_value = mock_response
        result = get_wikidata_rki_organization()
        assert result is None
        mock_logger.warning.assert_called_once_with(
            "StableTargetId for RKI organization not found in backend response."
        )


def test_returns_none_when_wrong_type() -> None:
    mock_response = MagicMock(total=1, items=[MagicMock(stableTargetId="not-an-id")])
    with (
        patch("mex.common.ldap.helpers.BackendApiConnector.get") as mock_connector,
        patch("mex.common.ldap.helpers.logger") as mock_logger,
    ):
        mock_connector.return_value.fetch_extracted_items.return_value = mock_response
        result = get_wikidata_rki_organization()
        assert result is None
        mock_logger.warning.assert_called_once_with(
            "StableTargetId for RKI organization not found in backend response."
        )
