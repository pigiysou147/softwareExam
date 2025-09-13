from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import orjson
from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field

from .classifier import (
    IntrospectionResult,
    classify_schema_with_llm,
    introspect_database_schema,
)
from .excel_utils import save_classification_to_excel


def orjson_dumps(v: Any, *, default: Any) -> str:
    return orjson.dumps(v, default=default).decode()


app = FastAPI(default_response_class=JSONResponse)


class IntrospectRequest(BaseModel):
    database_url: Optional[str] = Field(
        default=os.getenv("DATABASE_URL"), description="SQLAlchemy 连接串 eg. postgresql+psycopg://user:pass@host:5432/db"
    )


class ClassifyRequest(BaseModel):
    database_url: Optional[str] = Field(default=None)
    schema: Optional[List[IntrospectionResult]] = Field(default=None)
    policy_text: Optional[str] = Field(default=None, description="分级分类规则文本（可选）")
    llm_base_url: Optional[str] = Field(default=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1"))
    llm_api_key: Optional[str] = Field(default=os.getenv("LLM_API_KEY", "ollama"))
    llm_model: Optional[str] = Field(default=os.getenv("LLM_MODEL", "deepseek-r1:7b"))
    temperature: Optional[float] = Field(default=0.2)
    top_p: Optional[float] = Field(default=0.9)


class ExportRequest(BaseModel):
    classification: List[Dict[str, Any]]
    output_filename: Optional[str] = Field(default="db_classification.xlsx")


class ClassifyAndExportRequest(BaseModel):
    database_url: Optional[str] = Field(default=os.getenv("DATABASE_URL"))
    policy_text: Optional[str] = Field(default=None)
    llm_base_url: Optional[str] = Field(default=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1"))
    llm_api_key: Optional[str] = Field(default=os.getenv("LLM_API_KEY", "ollama"))
    llm_model: Optional[str] = Field(default=os.getenv("LLM_MODEL", "deepseek-r1:7b"))
    temperature: Optional[float] = Field(default=0.2)
    top_p: Optional[float] = Field(default=0.9)
    output_filename: Optional[str] = Field(default="db_classification.xlsx")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/introspect")
def introspect(req: IntrospectRequest) -> Dict[str, Any]:
    if not req.database_url:
        raise HTTPException(status_code=400, detail="database_url is required")
    result = introspect_database_schema(req.database_url)
    return {"schema": [r.model_dump() for r in result]}


@app.post("/classify")
def classify(req: ClassifyRequest) -> Dict[str, Any]:
    if not req.schema and not req.database_url:
        raise HTTPException(status_code=400, detail="either schema or database_url is required")
    schema: List[IntrospectionResult]
    if req.schema:
        schema = [IntrospectionResult(**s) if isinstance(s, dict) else s for s in req.schema]  # type: ignore[arg-type]
    else:
        schema = introspect_database_schema(req.database_url or "")

    classification = classify_schema_with_llm(
        schema=schema,
        llm_base_url=req.llm_base_url,
        llm_api_key=req.llm_api_key,
        llm_model=req.llm_model,
        policy_text=req.policy_text,
        temperature=req.temperature or 0.2,
        top_p=req.top_p or 0.9,
    )
    return {"classification": classification}


@app.post("/export-excel")
def export_excel(req: ExportRequest) -> Dict[str, Any]:
    output_dir = os.getenv("OUTPUT_DIR", "/data/outputs")
    os.makedirs(output_dir, exist_ok=True)
    file_path = save_classification_to_excel(req.classification, os.path.join(output_dir, req.output_filename))
    return {"file_path": file_path}


@app.get("/download/{filename}")
def download(filename: str):
    output_dir = os.getenv("OUTPUT_DIR", "/data/outputs")
    file_path = os.path.join(output_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="file not found")
    return FileResponse(path=file_path, filename=filename)


@app.post("/classify_and_export")
def classify_and_export(req: ClassifyAndExportRequest) -> Dict[str, Any]:
    if not req.database_url:
        raise HTTPException(status_code=400, detail="database_url is required")

    schema = introspect_database_schema(req.database_url)
    classification = classify_schema_with_llm(
        schema=schema,
        llm_base_url=req.llm_base_url,
        llm_api_key=req.llm_api_key,
        llm_model=req.llm_model,
        policy_text=req.policy_text,
        temperature=req.temperature or 0.2,
        top_p=req.top_p or 0.9,
    )

    output_dir = os.getenv("OUTPUT_DIR", "/data/outputs")
    os.makedirs(output_dir, exist_ok=True)
    file_path = save_classification_to_excel(classification, os.path.join(output_dir, req.output_filename))

    preview_rows = min(5, len(classification))
    return {
        "file_path": file_path,
        "preview": classification[:preview_rows],
        "count": len(classification),
    }

