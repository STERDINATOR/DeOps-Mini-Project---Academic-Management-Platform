"""REST API routes for Enterprise Student Record & Academic Management."""

from flask import Blueprint, jsonify, request
from app.services.student_service import (
    StudentService,
    ValidationError,
    NotFoundError,
    DuplicateError
)

api_bp = Blueprint("api", __name__, url_prefix="/api")
service = StudentService()


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------
@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint used by Docker, Kubernetes, and monitoring."""
    return jsonify({
        "status": "UP",
        "service": "Enterprise Student Record & Academic Management Platform",
        "version": "1.0.0"
    }), 200


# ---------------------------------------------------------------------------
# Students
# ---------------------------------------------------------------------------
@api_bp.route("/students", methods=["POST"])
def create_student():
    """Create a new student record."""
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    try:
        created = service.add_student(data)
        return jsonify(created), 201
    except DuplicateError as err:
        return jsonify({"error": str(err)}), 409
    except ValidationError as err:
        return jsonify({"error": str(err)}), 400


@api_bp.route("/students", methods=["GET"])
def list_students():
    """Retrieve all students."""
    students = service.get_all_students()
    return jsonify(students), 200


@api_bp.route("/students/<student_id>", methods=["GET"])
def get_student(student_id):
    """Retrieve a single student by student_id."""
    try:
        student = service.get_student(student_id)
        return jsonify(student), 200
    except NotFoundError as err:
        return jsonify({"error": str(err)}), 404


@api_bp.route("/students/<student_id>", methods=["DELETE"])
def delete_student(student_id):
    """Delete a student and associated records."""
    try:
        service.delete_student(student_id)
        msg = f"Student '{student_id}' deleted successfully"
        return jsonify({"message": msg}), 200
    except NotFoundError as err:
        return jsonify({"error": str(err)}), 404


# ---------------------------------------------------------------------------
# Faculty
# ---------------------------------------------------------------------------
@api_bp.route("/faculty", methods=["POST"])
def create_faculty():
    """Create a new faculty record."""
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    try:
        created = service.add_faculty(data)
        return jsonify(created), 201
    except DuplicateError as err:
        return jsonify({"error": str(err)}), 409
    except ValidationError as err:
        return jsonify({"error": str(err)}), 400


@api_bp.route("/faculty", methods=["GET"])
def list_faculty():
    """Retrieve all faculty members."""
    faculty_list = service.get_all_faculty()
    return jsonify(faculty_list), 200


@api_bp.route("/faculty/<faculty_id>", methods=["GET"])
def get_faculty(faculty_id):
    """Retrieve a single faculty member by faculty_id."""
    try:
        faculty = service.get_faculty(faculty_id)
        return jsonify(faculty), 200
    except NotFoundError as err:
        return jsonify({"error": str(err)}), 404


# ---------------------------------------------------------------------------
# Courses
# ---------------------------------------------------------------------------
@api_bp.route("/courses", methods=["POST"])
def create_course():
    """Create a new academic course."""
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    try:
        created = service.add_course(data)
        return jsonify(created), 201
    except DuplicateError as err:
        return jsonify({"error": str(err)}), 409
    except ValidationError as err:
        return jsonify({"error": str(err)}), 400


@api_bp.route("/courses", methods=["GET"])
def list_courses():
    """Retrieve all academic courses."""
    courses = service.get_courses()
    return jsonify(courses), 200


@api_bp.route("/courses/<course_id>", methods=["GET"])
def get_course(course_id):
    """Retrieve a single course by course_id."""
    try:
        course = service.get_course(course_id)
        return jsonify(course), 200
    except NotFoundError as err:
        return jsonify({"error": str(err)}), 404


# ---------------------------------------------------------------------------
# Enrollments
# ---------------------------------------------------------------------------
@api_bp.route("/enroll", methods=["POST"])
def enroll_student():
    """Enroll a student in a course enforcing academic limits."""
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    student_id = data.get("student_id")
    course_id = data.get("course_id")

    if not student_id or not str(student_id).strip():
        return jsonify({"error": "student_id is required"}), 400
    if not course_id or not str(course_id).strip():
        return jsonify({"error": "course_id is required"}), 400

    try:
        enrollment = service.enroll_student(student_id, course_id)
        return jsonify(enrollment), 201
    except NotFoundError as err:
        return jsonify({"error": str(err)}), 404
    except DuplicateError as err:
        return jsonify({"error": str(err)}), 409
    except ValidationError as err:
        return jsonify({"error": str(err)}), 400


@api_bp.route("/students/<student_id>/enrollments", methods=["GET"])
def get_student_enrollments(student_id):
    """Retrieve all course enrollments for a given student."""
    try:
        enrollments = service.get_student_enrollments(student_id)
        return jsonify(enrollments), 200
    except NotFoundError as err:
        return jsonify({"error": str(err)}), 404


@api_bp.route("/enrollments", methods=["GET"])
def list_all_enrollments():
    """Retrieve all enrollments across platform."""
    enrollments = service.get_all_enrollments()
    return jsonify(enrollments), 200


# ---------------------------------------------------------------------------
# Marks
# ---------------------------------------------------------------------------
@api_bp.route("/marks", methods=["POST"])
def record_marks():
    """Add or update academic marks for an enrolled course."""
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    student_id = data.get("student_id")
    course_id = data.get("course_id")
    marks = data.get("marks")

    if not student_id or not str(student_id).strip():
        return jsonify({"error": "student_id is required"}), 400
    if not course_id or not str(course_id).strip():
        return jsonify({"error": "course_id is required"}), 400
    if marks is None:
        return jsonify({"error": "marks is required"}), 400

    try:
        record = service.add_or_update_marks(student_id, course_id, marks)
        return jsonify(record), 200
    except NotFoundError as err:
        return jsonify({"error": str(err)}), 404
    except ValidationError as err:
        return jsonify({"error": str(err)}), 400


# ---------------------------------------------------------------------------
# GPA Calculation
# ---------------------------------------------------------------------------
@api_bp.route("/students/<student_id>/gpa", methods=["GET"])
def get_student_gpa(student_id):
    """Calculate and return weighted GPA for a student."""
    try:
        gpa_data = service.calculate_gpa(student_id)
        return jsonify(gpa_data), 200
    except NotFoundError as err:
        return jsonify({"error": str(err)}), 404
