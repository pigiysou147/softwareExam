from __future__ import annotations

import io
import base64
from typing import Dict, List

import pandas as pd


EXCEL_COLUMNS = [
    "database",
    "table",
    "column",
    "data_type",
    "comment",
    "level",
    "tags",
    "rationale",
]


def to_excel_bytes(rows: List[Dict[str, str]]) -> bytes:
    df = pd.DataFrame(rows, columns=EXCEL_COLUMNS)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="classification", index=False)
    return output.getvalue()


def to_excel_base64(rows: List[Dict[str, str]]) -> str:
    return base64.b64encode(to_excel_bytes(rows)).decode("utf-8")

