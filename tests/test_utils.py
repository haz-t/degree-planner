"""
Unit tests for utility functions
"""
import pytest
import tempfile
import os
from models import Course, Requirement, Plan
from utils import (
    validate_requirements,
    calculate_total_credits,
    export_plan_to_csv,
    get_courses_by_requirement,
    get_courses_by_semester,
    format_time_slot,
    format_days,
    get_requirement_progress
)


class TestValidation:
    """Test requirement validation functions"""
    
    def test_validate_requirements_met(self):
        """Test validation when all requirements are met"""
        # Create requirements
        bible_req = Requirement('bible', 'Bible/Sacred Texts', 12.0)
        theo_req = Requirement('theology', 'Theology & Ethics', 9.0)
        requirements = [bible_req, theo_req]
        
        # Create courses
        course1 = Course(
            id='BIBL101',
            code='BIBL 101',
            title='Biblical Studies I',
            faculty='Dr. Smith',
            credits=12.0,
            days='MW',
            time='10:00-11:30',
            semester='Fall 2025',
            delivery_mode='In Person',
            description='Biblical studies course',
            satisfies={'bible'}
        )
        
        course2 = Course(
            id='THEO201',
            code='THEO 201',
            title='Theology I',
            faculty='Dr. Jones',
            credits=9.0,
            days='TR',
            time='14:00-15:30',
            semester='Fall 2025',
            delivery_mode='In Person',
            description='Theology course',
            satisfies={'theology'}
        )
        
        courses = [course1, course2]
        
        # Create plan
        plan = Plan()
        plan.add_course('Fall 2025', 'BIBL101')
        plan.add_course('Fall 2025', 'THEO201')
        
        # Validate
        results = validate_requirements(plan, courses, requirements)
        
        assert results['bible']['is_met'] == True
        assert results['bible']['total_credits'] == 12.0
        assert results['bible']['deficit'] == 0.0
        
        assert results['theology']['is_met'] == True
        assert results['theology']['total_credits'] == 9.0
        assert results['theology']['deficit'] == 0.0
    
    def test_validate_requirements_not_met(self):
        """Test validation when requirements are not met"""
        # Create requirement
        bible_req = Requirement('bible', 'Bible/Sacred Texts', 12.0)
        requirements = [bible_req]
        
        # Create course with insufficient credits
        course = Course(
            id='BIBL101',
            code='BIBL 101',
            title='Biblical Studies I',
            faculty='Dr. Smith',
            credits=6.0,
            days='MW',
            time='10:00-11:30',
            semester='Fall 2025',
            delivery_mode='In Person',
            description='Biblical studies course',
            satisfies={'bible'}
        )
        
        courses = [course]
        
        # Create plan
        plan = Plan()
        plan.add_course('Fall 2025', 'BIBL101')
        
        # Validate
        results = validate_requirements(plan, courses, requirements)
        
        assert results['bible']['is_met'] == False
        assert results['bible']['total_credits'] == 6.0
        assert results['bible']['deficit'] == 6.0
    
    def test_validate_requirements_multiple_courses(self):
        """Test validation with multiple courses satisfying same requirement"""
        # Create requirement
        bible_req = Requirement('bible', 'Bible/Sacred Texts', 12.0)
        requirements = [bible_req]
        
        # Create courses
        course1 = Course(
            id='BIBL101',
            code='BIBL 101',
            title='Biblical Studies I',
            faculty='Dr. Smith',
            credits=6.0,
            days='MW',
            time='10:00-11:30',
            semester='Fall 2025',
            delivery_mode='In Person',
            description='Biblical studies course',
            satisfies={'bible'}
        )
        
        course2 = Course(
            id='BIBL201',
            code='BIBL 201',
            title='Biblical Studies II',
            faculty='Dr. Jones',
            credits=6.0,
            days='TR',
            time='14:00-15:30',
            semester='Spring 2026',
            delivery_mode='In Person',
            description='Advanced biblical studies',
            satisfies={'bible'}
        )
        
        courses = [course1, course2]
        
        # Create plan
        plan = Plan()
        plan.add_course('Fall 2025', 'BIBL101')
        plan.add_course('Spring 2026', 'BIBL201')
        
        # Validate
        results = validate_requirements(plan, courses, requirements)
        
        assert results['bible']['is_met'] == True
        assert results['bible']['total_credits'] == 12.0
        assert len(results['bible']['selected_courses']) == 2


class TestCreditCalculations:
    """Test credit calculation functions"""
    
    def test_calculate_total_credits_all_semesters(self):
        """Test calculating total credits across all semesters"""
        # Create courses
        course1 = Course(
            id='BIBL101',
            code='BIBL 101',
            title='Biblical Studies I',
            faculty='Dr. Smith',
            credits=3.0,
            days='MW',
            time='10:00-11:30',
            semester='Fall 2025',
            delivery_mode='In Person',
            description='Biblical studies course'
        )
        
        course2 = Course(
            id='THEO201',
            code='THEO 201',
            title='Theology I',
            faculty='Dr. Jones',
            credits=3.0,
            days='TR',
            time='14:00-15:30',
            semester='Spring 2026',
            delivery_mode='In Person',
            description='Theology course'
        )
        
        courses = [course1, course2]
        
        # Create plan
        plan = Plan()
        plan.add_course('Fall 2025', 'BIBL101')
        plan.add_course('Spring 2026', 'THEO201')
        
        # Calculate total
        total = calculate_total_credits(plan, courses)
        assert total == 6.0
    
    def test_calculate_total_credits_specific_semester(self):
        """Test calculating total credits for a specific semester"""
        # Create courses
        course1 = Course(
            id='BIBL101',
            code='BIBL 101',
            title='Biblical Studies I',
            faculty='Dr. Smith',
            credits=3.0,
            days='MW',
            time='10:00-11:30',
            semester='Fall 2025',
            delivery_mode='In Person',
            description='Biblical studies course'
        )
        
        course2 = Course(
            id='THEO201',
            code='THEO 201',
            title='Theology I',
            faculty='Dr. Jones',
            credits=3.0,
            days='TR',
            time='14:00-15:30',
            semester='Spring 2026',
            delivery_mode='In Person',
            description='Theology course'
        )
        
        courses = [course1, course2]
        
        # Create plan
        plan = Plan()
        plan.add_course('Fall 2025', 'BIBL101')
        plan.add_course('Spring 2026', 'THEO201')
        
        # Calculate for specific semester
        fall_total = calculate_total_credits(plan, courses, 'Fall 2025')
        assert fall_total == 3.0
        
        spring_total = calculate_total_credits(plan, courses, 'Spring 2026')
        assert spring_total == 3.0


class TestFiltering:
    """Test course filtering functions"""
    
    def test_get_courses_by_requirement(self):
        """Test filtering courses by requirement"""
        # Create courses
        course1 = Course(
            id='BIBL101',
            code='BIBL 101',
            title='Biblical Studies I',
            faculty='Dr. Smith',
            credits=3.0,
            days='MW',
            time='10:00-11:30',
            semester='Fall 2025',
            delivery_mode='In Person',
            description='Biblical studies course',
            satisfies={'bible'}
        )
        
        course2 = Course(
            id='THEO201',
            code='THEO 201',
            title='Theology I',
            faculty='Dr. Jones',
            credits=3.0,
            days='TR',
            time='14:00-15:30',
            semester='Fall 2025',
            delivery_mode='In Person',
            description='Theology course',
            satisfies={'theology'}
        )
        
        course3 = Course(
            id='BIBL201',
            code='BIBL 201',
            title='Biblical Studies II',
            faculty='Dr. Brown',
            credits=3.0,
            days='F',
            time='09:00-12:00',
            semester='Spring 2026',
            delivery_mode='In Person',
            description='Advanced biblical studies',
            satisfies={'bible', 'electives'}
        )
        
        courses = [course1, course2, course3]
        
        # Filter by requirement
        bible_courses = get_courses_by_requirement(courses, 'bible')
        assert len(bible_courses) == 2
        assert all('bible' in course.satisfies for course in bible_courses)
        
        theology_courses = get_courses_by_requirement(courses, 'theology')
        assert len(theology_courses) == 1
        assert theology_courses[0].code == 'THEO 201'
    
    def test_get_courses_by_semester(self):
        """Test filtering courses by semester"""
        # Create courses
        course1 = Course(
            id='BIBL101',
            code='BIBL 101',
            title='Biblical Studies I',
            faculty='Dr. Smith',
            credits=3.0,
            days='MW',
            time='10:00-11:30',
            semester='Fall 2025',
            delivery_mode='In Person',
            description='Biblical studies course'
        )
        
        course2 = Course(
            id='THEO201',
            code='THEO 201',
            title='Theology I',
            faculty='Dr. Jones',
            credits=3.0,
            days='TR',
            time='14:00-15:30',
            semester='Spring 2026',
            delivery_mode='In Person',
            description='Theology course'
        )
        
        courses = [course1, course2]
        
        # Filter by semester
        fall_courses = get_courses_by_semester(courses, 'Fall 2025')
        assert len(fall_courses) == 1
        assert fall_courses[0].code == 'BIBL 101'
        
        spring_courses = get_courses_by_semester(courses, 'Spring 2026')
        assert len(spring_courses) == 1
        assert spring_courses[0].code == 'THEO 201'


class TestFormatting:
    """Test formatting functions"""
    
    def test_format_time_slot(self):
        """Test time slot formatting"""
        assert format_time_slot('10:00-11:30') == '10:00 - 11:30'
        assert format_time_slot('14:00-15:30') == '14:00 - 15:30'
        assert format_time_slot('') == 'TBD'
        assert format_time_slot(None) == 'TBD'
    
    def test_format_days(self):
        """Test days formatting"""
        assert format_days('MW') == 'Mon, Wed'
        assert format_days('TR') == 'Tue, Thu'
        assert format_days('F') == 'Fri'
        assert format_days('MTWRF') == 'Mon, Tue, Wed, Thu, Fri'
        assert format_days('') == 'TBD'
        assert format_days(None) == 'TBD'


class TestExport:
    """Test export functions"""
    
    def test_export_plan_to_csv(self):
        """Test exporting plan to CSV"""
        # Create courses
        course1 = Course(
            id='BIBL101',
            code='BIBL 101',
            title='Biblical Studies I',
            faculty='Dr. Smith',
            credits=3.0,
            days='MW',
            time='10:00-11:30',
            semester='Fall 2025',
            delivery_mode='In Person',
            description='Biblical studies course',
            satisfies={'bible'}
        )
        
        courses = [course1]
        
        # Create plan
        plan = Plan()
        plan.add_course('Fall 2025', 'BIBL101')
        
        # Export to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
            df = export_plan_to_csv(plan, courses, tmp_file.name)
            
            # Check that file was created
            assert os.path.exists(tmp_file.name)
            
            # Check DataFrame content
            assert len(df) == 1
            assert df.iloc[0]['Course Code'] == 'BIBL 101'
            assert df.iloc[0]['Semester'] == 'Fall 2025'
            assert df.iloc[0]['Credits'] == 3.0
            
            # Clean up
            os.unlink(tmp_file.name)


class TestProgress:
    """Test progress calculation functions"""
    
    def test_get_requirement_progress(self):
        """Test requirement progress calculation"""
        # Create requirements
        bible_req = Requirement('bible', 'Bible/Sacred Texts', 12.0)
        theo_req = Requirement('theology', 'Theology & Ethics', 9.0)
        requirements = [bible_req, theo_req]
        
        # Create courses
        course1 = Course(
            id='BIBL101',
            code='BIBL 101',
            title='Biblical Studies I',
            faculty='Dr. Smith',
            credits=12.0,
            days='MW',
            time='10:00-11:30',
            semester='Fall 2025',
            delivery_mode='In Person',
            description='Biblical studies course',
            satisfies={'bible'}
        )
        
        course2 = Course(
            id='THEO201',
            code='THEO 201',
            title='Theology I',
            faculty='Dr. Jones',
            credits=6.0,
            days='TR',
            time='14:00-15:30',
            semester='Fall 2025',
            delivery_mode='In Person',
            description='Theology course',
            satisfies={'theology'}
        )
        
        courses = [course1, course2]
        
        # Create plan
        plan = Plan()
        plan.add_course('Fall 2025', 'BIBL101')
        plan.add_course('Fall 2025', 'THEO201')
        
        # Get progress
        progress = get_requirement_progress(plan, courses, requirements)
        
        assert progress['total_requirements'] == 2
        assert progress['met_requirements'] == 1  # Only bible requirement is met
        assert progress['progress_percentage'] == 50.0
        assert 'validation_results' in progress 