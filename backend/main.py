from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
from striprtf.striprtf import rtf_to_text
import tempfile
from parsers import parse_context_files
import re

app = FastAPI(
    title="Degree Planner API",
    description="API for Union Theological Seminary M.Div + Columbia MSSW dual degree planning",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Course(BaseModel):
    code: str
    name: str
    credits: int
    description: str
    prerequisites: List[str] = []
    corequisites: List[str] = []
    semester_offered: List[str] = []
    school: str  # "UTS" or "Columbia"

class Requirement(BaseModel):
    name: str
    description: str
    credits_required: int
    courses: List[str] = []
    sub_requirements: List['Requirement'] = []

class DegreePlan(BaseModel):
    student_name: str
    start_semester: str
    courses: Dict[str, str] = {}  # course_code -> semester
    total_credits: int = 0

# Global data storage
PARSED_DATA = {
    "courses": [],
    "requirements": [],
    "parse_results": [],
    "total_files_processed": 0,
    "total_courses_found": 0,
    "total_requirements_found": 0
}

# NEW_GLOBAL_STORAGE
PLAN_STORAGE: Dict[str, DegreePlan] = {}
PLANS_DIR = os.path.join(os.path.dirname(__file__), "plans")
os.makedirs(PLANS_DIR, exist_ok=True)

# Helper functions to load/save plans to disk

def _plan_file_path(student_name: str) -> str:
    safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", student_name)
    return os.path.join(PLANS_DIR, f"{safe_name}.json")


def _save_plan_to_disk(plan: DegreePlan):
    file_path = _plan_file_path(plan.student_name)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(plan.model_dump(), f, indent=2)


def _load_plan_from_disk(student_name: str) -> Optional[DegreePlan]:
    file_path = _plan_file_path(student_name)
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return DegreePlan(**data)

# END_NEW_GLOBAL_STORAGE

def load_context_data():
    """Load and parse all files from the _context directory at startup"""
    global PARSED_DATA
    
    print("Loading and parsing files from _context directory...")
    
    # Check if _context directory exists
    context_dir = "../_context"
    if not os.path.exists(context_dir):
        print(f"Warning: {context_dir} directory not found. Using sample data.")
        return
    
    # Parse all files
    parsed_data = parse_context_files(context_dir)
    
    if "error" in parsed_data:
        print(f"Error parsing context files: {parsed_data['error']}")
        return
    
    # Update global data
    PARSED_DATA = parsed_data
    
    print(f"Successfully parsed {parsed_data['total_files_processed']} files")
    print(f"Found {parsed_data['total_courses_found']} courses")
    print(f"Found {parsed_data['total_requirements_found']} requirements")
    
    # Print some sample courses for verification
    if parsed_data['courses']:
        print("\nSample courses found:")
        for course in parsed_data['courses'][:3]:
            print(f"  - {course.get('code', 'N/A')}: {course.get('name', 'N/A')}")

# Load data at startup
load_context_data()

# Sample data (fallback if parsing fails)
SAMPLE_COURSES = [
    {
        "code": "BIBL101",
        "name": "Introduction to Biblical Studies",
        "credits": 3,
        "description": "Foundational course in biblical interpretation and analysis",
        "prerequisites": [],
        "corequisites": [],
        "semester_offered": ["Fall", "Spring"],
        "school": "UTS"
    },
    {
        "code": "THEO201",
        "name": "Systematic Theology",
        "credits": 3,
        "description": "Study of theological doctrines and systematic approaches",
        "prerequisites": ["BIBL101"],
        "corequisites": [],
        "semester_offered": ["Spring"],
        "school": "UTS"
    },
    {
        "code": "SW501",
        "name": "Social Work Practice I",
        "credits": 3,
        "description": "Introduction to social work practice and methods",
        "prerequisites": [],
        "corequisites": [],
        "semester_offered": ["Fall", "Spring"],
        "school": "Columbia"
    }
]

SAMPLE_REQUIREMENTS = [
    {
        "name": "UTS M.Div Core Requirements",
        "description": "Core theological education requirements",
        "credits_required": 60,
        "courses": ["BIBL101", "THEO201"],
        "sub_requirements": []
    },
    {
        "name": "Columbia MSSW Requirements",
        "description": "Social work degree requirements",
        "credits_required": 60,
        "courses": ["SW501"],
        "sub_requirements": []
    }
]

@app.get("/")
async def root():
    return {"message": "Degree Planner API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/courses", response_model=List[Course])
async def get_courses():
    """Get all available courses"""
    # Use parsed data if available, otherwise fall back to sample data
    courses_data = PARSED_DATA.get("courses", []) if PARSED_DATA.get("courses") else SAMPLE_COURSES
    return [Course(**course) for course in courses_data]

@app.get("/courses/{course_code}", response_model=Course)
async def get_course(course_code: str):
    """Get a specific course by code"""
    # Use parsed data if available, otherwise fall back to sample data
    courses_data = PARSED_DATA.get("courses", []) if PARSED_DATA.get("courses") else SAMPLE_COURSES
    
    for course in courses_data:
        if course["code"] == course_code:
            return Course(**course)
    raise HTTPException(status_code=404, detail="Course not found")

@app.get("/requirements", response_model=List[Requirement])
def get_requirements():
    requirements_data = PARSED_DATA.get('requirements', [])
    # Ensure credits_required is always an int
    for req in requirements_data:
        if 'credits_required' not in req or not isinstance(req['credits_required'], int):
            try:
                req['credits_required'] = int(req.get('credits_required', 0) or 0)
            except Exception:
                req['credits_required'] = 0
    return [Requirement(**req) for req in requirements_data]

@app.get("/parse-status")
async def get_parse_status():
    """Get the status of file parsing"""
    return {
        "total_files_processed": PARSED_DATA.get("total_files_processed", 0),
        "total_courses_found": PARSED_DATA.get("total_courses_found", 0),
        "total_requirements_found": PARSED_DATA.get("total_requirements_found", 0),
        "parse_results": PARSED_DATA.get("parse_results", []),
        "using_parsed_data": len(PARSED_DATA.get("courses", [])) > 0
    }

@app.post("/reload-data")
async def reload_data():
    """Reload and reparse all files from the _context directory"""
    load_context_data()
    return {
        "message": "Data reloaded successfully",
        "total_courses_found": PARSED_DATA.get("total_courses_found", 0),
        "total_requirements_found": PARSED_DATA.get("total_requirements_found", 0)
    }

@app.post("/parse-rtf")
async def parse_rtf(file: UploadFile = File(...)):
    """Parse RTF file and extract text content"""
    if not file.filename.endswith('.rtf'):
        raise HTTPException(status_code=400, detail="File must be an RTF file")
    
    try:
        # Read RTF content
        rtf_content = await file.read()
        rtf_text = rtf_content.decode('utf-8', errors='ignore')
        
        # Convert RTF to plain text
        plain_text = rtf_to_text(rtf_text)
        
        # Basic parsing logic (can be enhanced)
        parsed_data = {
            "filename": file.filename,
            "text_content": plain_text,
            "word_count": len(plain_text.split()),
            "extracted_courses": [],
            "extracted_requirements": []
        }
        
        # Simple course extraction (look for patterns like "COURSE CODE - Course Name")
        lines = plain_text.split('\n')
        for line in lines:
            line = line.strip()
            if ' - ' in line and len(line) > 10:
                # Basic pattern matching for course codes
                parts = line.split(' - ', 1)
                if len(parts) == 2 and len(parts[0]) <= 10:
                    parsed_data["extracted_courses"].append({
                        "code": parts[0].strip(),
                        "name": parts[1].strip()
                    })
        
        return parsed_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing RTF file: {str(e)}")

@app.post("/parse-rtf-batch")
async def parse_rtf_batch(files: List[UploadFile] = File(...)):
    """Parse multiple RTF files"""
    results = []
    
    for file in files:
        if not file.filename.endswith('.rtf'):
            results.append({
                "filename": file.filename,
                "error": "File must be an RTF file"
            })
            continue
        
        try:
            rtf_content = await file.read()
            rtf_text = rtf_content.decode('utf-8', errors='ignore')
            plain_text = rtf_to_text(rtf_text)
            
            results.append({
                "filename": file.filename,
                "text_content": plain_text[:500] + "..." if len(plain_text) > 500 else plain_text,
                "word_count": len(plain_text.split()),
                "status": "success"
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": str(e),
                "status": "error"
            })
    
    return {"results": results}

@app.get("/sample-data")
async def get_sample_data():
    """Get sample data for testing"""
    return {
        "courses": SAMPLE_COURSES,
        "requirements": SAMPLE_REQUIREMENTS
    }

@app.post("/plans", response_model=DegreePlan)
async def save_plan(plan: DegreePlan):
    """Save or update a degree plan for a student"""
    PLAN_STORAGE[plan.student_name] = plan
    _save_plan_to_disk(plan)
    return plan


@app.get("/plans/{student_name}", response_model=DegreePlan)
async def get_plan(student_name: str):
    """Retrieve a saved degree plan by student name"""
    # Check in-memory first
    if student_name in PLAN_STORAGE:
        return PLAN_STORAGE[student_name]
    # Fallback to disk
    plan = _load_plan_from_disk(student_name)
    if plan:
        PLAN_STORAGE[student_name] = plan
        return plan
    raise HTTPException(status_code=404, detail="Degree plan not found")


@app.get("/plans", response_model=List[str])
async def list_plans():
    """List all student names that have saved plans"""
    names = list(PLAN_STORAGE.keys())
    # Include any plans that might exist on disk but not loaded yet
    for filename in os.listdir(PLANS_DIR):
        if filename.endswith(".json"):
            name = filename[:-5]
            if name not in names:
                names.append(name)
    return names

# Allow running with `python main.py` for local dev
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 