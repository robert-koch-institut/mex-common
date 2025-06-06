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
    **kwargs: Any,  # noqa: ANN401
) -> Generator[_BaseModelT, None, None]:
    """Parse a CSV file into an iterable of the given model type.

    Args:
        path_or_buffer: Location of CSV file or read buffer with CSV content
        into: Type of model to parse
        chunksize: Buffer size for chunked reading
        kwargs: Additional keywords arguments for pandas

    Returns:
        Generator for models
    """
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
            for index, row in chunk.iterrows():
                try:
                    model = into.model_validate(
                        row.replace(to_replace=np.nan, value=None)
                        .replace(regex=r"^\s*$", value=None)
                        .to_dict()
                    )
                    yield model
                except ValidationError as error:
                    logger.error(
                        "parse_csv - %s %s - %s - %s",
                        into.__name__,
                        index,
                        error.__class__.__name__,
                        error.errors(),
                    )
