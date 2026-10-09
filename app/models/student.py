"""Student model definition."""

import re
from typing import Dict, Any


class Student:
    """Represents a college student record."""

    def __init__(
        self,
        student_id: str,
        name: str,
        email: str,
        department: str,
        semester: int
    ) -> None:
        self.student_id = str(student_id).strip()
        self.name = str(name).strip()
        self.email = str(email).strip()
        self.department = str(department).strip()
        self.semester = int(semester)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Student":
        """Instantiate Student from dictionary with strict validation."""
        if not isinstance(data, dict):
            raise ValueError("Student data must be a dictionary")

        student_id = data.get("student_id")
        name = data.get("name")
        email = data.get("email")
        department = data.get("department")
        semester = data.get("semester")

        if not student_id or not str(student_id).strip():
            raise ValueError("student_id is required")
        if not name or not str(name).strip():
            raise ValueError("name is required")
        if not email or not str(email).strip():
            raise ValueError("email is required")
        if not department or not str(department).strip():
            raise ValueError("department is required")
        if semester is None:
            raise ValueError("semester is required")

        # Validate email structure
        email_str = str(email).strip()
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_regex, email_str):
            raise ValueError("Invalid email format")

        try:
            sem_int = int(semester)
        except (ValueError, TypeError):
            raise ValueError("semester must be an integer")

        if sem_int <= 0:
            raise ValueError("semester must be a positive integer")

        return cls(
            student_id=str(student_id).strip(),
            name=str(name).strip(),
            email=email_str,
            department=str(department).strip(),
            semester=sem_int
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert student record to dictionary representation."""
        return {
            "student_id": self.student_id,
            "name": self.name,
            "email": self.email,
            "department": self.department,
            "semester": self.semester
        }
