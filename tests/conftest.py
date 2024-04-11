from uuid import UUID

import pytest

from mex.common.models import ExtractedPerson
from mex.common.types import (
    Email,
    ExtractedPersonIdentifier,
    MergedOrganizationalUnitIdentifier,
    MergedOrganizationIdentifier,
    MergedPersonIdentifier,
    MergedPrimarySourceIdentifier,
)

pytest_plugins = ("mex.common.testing.plugin",)


@pytest.fixture
def extracted_person() -> ExtractedPerson:
    """Return a dummy extracted person for testing purposes."""
    return ExtractedPerson.model_construct(
        identifierInPrimarySource=str(UUID(int=990, version=4)),
        identifier=ExtractedPersonIdentifier.generate(seed=550),
        stableTargetId=MergedPersonIdentifier.generate(seed=876),
        hadPrimarySource=MergedPrimarySourceIdentifier.generate(seed=200),
        affiliation=[MergedOrganizationIdentifier.generate(seed=300)],
        email=[Email("TintzmannM@rki.de")],
        familyName=["Tintzmann"],
        givenName=["Meinrad"],
        fullName=["Meinrad I. Tintzmann"],
        isniId=["https://isni.org/isni/0000000109403744"],
        memberOf=[
            MergedOrganizationalUnitIdentifier.generate(seed=100),
            MergedOrganizationalUnitIdentifier.generate(seed=101),
        ],
        orcidId=["https://orcid.org/0000-0002-9079-593X"],
    )
