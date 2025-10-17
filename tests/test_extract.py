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
false,"another bad row",2000-01-01,,""
true,"another good row",2001-02-03,3.14,42
        """.strip()
    )

    parsed_models = list(parse_csv(buffer, DummyModel, chunksize=2))
    assert len(parsed_models) == 2
    assert parsed_models[0].str_ == "good row"
    assert parsed_models[1].str_ == "another good row"

    records = caplog.records

    assert (
        len(records) == 7
    )  # 2 info logs for chunks, 1+3 error logs and 1 info log for amount processed

    assert records[0].levelname == "INFO"
    assert "parse_csv - DummyModel chunk 0 - OK" in records[0].message
    assert records[1].levelname == "INFO"
    assert "parse_csv - DummyModel chunk 1 - OK" in records[1].message

    assert records[2].levelname == "ERROR"
    assert "Summarizing errors for remaining rows" in records[2].message
    assert records[3].levelname == "ERROR"
    assert "Error type 'date_type': 1 occurrences" in records[3].message
    assert records[4].levelname == "ERROR"
    assert "Error type 'float_type': 2 occurrences" in records[4].message
    assert records[5].levelname == "ERROR"
    assert "Error type 'int_type': 2 occurrences" in records[5].message

    assert records[6].levelname == "INFO"
    assert "Successfully processed 2 items." in records[6].message


def test_parse_csv_batch_summary(caplog: LogCaptureFixture) -> None:
    buffer = StringIO(
        """
bool_,str_,date_,float_,int_
true,"good",2000-01-01,1.0,1
false,"bad1",,,
false,"bad2",,,
true,"good",2000-01-01,1.0,1
false,"bad3",,,
        """.strip()
    )

    parsed_models = list(parse_csv(buffer, DummyModel, summary_batch_size=3))
    assert len(parsed_models) == 2
    assert parsed_models[0].str_ == "good"
    assert parsed_models[1].str_ == "good"

    records = caplog.records

    assert (
        len(records) == 10
    )  # 1 info log for chunk, 1+3+1+3 error logs for 2 batches and 1 info log for amount processed

    assert records[0].levelname == "INFO"
    assert "parse_csv - DummyModel chunk 0 - OK" in records[0].message

    assert records[1].levelname == "ERROR"
    assert "Summarizing errors for batch with rows 1 to 3" in records[1].message
    assert records[2].levelname == "ERROR"
    assert "Error type 'date_type': 2 occurrences" in records[2].message
    assert records[3].levelname == "ERROR"
    assert "Error type 'float_type': 2 occurrences" in records[3].message
    assert records[4].levelname == "ERROR"
    assert "Error type 'int_type': 2 occurrences" in records[4].message

    assert records[5].levelname == "ERROR"
    assert "Summarizing errors for remaining rows" in records[5].message
    assert records[6].levelname == "ERROR"
    assert "Error type 'date_type': 1 occurrences" in records[6].message
    assert records[7].levelname == "ERROR"
    assert "Error type 'float_type': 1 occurrences" in records[7].message
    assert records[8].levelname == "ERROR"
    assert "Error type 'int_type': 1 occurrences" in records[8].message

    assert records[9].levelname == "INFO"
    assert "Successfully processed 2 items." in records[9].message
