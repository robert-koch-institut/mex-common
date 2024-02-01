from click.testing import CliRunner

from mex.common.settings import BaseSettings
from mex.ops.mapping.main import generate_mapping_schemas_and_templates


def test_run() -> None:
    settings = BaseSettings.get()
    settings.assets_dir = settings.work_dir
    result = CliRunner().invoke(
        generate_mapping_schemas_and_templates,
        args=[f"--assets-dir={settings.assets_dir}"],
        catch_exceptions=False,
    )
    assert result.exit_code == 0, result.stdout
