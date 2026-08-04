import pytest

pytestmark = pytest.mark.integration


def test_is_integration_test_module_marker(is_integration_test: bool) -> None:  # noqa: FBT001
    assert is_integration_test is True
