"""
Data models for the Dual-Degree Course Planner
"""
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional
from datetime import datetime
import json


@dataclass
class Requirement:
    """Represents a degree requirement that courses can satisfy"""
    id: str
    label: str
    min_credits: float
    satisfied_by: Set[str] = field(default_factory=set)  # Set of Course IDs
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'label': self.label,
            'min_credits': self.min_credits,
            'satisfied_by': list(self.satisfied_by)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Requirement':
        """Create from dictionary"""
        return cls(
            id=data['id'],
            label=data['label'],
            min_credits=data['min_credits'],
            satisfied_by=set(data.get('satisfied_by', []))
        )


@dataclass
class Course:
    """Represents a course offering"""
    id: str
    code: str
    title: str
    faculty: str
    credits: float
    days: str
    time: str
    semester: str
    delivery_mode: str
    description: str
    satisfies: Set[str] = field(default_factory=set)  # Set of Requirement IDs
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'code': self.code,
            'title': self.title,
            'faculty': self.faculty,
            'credits': self.credits,
            'days': self.days,
            'time': self.time,
            'semester': self.semester,
            'delivery_mode': self.delivery_mode,
            'description': self.description,
            'satisfies': list(self.satisfies)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Course':
        """Create from dictionary"""
        return cls(
            id=data['id'],
            code=data['code'],
            title=data['title'],
            faculty=data['faculty'],
            credits=data['credits'],
            days=data['days'],
            time=data['time'],
            semester=data['semester'],
            delivery_mode=data['delivery_mode'],
            description=data['description'],
            satisfies=set(data.get('satisfies', []))
        )


@dataclass
class Plan:
    """Represents a student's course plan"""
    selections: Dict[str, List[str]] = field(default_factory=dict)  # semester -> [course_ids]
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'selections': self.selections,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Plan':
        """Create from dictionary"""
        return cls(
            selections=data.get('selections', {}),
            notes=data.get('notes', ''),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat()))
        )
    
    def add_course(self, semester: str, course_id: str):
        """Add a course to the plan"""
        if semester not in self.selections:
            self.selections[semester] = []
        if course_id not in self.selections[semester]:
            self.selections[semester].append(course_id)
            self.updated_at = datetime.now()
    
    def remove_course(self, semester: str, course_id: str):
        """Remove a course from the plan"""
        if semester in self.selections and course_id in self.selections[semester]:
            self.selections[semester].remove(course_id)
            self.updated_at = datetime.now()
    
    def get_courses_for_semester(self, semester: str) -> List[str]:
        """Get all course IDs for a given semester"""
        return self.selections.get(semester, [])
    
    def save_to_file(self, filepath: str):
        """Save plan to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'Plan':
        """Load plan from JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except FileNotFoundError:
            return cls()  # Return empty plan if file doesn't exist 