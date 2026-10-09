"""Integration and REST API endpoint tests for Flask application."""

import pytest
from app import create_app
from database.db import get_db


@pytest.fixture
def app():
    """Create Flask application instance in testing mode."""
    app_instance = create_app({"TESTING": True})
    return app_instance


@pytest.fixture
def client(app):
    """Provide a test client for Flask application."""
    return app.test_client()


@pytest.fixture(autouse=True)
def clean_db():
    """Ensure clean isolated database for every test."""
    db = get_db()
    db.reset(seed=False)
    yield db
    db.reset(seed=False)


# ---------------------------------------------------------------------------
# Health Check Endpoint
# ---------------------------------------------------------------------------
def test_health_check_endpoint(client):
    """Test GET /api/health returns UP status and exact service name."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "UP"
    expected_service = (
        "Enterprise Student Record & Academic Management Platform"
    )
    assert data["service"] == expected_service
    assert data["version"] == "1.0.0"


# ---------------------------------------------------------------------------
# Student API Endpoints
# ---------------------------------------------------------------------------
def test_create_and_get_student_api(client):
    """Test POST /api/students and GET /api/students/<id>."""
    student_payload = {
        "student_id": "STU901",
        "name": "Kavita Rao",
        "email": "kavita@example.com",
        "department": "Computer Science",
        "semester": 2
    }
    # Create
    post_res = client.post("/api/students", json=student_payload)
    assert post_res.status_code == 201
    assert post_res.get_json()["student_id"] == "STU901"

    # Get
    get_res = client.get("/api/students/STU901")
    assert get_res.status_code == 200
    assert get_res.get_json()["name"] == "Kavita Rao"

    # List
    list_res = client.get("/api/students")
    assert list_res.status_code == 200
    assert len(list_res.get_json()) == 1


def test_create_duplicate_student_api_returns_409(client):
    """Test duplicate student returns HTTP 409 conflict."""
    payload = {
        "student_id": "STU901",
        "name": "Kavita Rao",
        "email": "kavita@example.com",
        "department": "Computer Science",
        "semester": 2
    }
    client.post("/api/students", json=payload)
    res = client.post("/api/students", json=payload)
    assert res.status_code == 409
    assert "already exists" in res.get_json()["error"]


def test_create_student_invalid_data_returns_400(client):
    """Test invalid or missing data returns HTTP 400."""
    res = client.post("/api/students", json={"name": "No ID"})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_get_nonexistent_student_returns_404(client):
    """Test non-existent student returns HTTP 404."""
    res = client.get("/api/students/STU_UNKNOWN")
    assert res.status_code == 404
    assert "not found" in res.get_json()["error"]


def test_delete_student_api(client):
    """Test DELETE /api/students/<id>."""
    payload = {
        "student_id": "STU902",
        "name": "Rohan Das",
        "email": "rohan@example.com",
        "department": "AI",
        "semester": 1
    }
    client.post("/api/students", json=payload)
    del_res = client.delete("/api/students/STU902")
    assert del_res.status_code == 200

    # Verify deleted
    get_res = client.get("/api/students/STU902")
    assert get_res.status_code == 404


# ---------------------------------------------------------------------------
# Faculty API Endpoints
# ---------------------------------------------------------------------------
def test_faculty_api_crud(client):
    """Test POST /api/faculty, GET /api/faculty, and GET /api/faculty/<id>."""
    payload = {
        "faculty_id": "FAC501",
        "name": "Dr. Raman",
        "email": "raman@example.com",
        "department": "Physics"
    }
    post_res = client.post("/api/faculty", json=payload)
    assert post_res.status_code == 201

    get_res = client.get("/api/faculty/FAC501")
    assert get_res.status_code == 200
    assert get_res.get_json()["name"] == "Dr. Raman"

    list_res = client.get("/api/faculty")
    assert list_res.status_code == 200
    assert len(list_res.get_json()) == 1


# ---------------------------------------------------------------------------
# Course API Endpoints
# ---------------------------------------------------------------------------
def test_courses_api_crud_and_validation(client):
    """Test POST /api/courses with faculty dependency and validation."""
    # First create faculty
    client.post("/api/faculty", json={
        "faculty_id": "FAC501",
        "name": "Dr. Raman",
        "email": "raman@example.com",
        "department": "Physics"
    })

    # Valid course
    course_res = client.post("/api/courses", json={
        "course_id": "PHY101",
        "name": "Quantum Mechanics",
        "credits": 4,
        "faculty_id": "FAC501",
        "semester": 1
    })
    assert course_res.status_code == 201

    # Non-existent faculty -> 400
    bad_res = client.post("/api/courses", json={
        "course_id": "PHY102",
        "name": "Classical Mechanics",
        "credits": 4,
        "faculty_id": "FAC_NONEXISTENT",
        "semester": 1
    })
    assert bad_res.status_code == 400

    # Retrieve course
    get_res = client.get("/api/courses/PHY101")
    assert get_res.status_code == 200
    assert get_res.get_json()["name"] == "Quantum Mechanics"


# ---------------------------------------------------------------------------
# Enrollment API Endpoints
# ---------------------------------------------------------------------------
def test_enrollment_api_flow(client):
    """Test POST /api/enroll and GET /api/students/<id>/enrollments."""
    # Setup student, faculty, course
    client.post("/api/faculty", json={
        "faculty_id": "FAC1",
        "name": "Faculty 1",
        "email": "f1@example.com",
        "department": "CS"
    })
    client.post("/api/student", json={})  # test bad url or missing
    client.post("/api/students", json={
        "student_id": "STU1",
        "name": "Alice",
        "email": "alice@example.com",
        "department": "CS",
        "semester": 2
    })
    client.post("/api/courses", json={
        "course_id": "CS201",
        "name": "Data Structures",
        "credits": 4,
        "faculty_id": "FAC1",
        "semester": 2
    })

    # Valid enrollment
    enr_res = client.post("/api/enroll", json={
        "student_id": "STU1",
        "course_id": "CS201"
    })
    assert enr_res.status_code == 201

    # Duplicate enrollment -> 409
    dup_res = client.post("/api/enroll", json={
        "student_id": "STU1",
        "course_id": "CS201"
    })
    assert dup_res.status_code == 409

    # List enrollments for student
    list_res = client.get("/api/students/STU1/enrollments")
    assert list_res.status_code == 200
    assert len(list_res.get_json()) == 1
    assert list_res.get_json()[0]["course_id"] == "CS201"


# ---------------------------------------------------------------------------
# Marks and GPA API Endpoints
# ---------------------------------------------------------------------------
def test_marks_and_gpa_api(client):
    """Test POST /api/marks and GET /api/students/<id>/gpa."""
    # Setup base entities
    client.post("/api/faculty", json={
        "faculty_id": "FAC1",
        "name": "Fac",
        "email": "fac@example.com",
        "department": "CS"
    })
    client.post("/api/students", json={
        "student_id": "STU77",
        "name": "Bob",
        "email": "bob@example.com",
        "department": "CS",
        "semester": 1
    })
    client.post("/api/courses", json={
        "course_id": "MAT101",
        "name": "Calculus",
        "credits": 4,
        "faculty_id": "FAC1",
        "semester": 1
    })
    client.post("/api/enroll", json={
        "student_id": "STU77",
        "course_id": "MAT101"
    })

    # Post marks
    marks_res = client.post("/api/marks", json={
        "student_id": "STU77",
        "course_id": "MAT101",
        "marks": 91
    })
    assert marks_res.status_code == 200
    assert marks_res.get_json()["grade_point"] == 10

    # Check GPA endpoint
    gpa_res = client.get("/api/students/STU77/gpa")
    assert gpa_res.status_code == 200
    gpa_data = gpa_res.get_json()
    assert gpa_data["gpa"] == 10.0
    assert gpa_data["total_credits"] == 4
    assert len(gpa_data["courses"]) == 1


# ---------------------------------------------------------------------------
# Web Portal HTML Template Rendering Tests
# ---------------------------------------------------------------------------
def test_web_routes_render_templates(client):
    """Test web pages return HTTP 200 and render HTML properly."""
    # Seed data
    client.post("/api/faculty", json={
        "faculty_id": "F10",
        "name": "Prof. Smith",
        "email": "smith@example.com",
        "department": "CS"
    })
    client.post("/api/students", json={
        "student_id": "S10",
        "name": "Jane Doe",
        "email": "jane@example.com",
        "department": "CS",
        "semester": 1
    })
    client.post("/api/courses", json={
        "course_id": "CS100",
        "name": "Intro to CS",
        "credits": 3,
        "faculty_id": "F10",
        "semester": 1
    })
    client.post("/api/enroll", json={
        "student_id": "S10",
        "course_id": "CS100"
    })
    client.post("/api/marks", json={
        "student_id": "S10",
        "course_id": "CS100",
        "marks": 88
    })

    # Test dashboard
    res = client.get("/")
    assert res.status_code == 200
    assert b"Administration Dashboard" in res.data

    res_dash = client.get("/dashboard")
    assert res_dash.status_code == 200

    # Test students page
    res_students = client.get("/students")
    assert res_students.status_code == 200
    assert b"Student Management" in res_students.data
    assert b"Jane Doe" in res_students.data

    # Test student details page
    res_details = client.get("/students/S10")
    assert res_details.status_code == 200
    assert b"Student Academic Profile" in res_details.data

    # Test missing student details 404
    res_missing = client.get("/students/NONEXISTENT")
    assert res_missing.status_code == 404

    # Test faculty page
    res_faculty = client.get("/faculty")
    assert res_faculty.status_code == 200
    assert b"Faculty Directory" in res_faculty.data

    # Test courses page
    res_courses = client.get("/courses")
    assert res_courses.status_code == 200
    assert b"Course Catalog" in res_courses.data

    # Test enrollments page
    res_enroll = client.get("/enrollments")
    assert res_enroll.status_code == 200
    assert b"Course Enrollments" in res_enroll.data

    # Test marks page
    res_marks = client.get("/marks")
    assert res_marks.status_code == 200
    assert b"Academic Marks & GPA Management" in res_marks.data
