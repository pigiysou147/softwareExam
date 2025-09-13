from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple

import requests
from sqlalchemy import create_engine, inspect
from tenacity import retry, stop_after_attempt, wait_exponential


@dataclass
class IntrospectionResult:
    database: str
    schema: str
    table_name: str
    column_name: str
    data_type: str
    is_nullable: bool
    is_primary_key: bool

    def model_dump(self) -> Dict[str, Any]:
        return asdict(self)


def introspect_database_schema(database_url: str) -> List[IntrospectionResult]:
    engine = create_engine(database_url)
    inspector = inspect(engine)
    results: List[IntrospectionResult] = []

    default_schema = "public"
    database_name = engine.url.database or "database"
    schemas = inspector.get_schema_names()
    for schema_name in schemas:
        if schema_name.startswith("pg_"):
            continue
        for table_name in inspector.get_table_names(schema=schema_name):
            pk_cols = set(inspector.get_primary_keys(table_name, schema=schema_name) or [])
            for col in inspector.get_columns(table_name, schema=schema_name):
                results.append(
                    IntrospectionResult(
                        database=database_name,
                        schema=schema_name or default_schema,
                        table_name=table_name,
                        column_name=col["name"],
                        data_type=str(col.get("type", "")),
                        is_nullable=bool(col.get("nullable", True)),
                        is_primary_key=col["name"] in pk_cols,
                    )
                )
    return results


def _build_prompt(schema: List[IntrospectionResult], policy_text: Optional[str]) -> str:
    sample_rows = schema[:200]  # 控制上下文长度
    schema_json = [r.model_dump() for r in sample_rows]
    base_policy = (
        policy_text
        or """
你是数据分级与敏感信息识别专家。请根据字段名、数据类型与表语义，为每个字段判定：
- level: 公开、内部、敏感、机密（四选一）
- tags: 逗号分隔标签，如 PII, Account, Credential, Payment, Transaction, Product
- reason: 简要说明判定理由
要求：输出 JSON 数组，每个元素包含字段：database, schema, table_name, column_name, level, tags, reason。
若无法判断请尽量根据经验合理推测。
        """
    ).strip()
    return (
        f"请基于以下数据库结构进行分级分类：\n\n"
        f"策略：\n{base_policy}\n\n"
        f"结构样本（至多200行）：\n{json.dumps(schema_json, ensure_ascii=False)}\n\n"
        f"仅输出 JSON 数组，不要包含多余文本。"
    )


@retry(wait=wait_exponential(multiplier=1, min=1, max=8), stop=stop_after_attempt(3))
def _chat_completion(
    base_url: str,
    api_key: str,
    model: str,
    messages: List[Dict[str, str]],
    temperature: float,
    top_p: float,
) -> str:
    url = base_url.rstrip("/") + "/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
        "stream": False,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    # OpenAI 兼容格式
    content = data["choices"][0]["message"]["content"]
    return content


def _parse_classification(content: str) -> List[Dict[str, Any]]:
    # 简单健壮解析：尝试找到首尾 JSON 数组
    start = content.find("[")
    end = content.rfind("]")
    if start != -1 and end != -1 and end > start:
        content = content[start : end + 1]
    try:
        parsed = json.loads(content)
        if isinstance(parsed, list):
            # 规范化字段
            normalized: List[Dict[str, Any]] = []
            for item in parsed:
                if not isinstance(item, dict):
                    continue
                normalized.append(
                    {
                        "database": item.get("database"),
                        "schema": item.get("schema"),
                        "table_name": item.get("table_name"),
                        "column_name": item.get("column_name"),
                        "level": item.get("level"),
                        "tags": item.get("tags"),
                        "reason": item.get("reason"),
                    }
                )
            return normalized
    except Exception:
        pass
    # 回退空
    return []


def classify_schema_with_llm(
    schema: List[IntrospectionResult],
    llm_base_url: str,
    llm_api_key: str,
    llm_model: str,
    policy_text: Optional[str] = None,
    temperature: float = 0.2,
    top_p: float = 0.9,
) -> List[Dict[str, Any]]:
    prompt = _build_prompt(schema, policy_text)
    messages = [{"role": "user", "content": prompt}]
    content = _chat_completion(
        base_url=llm_base_url,
        api_key=llm_api_key,
        model=llm_model,
        messages=messages,
        temperature=temperature,
        top_p=top_p,
    )
    classification = _parse_classification(content)
    # 若为空，进行简单启发式回退：对常见 PII 关键词打标签
    if not classification:
        keywords = {
            "email": ("敏感", "PII"),
            "phone": ("敏感", "PII"),
            "card": ("机密", "Payment"),
            "password": ("机密", "Credential"),
            "order": ("内部", "Transaction"),
        }
        for r in schema:
            field = r.column_name.lower()
            level, tag = "公开", "General"
            for k, (lev, tg) in keywords.items():
                if k in field:
                    level, tag = lev, tg
                    break
            classification.append(
                {
                    "database": r.database,
                    "schema": r.schema,
                    "table_name": r.table_name,
                    "column_name": r.column_name,
                    "level": level,
                    "tags": tag,
                    "reason": "fallback heuristic",
                }
            )
    return classification

