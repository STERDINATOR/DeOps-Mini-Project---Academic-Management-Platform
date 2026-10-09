"""Models package initialization."""
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.course import Course

__all__ = ["Student", "Faculty", "Course"]
