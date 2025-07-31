from typing import Any, Literal, cast

import pytest

from mex.common.exceptions import MExError
from mex.common.merged.main import (
    create_merged_item,
)
from mex.common.models import (
    ActivityRuleSetRequest,
    AdditivePerson,
    AdditiveResource,
    AnyExtractedModel,
    AnyRuleSetRequest,
    ContactPointRuleSetRequest,
    ExtractedActivity,
    ExtractedContactPoint,
    ExtractedPerson,
    ExtractedResource,
    MergedContactPoint,
    PersonRuleSetRequest,
    PreventivePerson,
    PreventiveResource,
    ResourceRuleSetRequest,
    SubtractiveActivity,
    SubtractiveContactPoint,
    SubtractivePerson,
    SubtractiveResource,
)
from mex.common.testing import Joker
from mex.common.types import (
    AccessRestriction,
    Identifier,
    Text,
    TextLanguage,
    Theme,
)
from mex.common.types.validation import Validation


def test_create_merged_item_stable_order() -> None:
    # create a batch of 20 contact points
    contact_points = [
        ExtractedContactPoint(
            email=[f"{i}@contact-point.com"],
            hadPrimarySource=Identifier.generate(seed=1),
            identifierInPrimarySource=f"{i}",
        )
        for i in range(20)
    ]

    # merge the extracted items into a merged item
    merged_contact_person = cast(
        "MergedContactPoint",
        create_merged_item(
            Identifier.generate(),
            contact_points,
            None,
            validation=Validation.IGNORE,
        ),
    )

    # check that the list of emails is stable in its order
    assert merged_contact_person.email == [
        c.email[0] for c in sorted(contact_points, key=lambda e: e.identifier)
    ]


@pytest.mark.parametrize(
    ("extracted_items", "rule_set", "validation", "expected"),
    [
        pytest.param(
            [
                ExtractedResource(
                    identifierInPrimarySource="r1",
                    hadPrimarySource=Identifier.generate(seed=42),
                    accessRestriction=AccessRestriction["OPEN"],
                    contact=[Identifier.generate(seed=999)],
                    unitInCharge=[Identifier.generate(seed=999)],
                    theme=[Theme["PUBLIC_HEALTH"]],
                    title=[Text(value="Dummy resource")],
                )
            ],
            ResourceRuleSetRequest(
                additive=AdditiveResource(),
                subtractive=SubtractiveResource(),
                preventive=PreventiveResource(),
            ),
            Validation.STRICT,
            {
                "accessRestriction": "https://mex.rki.de/item/access-restriction-1",
                "contact": ["bFQoRhcVH5DIax"],
                "theme": ["https://mex.rki.de/item/theme-1"],
                "title": [{"value": "Dummy resource", "language": TextLanguage.EN}],
                "unitInCharge": ["bFQoRhcVH5DIax"],
                "entityType": "MergedResource",
                "identifier": "bFQoRhcVH5DHU6",
            },
            id="single extracted item",
        ),
        pytest.param(
            [
                ExtractedPerson(
                    fullName="Dr. Zoidberg",
                    affiliation=Identifier.generate(seed=99),
                    email="z@express.planet",
                    identifierInPrimarySource="drz",
                    hadPrimarySource=Identifier.generate(seed=9),
                ),
                ExtractedPerson(
                    fullName="Mr. Krabs",
                    email="manager@krusty.ocean",
                    affiliation=Identifier.generate(seed=101),
                    memberOf=[
                        Identifier.generate(seed=500),
                        Identifier.generate(seed=750),
                    ],
                    hadPrimarySource=Identifier.generate(seed=11),
                    identifierInPrimarySource="mrk",
                ),
            ],
            PersonRuleSetRequest(
                additive=AdditivePerson(
                    givenName=["Eugene", "Harold", "John"],
                    memberOf=[Identifier.generate(seed=500)],
                ),
                subtractive=SubtractivePerson(
                    email=["manager@krusty.ocean"],
                    givenName=["John"],
                ),
                preventive=PreventivePerson(
                    email=[Identifier.generate(seed=9)],
                    fullName=[Identifier.generate(seed=9)],
                ),
            ),
            Validation.STRICT,
            {
                "affiliation": [
                    Identifier.generate(seed=99),
                    Identifier.generate(seed=101),
                ],
                "fullName": ["Mr. Krabs"],
                "givenName": ["Eugene", "Harold"],
                "memberOf": [
                    Identifier.generate(seed=500),
                    Identifier.generate(seed=750),
                ],
                "identifier": Identifier.generate(seed=42),
                "entityType": "MergedPerson",
            },
            id="extracted items and rule set",
        ),
        pytest.param(
            [],
            PersonRuleSetRequest(
                additive=AdditivePerson(
                    givenName=["Eugene", "Harold", "John"],
                    memberOf=[Identifier.generate(seed=500)],
                ),
                subtractive=SubtractivePerson(
                    email=["manager@krusty.ocean"],
                    givenName=["John"],
                ),
                preventive=PreventivePerson(
                    email=[Identifier.generate(seed=9)],
                    fullName=[Identifier.generate(seed=9)],
                ),
            ),
            Validation.STRICT,
            {
                "givenName": ["Eugene", "Harold"],
                "memberOf": [
                    Identifier.generate(seed=500),
                ],
                "identifier": Identifier.generate(seed=42),
                "entityType": "MergedPerson",
            },
            id="only rule set",
        ),
        pytest.param(
            [
                ExtractedPerson(
                    fullName="Dr. Zoidberg",
                    affiliation=Identifier.generate(seed=99),
                    email="z@express.planet",
                    identifierInPrimarySource="drz",
                    hadPrimarySource=Identifier.generate(seed=9),
                ),
                ExtractedPerson(
                    fullName="Mr. Krabs",
                    email="manager@krusty.ocean",
                    affiliation=Identifier.generate(seed=101),
                    memberOf=[
                        Identifier.generate(seed=500),
                        Identifier.generate(seed=750),
                    ],
                    hadPrimarySource=Identifier.generate(seed=11),
                    identifierInPrimarySource="mrk",
                ),
            ],
            None,
            Validation.STRICT,
            {
                "affiliation": [
                    Identifier.generate(seed=99),
                    Identifier.generate(seed=101),
                ],
                "email": ["z@express.planet", "manager@krusty.ocean"],
                "fullName": ["Dr. Zoidberg", "Mr. Krabs"],
                "memberOf": [
                    Identifier.generate(seed=500),
                    Identifier.generate(seed=750),
                ],
                "identifier": Identifier.generate(seed=42),
                "entityType": "MergedPerson",
            },
            id="only extracted items",
        ),
        pytest.param(
            [],
            None,
            Validation.STRICT,
            "One of rule_set or extracted_items is required.",
            id="error if neither is supplied",
        ),
        pytest.param(
            [
                ExtractedContactPoint(
                    identifierInPrimarySource="krusty",
                    hadPrimarySource=Identifier.generate(seed=99),
                    email=["manager@krusty.ocean"],
                )
            ],
            ContactPointRuleSetRequest(
                subtractive=SubtractiveContactPoint(
                    email=["flipper@krusty.ocean", "manager@krusty.ocean"]
                )
            ),
            Validation.STRICT,
            "List should have at least 1 item after validation, not 0",
            id="merging raises cardinality error",
        ),
        pytest.param(
            [
                ExtractedActivity(
                    title=Text(value="Burger flipping"),
                    alternativeTitle=[],
                    contact=Identifier.generate(seed=97),
                    responsibleUnit=Identifier.generate(seed=98),
                    identifierInPrimarySource="BF",
                    hadPrimarySource=Identifier.generate(seed=99),
                ),
            ],
            ActivityRuleSetRequest(
                subtractive=SubtractiveActivity(
                    title=Text(value="Burger flipping"),
                    alternativeTitle=Text(value="Cash making"),
                ),
            ),
            Validation.LENIENT,
            {
                "title": [{"value": "Burger flipping", "language": None}],
                "alternativeTitle": [{"value": "Cash making", "language": None}],
                "contact": [Identifier.generate(seed=97)],
                "identifier": Identifier.generate(seed=42),
                "responsibleUnit": [Identifier.generate(seed=98)],
                "entityType": "PreviewActivity",
            },
            id="get preview of merged items",
        ),
        pytest.param(
            [
                ExtractedContactPoint(
                    identifierInPrimarySource="krusty",
                    hadPrimarySource=Identifier.generate(seed=99),
                    email=["manager@krusty.ocean"],
                )
            ],
            ContactPointRuleSetRequest(
                subtractive=SubtractiveContactPoint(
                    email=["flipper@krusty.ocean", "manager@krusty.ocean"]
                )
            ),
            Validation.LENIENT,
            {
                "identifier": Joker(),
                "entityType": "PreviewContactPoint",
                "email": ["manager@krusty.ocean"],
            },
            id="preview allows cardinality error",
        ),
        pytest.param(
            [
                ExtractedContactPoint(
                    identifierInPrimarySource="orders",
                    hadPrimarySource=Identifier.generate(seed=98),
                    email=["orders@krusty.ocean"],
                )
            ],
            ContactPointRuleSetRequest(
                subtractive=SubtractiveContactPoint(
                    email=["orders@krusty.ocean"],
                )
            ),
            Validation.IGNORE,
            None,
            id="ignore mode validation returns none",
        ),
    ],
)
def test_create_merged_item(
    extracted_items: list[AnyExtractedModel],
    rule_set: AnyRuleSetRequest | None,
    validation: Literal[Validation.STRICT, Validation.LENIENT, Validation.IGNORE],
    expected: dict[str, Any] | str | None,
) -> None:
    try:
        merged_item = create_merged_item(
            Identifier.generate(seed=42),
            extracted_items,
            rule_set,
            validation,
        )
    except MExError as error:
        if str(expected) not in f"{error}: {error.__cause__}":
            raise AssertionError(expected) from error
    else:
        if merged_item is None:
            assert expected is None
        else:
            assert {k: v for k, v in merged_item.model_dump().items() if v} == expected
