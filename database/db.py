"""Thread-safe in-memory database singleton for Academic Management."""

import threading
from typing import Dict, List, Optional, Any


class Database:
    """Thread-safe in-memory database implementation."""

    _instance: Optional["Database"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "Database":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Database, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return

        self._lock = threading.Lock()
        self.students: Dict[str, Dict[str, Any]] = {}
        self.faculty: Dict[str, Dict[str, Any]] = {}
        self.courses: Dict[str, Dict[str, Any]] = {}
        self.enrollments: List[Dict[str, Any]] = []
        # Marks keyed by (student_id, course_id)
        self.marks: Dict[str, Dict[str, Any]] = {}
        self._initialized = True

    def reset(self, seed: bool = False) -> None:
        """Reset all in-memory tables to empty."""
        with self._lock:
            self.students.clear()
            self.faculty.clear()
            self.courses.clear()
            self.enrollments.clear()
            self.marks.clear()

    def seed_demo_data(self) -> None:
        """No-op: All mock data removed."""
        pass


def get_db() -> Database:
    """Helper function to obtain the Database singleton."""
    return Database()
