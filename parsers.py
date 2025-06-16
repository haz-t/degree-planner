"""
PDF parsers for extracting course and requirement data from Union Theological Seminary documents
"""
import pdfplumber
import re
from typing import List, Dict, Tuple, Optional
from models import Course, Requirement
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CourseScheduleParser:
    """Parser for course schedule PDFs"""
    
    def __init__(self):
        self.course_pattern = re.compile(
            r'([A-Z]{2,4}\s+\d{3,4}[A-Z]?)\s*'  # Course code
            r'([^0-9\n]+?)\s*'  # Title
            r'([A-Za-z\s,\.]+?)\s*'  # Faculty
            r'(\d+(?:\.\d+)?)\s*'  # Credits
            r'([MTWRF]+)\s*'  # Days
            r'([0-9:]+-[0-9:]+(?:AM|PM)?)\s*'  # Time
            r'([A-Za-z\s]+?)\s*'  # Delivery mode
            r'([^0-9\n]{20,100})',  # Description
            re.MULTILINE | re.DOTALL
        )
    
    def parse_schedule_pdf(self, filepath: str, semester: str) -> List[Course]:
        """Parse a course schedule PDF and extract course information"""
        courses = []
        
        try:
            with pdfplumber.open(filepath) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
                # Debug: print first 500 characters of extracted text
                logger.info(f"[DEBUG] First 500 chars from {filepath}:\n{text[:500]}")
                
                # Find course entries
                matches = self.course_pattern.finditer(text)
                
                for match in matches:
                    try:
                        code = match.group(1).strip()
                        title = match.group(2).strip()
                        faculty = match.group(3).strip()
                        credits = float(match.group(4))
                        days = match.group(5).strip()
                        time = match.group(6).strip()
                        delivery_mode = match.group(7).strip()
                        description = match.group(8).strip()[:200]  # Limit description length
                        
                        # Create unique ID
                        course_id = f"{code}_{semester}_{faculty.split()[0]}"
                        
                        course = Course(
                            id=course_id,
                            code=code,
                            title=title,
                            faculty=faculty,
                            credits=credits,
                            days=days,
                            time=time,
                            semester=semester,
                            delivery_mode=delivery_mode,
                            description=description
                        )
                        
                        courses.append(course)
                        
                    except (IndexError, ValueError) as e:
                        logger.warning(f"Failed to parse course match: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error parsing PDF {filepath}: {e}")
            
        return courses


class MDivRequirementParser:
    """Parser for MDiv program requirements"""
    
    def __init__(self):
        self.requirement_patterns = {
            'bible': re.compile(r'Bible|Sacred\s+Texts?', re.IGNORECASE),
            'historical': re.compile(r'Historical\s+Studies?', re.IGNORECASE),
            'interreligious': re.compile(r'Interreligious\s+Engagement', re.IGNORECASE),
            'practical': re.compile(r'Practical\s+Theology', re.IGNORECASE),
            'theology_ethics': re.compile(r'Theology\s+&\s+Ethics|Theology\s+and\s+Ethics', re.IGNORECASE),
            'field_ed': re.compile(r'Field\s+Education|Field\s+Ed', re.IGNORECASE),
            'electives': re.compile(r'Electives?', re.IGNORECASE)
        }
        
        self.credit_pattern = re.compile(r'(\d+(?:\.\d+)?)\s*(?:credit|credits)', re.IGNORECASE)
    
    def parse_mdiv_requirements(self, filepath: str) -> List[Requirement]:
        """Parse MDiv program guide and extract requirements"""
        requirements = []
        
        try:
            with pdfplumber.open(filepath) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
                # Debug: print first 500 characters of extracted text
                logger.info(f"[DEBUG] First 500 chars from {filepath}:\n{text[:500]}")
                
                # Define core MDiv requirements with default credit minima
                core_requirements = [
                    ('bible', 'Bible/Sacred Texts', 12.0),
                    ('historical', 'Historical Studies', 9.0),
                    ('interreligious', 'Interreligious Engagement', 6.0),
                    ('practical', 'Practical Theology', 12.0),
                    ('theology_ethics', 'Theology & Ethics', 12.0),
                    ('field_ed', 'Field Education', 6.0),
                    ('electives', 'Electives', 15.0)
                ]
                
                for req_id, label, default_credits in core_requirements:
                    # Try to find specific credit requirements in text
                    pattern = self.requirement_patterns.get(req_id)
                    if pattern:
                        matches = pattern.finditer(text)
                        for match in matches:
                            # Look for credit information near the match
                            start = max(0, match.start() - 200)
                            end = min(len(text), match.end() + 200)
                            context = text[start:end]
                            
                            # Extract credit requirement
                            credit_match = self.credit_pattern.search(context)
                            if credit_match:
                                credits = float(credit_match.group(1))
                            else:
                                credits = default_credits
                            
                            requirement = Requirement(
                                id=req_id,
                                label=label,
                                min_credits=credits
                            )
                            requirements.append(requirement)
                            break  # Only take first match for each requirement
                    
                    # If no match found, create with default credits
                    if not any(r.id == req_id for r in requirements):
                        requirement = Requirement(
                            id=req_id,
                            label=label,
                            min_credits=default_credits
                        )
                        requirements.append(requirement)
                        
        except Exception as e:
            logger.error(f"Error parsing MDiv requirements from {filepath}: {e}")
            
        return requirements


class DualDegreeParser:
    """Parser for dual-degree specific requirements"""
    
    def parse_dual_degree_requirements(self, filepath: str) -> List[Requirement]:
        """Parse dual-degree planner and extract MSSW requirements"""
        requirements = []
        
        try:
            with pdfplumber.open(filepath) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
                # Debug: print first 500 characters of extracted text
                logger.info(f"[DEBUG] First 500 chars from {filepath}:\n{text[:500]}")
                
                # Add MSSW-specific requirements
                mssw_requirements = [
                    ('mssw_core', 'MSSW Core Courses', 30.0),
                    ('integrative_seminar', 'Integrative Seminar', 3.0),
                    ('social_work_practice', 'Social Work Practice', 12.0),
                    ('social_work_research', 'Social Work Research', 6.0),
                    ('social_work_policy', 'Social Work Policy', 6.0)
                ]
                
                for req_id, label, credits in mssw_requirements:
                    requirement = Requirement(
                        id=req_id,
                        label=label,
                        min_credits=credits
                    )
                    requirements.append(requirement)
                    
        except Exception as e:
            logger.error(f"Error parsing dual-degree requirements from {filepath}: {e}")
            
        return requirements


def parse_all_data() -> Tuple[List[Course], List[Requirement]]:
    """Parse all PDF files and return courses and requirements"""
    course_parser = CourseScheduleParser()
    mdiv_parser = MDivRequirementParser()
    dual_parser = DualDegreeParser()
    
    # Parse course schedules
    courses = []
    courses.extend(course_parser.parse_schedule_pdf('_context/2025-Fall-Course-Schedule.pdf', 'Fall 2025'))
    courses.extend(course_parser.parse_schedule_pdf('_context/2026-Spring-Course-Schedule.pdf', 'Spring 2026'))
    
    # Parse requirements
    requirements = []
    requirements.extend(mdiv_parser.parse_mdiv_requirements('_context/MDiv-Program-Guide.AY-24-25.pdf'))
    requirements.extend(dual_parser.parse_dual_degree_requirements('_context/ML.MDSW-C.24-25.pdf'))
    
    # Link courses to requirements (simplified mapping)
    link_courses_to_requirements(courses, requirements)
    
    return courses, requirements


def link_courses_to_requirements(courses: List[Course], requirements: List[Requirement]):
    """Link courses to requirements based on course codes and titles"""
    # Simplified mapping - in practice, this would be more sophisticated
    mapping = {
        'bible': ['BIBL', 'BIBLE', 'SCRIPTURE'],
        'historical': ['HIST', 'HISTORY', 'CHURCH'],
        'interreligious': ['INTER', 'RELIGION', 'DIVERSITY'],
        'practical': ['PRAC', 'MINISTRY', 'PASTORAL'],
        'theology_ethics': ['THEO', 'ETHICS', 'MORAL'],
        'field_ed': ['FIELD', 'INTERN', 'PRACTICUM'],
        'mssw_core': ['MSSW', 'SOCIAL'],
        'integrative_seminar': ['SEMINAR', 'INTEGRATIVE'],
        'social_work_practice': ['PRACTICE', 'CLINICAL'],
        'social_work_research': ['RESEARCH', 'METHODS'],
        'social_work_policy': ['POLICY', 'ADVOCACY']
    }
    
    for course in courses:
        course_text = f"{course.code} {course.title}".upper()
        
        for req_id, keywords in mapping.items():
            if any(keyword in course_text for keyword in keywords):
                course.satisfies.add(req_id)
                
                # Also add to requirement's satisfied_by set
                for req in requirements:
                    if req.id == req_id:
                        req.satisfied_by.add(course.id)
                        break 