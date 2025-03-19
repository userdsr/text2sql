from collections.abc import Generator
from typing import Any

import records
from sqlalchemy import text
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class SQLExecuteTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        db_uri = tool_parameters.get("db_uri") or self.runtime.credentials.get("db_uri")
        db = records.Database(db_uri)
        query = tool_parameters.get("query").strip()
        format = tool_parameters.get("format", "json")

        
        if query.lower().startswith('select'):
            rows = db.query(query)
            if format == 'json':
                result = rows.as_dict()
                for r in result:
                    yield self.create_json_message(r)
            elif format == 'md':
                result = str(rows.dataset)
                yield self.create_text_message(result)
            elif format == 'csv':
                result = rows.export('csv').encode()
                yield self.create_blob_message(result, meta={'mime_type': 'text/csv', 'filename': 'result.csv'})
            elif format == 'yaml':
                result = rows.export('yaml').encode()
                yield self.create_blob_message(result, meta={'mime_type': 'text/yaml', 'filename': 'result.yaml'})
            elif format == 'xlsx':
                result = rows.export('xlsx')
                yield self.create_blob_message(result, meta={'mime_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'filename': 'result.xlsx'})
            elif format == 'html':
                result = rows.export('html').encode()
                yield self.create_blob_message(result, meta={'mime_type': 'text/html', 'filename': 'result.html'})
            else:
                raise ValueError(f"Unsupported format: {format}")
        elif query.lower().startswith('desc') or query.lower().startswith('describe'):
            rows = db.query(desc_query)

            if format == 'json':
                result = rows.as_dict()
                for r in result:
                    yield self.create_json_message(r)
            elif format == 'md':
                result = str(rows.dataset)
                yield self.create_text_message(result)
            elif format == 'csv':
                result = rows.export('csv').encode()
                yield self.create_blob_message(result, meta={'mime_type': 'text/csv', 'filename': f'{table_name}_desc.csv'})
            elif format == 'yaml':
                result = rows.export('yaml').encode()
                yield self.create_blob_message(result, meta={'mime_type': 'text/yaml', 'filename': f'{table_name}_desc.yaml'})
            elif format == 'xlsx':
                result = rows.export('xlsx')
                yield self.create_blob_message(result, meta={'mime_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'filename': f'{table_name}_desc.xlsx'})
            elif format == 'html':
                result = rows.export('html').encode()
                yield self.create_blob_message(result, meta={'mime_type': 'text/html', 'filename': f'{table_name}_desc.html'})
            else:
                raise ValueError(f"Unsupported format: {format}")
        else:
             with db.get_connection() as conn: 
                trans = conn._conn.begin()
                try:
                    result = conn._conn.execute(text(query))
                    affected_rows = result.rowcount
                    trans.commit()
                    yield self.create_text_message(f"Query executed successfully. Affected rows: {affected_rows}")
                except Exception as e:
                    trans.rollback()
                    yield self.create_text_message(f"Error: {str(e)}")
