import os
import re
from typing import List, Dict, Any, Optional
from striprtf.striprtf import rtf_to_text
import PyPDF2
import io

class CourseParser:
    """Parser for extracting course information from RTF and PDF files"""
    
    def __init__(self):
        self.courses = []
        self.requirements = []
    
    def parse_rtf_file(self, file_path: str) -> Dict[str, Any]:
        """Parse an RTF file and extract course information"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                rtf_content = file.read()
            
            plain_text = rtf_to_text(rtf_content)
            return self._extract_courses_from_text(plain_text, file_path)
        except Exception as e:
            return {
                "filename": os.path.basename(file_path),
                "error": f"Error parsing RTF file: {str(e)}",
                "status": "error"
            }
    
    def parse_pdf_file(self, file_path: str) -> Dict[str, Any]:
        """Parse a PDF file and extract course information"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                plain_text = ""
                
                for page in pdf_reader.pages:
                    plain_text += page.extract_text() + "\n"
            
            return self._extract_courses_from_text(plain_text, file_path)
        except Exception as e:
            return {
                "filename": os.path.basename(file_path),
                "error": f"Error parsing PDF file: {str(e)}",
                "status": "error"
            }
    
    def _extract_courses_from_text(self, text: str, file_path: str) -> Dict[str, Any]:
        """Extract course information from plain text"""
        filename = os.path.basename(file_path)
        extracted_courses = []
        extracted_requirements = []
        
        # Split text into lines for processing
        lines = text.split('\n')
        
        # Improved course extraction pattern: e.g. BIBL 101, SW501, NT 233E
        course_pattern = re.compile(r'\b([A-Z]{2,4}\s?\d{3,4}[A-Z]?)\b[\s:–—-]+(.+?)(?:\s*\((\d+)\s*credits?\))?$', re.IGNORECASE)
        
        # Requirement extraction patterns (unchanged for now)
        requirement_patterns = [
            r'(Core\s+Requirements?|Electives?|Required\s+Courses?|Program\s+Requirements?)',
            r'(Total\s+Credits?\s*:\s*\d+)',
            r'(\d+\s+credits?\s+required)',
        ]
        
        current_section = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Filter out lines that are all uppercase, years, or not likely to be courses
            if line.isupper() or re.match(r'^(19|20)\d{2}$', line) or re.match(r'^[A-Z ]{5,}$', line):
                continue
            # Filter out lines that are just a year or semester
            if re.match(r'^(fall|spring|summer|winter)\s*\d{4}$', line, re.IGNORECASE):
                continue
            # Check for section headers
            for pattern in requirement_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    current_section = match.group(1)
                    extracted_requirements.append({
                        "name": current_section,
                        "description": line,
                        "credits_required": self._extract_credits(line),
                        "courses": []
                    })
                    break
            # Check for course pattern
            match = course_pattern.search(line)
            if match:
                course_code = match.group(1).replace(' ', '').upper()
                course_name = match.group(2).strip()
                credits = match.group(3) if match.group(3) else self._extract_credits(line)
                # Filter out junk course codes (e.g., codes that are not at least 2 letters + 3 digits)
                if not re.match(r'^[A-Z]{2,4}\d{3,4}[A-Z]?$', course_code):
                    continue
                # Determine school based on course code or filename
                school = self._determine_school(course_code, filename)
                # Determine semester offered based on filename
                semester_offered = self._determine_semester(filename)
                course = {
                    "code": course_code,
                    "name": course_name,
                    "credits": int(credits) if credits else 3,
                    "description": self._extract_description(line),
                    "prerequisites": self._extract_prerequisites(line),
                    "corequisites": [],
                    "semester_offered": semester_offered,
                    "school": school
                }
                extracted_courses.append(course)
                # Add to current requirement section if exists
                if current_section and extracted_requirements:
                    extracted_requirements[-1]["courses"].append(course_code)
        return {
            "filename": filename,
            "text_content": text[:1000] + "..." if len(text) > 1000 else text,
            "word_count": len(text.split()),
            "extracted_courses": extracted_courses,
            "extracted_requirements": extracted_requirements,
            "status": "success"
        }
    
    def _extract_credits(self, text: str) -> Optional[int]:
        """Extract credit information from text"""
        credit_patterns = [
            r'(\d+)\s*credits?',
            r'\((\d+)\s*credits?\)',
            r'(\d+)\s*credit\s*hours?',
        ]
        
        for pattern in credit_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None
    
    def _extract_description(self, text: str) -> str:
        """Extract course description from text"""
        # Look for description after course name
        if ' - ' in text:
            parts = text.split(' - ', 1)
            if len(parts) > 1:
                return parts[1].strip()
        return ""
    
    def _extract_prerequisites(self, text: str) -> List[str]:
        """Extract prerequisites from text"""
        prereq_patterns = [
            r'prerequisite[s]?\s*:\s*([^.]+)',
            r'prerequisite[s]?\s*\(([^)]+)\)',
            r'prereq[s]?\s*:\s*([^.]+)',
        ]
        
        for pattern in prereq_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                prereq_text = match.group(1)
                # Extract course codes from prerequisite text
                course_codes = re.findall(r'[A-Z]{2,4}\s?\d{3,4}[A-Z]?', prereq_text)
                return [code.strip() for code in course_codes]
        return []
    
    def _determine_school(self, course_code: str, filename: str) -> str:
        """Determine which school a course belongs to"""
        # UTS course patterns
        uts_patterns = [
            r'BIBL', r'THEO', r'HIST', r'ETH', r'MIN', r'PAST', r'LANG'
        ]
        
        # Columbia course patterns
        columbia_patterns = [
            r'SW', r'SOC', r'PSYCH', r'POL', r'ECON'
        ]
        
        for pattern in uts_patterns:
            if re.search(pattern, course_code, re.IGNORECASE):
                return "UTS"
        
        for pattern in columbia_patterns:
            if re.search(pattern, course_code, re.IGNORECASE):
                return "Columbia"
        
        # Default based on filename
        if 'MDiv' in filename or 'UTS' in filename:
            return "UTS"
        elif 'MSSW' in filename or 'Columbia' in filename:
            return "Columbia"
        
        return "UTS"  # Default to UTS
    
    def _determine_semester(self, filename: str) -> List[str]:
        """Determine semester offered based on filename"""
        filename_lower = filename.lower()
        
        if 'fall' in filename_lower:
            return ["Fall"]
        elif 'spring' in filename_lower:
            return ["Spring"]
        elif 'summer' in filename_lower:
            return ["Summer"]
        else:
            return ["Fall", "Spring"]  # Default to both semesters

def parse_context_files(context_dir: str = "_context") -> Dict[str, Any]:
    """Parse all RTF and PDF files in the context directory"""
    parser = CourseParser()
    all_courses = []
    all_requirements = []
    parse_results = []
    
    if not os.path.exists(context_dir):
        return {
            "error": f"Context directory '{context_dir}' not found",
            "courses": [],
            "requirements": []
        }
    
    # Get all RTF and PDF files
    rtf_files = [f for f in os.listdir(context_dir) if f.endswith('.rtf')]
    pdf_files = [f for f in os.listdir(context_dir) if f.endswith('.pdf')]
    
    # Parse RTF files
    for rtf_file in rtf_files:
        file_path = os.path.join(context_dir, rtf_file)
        result = parser.parse_rtf_file(file_path)
        parse_results.append(result)
        
        if result.get("status") == "success":
            all_courses.extend(result.get("extracted_courses", []))
            all_requirements.extend(result.get("extracted_requirements", []))
    
    # Parse PDF files
    for pdf_file in pdf_files:
        file_path = os.path.join(context_dir, pdf_file)
        result = parser.parse_pdf_file(file_path)
        parse_results.append(result)
        
        if result.get("status") == "success":
            all_courses.extend(result.get("extracted_courses", []))
            all_requirements.extend(result.get("extracted_requirements", []))
    
    # Remove duplicate courses based on course code
    unique_courses = {}
    for course in all_courses:
        code = course.get("code", "")
        if code and code not in unique_courses:
            unique_courses[code] = course
    
    # Remove duplicate requirements based on name
    unique_requirements = {}
    for req in all_requirements:
        name = req.get("name", "")
        if name and name not in unique_requirements:
            unique_requirements[name] = req
    
    return {
        "parse_results": parse_results,
        "courses": list(unique_courses.values()),
        "requirements": list(unique_requirements.values()),
        "total_files_processed": len(rtf_files) + len(pdf_files),
        "total_courses_found": len(unique_courses),
        "total_requirements_found": len(unique_requirements)
    } 