from datetime import date
from io import StringIO

from pytest import LogCaptureFixture

from mex.common.extract import get_dtypes_for_model, parse_csv
from mex.common.models import BaseModel


class DummyModel(BaseModel):
    bool_: bool
    str_: str
    date_: date
    float_: float
    int_: int


def test_get_dtypes_for_model() -> None:
    assert get_dtypes_for_model(DummyModel) == {
        "bool_": "bool",
        "str_": "string",
        "date_": "string",
        "float_": "Float64",
        "int_": "Int64",
    }


def test_parse_csv(caplog: LogCaptureFixture) -> None:
    buffer = StringIO(
        """
bool_,str_,date_,float_,int_
true,"good row",2000-01-01,2.718,42
false,"bad row",,,
    """.strip()
    )

    parsed_models = list(parse_csv(buffer, DummyModel, chunksize=2))
    assert len(parsed_models) == 1
    assert parsed_models[0].model_dump() == {  # good row
        "bool_": True,
        "date_": date(2000, 1, 1),
        "float_": 2.718,
        "int_": 42,
        "str_": "good row",
    }
    assert len(caplog.text.splitlines()) == 2
    good_row_log, bad_row_log = caplog.text.splitlines()
    assert "parse_csv - DummyModel chunk 0 - OK" in good_row_log
    assert "parse_csv - DummyModel 1 - ValidationError" in bad_row_log
