"""Unit tests for StudentService core domain business rules."""

import pytest
from database.db import get_db
from app.services.student_service import (
    StudentService,
    ValidationError,
    NotFoundError,
    DuplicateError
)


@pytest.fixture(autouse=True)
def clean_db():
    """Reset the database before each test execution."""
    db = get_db()
    db.reset(seed=False)
    yield db
    db.reset(seed=False)


@pytest.fixture
def service():
    """Provide a StudentService instance."""
    return StudentService()


# ---------------------------------------------------------------------------
# Student Domain Tests
# ---------------------------------------------------------------------------
def test_create_student_success(service):
    """Test valid student creation."""
    student_data = {
        "student_id": "STU101",
        "name": "Aarav Sharma",
        "email": "aarav@example.com",
        "department": "Computer Science",
        "semester": 1
    }
    created = service.add_student(student_data)
    assert created["student_id"] == "STU101"
    assert created["name"] == "Aarav Sharma"
    assert created["semester"] == 1


def test_create_duplicate_student_raises_duplicate_error(service):
    """Test creating student with duplicate ID raises DuplicateError."""
    student_data = {
        "student_id": "STU101",
        "name": "Aarav Sharma",
        "email": "aarav@example.com",
        "department": "Computer Science",
        "semester": 1
    }
    service.add_student(student_data)

    with pytest.raises(DuplicateError) as exc_info:
        service.add_student(student_data)
    assert "already exists" in str(exc_info.value)


def test_get_student_success(service):
    """Test retrieving existing student."""
    student_data = {
        "student_id": "STU102",
        "name": "Bhavna Patel",
        "email": "bhavna@example.com",
        "department": "AI & DS",
        "semester": 2
    }
    service.add_student(student_data)
    retrieved = service.get_student("STU102")
    assert retrieved["name"] == "Bhavna Patel"
    assert retrieved["department"] == "AI & DS"


def test_get_missing_student_raises_not_found(service):
    """Test retrieving non-existent student raises NotFoundError."""
    with pytest.raises(NotFoundError) as exc_info:
        service.get_student("STU_NONEXISTENT")
    assert "not found" in str(exc_info.value)


def test_delete_student_success(service):
    """Test deleting existing student."""
    student_data = {
        "student_id": "STU103",
        "name": "Chetan Kumar",
        "email": "chetan@example.com",
        "department": "IT",
        "semester": 3
    }
    service.add_student(student_data)
    assert service.delete_student("STU103") is True

    with pytest.raises(NotFoundError):
        service.get_student("STU103")


def test_delete_missing_student_raises_not_found(service):
    """Test deleting non-existent student raises NotFoundError."""
    with pytest.raises(NotFoundError):
        service.delete_student("STU_NONEXISTENT")


# ---------------------------------------------------------------------------
# Faculty Domain Tests
# ---------------------------------------------------------------------------
def test_create_faculty_success(service):
    """Test creating a new faculty member."""
    faculty_data = {
        "faculty_id": "FAC101",
        "name": "Dr. Sunita Rao",
        "email": "sunita@example.com",
        "department": "Computer Science"
    }
    created = service.add_faculty(faculty_data)
    assert created["faculty_id"] == "FAC101"
    assert created["name"] == "Dr. Sunita Rao"


def test_create_duplicate_faculty_raises_duplicate_error(service):
    """Test registering duplicate faculty ID raises DuplicateError."""
    faculty_data = {
        "faculty_id": "FAC101",
        "name": "Dr. Sunita Rao",
        "email": "sunita@example.com",
        "department": "Computer Science"
    }
    service.add_faculty(faculty_data)

    with pytest.raises(DuplicateError):
        service.add_faculty(faculty_data)


def test_get_faculty_success_and_not_found(service):
    """Test faculty retrieval for both existing and missing records."""
    faculty_data = {
        "faculty_id": "FAC102",
        "name": "Prof. David",
        "email": "david@example.com",
        "department": "Mathematics"
    }
    service.add_faculty(faculty_data)
    assert service.get_faculty("FAC102")["name"] == "Prof. David"

    with pytest.raises(NotFoundError):
        service.get_faculty("FAC_UNKNOWN")


# ---------------------------------------------------------------------------
# Course Domain Tests
# ---------------------------------------------------------------------------
def test_create_course_success(service):
    """Test creating course with valid faculty."""
    service.add_faculty({
        "faculty_id": "FAC101",
        "name": "Dr. Sunita Rao",
        "email": "sunita@example.com",
        "department": "Computer Science"
    })
    course_data = {
        "course_id": "CS101",
        "name": "Algorithms",
        "credits": 4,
        "faculty_id": "FAC101",
        "semester": 1
    }
    created = service.add_course(course_data)
    assert created["course_id"] == "CS101"
    assert created["credits"] == 4


def test_create_duplicate_course_raises_duplicate_error(service):
    """Test duplicate course ID raises DuplicateError."""
    service.add_faculty({
        "faculty_id": "FAC101",
        "name": "Dr. Sunita",
        "email": "sunita@example.com",
        "department": "CS"
    })
    course_data = {
        "course_id": "CS101",
        "name": "Algorithms",
        "credits": 4,
        "faculty_id": "FAC101",
        "semester": 1
    }
    service.add_course(course_data)

    with pytest.raises(DuplicateError):
        service.add_course(course_data)


def test_create_course_with_invalid_faculty(service):
    """Test creating course with non-existent faculty raises error."""
    course_data = {
        "course_id": "CS102",
        "name": "Networks",
        "credits": 3,
        "faculty_id": "FAC_NONEXISTENT",
        "semester": 1
    }
    with pytest.raises(ValidationError) as exc:
        service.add_course(course_data)
    assert "does not exist" in str(exc.value)


def test_create_course_with_invalid_credits_raises_validation_error(service):
    """Test course with zero or negative credits raises ValidationError."""
    service.add_faculty({
        "faculty_id": "FAC101",
        "name": "Dr. Sunita",
        "email": "sunita@example.com",
        "department": "CS"
    })
    with pytest.raises(ValidationError):
        service.add_course({
            "course_id": "CS103",
            "name": "Invalid Credits",
            "credits": 0,
            "faculty_id": "FAC101",
            "semester": 1
        })

    with pytest.raises(ValidationError):
        service.add_course({
            "course_id": "CS104",
            "name": "Invalid Credits",
            "credits": -2,
            "faculty_id": "FAC101",
            "semester": 1
        })


# ---------------------------------------------------------------------------
# Enrollment Domain & 18-Credit Business Rule Tests
# ---------------------------------------------------------------------------
def test_valid_enrollment(service):
    """Test successful student enrollment."""
    service.add_faculty({
        "faculty_id": "FAC01",
        "name": "Faculty One",
        "email": "f1@example.com",
        "department": "CS"
    })
    service.add_student({
        "student_id": "STU01",
        "name": "Student One",
        "email": "s1@example.com",
        "department": "CS",
        "semester": 2
    })
    service.add_course({
        "course_id": "CS201",
        "name": "Data Structures",
        "credits": 4,
        "faculty_id": "FAC01",
        "semester": 2
    })

    enr = service.enroll_student("STU01", "CS201")
    assert enr["student_id"] == "STU01"
    assert enr["course_id"] == "CS201"
    assert enr["semester"] == 2


def test_duplicate_enrollment_raises_duplicate_error(service):
    """Test re-enrolling in the same course raises DuplicateError."""
    service.add_faculty({
        "faculty_id": "FAC01",
        "name": "Faculty One",
        "email": "f1@example.com",
        "department": "CS"
    })
    service.add_student({
        "student_id": "STU01",
        "name": "Student One",
        "email": "s1@example.com",
        "department": "CS",
        "semester": 2
    })
    service.add_course({
        "course_id": "CS201",
        "name": "Data Structures",
        "credits": 4,
        "faculty_id": "FAC01",
        "semester": 2
    })

    service.enroll_student("STU01", "CS201")
    with pytest.raises(DuplicateError):
        service.enroll_student("STU01", "CS201")


def test_enrollment_missing_student_raises_not_found(service):
    """Test enrolling a non-existent student raises NotFoundError."""
    service.add_faculty({
        "faculty_id": "FAC01",
        "name": "Faculty",
        "email": "f@example.com",
        "department": "CS"
    })
    service.add_course({
        "course_id": "CS201",
        "name": "Course",
        "credits": 3,
        "faculty_id": "FAC01",
        "semester": 2
    })
    with pytest.raises(NotFoundError):
        service.enroll_student("NONEXISTENT_STUDENT", "CS201")


def test_enrollment_missing_course_raises_not_found(service):
    """Test enrolling in a non-existent course raises NotFoundError."""
    service.add_student({
        "student_id": "STU01",
        "name": "Student",
        "email": "s@example.com",
        "department": "CS",
        "semester": 2
    })
    with pytest.raises(NotFoundError):
        service.enroll_student("STU01", "NONEXISTENT_COURSE")


def test_enrollment_semester_mismatch(service):
    """Test semester mismatch raises ValidationError."""
    service.add_faculty({
        "faculty_id": "FAC01",
        "name": "Faculty",
        "email": "f@example.com",
        "department": "CS"
    })
    service.add_student({
        "student_id": "STU01",
        "name": "Student",
        "email": "s@example.com",
        "department": "CS",
        "semester": 3  # Semester 3
    })
    service.add_course({
        "course_id": "CS401",
        "name": "Senior Seminar",
        "credits": 3,
        "faculty_id": "FAC01",
        "semester": 4  # Semester 4 mismatch!
    })

    with pytest.raises(ValidationError) as exc:
        service.enroll_student("STU01", "CS401")
    assert "Semester mismatch" in str(exc.value)


def test_enrollment_maximum_18_credit_rule(service):
    """Test that total semester credits cannot exceed 18."""
    service.add_faculty({
        "faculty_id": "FAC01",
        "name": "Faculty One",
        "email": "f1@example.com",
        "department": "CS"
    })
    service.add_student({
        "student_id": "STU_CREDIT",
        "name": "Credit Tester",
        "email": "credit@example.com",
        "department": "CS",
        "semester": 3
    })

    # Create 5 courses: 4 + 4 + 3 + 4 + 3 = 18 credits exactly
    courses = [
        ("C1", "Course 1", 4),
        ("C2", "Course 2", 4),
        ("C3", "Course 3", 3),
        ("C4", "Course 4", 4),
        ("C5", "Course 5", 3),
        ("C6", "Course 6", 3)
    ]
    for cid, cname, cr in courses:
        service.add_course({
            "course_id": cid,
            "name": cname,
            "credits": cr,
            "faculty_id": "FAC01",
            "semester": 3
        })

    # Enroll in 18 credits (4 + 4 + 3 + 4 + 3 = 18)
    for cid in ["C1", "C2", "C3", "C4", "C5"]:
        service.enroll_student("STU_CREDIT", cid)

    # Attempting to enroll in C6 (3 cr) brings total to 21 > 18
    with pytest.raises(ValidationError) as exc:
        service.enroll_student("STU_CREDIT", "C6")

    assert "Maximum 18 credits exceeded" in str(exc.value)
