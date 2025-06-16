import os
import re
import logging
from typing import List, Dict, Any

import pdfplumber
from collections import defaultdict

try:
    from striprtf.striprtf import rtf_to_text
except ImportError:  # striprtf is optional – only required for RTF parsing
    rtf_to_text = None  # type: ignore

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------------------------------------------------------
# 1. CONFIGURABLE DATA DIRECTORY & REQUIREMENT MAP
# ---------------------------------------------------------------------------
DATA_DIR = os.getenv("DATA_DIR", "./_context")

REQ_MAP: Dict[str, List[str]] = {
    "BX": ["Bible/Sacred Texts"],
    "BIBL": ["Bible/Sacred Texts"],
    "HB": ["Bible/Sacred Texts"],
    "NT": ["Bible/Sacred Texts"],
    "CH": ["Historical Studies"],
    "HS": ["Historical Studies"],
    "PR": ["Practical Theology"],
    "PT": ["Practical Theology"],
    "TH": ["Theology & Ethics"],
    "ETH": ["Theology & Ethics"],
    "IE": ["Interreligious Engagement"],
    # Social-work prefixes
    "SW": ["MSSW Core Courses"],
}

# ---------------------------------------------------------------------------
# 2. TWO-STEP ROW EXTRACTION
# ---------------------------------------------------------------------------

def _table_rows_from_pdf(path: str) -> List[List[str]]:
    rows: List[List[str]] = []
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables() or []
                for tbl in tables:
                    for r in tbl:
                        if r and any(cell is not None and str(cell).strip() for cell in r):
                            rows.append([str(cell).strip() if cell is not None else "" for cell in r])
    except Exception as e:
        logger.warning(f"Failed table extraction for {path}: {e}")
    return rows


def _fallback_rows_from_text(text: str) -> List[List[str]]:
    rows: List[List[str]] = []
    for raw_line in text.split("\n"):
        line = raw_line.rstrip()
        # Split when we have runs of 2+ spaces (PDF column spacing)
        parts = re.split(r"\s{2,}", line)
        parts = [p.strip() for p in parts if p.strip()]
        if parts:
            rows.append(parts)
    return rows


def extract_rows(path: str) -> List[List[str]]:
    """Return a flat list-of-rows where each row is list[str]. Works for PDF & RTF."""
    path = os.path.join(DATA_DIR, os.path.basename(path))
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    rows: List[List[str]] = []

    if path.lower().endswith(".pdf"):
        # First try table extraction
        rows = _table_rows_from_pdf(path)
        if rows:
            return rows  # success
        # Fallback to text-line splitting
        try:
            with pdfplumber.open(path) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception as e:
            logger.error(f"Failed text extraction for {path}: {e}")
            raise
        rows = _fallback_rows_from_text(text)
        return rows

    elif path.lower().endswith(".rtf"):
        if rtf_to_text is None:
            raise RuntimeError("striprtf is required for RTF parsing – install via `pip install striprtf`. ")
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = rtf_to_text(f.read())
        rows = _fallback_rows_from_text(text)
        return rows
    else:
        raise ValueError("Unsupported file format: " + path)

# ---------------------------------------------------------------------------
# 3. COURSE ROW -> OBJECT (DICT)
# ---------------------------------------------------------------------------

_HEADER_KEYWORDS = {
    "course code": "Course Code",
    "course title": "Course Title",
    "credits": "Credits",
    "instructor": "Instructor",
    "days": "Days/Times",  # allow older schedules that split days/time
    "days/times": "Days/Times",
    "description": "Description",
}


def _find_header_row(rows: List[List[str]]) -> int:
    for i, row in enumerate(rows):
        row_join = " ".join(cell.lower() for cell in row)
        if "course" in row_join and "code" in row_join:
            return i
    raise RuntimeError("Header row with 'Course Code' not found.")


def _build_col_index(header_row: List[str]) -> Dict[str, int]:
    mapping: Dict[str, int] = {}
    for idx, cell in enumerate(header_row):
        cell_clean = cell.strip().lower()
        for key, canonical in _HEADER_KEYWORDS.items():
            if key in cell_clean:
                mapping[canonical] = idx
                break
    # Ensure required columns present
    required = ["Course Code", "Course Title", "Credits"]
    for req in required:
        if req not in mapping:
            raise RuntimeError(f"Required column '{req}' missing from header.")
    return mapping


def row_to_course(row: List[str], col_index: Dict[str, int]) -> Dict[str, Any]:
    def _get(col: str) -> str:
        idx = col_index.get(col)
        return row[idx] if idx is not None and idx < len(row) else ""

    code_raw = _get("Course Code")
    return {
        "code": code_raw.strip(),
        "title": _get("Course Title").strip(),
        "credits": float(re.split(r"\s", _get("Credits"))[0]) if _get("Credits") else 0.0,
        "professor": _get("Instructor").strip(),
        "schedule": _get("Days/Times").strip(),
        "description": _get("Description").strip(),
    }

# ---------------------------------------------------------------------------
# 4. PARSE FILE -> {courses, totals}
# ---------------------------------------------------------------------------

def parse_file(path: str) -> Dict[str, Any]:
    path = os.path.join(DATA_DIR, os.path.basename(path))
    try:
        rows = extract_rows(path)
        header_idx = _find_header_row(rows)
        col_index = _build_col_index(rows[header_idx])

        courses: List[Dict[str, Any]] = []
        prev_course: Dict[str, Any] | None = None
        for raw_row in rows[header_idx + 1 :]:
            if not raw_row:
                continue
            course_code = raw_row[col_index["Course Code"]] if col_index["Course Code"] < len(raw_row) else ""
            if not course_code.strip():
                # Wrapped description – append
                if prev_course is not None:
                    prev_course["description"] += " " + raw_row[col_index["Description"]] if "Description" in col_index and col_index["Description"] < len(raw_row) else " " + " ".join(raw_row)
                continue
            # Normal row
            course = row_to_course(raw_row, col_index)
            # Map to requirements & accumulate credits later
            courses.append(course)
            prev_course = course

        # Requirement mapping & credit tally
        totals: Dict[str, float] = defaultdict(float)
        for c in courses:
            prefix = re.split(r"\s", c["code"])[0]
            fields = REQ_MAP.get(prefix, [])
            c["fields"] = fields
            for f in fields:
                totals[f] += c["credits"]

        return {"courses": courses, "totals": dict(totals)}

    except Exception as e:
        logger.error(f"Failed parsing {path}: {e}")
        raise

# ---------------------------------------------------------------------------
# 5. OPTIONAL DIRECTORY PARSE HELPERS
# ---------------------------------------------------------------------------

def parse_directory(directory: str | None = None) -> Dict[str, Any]:
    directory = directory or DATA_DIR
    data: List[Dict[str, Any]] = []
    for fname in os.listdir(directory):
        if fname.lower().endswith((".pdf", ".rtf")):
            try:
                data.append(parse_file(os.path.join(directory, fname)))
            except Exception as e:
                logger.warning(f"Skipping {fname}: {e}")
    # Aggregate totals across files
    agg_totals: Dict[str, float] = defaultdict(float)
    all_courses: List[Dict[str, Any]] = []
    for d in data:
        all_courses.extend(d["courses"])
        for k, v in d["totals"].items():
            agg_totals[k] += v
    return {"courses": all_courses, "totals": dict(agg_totals)} 