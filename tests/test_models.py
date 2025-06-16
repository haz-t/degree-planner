"""
Unit tests for data models
"""
import pytest
import json
from datetime import datetime
from models import Course, Requirement, Plan


class TestRequirement:
    """Test Requirement model"""
    
    def test_requirement_creation(self):
        """Test creating a requirement"""
        req = Requirement('bible', 'Bible/Sacred Texts', 12.0)
        assert req.id == 'bible'
        assert req.label == 'Bible/Sacred Texts'
        assert req.min_credits == 12.0
        assert req.satisfied_by == set()
    
    def test_requirement_to_dict(self):
        """Test converting requirement to dictionary"""
        req = Requirement('bible', 'Bible/Sacred Texts', 12.0)
        req.satisfied_by.add('course1')
        req.satisfied_by.add('course2')
        
        data = req.to_dict()
        assert data['id'] == 'bible'
        assert data['label'] == 'Bible/Sacred Texts'
        assert data['min_credits'] == 12.0
        assert set(data['satisfied_by']) == {'course1', 'course2'}
    
    def test_requirement_from_dict(self):
        """Test creating requirement from dictionary"""
        data = {
            'id': 'bible',
            'label': 'Bible/Sacred Texts',
            'min_credits': 12.0,
            'satisfied_by': ['course1', 'course2']
        }
        
        req = Requirement.from_dict(data)
        assert req.id == 'bible'
        assert req.label == 'Bible/Sacred Texts'
        assert req.min_credits == 12.0
        assert req.satisfied_by == {'course1', 'course2'}


class TestCourse:
    """Test Course model"""
    
    def test_course_creation(self):
        """Test creating a course"""
        course = Course(
            id='BIBL101_Fall2025_Smith',
            code='BIBL 101',
            title='Introduction to Biblical Studies',
            faculty='Dr. Smith',
            credits=3.0,
            days='MW',
            time='10:00-11:30',
            semester='Fall 2025',
            delivery_mode='In Person',
            description='An introduction to biblical texts.'
        )
        
        assert course.id == 'BIBL101_Fall2025_Smith'
        assert course.code == 'BIBL 101'
        assert course.title == 'Introduction to Biblical Studies'
        assert course.faculty == 'Dr. Smith'
        assert course.credits == 3.0
        assert course.days == 'MW'
        assert course.time == '10:00-11:30'
        assert course.semester == 'Fall 2025'
        assert course.delivery_mode == 'In Person'
        assert course.description == 'An introduction to biblical texts.'
        assert course.satisfies == set()
    
    def test_course_to_dict(self):
        """Test converting course to dictionary"""
        course = Course(
            id='BIBL101_Fall2025_Smith',
            code='BIBL 101',
            title='Introduction to Biblical Studies',
            faculty='Dr. Smith',
            credits=3.0,
            days='MW',
            time='10:00-11:30',
            semester='Fall 2025',
            delivery_mode='In Person',
            description='An introduction to biblical texts.'
        )
        course.satisfies.add('bible')
        course.satisfies.add('electives')
        
        data = course.to_dict()
        assert data['id'] == 'BIBL101_Fall2025_Smith'
        assert data['code'] == 'BIBL 101'
        assert data['title'] == 'Introduction to Biblical Studies'
        assert data['faculty'] == 'Dr. Smith'
        assert data['credits'] == 3.0
        assert data['days'] == 'MW'
        assert data['time'] == '10:00-11:30'
        assert data['semester'] == 'Fall 2025'
        assert data['delivery_mode'] == 'In Person'
        assert data['description'] == 'An introduction to biblical texts.'
        assert set(data['satisfies']) == {'bible', 'electives'}
    
    def test_course_from_dict(self):
        """Test creating course from dictionary"""
        data = {
            'id': 'BIBL101_Fall2025_Smith',
            'code': 'BIBL 101',
            'title': 'Introduction to Biblical Studies',
            'faculty': 'Dr. Smith',
            'credits': 3.0,
            'days': 'MW',
            'time': '10:00-11:30',
            'semester': 'Fall 2025',
            'delivery_mode': 'In Person',
            'description': 'An introduction to biblical texts.',
            'satisfies': ['bible', 'electives']
        }
        
        course = Course.from_dict(data)
        assert course.id == 'BIBL101_Fall2025_Smith'
        assert course.code == 'BIBL 101'
        assert course.title == 'Introduction to Biblical Studies'
        assert course.faculty == 'Dr. Smith'
        assert course.credits == 3.0
        assert course.days == 'MW'
        assert course.time == '10:00-11:30'
        assert course.semester == 'Fall 2025'
        assert course.delivery_mode == 'In Person'
        assert course.description == 'An introduction to biblical texts.'
        assert course.satisfies == {'bible', 'electives'}


class TestPlan:
    """Test Plan model"""
    
    def test_plan_creation(self):
        """Test creating a plan"""
        plan = Plan()
        assert plan.selections == {}
        assert plan.notes == ""
        assert isinstance(plan.created_at, datetime)
        assert isinstance(plan.updated_at, datetime)
    
    def test_plan_add_course(self):
        """Test adding a course to a plan"""
        plan = Plan()
        plan.add_course('Fall 2025', 'course1')
        plan.add_course('Fall 2025', 'course2')
        plan.add_course('Spring 2026', 'course3')
        
        assert plan.selections['Fall 2025'] == ['course1', 'course2']
        assert plan.selections['Spring 2026'] == ['course3']
    
    def test_plan_remove_course(self):
        """Test removing a course from a plan"""
        plan = Plan()
        plan.add_course('Fall 2025', 'course1')
        plan.add_course('Fall 2025', 'course2')
        
        plan.remove_course('Fall 2025', 'course1')
        assert plan.selections['Fall 2025'] == ['course2']
        
        # Removing non-existent course should not error
        plan.remove_course('Fall 2025', 'nonexistent')
        assert plan.selections['Fall 2025'] == ['course2']
    
    def test_plan_get_courses_for_semester(self):
        """Test getting courses for a specific semester"""
        plan = Plan()
        plan.add_course('Fall 2025', 'course1')
        plan.add_course('Fall 2025', 'course2')
        plan.add_course('Spring 2026', 'course3')
        
        assert plan.get_courses_for_semester('Fall 2025') == ['course1', 'course2']
        assert plan.get_courses_for_semester('Spring 2026') == ['course3']
        assert plan.get_courses_for_semester('Summer 2025') == []
    
    def test_plan_to_dict(self):
        """Test converting plan to dictionary"""
        plan = Plan()
        plan.add_course('Fall 2025', 'course1')
        plan.notes = "Test plan"
        
        data = plan.to_dict()
        assert data['selections'] == {'Fall 2025': ['course1']}
        assert data['notes'] == "Test plan"
        assert 'created_at' in data
        assert 'updated_at' in data
    
    def test_plan_from_dict(self):
        """Test creating plan from dictionary"""
        data = {
            'selections': {'Fall 2025': ['course1', 'course2']},
            'notes': 'Test plan',
            'created_at': '2023-01-01T00:00:00',
            'updated_at': '2023-01-02T00:00:00'
        }
        
        plan = Plan.from_dict(data)
        assert plan.selections == {'Fall 2025': ['course1', 'course2']}
        assert plan.notes == 'Test plan'
        assert plan.created_at == datetime.fromisoformat('2023-01-01T00:00:00')
        assert plan.updated_at == datetime.fromisoformat('2023-01-02T00:00:00')
    
    def test_plan_duplicate_course_prevention(self):
        """Test that adding the same course twice doesn't create duplicates"""
        plan = Plan()
        plan.add_course('Fall 2025', 'course1')
        plan.add_course('Fall 2025', 'course1')  # Duplicate
        
        assert plan.selections['Fall 2025'] == ['course1']  # Only one instance 