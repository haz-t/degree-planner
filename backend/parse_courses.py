import os
import re
import json
import pdfplumber
from collections import defaultdict

# Example REQ_MAP (customize as needed)
REQ_MAP = {
    "BX": ["Bible/Sacred Texts"],
    "NT": ["Bible/Sacred Texts", "Cross-Testament"],
    "CH": ["Historical Studies"],
    "HB": ["Bible/Sacred Texts"],
    "OT": ["Bible/Sacred Texts"],
    "TH": ["Theological Studies"],
    "PT": ["Practical Theology"],
    "ET": ["Ethics"],
    "SW": ["Social Work"],
    "MSSW": ["Social Work"],
    # ... add more mappings as needed
}

DATA_DIR = "../_context"
OUTPUT_DIR = "../_context/json_output"

PDFS = [
    ("2025-Fall-Course-Schedule.pdf", "Fall 2025"),
    ("2026-Spring-Course-Schedule.pdf", "Spring 2026"),
    ("2025-2026-Courses-Revised-May-2025.pdf", "2025-2026"),
    ("MDiv-Program-Guide.AY-24-25.pdf", "MDiv Guide"),
    ("ML.MDSW-C.24-25.pdf", "ML.MDSW-C"),
]

os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_rows(pdf_path):
    """
    Extract rows from a PDF using tables if possible, else fallback to regex-splitting raw text.
    Returns a list of rows (each row is a list of columns).
    """
    rows = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            if tables and any(tables):
                for table in tables:
                    for row in table:
                        if any(cell and cell.strip() for cell in row):
                            rows.append([cell.strip() if cell else "" for cell in row])
            else:
                text = page.extract_text() or ""
                # Remove headers/footers/page numbers
                text = re.sub(r"Page \d+|Union Theological Seminary.*", "", text)
                for line in text.splitlines():
                    if not line.strip():
                        continue
                    # Split on multiple spaces or tabs
                    row = re.split(r"\t| {2,}", line)
                    rows.append([cell.strip() for cell in row])
    return rows

def row_to_course(row):
    """
    Map a row to a course dict. Adjust indices as needed for your PDFs.
    """
    # Example: [code, title, credits, professor, schedule, description]
    course = {
        "code": row[0] if len(row) > 0 else "",
        "title": row[1] if len(row) > 1 else "",
        "credits": float(row[2]) if len(row) > 2 and row[2].replace('.', '', 1).isdigit() else 0,
        "professor": row[3] if len(row) > 3 else "",
        "schedule": row[4] if len(row) > 4 else "",
        "description": row[5] if len(row) > 5 else "",
        "fields": [],
        "delivery": "",
    }
    return course

def assign_fields_and_tally(courses, req_map):
    """
    Tag each course with its requirement fields and tally total credits per field.
    """
    field_credits = defaultdict(float)
    for course in courses:
        prefix = course["code"].split()[0] if course["code"] else ""
        course["fields"] = req_map.get(prefix, [])
        for field in course["fields"]:
            field_credits[field] += course["credits"]
    return dict(field_credits)

def parse_pdf_to_json(pdf_path, semester, req_map):
    """
    Full pipeline: extract, clean, map, assign fields, and output JSON for a semester.
    """
    rows = extract_rows(pdf_path)
    courses = []
    last_course = None
    
    for row in rows:
        # Skip empty rows
        if not row or not any(cell.strip() for cell in row):
            continue
            
        # Check if this looks like a course code (e.g., BX101, NT201, etc.)
        first_col = row[0].strip() if row else ""
        if re.match(r"^[A-Z]{2,4}\d{2,4}[A-Z]?", first_col):
            course = row_to_course(row)
            courses.append(course)
            last_course = course
        elif last_course and first_col:
            # This might be a continuation of the previous course
            if len(row) > 1:
                last_course["description"] += " " + " ".join(row).strip()
            else:
                last_course["description"] += " " + first_col
    
    # Clean up descriptions and filter out invalid courses
    valid_courses = []
    for course in courses:
        if course["code"] and course["title"]:  # Only include courses with both code and title
            course["description"] = re.sub(r"\s+", " ", course["description"]).strip()
            valid_courses.append(course)
    
    totals = assign_fields_and_tally(valid_courses, req_map)
    output = {
        "semester": semester,
        "totals": totals,
        "courses": valid_courses,
    }
    return output

def parse_requirements_to_json(requirements_pdf_path):
    """
    Parse requirements PDF to JSON. (Stub: implement as needed for your requirements format)
    """
    requirements = {
        "MDiv": {"Bible/Sacred Texts": 10, "Historical Studies": 6},
        "MSSW": {"Practical Theology": 7}
    }
    return requirements

def main():
    for pdf_file, semester in PDFS:
        pdf_path = os.path.join(DATA_DIR, pdf_file)
        if not os.path.exists(pdf_path):
            print(f"File not found: {pdf_path}")
            continue
        print(f"Processing {pdf_file}...")
        semester_json = parse_pdf_to_json(pdf_path, semester, REQ_MAP)
        out_path = os.path.join(OUTPUT_DIR, f"{semester.replace(' ', '_')}.json")
        with open(out_path, "w") as f:
            json.dump(semester_json, f, indent=2)
        print(f"Wrote {out_path} with {len(semester_json['courses'])} courses")
    
    # Parse requirements
    req_pdf = os.path.join(DATA_DIR, "MDiv-Program-Guide.AY-24-25.pdf")
    req_json = parse_requirements_to_json(req_pdf)
    with open(os.path.join(OUTPUT_DIR, "requirements.json"), "w") as f:
        json.dump(req_json, f, indent=2)
    print("Wrote requirements.json")

if __name__ == "__main__":
    main() 