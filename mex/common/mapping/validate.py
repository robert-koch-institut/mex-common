import re
import subprocess
import sys
from os import PathLike
from pathlib import Path
from typing import TextIO

from mex.common.logging import echo


def _get_schema_path_from_handle(handle: TextIO) -> str | None:
    schema_pattern = re.compile(r"^# yaml-language-server: \$schema=(.*\.json)")
    match: re.Match[str] | None = None
    for line in handle:
        if match := schema_pattern.search(line):
            break
    if match:
        return match.group(1)
    return None


def validate_mappings() -> None:
    """Validate each mapping file in sys.argv[1:] against the respective schema.

    Each argument is expected to be path to a mapping file.

    The path to the schema is read from the file body line:
    `# yaml-language-server: $schema=path/to/schema.json`
    """
    invalid_mappings = []
    echo("Validating mappings...")
    for mapping_path in sys.argv[1:]:
        msg = mapping_path
        with open(mapping_path, "r") as f:
            schema_path_relative_to_mapping = _get_schema_path_from_handle(f)
        if not schema_path_relative_to_mapping:
            raise ValueError(f"Could not find schema in `{mapping_path}`")
        schema_path = Path(mapping_path).parent / schema_path_relative_to_mapping
        args: list[str | PathLike[str]] = [
            "check-jsonschema",
            "--schemafile",
            schema_path,
            mapping_path,
        ]
        process = subprocess.run(
            args,  # noqa: S603 # user controls the dynamic input
            capture_output=True,
            text=True,
        )
        if process.returncode == 0:
            echo(msg + " PASS", fg="green")
        else:
            echo(msg + " FAIL", fg="red")
            echo("Details:")
            echo(process.stdout)
            invalid_mappings.append(mapping_path)
    if invalid_mappings:
        echo(
            "The following mappings did not validate:\n" + "\n".join(invalid_mappings),
        )
        exit(1)
    exit(0)
