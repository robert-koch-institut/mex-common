from uuid import UUID

import pytest

from mex.common.models import ExtractedPerson
from mex.common.types import Email, Identifier

pytest_plugins = ("mex.common.testing.plugin",)


@pytest.fixture()
def extracted_person() -> ExtractedPerson:
    """Return a dummy extracted person for testing purposes."""
    return ExtractedPerson.construct(
        identifierInPrimarySource=str(UUID(int=990, version=4)),
        identifier=Identifier.generate(seed=550),
        stableTargetId=Identifier.generate(seed=876),
        hadPrimarySource=Identifier.generate(seed=200),
        affiliation=[Identifier.generate(seed=300)],
        email=Email("TintzmannM@rki.de"),
        familyName=["Tintzmann"],
        givenName=["Meinrad"],
        fullName=["Meinrad I. Tintzmann"],
        isniId="https://isni.org/isni/0000000109403744",
        memberOf=[Identifier.generate(seed=100), Identifier.generate(seed=101)],
        orcidId="https://orcid.org/0000-0002-9079-593X",
    )
