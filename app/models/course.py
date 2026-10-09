"""Course model definition."""

from typing import Dict, Any


class Course:
    """Represents an academic course record."""

    def __init__(
        self,
        course_id: str,
        name: str,
        credits: int,
        faculty_id: str,
        semester: int
    ) -> None:
        self.course_id = str(course_id).strip()
        self.name = str(name).strip()
        self.credits = int(credits)
        self.faculty_id = str(faculty_id).strip()
        self.semester = int(semester)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Course":
        """Instantiate Course from dictionary with validation."""
        if not isinstance(data, dict):
            raise ValueError("Course data must be a dictionary")

        course_id = data.get("course_id")
        name = data.get("name")
        credits_val = data.get("credits")
        faculty_id = data.get("faculty_id")
        semester = data.get("semester")

        if not course_id or not str(course_id).strip():
            raise ValueError("course_id is required")
        if not name or not str(name).strip():
            raise ValueError("name is required")
        if credits_val is None:
            raise ValueError("credits is required")
        if not faculty_id or not str(faculty_id).strip():
            raise ValueError("faculty_id is required")
        if semester is None:
            raise ValueError("semester is required")

        try:
            credits_int = int(credits_val)
        except (ValueError, TypeError):
            raise ValueError("credits must be an integer")

        if credits_int <= 0:
            raise ValueError("credits must be a positive integer")

        try:
            sem_int = int(semester)
        except (ValueError, TypeError):
            raise ValueError("semester must be an integer")

        if sem_int <= 0:
            raise ValueError("semester must be a positive integer")

        return cls(
            course_id=str(course_id).strip(),
            name=str(name).strip(),
            credits=credits_int,
            faculty_id=str(faculty_id).strip(),
            semester=sem_int
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert course record to dictionary representation."""
        return {
            "course_id": self.course_id,
            "name": self.name,
            "credits": self.credits,
            "faculty_id": self.faculty_id,
            "semester": self.semester
        }
