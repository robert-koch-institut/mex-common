from typing import Any, Literal

import pytest

from mex.common.exceptions import MExError
from mex.common.merged.main import (
    _apply_additive_rule,
    _apply_subtractive_rule,
    _merge_extracted_items_and_apply_preventive_rule,
    create_merged_item,
)
from mex.common.models import (
    ActivityRuleSetRequest,
    AdditiveOrganizationalUnit,
    AdditivePerson,
    AdditiveResource,
    AnyExtractedModel,
    AnyRuleSetRequest,
    ContactPointRuleSetRequest,
    ExtractedActivity,
    ExtractedContactPoint,
    ExtractedPerson,
    ExtractedResource,
    PersonRuleSetRequest,
    PreventiveContactPoint,
    PreventivePerson,
    PreventiveResource,
    ResourceRuleSetRequest,
    SubtractiveActivity,
    SubtractiveContactPoint,
    SubtractiveOrganizationalUnit,
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


def test_merge_extracted_items_stable_order() -> None:
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
    merged_dict: dict[str, Any] = {}
    _merge_extracted_items_and_apply_preventive_rule(
        merged_dict,
        ["email"],
        contact_points,
        None,
    )

    # check that the list of emails is stable in its order
    assert merged_dict["email"] == [
        c.email[0] for c in sorted(contact_points, key=lambda e: e.identifier)
    ]


def test_merge_extracted_items_and_apply_preventive_rule() -> None:
    merged_dict: dict[str, Any] = {}
    contact_points: list[AnyExtractedModel] = [
        ExtractedContactPoint(
            email=["info@contact-point.one"],
            hadPrimarySource=Identifier.generate(seed=1),
            identifierInPrimarySource="one",
        ),
        ExtractedContactPoint(
            email=["hello@contact-point.two"],
            hadPrimarySource=Identifier.generate(seed=2),
            identifierInPrimarySource="two",
        ),
    ]
    rule = PreventiveContactPoint(
        email=[contact_points[1].hadPrimarySource],
    )
    _merge_extracted_items_and_apply_preventive_rule(
        merged_dict,
        ["email"],
        contact_points,
        rule,
    )
    assert merged_dict == {
        "email": ["info@contact-point.one"],
    }

    merged_dict.clear()
    _merge_extracted_items_and_apply_preventive_rule(
        merged_dict,
        ["email"],
        contact_points,
        None,
    )
    assert merged_dict == {
        "email": ["info@contact-point.one", "hello@contact-point.two"],
    }

    merged_dict.clear()
    _merge_extracted_items_and_apply_preventive_rule(
        merged_dict,
        ["email"],
        [],
        rule,
    )
    assert merged_dict == {}


def test_apply_additive_rule() -> None:
    merged_dict: dict[str, Any] = {
        "email": ["info@org-unit.one"],
    }
    rule = AdditiveOrganizationalUnit(
        email=["new-mail@who.dis", "info@org-unit.one"],
        name=[Text(value="org unit one", language=TextLanguage.EN)],
    )
    _apply_additive_rule(
        merged_dict,
        ["email", "name"],
        rule,
    )
    assert merged_dict == {
        "email": ["info@org-unit.one", "new-mail@who.dis"],
        "name": [Text(value="org unit one", language=TextLanguage.EN)],
    }


def test_apply_subtractive_rule() -> None:
    merged_dict: dict[str, Any] = {
        "email": ["info@org-unit.one"],
        "name": [Text(value="org unit one", language=TextLanguage.EN)],
    }
    rule = SubtractiveOrganizationalUnit(
        email=["unknown@email.why", "info@org-unit.one"],
        name=[Text(value="org unit one", language=TextLanguage.DE)],
    )
    _apply_subtractive_rule(
        merged_dict,
        ["email", "name"],
        rule,
    )
    assert merged_dict == {
        "email": [],
        "name": [Text(value="org unit one", language=TextLanguage.EN)],
    }


@pytest.mark.parametrize(
    ("extracted_items", "rule_set", "validate_cardinality", "expected"),
    [
        (
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
            True,
            {
                "accessRestriction": "https://mex.rki.de/item/access-restriction-1",
                "contact": ["bFQoRhcVH5DIax"],
                "theme": ["https://mex.rki.de/item/theme-1"],
                "title": [{"value": "Dummy resource", "language": TextLanguage.EN}],
                "unitInCharge": ["bFQoRhcVH5DIax"],
                "entityType": "MergedResource",
                "identifier": "bFQoRhcVH5DHU6",
            },
        ),
        (
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
            True,
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
        ),
        (
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
            True,
            {
                "givenName": ["Eugene", "Harold"],
                "memberOf": [
                    Identifier.generate(seed=500),
                ],
                "identifier": Identifier.generate(seed=42),
                "entityType": "MergedPerson",
            },
        ),
        (
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
            True,
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
        ),
        ([], None, True, "One of rule_set or extracted_items is required."),
        (
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
            True,
            "List should have at least 1 item after validation, not 0",
        ),
        (
            [
                ExtractedActivity(
                    title=Text(value="Burger flipping"),
                    contact=Identifier.generate(seed=97),
                    responsibleUnit=Identifier.generate(seed=98),
                    identifierInPrimarySource="BF",
                    hadPrimarySource=Identifier.generate(seed=99),
                ),
            ],
            ActivityRuleSetRequest(
                subtractive=SubtractiveActivity(title=Text(value="Burger flipping")),
            ),
            False,
            {
                "contact": [Identifier.generate(seed=97)],
                "identifier": Identifier.generate(seed=42),
                "responsibleUnit": [Identifier.generate(seed=98)],
                "entityType": "PreviewActivity",
            },
        ),
        (
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
            False,
            {
                "identifier": Joker(),
                "entityType": "PreviewContactPoint",
            },
        ),
    ],
    ids=(
        "single extracted item",
        "extracted items and rule set",
        "only rule set",
        "only extracted items",
        "error if neither is supplied",
        "merging raises cardinality error",
        "get preview of merged items",
        "preview allows cardinality error",
    ),
)
def test_create_merged_item(
    extracted_items: list[AnyExtractedModel],
    rule_set: AnyRuleSetRequest | None,
    validate_cardinality: Literal[True, False],
    expected: Any,  # noqa: ANN401
) -> None:
    try:
        merged_item = create_merged_item(
            Identifier.generate(seed=42),
            extracted_items,
            rule_set,
            validate_cardinality,
        )
    except MExError as error:
        if str(expected) not in f"{error}: {error.__cause__}":
            raise AssertionError(expected) from error
    else:
        assert {k: v for k, v in merged_item.model_dump().items() if v} == expected
