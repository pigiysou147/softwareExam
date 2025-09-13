from __future__ import annotations

import os
from typing import Any, Dict, List

import pandas as pd


def save_classification_to_excel(classification: List[Dict[str, Any]], file_path: str) -> str:
    if not classification:
        # 仍然生成一个空模板
        df = pd.DataFrame(
            columns=["database", "schema", "table_name", "column_name", "level", "tags", "reason"]
        )
    else:
        df = pd.DataFrame(classification)

    os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
    df.to_excel(file_path, index=False)
    return file_path

