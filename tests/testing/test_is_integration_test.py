import pytest


@pytest.mark.integration
def test_is_integration_test_is_true_for_integration_test(
    is_integration_test: bool,  # noqa: FBT001
) -> None:
    assert is_integration_test is True


def test_is_integration_test_is_false_for_unit_test(is_integration_test: bool) -> None:  # noqa: FBT001
    assert is_integration_test is False
