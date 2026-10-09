"""Web interface controller rendering Jinja2 templates."""

from flask import Blueprint, render_template, abort
from app.services.student_service import StudentService, NotFoundError

web_bp = Blueprint("web", __name__)
service = StudentService()


@web_bp.route("/", methods=["GET"])
@web_bp.route("/dashboard", methods=["GET"])
def dashboard():
    """Render university management dashboard with high-level statistics."""
    students = service.get_all_students()
    faculty_list = service.get_all_faculty()
    courses = service.get_courses()
    enrollments = service.get_all_enrollments()

    stats = {
        "total_students": len(students),
        "total_faculty": len(faculty_list),
        "total_courses": len(courses),
        "total_enrollments": len(enrollments)
    }

    return render_template(
        "dashboard.html",
        stats=stats,
        students=students[:5],
        enrollments=enrollments[:5],
        active_page="dashboard"
    )


@web_bp.route("/students", methods=["GET"])
def students():
    """Render student directory and student registration form."""
    students_list = service.get_all_students()
    return render_template(
        "students.html",
        students=students_list,
        active_page="students"
    )


@web_bp.route("/students/<student_id>", methods=["GET"])
def student_details(student_id):
    """Render detailed profile of a student with enrollments and GPA."""
    try:
        student = service.get_student(student_id)
        enrollments = service.get_student_enrollments(student_id)
        marks_list = service.get_student_marks(student_id)
        gpa_info = service.calculate_gpa(student_id)

        # Merge enrollment details with marks
        marks_map = {m["course_id"]: m for m in marks_list}
        courses_summary = []
        for enr in enrollments:
            cid = enr["course_id"]
            m_record = marks_map.get(cid)
            courses_summary.append({
                "course_id": cid,
                "course_name": enr["course_name"],
                "credits": enr["credits"],
                "semester": enr["semester"],
                "faculty_name": enr["faculty_name"],
                "marks": m_record["marks"] if m_record else None,
                "grade_point": m_record["grade_point"] if m_record else None
            })

        return render_template(
            "student_details.html",
            student=student,
            courses_summary=courses_summary,
            gpa_info=gpa_info,
            active_page="students"
        )
    except NotFoundError:
        abort(404)


@web_bp.route("/faculty", methods=["GET"])
def faculty():
    """Render faculty directory and registration form."""
    faculty_list = service.get_all_faculty()
    return render_template(
        "faculty.html",
        faculty=faculty_list,
        active_page="faculty"
    )


@web_bp.route("/courses", methods=["GET"])
def courses():
    """Render course catalog and course creation form."""
    course_list = service.get_courses()
    faculty_list = service.get_all_faculty()
    return render_template(
        "courses.html",
        courses=course_list,
        faculty=faculty_list,
        active_page="courses"
    )


@web_bp.route("/enrollments", methods=["GET"])
def enrollments():
    """Render course enrollment page."""
    students_list = service.get_all_students()
    courses_list = service.get_courses()
    all_enrollments = service.get_all_enrollments()
    return render_template(
        "enrollments.html",
        students=students_list,
        courses=courses_list,
        enrollments=all_enrollments,
        active_page="enrollments"
    )


@web_bp.route("/marks", methods=["GET"])
def marks():
    """Render academic marks entry and GPA overview page."""
    students_list = service.get_all_students()
    courses_list = service.get_courses()

    # Calculate GPAs for all students for overview table
    student_summaries = []
    for s in students_list:
        gpa_info = service.calculate_gpa(s["student_id"])
        marks_records = service.get_student_marks(s["student_id"])
        student_summaries.append({
            "student": s,
            "gpa": gpa_info["gpa"],
            "credits": gpa_info["total_credits"],
            "marks_count": len(marks_records)
        })

    return render_template(
        "marks.html",
        students=students_list,
        courses=courses_list,
        student_summaries=student_summaries,
        active_page="marks"
    )
