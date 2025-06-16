"""
Utility functions for the Dual-Degree Course Planner
"""
from typing import List, Dict, Tuple
from models import Course, Requirement, Plan
import pandas as pd
import json
from datetime import datetime


def validate_requirements(plan: Plan, courses: List[Course], requirements: List[Requirement]) -> Dict[str, Dict]:
    """
    Validate that the plan meets all credit requirements
    
    Returns:
        Dict with validation results for each requirement
    """
    validation_results = {}
    
    # Create course lookup
    course_lookup = {course.id: course for course in courses}
    requirement_lookup = {req.id: req for req in requirements}
    
    for requirement in requirements:
        selected_courses = []
        total_credits = 0.0
        
        # Find all selected courses that satisfy this requirement
        for semester, course_ids in plan.selections.items():
            for course_id in course_ids:
                if course_id in course_lookup:
                    course = course_lookup[course_id]
                    if requirement.id in course.satisfies:
                        selected_courses.append(course)
                        total_credits += course.credits
        
        # Check if requirement is met
        is_met = total_credits >= requirement.min_credits
        deficit = max(0, requirement.min_credits - total_credits)
        
        validation_results[requirement.id] = {
            'requirement': requirement,
            'selected_courses': selected_courses,
            'total_credits': total_credits,
            'min_credits': requirement.min_credits,
            'is_met': is_met,
            'deficit': deficit,
            'status': '✅ Met' if is_met else f'❌ Need {deficit:.1f} more credits'
        }
    
    return validation_results


def calculate_total_credits(plan: Plan, courses: List[Course], semester: str = None) -> float:
    """Calculate total credits for a plan or specific semester"""
    course_lookup = {course.id: course for course in courses}
    total = 0.0
    
    if semester:
        course_ids = plan.get_courses_for_semester(semester)
    else:
        course_ids = []
        for semester_courses in plan.selections.values():
            course_ids.extend(semester_courses)
    
    for course_id in course_ids:
        if course_id in course_lookup:
            total += course_lookup[course_id].credits
    
    return total


def export_plan_to_csv(plan: Plan, courses: List[Course], filepath: str):
    """Export the plan to CSV format"""
    course_lookup = {course.id: course for course in courses}
    
    # Prepare data for CSV
    csv_data = []
    
    for semester, course_ids in plan.selections.items():
        for course_id in course_ids:
            if course_id in course_lookup:
                course = course_lookup[course_id]
                csv_data.append({
                    'Semester': semester,
                    'Course Code': course.code,
                    'Course Title': course.title,
                    'Faculty': course.faculty,
                    'Credits': course.credits,
                    'Days': course.days,
                    'Time': course.time,
                    'Delivery Mode': course.delivery_mode,
                    'Description': course.description,
                    'Satisfies Requirements': ', '.join(course.satisfies)
                })
    
    # Create DataFrame and export
    df = pd.DataFrame(csv_data)
    df.to_csv(filepath, index=False)
    
    return df


def get_courses_by_requirement(courses: List[Course], requirement_id: str) -> List[Course]:
    """Get all courses that satisfy a specific requirement"""
    return [course for course in courses if requirement_id in course.satisfies]


def get_courses_by_semester(courses: List[Course], semester: str) -> List[Course]:
    """Get all courses for a specific semester"""
    return [course for course in courses if course.semester == semester]


def format_time_slot(time_str: str) -> str:
    """Format time slot for better display"""
    if not time_str:
        return "TBD"
    
    # Clean up time format
    time_str = time_str.strip()
    if '-' in time_str:
        start, end = time_str.split('-', 1)
        return f"{start.strip()} - {end.strip()}"
    
    return time_str


def format_days(days_str: str) -> str:
    """Format days for better display"""
    if not days_str:
        return "TBD"
    
    day_map = {
        'M': 'Mon',
        'T': 'Tue', 
        'W': 'Wed',
        'R': 'Thu',
        'F': 'Fri'
    }
    
    formatted_days = []
    for day in days_str.strip():
        if day in day_map:
            formatted_days.append(day_map[day])
    
    return ', '.join(formatted_days) if formatted_days else days_str


def create_sample_data() -> Tuple[List[Course], List[Requirement]]:
    """Create sample data for testing when PDF parsing fails"""
    requirements = [
        Requirement('bible', 'Bible/Sacred Texts', 12.0),
        Requirement('historical', 'Historical Studies', 9.0),
        Requirement('interreligious', 'Interreligious Engagement', 6.0),
        Requirement('practical', 'Practical Theology', 12.0),
        Requirement('theology_ethics', 'Theology & Ethics', 12.0),
        Requirement('field_ed', 'Field Education', 6.0),
        Requirement('electives', 'Electives', 15.0),
        Requirement('mssw_core', 'MSSW Core Courses', 30.0),
        Requirement('integrative_seminar', 'Integrative Seminar', 3.0),
        Requirement('social_work_practice', 'Social Work Practice', 12.0),
        Requirement('social_work_research', 'Social Work Research', 6.0),
        Requirement('social_work_policy', 'Social Work Policy', 6.0)
    ]
    
    courses = [
        Course(
            id='BIBL101_Fall2025_Smith',
            code='BIBL 101',
            title='Introduction to Biblical Studies',
            faculty='Dr. Smith',
            credits=3.0,
            days='MW',
            time='10:00-11:30',
            semester='Fall 2025',
            delivery_mode='In Person',
            description='An introduction to the study of biblical texts and their interpretation.',
            satisfies={'bible'}
        ),
        Course(
            id='HIST201_Fall2025_Jones',
            code='HIST 201',
            title='Church History',
            faculty='Dr. Jones',
            credits=3.0,
            days='TR',
            time='14:00-15:30',
            semester='Fall 2025',
            delivery_mode='In Person',
            description='Survey of Christian history from the early church to the present.',
            satisfies={'historical'}
        ),
        Course(
            id='THEO301_Fall2025_Brown',
            code='THEO 301',
            title='Systematic Theology',
            faculty='Dr. Brown',
            credits=3.0,
            days='F',
            time='09:00-12:00',
            semester='Fall 2025',
            delivery_mode='In Person',
            description='Comprehensive study of Christian theological doctrines.',
            satisfies={'theology_ethics'}
        ),
        Course(
            id='MSSW401_Fall2025_Wilson',
            code='MSSW 401',
            title='Social Work Practice I',
            faculty='Dr. Wilson',
            credits=3.0,
            days='MW',
            time='16:00-17:30',
            semester='Fall 2025',
            delivery_mode='In Person',
            description='Foundation course in social work practice methods.',
            satisfies={'mssw_core', 'social_work_practice'}
        ),
        Course(
            id='PRAC501_Fall2025_Davis',
            code='PRAC 501',
            title='Pastoral Care',
            faculty='Dr. Davis',
            credits=3.0,
            days='TR',
            time='10:00-11:30',
            semester='Fall 2025',
            delivery_mode='In Person',
            description='Introduction to pastoral care and counseling.',
            satisfies={'practical'}
        )
    ]
    
    # Link courses to requirements
    for course in courses:
        for req in requirements:
            if req.id in course.satisfies:
                req.satisfied_by.add(course.id)
    
    return courses, requirements


def get_requirement_progress(plan: Plan, courses: List[Course], requirements: List[Requirement]) -> Dict:
    """Get progress summary for all requirements"""
    validation = validate_requirements(plan, courses, requirements)
    
    total_requirements = len(requirements)
    met_requirements = sum(1 for result in validation.values() if result['is_met'])
    
    return {
        'total_requirements': total_requirements,
        'met_requirements': met_requirements,
        'progress_percentage': (met_requirements / total_requirements * 100) if total_requirements > 0 else 0,
        'validation_results': validation
    } 