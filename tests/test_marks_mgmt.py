"""Unit tests for marks entry, grading scale, and GPA calculations."""

import pytest
from database.db import get_db
from app.services.student_service import (
    StudentService,
    ValidationError,
    NotFoundError
)


@pytest.fixture(autouse=True)
def clean_db():
    """Reset the database before each test execution."""
    db = get_db()
    db.reset(seed=False)
    yield db
    db.reset(seed=False)


@pytest.fixture
def setup_student_and_courses():
    """Seed base student, faculty, and enrolled courses for marks testing."""
    service = StudentService()
    service.add_faculty({
        "faculty_id": "FAC10",
        "name": "Prof. Alan Turing",
        "email": "alan@example.com",
        "department": "CS"
    })
    service.add_student({
        "student_id": "STU501",
        "name": "Grace Hopper",
        "email": "grace@example.com",
        "department": "CS",
        "semester": 3
    })
    service.add_course({
        "course_id": "CS301",
        "name": "Data Structures",
        "credits": 4,
        "faculty_id": "FAC10",
        "semester": 3
    })
    service.add_course({
        "course_id": "CS302",
        "name": "Computer Architecture",
        "credits": 4,
        "faculty_id": "FAC10",
        "semester": 3
    })
    service.add_course({
        "course_id": "CS303",
        "name": "Discrete Math",
        "credits": 3,
        "faculty_id": "FAC10",
        "semester": 3
    })
    service.add_course({
        "course_id": "CS304",
        "name": "Unenrolled Course",
        "credits": 3,
        "faculty_id": "FAC10",
        "semester": 3
    })

    # Enroll in 3 courses (4 + 4 + 3 = 11 credits)
    service.enroll_student("STU501", "CS301")
    service.enroll_student("STU501", "CS302")
    service.enroll_student("STU501", "CS303")
    return service


# ---------------------------------------------------------------------------
# Marks Tests
# ---------------------------------------------------------------------------
def test_add_valid_marks(setup_student_and_courses):
    """Test recording valid marks and verifying correct grade point."""
    service = setup_student_and_courses
    rec = service.add_or_update_marks("STU501", "CS301", 85)
    assert rec["marks"] == 85.0
    assert rec["grade_point"] == 9

    rec2 = service.add_or_update_marks("STU501", "CS302", 95)
    assert rec2["grade_point"] == 10

    rec3 = service.add_or_update_marks("STU501", "CS303", 72)
    assert rec3["grade_point"] == 8


def test_invalid_marks_below_zero(setup_student_and_courses):
    """Test that negative marks raise ValidationError."""
    service = setup_student_and_courses
    with pytest.raises(ValidationError) as exc:
        service.add_or_update_marks("STU501", "CS301", -5)
    assert "between 0 and 100" in str(exc.value)


def test_invalid_marks_above_100(setup_student_and_courses):
    """Test that marks above 100 raise ValidationError."""
    service = setup_student_and_courses
    with pytest.raises(ValidationError) as exc:
        service.add_or_update_marks("STU501", "CS301", 105)
    assert "between 0 and 100" in str(exc.value)


def test_marks_for_non_enrolled_course(setup_student_and_courses):
    """Test entering marks for non-enrolled course raises error."""
    service = setup_student_and_courses
    with pytest.raises(ValidationError) as exc:
        service.add_or_update_marks("STU501", "CS304", 80)
    assert "not enrolled" in str(exc.value)


def test_marks_for_missing_student_or_course(setup_student_and_courses):
    """Test that non-existent student or course raises NotFoundError."""
    service = setup_student_and_courses
    with pytest.raises(NotFoundError):
        service.add_or_update_marks("NONEXISTENT_STU", "CS301", 75)

    with pytest.raises(NotFoundError):
        service.add_or_update_marks("STU501", "NONEXISTENT_COURSE", 75)


def test_update_existing_marks(setup_student_and_courses):
    """Test that existing marks can be updated and grade points recalculate."""
    service = setup_student_and_courses
    service.add_or_update_marks("STU501", "CS301", 65)
    marks_list = service.get_student_marks("STU501")
    assert marks_list[0]["marks"] == 65.0
    assert marks_list[0]["grade_point"] == 7

    # Update to 92
    service.add_or_update_marks("STU501", "CS301", 92)
    updated_list = service.get_student_marks("STU501")
    assert updated_list[0]["marks"] == 92.0
    assert updated_list[0]["grade_point"] == 10


# ---------------------------------------------------------------------------
# Grading Scale & GPA Calculation Tests
# ---------------------------------------------------------------------------
def test_grading_scale_tiers():
    """Verify all grade point bands: 90-100=10, 80-89=9, 70-79=8, etc."""
    assert StudentService.calculate_grade_point(100) == 10
    assert StudentService.calculate_grade_point(90) == 10
    assert StudentService.calculate_grade_point(89.5) == 9
    assert StudentService.calculate_grade_point(80) == 9
    assert StudentService.calculate_grade_point(79) == 8
    assert StudentService.calculate_grade_point(70) == 8
    assert StudentService.calculate_grade_point(69) == 7
    assert StudentService.calculate_grade_point(60) == 7
    assert StudentService.calculate_grade_point(59) == 6
    assert StudentService.calculate_grade_point(50) == 6
    assert StudentService.calculate_grade_point(49) == 5
    assert StudentService.calculate_grade_point(40) == 5
    assert StudentService.calculate_grade_point(39) == 0
    assert StudentService.calculate_grade_point(0) == 0


def test_gpa_with_no_marks(setup_student_and_courses):
    """Test that a student with no marks has GPA = 0.0."""
    service = setup_student_and_courses
    res = service.calculate_gpa("STU501")
    assert res["gpa"] == 0.0
    assert res["total_credits"] == 0
    assert len(res["courses"]) == 0


def test_correct_weighted_gpa(setup_student_and_courses):
    """Test weighted GPA calculation: SUM(grade_point * credits) / credits.

    CS301: 4 credits, marks=85 -> gp=9  -> 9 * 4 = 36
    CS302: 4 credits, marks=92 -> gp=10 -> 10 * 4 = 40
    CS303: 3 credits, marks=78 -> gp=8  -> 8 * 3 = 24
    Total weighted points = 36 + 40 + 24 = 100
    Total credits = 4 + 4 + 3 = 11
    GPA = 100 / 11 = 9.090909... -> 9.09 (rounded to 2 decimal places)
    """
    service = setup_student_and_courses
    service.add_or_update_marks("STU501", "CS301", 85)
    service.add_or_update_marks("STU501", "CS302", 92)
    service.add_or_update_marks("STU501", "CS303", 78)

    gpa_data = service.calculate_gpa("STU501")
    assert gpa_data["student_id"] == "STU501"
    assert gpa_data["gpa"] == 9.09
    assert gpa_data["total_credits"] == 11
    assert len(gpa_data["courses"]) == 3


def test_gpa_ignores_courses_without_marks(setup_student_and_courses):
    """Test GPA ignores enrolled courses where marks are not yet entered."""
    service = setup_student_and_courses
    # Only enter marks for CS301 (4 credits, marks=95 -> gp=10 -> 40 points)
    service.add_or_update_marks("STU501", "CS301", 95)

    gpa_data = service.calculate_gpa("STU501")
    # 40 / 4 = 10.0
    assert gpa_data["gpa"] == 10.0
    assert gpa_data["total_credits"] == 4
    assert len(gpa_data["courses"]) == 1
