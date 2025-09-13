from __future__ import annotations

import re
from typing import Dict, List, Optional

import requests
from rapidfuzz import fuzz


LEVELS = [
    "L1-HighlySensitive",
    "L2-Sensitive",
    "L3-Internal",
    "L4-Public",
]


KEYWORD_LEVEL_MAP = {
    # L1
    "id_card": "L1-HighlySensitive",
    "身份证": "L1-HighlySensitive",
    "password": "L1-HighlySensitive",
    "passwd": "L1-HighlySensitive",
    "pwd": "L1-HighlySensitive",
    "credit_card": "L1-HighlySensitive",
    "bank_card": "L1-HighlySensitive",
    "银行卡": "L1-HighlySensitive",
    "cvv": "L1-HighlySensitive",
    "ssn": "L1-HighlySensitive",
    "token": "L1-HighlySensitive",
    "secret": "L1-HighlySensitive",
    # L2
    "phone": "L2-Sensitive",
    "mobile": "L2-Sensitive",
    "手机号": "L2-Sensitive",
    "email": "L2-Sensitive",
    "mail": "L2-Sensitive",
    "姓名": "L2-Sensitive",
    "name": "L2-Sensitive",
    "address": "L2-Sensitive",
    "住址": "L2-Sensitive",
    "birthday": "L2-Sensitive",
    "birth": "L2-Sensitive",
    "gender": "L2-Sensitive",
    # L3
    "salary": "L3-Internal",
    "amount": "L3-Internal",
    "revenue": "L3-Internal",
    "cost": "L3-Internal",
    "internal": "L3-Internal",
}


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower())


def rule_based_classify(column_name: str, data_type: str, comment: str = "") -> Dict[str, str]:
    text = " ".join(filter(None, [column_name, data_type, comment]))
    normalized = normalize(text)

    best_level = "L4-Public"
    best_score = 0

    for keyword, level in KEYWORD_LEVEL_MAP.items():
        score = fuzz.partial_ratio(normalize(keyword), normalized)
        if score > best_score and score >= 80:
            best_score = score
            best_level = level

    tags: List[str] = []
    for keyword in KEYWORD_LEVEL_MAP.keys():
        if fuzz.partial_ratio(normalize(keyword), normalized) >= 90:
            tags.append(keyword)

    rationale = f"rule:{best_score} on text='{text[:80]}'"
    return {"level": best_level, "tags": ",".join(sorted(set(tags))), "rationale": rationale}


def refine_with_llm(
    rows: List[Dict[str, str]],
    model: str = "deepseek-r1:latest",
    ollama_base_url: str = "http://localhost:11434",
    temperature: float = 0.2,
    timeout: int = 120,
) -> List[Dict[str, str]]:
    """Call Ollama generate API to refine level/tags. Expects Ollama is running locally.

    API: POST {ollama_base_url}/api/generate
    {"model":"...","prompt":"..."}
    """
    try:
        prompt_lines = [
            "You are a data classification expert. Assign one level to each field: ",
            "- L1-HighlySensitive, L2-Sensitive, L3-Internal, L4-Public.",
            "Return CSV with columns: table,column,data_type,comment,level,tags.",
        ]
        for r in rows[:3000]:  # limit prompt size
            prompt_lines.append(
                f"{r['table']},{r['column']},{r.get('data_type','')},{r.get('comment','')},{r.get('level','')},{r.get('tags','')}"
            )
        prompt = "\n".join(prompt_lines)
        resp = requests.post(
            f"{ollama_base_url.rstrip('/')}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "options": {"temperature": temperature},
                "stream": False,
            },
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        text = data.get("response", "")
        refined: List[Dict[str, str]] = []
        for line in text.splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 6:
                continue
            refined.append(
                {
                    "table": parts[0],
                    "column": parts[1],
                    "data_type": parts[2],
                    "comment": parts[3],
                    "level": parts[4] if parts[4] in LEVELS else "L4-Public",
                    "tags": parts[5],
                }
            )
        # merge back by (table,column)
        by_key = {(r["table"], r["column"]): r for r in refined}
        merged: List[Dict[str, str]] = []
        for r in rows:
            key = (r["table"], r["column"])
            if key in by_key:
                nr = r.copy()
                nr.update({"level": by_key[key]["level"], "tags": by_key[key]["tags"], "rationale": "llm-refined"})
                merged.append(nr)
            else:
                merged.append(r)
        return merged
    except Exception:
        # fallback silently to original rows if LLM call fails
        return rows


def classify_rows(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    enriched: List[Dict[str, str]] = []
    for r in rows:
        rb = rule_based_classify(r["column"], r.get("data_type", ""), r.get("comment", ""))
        nr = r.copy()
        nr.update(rb)
        enriched.append(nr)
    return enriched

