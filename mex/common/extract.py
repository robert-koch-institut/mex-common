from collections import defaultdict
from collections.abc import Generator
from os import PathLike
from typing import TYPE_CHECKING, Any, TypeVar, Union

import numpy as np
import pandas as pd
from pydantic import ValidationError

from mex.common.logging import logger

if TYPE_CHECKING:  # pragma: no cover
    from pandas._typing import Dtype, ReadCsvBuffer

    from mex.common.models import BaseModel

_BaseModelT = TypeVar("_BaseModelT", bound="BaseModel")

PANDAS_DTYPE_MAP = defaultdict(
    lambda: "string",
    {bool: "bool", float: "Float64", int: "Int64"},
)


def get_dtypes_for_model(model: type["BaseModel"]) -> dict[str, "Dtype"]:
    """Get the basic dtypes per field for a model from the `PANDAS_DTYPE_MAP`.

    Args:
        model: Model class for which to get pandas data types per field alias

    Returns:
        Mapping from field alias to dtype strings
    """
    return {
        f.alias or name: PANDAS_DTYPE_MAP[f.annotation or type(None)]
        for name, f in model.model_fields.items()
    }


def parse_csv(
    path_or_buffer: Union[str, PathLike[str], "ReadCsvBuffer[Any]"],
    into: type[_BaseModelT],
    chunksize: int = 10000,
    summary_batch_size: int = 10000,
    **kwargs: Any,  # noqa: ANN401
) -> Generator[_BaseModelT, None, None]:
    """Parse a CSV file into an iterable of the given model type.

    Args:
        path_or_buffer: Location of CSV file or read buffer with CSV content
        into: Type of model to parse
        chunksize: Buffer size for chunked reading
        summary_batch_size: Batch size for summary logs
        kwargs: Additional keywords arguments for pandas

    Returns:
        Generator for models
    """
    error_summary: defaultdict[str, int] = defaultdict(int)
    total_rows_processed = 0
    total_rows_successfully_processed = 0

    with pd.read_csv(
        path_or_buffer,
        chunksize=chunksize,
        dtype=get_dtypes_for_model(into),  # type: ignore[arg-type]
        **kwargs,
    ) as reader:
        for i, chunk in enumerate(reader):
            logger.info(
                "parse_csv - %s chunk %s - OK",
                into.__name__,
                i,
            )
            for row in chunk.iterrows():
                try:
                    model = into.model_validate(
                        row.replace(to_replace=np.nan, value=None)
                        .replace(regex=r"^\s*$", value=None)
                        .to_dict()
                    )
                    total_rows_successfully_processed += 1
                    yield model
                except ValidationError as error:
                    for validation_error in error.errors():
                        error_type = validation_error["type"]
                        error_summary[error_type] += 1

                total_rows_processed += 1

                if total_rows_processed % summary_batch_size == 0 and error_summary:
                    logger.error(
                        "Summarizing errors for batch starting at row %s",
                        total_rows_processed - summary_batch_size,
                    )
                    for error_type, count in error_summary.items():
                        logger.error(
                            " - Error type '%s': %s occurences", error_type, count
                        )
                    error_summary.clear()

    if error_summary:
        logger.error("Summarizing errors for remaining rows")
        for error_type, count in error_summary.items():
            logger.error(" - Error type '%s': %s occurences", error_type, count)
        logger.info(
            "Successfully processed %s items.", total_rows_successfully_processed
        )
