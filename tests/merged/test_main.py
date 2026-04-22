import random
from typing import Any

import pytest
from pytest import FixtureRequest

from mex.common.exceptions import MExError
from mex.common.merged.main import (
    _apply_lenient_fallback,
    _collect_additive_values,
    _collect_extracted_values,
    _collect_preventive_sources,
    _collect_subtractive_values,
    _create_merged_dict,
    _ensure_rule_set,
    _filter_usable_values,
    _get_merged_class,
    _pick_usable_values,
    create_merged_item,
    create_merged_item_for_publishing_target,
)
from mex.common.merged.types import SourceAndValueList, SourceList, ValueList
from mex.common.models import (
    MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
    ActivityRuleSetRequest,
    AdditiveContactPoint,
    AdditivePerson,
    AdditiveResource,
    AnyExtractedModel,
    AnyMergedModel,
    AnyPreviewModel,
    AnyRuleSetRequest,
    ContactPointRuleSetRequest,
    ExtractedActivity,
    ExtractedContactPoint,
    ExtractedPerson,
    ExtractedResource,
    MergedPerson,
    PersonRuleSetRequest,
    PreventivePerson,
    PreventiveResource,
    PreviewPerson,
    ResourceRuleSetRequest,
    SubtractiveActivity,
    SubtractiveContactPoint,
    SubtractivePerson,
    SubtractiveResource,
    WorkflowContactPoint,
)
from mex.common.testing import Joker
from mex.common.types import (
    AccessRestriction,
    AnyValidation,
    Identifier,
    MergedPrimarySourceIdentifier,
    PublishingTarget,
    Text,
    TextLanguage,
    Theme,
    Validation,
)


def test_collect_extracted_values() -> None:
    person = ExtractedPerson(
        fullName="Squidward, Dr. med.",
        email="squidward@ocean.clinic",
        hadPrimarySource=Identifier("squidwardSourceId"),
        identifierInPrimarySource="squidward",
    )

    result = _collect_extracted_values("email", [person])

    assert result == [(Identifier("squidwardSourceId"), "squidward@ocean.clinic")]


def test_collect_additive_values() -> None:
    rule_set = PersonRuleSetRequest(
        additive=AdditivePerson(givenName=["Bubbles", "Barnacle"])
    )

    result = _collect_additive_values("givenName", rule_set)

    assert result == [
        (MEX_PRIMARY_SOURCE_STABLE_TARGET_ID, "Bubbles"),
        (MEX_PRIMARY_SOURCE_STABLE_TARGET_ID, "Barnacle"),
    ]


def test_collect_subtractive_values() -> None:
    rule_set = PersonRuleSetRequest(
        subtractive=SubtractivePerson(
            email=["pineapple@fruit.ocean", "rock@ocean.floor"]
        )
    )

    result = _collect_subtractive_values("email", rule_set)

    assert result == ["pineapple@fruit.ocean", "rock@ocean.floor"]


def test_collect_preventive_sources() -> None:
    rule_set = PersonRuleSetRequest(
        preventive=PreventivePerson(email=[Identifier("preventPlankton")])
    )

    result = _collect_preventive_sources("email", rule_set)

    assert result == ["preventPlankton"]


@pytest.mark.parametrize(
    ("sources_values", "prevented", "subtracted", "expected"),
    [
        pytest.param([], [], [], [], id="empty_input"),
        pytest.param(
            [("src1", "value1"), ("src2", "value2")],
            [],
            [],
            ["value1", "value2"],
            id="no_filtering",
        ),
        pytest.param(
            [("src1", "value1"), ("src2", "value2")],
            ["src1"],
            [],
            ["value2"],
            id="prevent_source",
        ),
        pytest.param(
            [("src1", "value1"), ("src2", "value2")],
            [],
            ["value1"],
            ["value2"],
            id="subtract_value",
        ),
        pytest.param(
            [("src1", "value"), ("src2", "value")],
            [],
            [],
            ["value"],
            id="deduplicate",
        ),
    ],
)
def test_filter_usable_values(
    sources_values: SourceAndValueList,
    prevented: SourceList,
    subtracted: ValueList,
    expected: ValueList,
) -> None:
    result = _filter_usable_values(sources_values, prevented, subtracted)

    assert result == expected


def test_apply_lenient_fallback_empty() -> None:
    assert _apply_lenient_fallback((), (), []) == []


def test_apply_lenient_fallback() -> None:
    extracted = [(MergedPrimarySourceIdentifier("src1"), "extracted_value")]
    additive = [(MergedPrimarySourceIdentifier("src2"), "additive_value")]
    subtracted: ValueList = ["subtracted_value"]

    result = _apply_lenient_fallback(extracted, additive, subtracted)

    assert result == ["extracted_value"]


def test_pick_usable_values_strict() -> None:
    person = ExtractedPerson(
        fullName="Alice",
        email="alice@example.com",
        hadPrimarySource=Identifier.generate(seed=1),
        identifierInPrimarySource="alice",
    )
    rule_set = PersonRuleSetRequest()

    result = _pick_usable_values("email", [person], rule_set, Validation.STRICT)

    assert result == ["alice@example.com"]


def test_pick_usable_values_lenient() -> None:
    person = ExtractedPerson(
        fullName="Alice",
        hadPrimarySource=Identifier.generate(seed=1),
        identifierInPrimarySource="alice",
    )
    rule_set = PersonRuleSetRequest(
        subtractive=SubtractivePerson(email="blocked@example.com")
    )

    result = _pick_usable_values("email", [person], rule_set, Validation.LENIENT)

    assert result == ["blocked@example.com"]


def test_create_merged_dict_strict() -> None:
    person = ExtractedPerson(
        fullName="Alice",
        hadPrimarySource=Identifier.generate(seed=1),
        identifierInPrimarySource="alice",
    )
    rule_set = PersonRuleSetRequest()

    result = _create_merged_dict(["fullName"], [person], rule_set, Validation.STRICT)

    assert result == {"fullName": ["Alice"]}


@pytest.mark.parametrize(
    ("extracted_items", "rule_set", "validation", "expected"),
    [
        pytest.param(
            [],
            PersonRuleSetRequest(),
            Validation.STRICT,
            MergedPerson,
            id="strict_with_rules",
        ),
        pytest.param(
            [],
            PersonRuleSetRequest(),
            Validation.LENIENT,
            PreviewPerson,
            id="lenient_with_rules",
        ),
        pytest.param(
            [
                ExtractedPerson(
                    fullName="Test Person",
                    hadPrimarySource=Identifier.generate(seed=1),
                    identifierInPrimarySource="test",
                )
            ],
            None,
            Validation.STRICT,
            MergedPerson,
            id="strict_no_ruleset",
        ),
        pytest.param(
            [],
            None,
            Validation.STRICT,
            None,
            id="empty_inputs_returns_none",
        ),
    ],
)
def test_get_merged_class(
    extracted_items: list[AnyExtractedModel],
    rule_set: AnyRuleSetRequest | None,
    validation: AnyValidation,
    expected: type[AnyMergedModel | AnyPreviewModel] | None,
) -> None:
    result = _get_merged_class(extracted_items, rule_set, validation)

    assert result == expected


def test_ensure_rule_set_creates_default() -> None:
    result = _ensure_rule_set(None, "Person")

    assert isinstance(result, PersonRuleSetRequest)


def test_ensure_rule_set_returns_existing() -> None:
    existing_rule_set = PersonRuleSetRequest()

    result = _ensure_rule_set(existing_rule_set, "Person")

    assert result is existing_rule_set


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
            id="single_extracted_item",
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
            id="extracted_items_and_rule_set",
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
            id="only_rule_set",
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
            id="only_extracted_items",
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
            id="get_preview_of_merged_items",
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
            id="preview_allows_cardinality_error",
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
            id="ignore_mode_validation_returns_none",
        ),
        pytest.param(
            [
                ExtractedContactPoint(
                    email=[f"{i}@contact-point.com"],
                    hadPrimarySource=Identifier.generate(seed=1),
                    identifierInPrimarySource=f"{i}",
                )
                for i in range(20)
            ],
            ContactPointRuleSetRequest(),
            Validation.IGNORE,
            {
                "email": [
                    "4@contact-point.com",
                    "15@contact-point.com",
                    "1@contact-point.com",
                    "12@contact-point.com",
                    "19@contact-point.com",
                    "11@contact-point.com",
                    "6@contact-point.com",
                    "16@contact-point.com",
                    "10@contact-point.com",
                    "17@contact-point.com",
                    "18@contact-point.com",
                    "14@contact-point.com",
                    "8@contact-point.com",
                    "9@contact-point.com",
                    "7@contact-point.com",
                    "2@contact-point.com",
                    "0@contact-point.com",
                    "3@contact-point.com",
                    "5@contact-point.com",
                    "13@contact-point.com",
                ],
                "entityType": "MergedContactPoint",
                "identifier": Joker(),
            },
            id="stable_order_by_identifier",
        ),
        pytest.param(
            [
                ExtractedResource(
                    identifierInPrimarySource="resource_1",
                    hadPrimarySource=Identifier.generate(seed=42),
                    sizeOfDataBasis="enormous",
                    accessRestriction=AccessRestriction["OPEN"],
                    contact=[Identifier.generate(seed=999)],
                    unitInCharge=[Identifier.generate(seed=999)],
                    theme=[Theme["PUBLIC_HEALTH"]],
                    title=[Text(value="Dummy resource")],
                )
            ],
            ResourceRuleSetRequest(
                additive=AdditiveResource(sizeOfDataBasis="gigantic"),
                subtractive=SubtractiveResource(),
                preventive=PreventiveResource(),
            ),
            Validation.LENIENT,
            {
                "accessRestriction": ["https://mex.rki.de/item/access-restriction-1"],
                "contact": ["bFQoRhcVH5DIax"],
                "entityType": "PreviewResource",
                "identifier": "bFQoRhcVH5DHU6",
                "sizeOfDataBasis": ["enormous", "gigantic"],
                "theme": ["https://mex.rki.de/item/theme-1"],
                "title": [{"language": TextLanguage.EN, "value": "Dummy resource"}],
                "unitInCharge": ["bFQoRhcVH5DIax"],
            },
            id="lenient_validation_allows_multiple_optional_values",
        ),
    ],
)
def test_create_merged_item(
    extracted_items: list[AnyExtractedModel],
    rule_set: AnyRuleSetRequest | None,
    validation: AnyValidation,
    expected: dict[str, Any] | None,
) -> None:
    merged_item = create_merged_item(
        Identifier.generate(seed=42),
        extracted_items,
        rule_set,
        validation,
    )
    if merged_item is None:
        assert expected is None
    else:
        clean_dict = {k: v for k, v in merged_item.model_dump().items() if v}
        assert clean_dict == expected


@pytest.mark.parametrize(
    ("extracted_items", "rule_set", "expected"),
    [
        pytest.param(
            [],
            None,
            "One of rule_set or extracted_items is required.",
            id="error_if_neither_is_supplied",
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
            "List should have at least 1 item after validation, not 0",
            id="merging_raises_cardinality_error",
        ),
    ],
)
def test_create_merged_item_errors(
    extracted_items: list[AnyExtractedModel],
    rule_set: AnyRuleSetRequest | None,
    expected: str,
) -> None:
    with pytest.raises(MExError) as exc_info:
        create_merged_item(
            Identifier.generate(seed=42),
            extracted_items,
            rule_set,
            Validation.STRICT,
        )
    error = exc_info.value
    assert expected in f"{error}: {error.__cause__}"


@pytest.mark.parametrize(
    ("extracted_items", "rule_set", "publishing_target", "expected"),
    [
        pytest.param(
            [
                ExtractedContactPoint(
                    identifierInPrimarySource="orders",
                    hadPrimarySource=Identifier.generate(seed=98),
                    email=["orders@krusty.ocean"],
                )
            ],
            ContactPointRuleSetRequest(
                additive=AdditiveContactPoint(
                    email=["info@krusty.ocean"],
                ),
                workflow=WorkflowContactPoint(
                    forbiddenPublishingTarget=["datenkompass"],
                ),
            ),
            "invenio",
            {
                "email": ["orders@krusty.ocean", "info@krusty.ocean"],
                "entityType": "MergedContactPoint",
                "identifier": Joker(),
            },
            id="publishing_target_is_valid",
        ),
    ],
)
def test_create_merged_item_for_publishing_target(
    extracted_items: list[AnyExtractedModel],
    rule_set: AnyRuleSetRequest | None,
    publishing_target: PublishingTarget,
    expected: dict[str, Any] | None,
) -> None:
    merged_item = create_merged_item_for_publishing_target(
        Identifier.generate(seed=42),
        extracted_items,
        rule_set,
        Validation.STRICT,
        publishing_target,
    )
    clean_dict = {k: v for k, v in merged_item.model_dump().items() if v}
    assert clean_dict == expected


@pytest.mark.parametrize(
    ("extracted_items", "rule_set", "publishing_target", "expected"),
    [
        pytest.param(
            [
                ExtractedContactPoint(
                    identifierInPrimarySource="orders",
                    hadPrimarySource=Identifier.generate(seed=98),
                    email=["orders@krusty.ocean"],
                )
            ],
            ContactPointRuleSetRequest(
                workflow=WorkflowContactPoint(
                    forbiddenPublishingTarget=["datenkompass"],
                ),
            ),
            "datenkompass",
            "Merged item forbidden to be published to datenkompass.",
            id="publishing_rule_prevents_creation_of_merged_item",
        ),
    ],
)
def test_create_merged_item_for_publishing_target_errors(
    extracted_items: list[AnyExtractedModel],
    rule_set: AnyRuleSetRequest | None,
    publishing_target: PublishingTarget,
    expected: str,
) -> None:
    with pytest.raises(MExError) as exc_info:
        create_merged_item_for_publishing_target(
            Identifier.generate(seed=42),
            extracted_items,
            rule_set,
            Validation.STRICT,
            publishing_target,
        )
    error = exc_info.value
    assert expected in f"{error}: {error.__cause__}"


@pytest.fixture(autouse=True)
def skip_fuzzing_tests_unless_requested(request: FixtureRequest) -> None:
    """Skips fuzzing test if fuzzing is not explicitly requested and mex.artificial is not installed.

    Rationale: fuzzing depends on mex-artificial, which in turn depends on mex-common. This is a dependency loop.
    If we introduce breaking changes in mex-common, mex-artificial must be updated to accomodate these breaking changes.
    We do not want to break our entire test pipeline if this happens and therefore isolate fuzzing tests.
    """
    # RATIONALE
    config = request.config
    is_test_marked_as_fuzzing = request.node.get_closest_marker("fuzzing") is not None
    if not is_test_marked_as_fuzzing:
        return
    is_fuzzing_explicitly_requested = config.option.markexpr and "fuzzing" in str(
        config.option.markexpr
    )
    if not is_fuzzing_explicitly_requested:
        pytest.skip(
            "Skipping fuzzing tests as they were not explicitly requested using pytest -m fuzzing"
        )


@pytest.mark.fuzzing
def test_create_merged_item_with_artificial_data() -> None:
    """Return artificial dummy data."""
    from mex.artificial.helpers import (  # noqa: PLC0415
        create_artificial_items_and_rule_sets,
    )

    seed = random.randint(-(2**31), 2**31 - 1)  # noqa: S311
    for i, container in enumerate(
        create_artificial_items_and_rule_sets(
            locale="de_DE",
            seed=seed,
            count=500,
            chattiness=8,
        )
    ):
        extracted_items = (
            [] if container.extracted_item is None else [container.extracted_item]
        )
        rule_set = container.rule_set
        returned = create_merged_item(
            Identifier.generate(seed=42),
            extracted_items,
            rule_set,
            Validation.LENIENT,
        )

        if extracted_items == [] and rule_set is None:
            assert returned is None, (
                f"Expected `None` for artificial item number {i} with seed {seed}"
            )
        else:
            assert returned is not None, (
                f"Expected Preview Item for artificial item number {i} with seed {seed}"
            )
