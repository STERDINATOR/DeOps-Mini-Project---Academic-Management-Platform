"""Faculty model definition."""

import re
from typing import Dict, Any


class Faculty:
    """Represents a college faculty member record."""

    def __init__(
        self,
        faculty_id: str,
        name: str,
        email: str,
        department: str
    ) -> None:
        self.faculty_id = str(faculty_id).strip()
        self.name = str(name).strip()
        self.email = str(email).strip()
        self.department = str(department).strip()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Faculty":
        """Instantiate Faculty from dictionary with validation."""
        if not isinstance(data, dict):
            raise ValueError("Faculty data must be a dictionary")

        faculty_id = data.get("faculty_id")
        name = data.get("name")
        email = data.get("email")
        department = data.get("department")

        if not faculty_id or not str(faculty_id).strip():
            raise ValueError("faculty_id is required")
        if not name or not str(name).strip():
            raise ValueError("name is required")
        if not email or not str(email).strip():
            raise ValueError("email is required")
        if not department or not str(department).strip():
            raise ValueError("department is required")

        email_str = str(email).strip()
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_regex, email_str):
            raise ValueError("Invalid email format")

        return cls(
            faculty_id=str(faculty_id).strip(),
            name=str(name).strip(),
            email=email_str,
            department=str(department).strip()
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert faculty record to dictionary representation."""
        return {
            "faculty_id": self.faculty_id,
            "name": self.name,
            "email": self.email,
            "department": self.department
        }
