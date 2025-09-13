from __future__ import annotations

from typing import Dict, List

import pymysql


def fetch_schema(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
) -> List[Dict[str, str]]:
    """Return schema rows for given database from INFORMATION_SCHEMA.

    Each row: {
        database, table, column, data_type, is_nullable, column_key, column_default, extra, comment
    }
    """
    connection = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with connection.cursor() as cursor:
            sql = (
                "SELECT c.TABLE_SCHEMA AS database_name, c.TABLE_NAME AS table_name, "
                "c.COLUMN_NAME AS column_name, c.DATA_TYPE AS data_type, c.IS_NULLABLE AS is_nullable, "
                "c.COLUMN_KEY AS column_key, c.COLUMN_DEFAULT AS column_default, c.EXTRA AS extra, "
                "IFNULL(c.COLUMN_COMMENT, '') AS column_comment "
                "FROM INFORMATION_SCHEMA.COLUMNS c "
                "WHERE c.TABLE_SCHEMA = %s "
                "ORDER BY c.TABLE_NAME, c.ORDINAL_POSITION"
            )
            cursor.execute(sql, (database,))
            rows = cursor.fetchall()
            result: List[Dict[str, str]] = []
            for r in rows:
                result.append(
                    {
                        "database": r["database_name"],
                        "table": r["table_name"],
                        "column": r["column_name"],
                        "data_type": r["data_type"],
                        "is_nullable": r["is_nullable"],
                        "column_key": r["column_key"],
                        "column_default": r["column_default"],
                        "extra": r["extra"],
                        "comment": r["column_comment"],
                    }
                )
            return result
    finally:
        try:
            connection.close()
        except Exception:
            pass

