from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator, TypeVar, Union

import numpy as np
import pandas as pd
from pydantic import ValidationError

from mex.common.logging import echo

if TYPE_CHECKING:  # pragma: no cover
    from pandas._typing import Dtype, ReadCsvBuffer

    from mex.common.models import BaseModel

ModelT = TypeVar("ModelT", bound="BaseModel")

PANDAS_DTYPE_MAP = defaultdict(
    lambda: "string",
    {bool: "bool", float: "Float64", int: "Int64"},
)


def get_dtypes_for_model(model: type["BaseModel"]) -> dict[str, "Dtype"]:
    """Get the basic dtypes per field for a model from the `PANDAS_DTYPE_MAP`.

    Args:
        model: Model class for which to get pandas dtypes per field alias

    Returns:
        Mapping from field alias to dtype strings
    """
    return {f.alias: PANDAS_DTYPE_MAP[f.type_] for f in model.__fields__.values()}


def parse_csv(
    path_or_buffer: Union[str, Path, "ReadCsvBuffer"],
    into: type[ModelT],
    chunksize: int = 10,
    **kwargs: Any,
) -> Generator[ModelT, None, None]:
    """Parse a CSV file into an iterable of the given model type.

    Args:
        path_or_buffer: Location of CSV file or read buffer with CSV content
        into: Type of model to parse
        chunkssize: Buffer size for chunked reading
        kwargs: Additional keywords arguments for pandas

    Returns:
        Generator for models
    """
    with pd.read_csv(
        path_or_buffer, chunksize=chunksize, dtype=get_dtypes_for_model(into), **kwargs
    ) as reader:
        for chunk in reader:
            for index, row in chunk.iterrows():
                row.replace(to_replace=np.nan, value=None, inplace=True)
                row.replace(regex=r"^\s*$", value=None, inplace=True)
                try:
                    model = into.parse_obj(row)
                    echo(f"[parse csv] {into.__name__} {index} OK")
                    yield model
                except ValidationError as error:
                    echo(
                        f"[parse csv] {into.__name__} {index} "
                        f"{error.__class__.__name__} "
                        f"Errors: {error.errors()}",
                        fg="red",
                    )
