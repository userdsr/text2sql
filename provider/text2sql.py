from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.sql_execute import SQLExecuteTool

class DatabaseProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            for _ in SQLExecuteTool.from_credentials(credentials).invoke(
                tool_parameters={
                    "query": "select 1"
                }
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
