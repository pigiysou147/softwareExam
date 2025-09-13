from __future__ import annotations

import os
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .db import fetch_schema
from .classifier import classify_rows, refine_with_llm
from .excel import to_excel_base64
from .scraper import fetch_to_markdown


class DbConn(BaseModel):
    host: str
    port: int = 3306
    user: str
    password: str
    database: str


class ClassifyRequest(BaseModel):
    connection: DbConn
    refine_by_llm: bool = Field(default=False)
    ollama_base_url: Optional[str] = Field(default=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    model: str = Field(default=os.getenv("OLLAMA_MODEL", "deepseek-r1:latest"))


class ClassifyResponse(BaseModel):
    rows: List[Dict[str, str]]
    excel_base64: str


app = FastAPI(title="Data Classification Assistant Service")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/classify", response_model=ClassifyResponse)
def classify(req: ClassifyRequest) -> ClassifyResponse:
    try:
        rows = fetch_schema(
            host=req.connection.host,
            port=req.connection.port,
            user=req.connection.user,
            password=req.connection.password,
            database=req.connection.database,
        )
        enriched = classify_rows(rows)
        if req.refine_by_llm:
            enriched = refine_with_llm(enriched, model=req.model, ollama_base_url=req.ollama_base_url)
        excel_b64 = to_excel_base64(enriched)
        return ClassifyResponse(rows=enriched, excel_base64=excel_b64)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ScrapeRequest(BaseModel):
    url: str


class ScrapeResponse(BaseModel):
    markdown: str


@app.post("/scrape", response_model=ScrapeResponse)
def scrape(req: ScrapeRequest) -> ScrapeResponse:
    try:
        md = fetch_to_markdown(req.url)
        return ScrapeResponse(markdown=md)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

