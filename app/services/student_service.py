"""Business logic service layer for academic records management."""

from typing import Dict, List, Any, Optional
from database.db import Database, get_db
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.course import Course


class ValidationError(ValueError):
    """Raised when domain business rules are violated (HTTP 400)."""
    pass


class NotFoundError(Exception):
    """Raised when an entity is not found in database (HTTP 404)."""
    pass


class DuplicateError(Exception):
    """Raised when attempting to create a duplicate record (HTTP 409)."""
    pass


class StudentService:
    """Core academic management service orchestrator."""

    def __init__(self, db: Optional[Database] = None) -> None:
        self.db = db if db is not None else get_db()

    # ---------------------------------------------------------
    # Students
    # ---------------------------------------------------------
    def add_student(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and create a new student record."""
        try:
            student = Student.from_dict(data)
        except ValueError as err:
            raise ValidationError(str(err)) from err

        with self.db._lock:
            if student.student_id in self.db.students:
                raise DuplicateError(
                    f"Student with ID '{student.student_id}' already exists"
                )
            record = student.to_dict()
            self.db.students[student.student_id] = record
            return record

    def get_student(self, student_id: str) -> Dict[str, Any]:
        """Retrieve student record by ID."""
        with self.db._lock:
            student = self.db.students.get(str(student_id).strip())
            if not student:
                raise NotFoundError(f"Student '{student_id}' not found")
            return dict(student)

    def get_all_students(self) -> List[Dict[str, Any]]:
        """Retrieve all student records."""
        with self.db._lock:
            return [dict(s) for s in self.db.students.values()]

    def delete_student(self, student_id: str) -> bool:
        """Delete student and all associated enrollments and marks."""
        s_id = str(student_id).strip()
        with self.db._lock:
            if s_id not in self.db.students:
                raise NotFoundError(f"Student '{student_id}' not found")

            del self.db.students[s_id]

            # Remove enrollments
            self.db.enrollments = [
                e for e in self.db.enrollments if e["student_id"] != s_id
            ]

            # Remove marks
            keys_to_del = [
                k for k, m in self.db.marks.items() if m["student_id"] == s_id
            ]
            for k in keys_to_del:
                del self.db.marks[k]

            return True

    # ---------------------------------------------------------
    # Faculty
    # ---------------------------------------------------------
    def add_faculty(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and register a new faculty member."""
        try:
            faculty = Faculty.from_dict(data)
        except ValueError as err:
            raise ValidationError(str(err)) from err

        with self.db._lock:
            if faculty.faculty_id in self.db.faculty:
                raise DuplicateError(
                    f"Faculty with ID '{faculty.faculty_id}' already exists"
                )
            record = faculty.to_dict()
            self.db.faculty[faculty.faculty_id] = record
            return record

    def get_faculty(self, faculty_id: str) -> Dict[str, Any]:
        """Retrieve faculty member by ID."""
        with self.db._lock:
            fac = self.db.faculty.get(str(faculty_id).strip())
            if not fac:
                raise NotFoundError(f"Faculty '{faculty_id}' not found")
            return dict(fac)

    def get_all_faculty(self) -> List[Dict[str, Any]]:
        """Retrieve list of all faculty members."""
        with self.db._lock:
            return [dict(f) for f in self.db.faculty.values()]

    # ---------------------------------------------------------
    # Courses
    # ---------------------------------------------------------
    def add_course(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and register a new academic course."""
        try:
            course = Course.from_dict(data)
        except ValueError as err:
            raise ValidationError(str(err)) from err

        with self.db._lock:
            if course.course_id in self.db.courses:
                raise DuplicateError(
                    f"Course with ID '{course.course_id}' already exists"
                )

            # Rule: faculty_id must exist
            if course.faculty_id not in self.db.faculty:
                raise ValidationError(
                    f"Assigned Faculty ID '{course.faculty_id}' does not exist"
                )

            record = course.to_dict()
            self.db.courses[course.course_id] = record
            return record

    def get_course(self, course_id: str) -> Dict[str, Any]:
        """Retrieve course details by ID."""
        with self.db._lock:
            course = self.db.courses.get(str(course_id).strip())
            if not course:
                raise NotFoundError(f"Course '{course_id}' not found")
            return dict(course)

    def get_courses(self) -> List[Dict[str, Any]]:
        """Retrieve list of all courses enriched with faculty name."""
        with self.db._lock:
            result = []
            for c in self.db.courses.values():
                c_dict = dict(c)
                fac = self.db.faculty.get(c.get("faculty_id"))
                c_dict["faculty_name"] = fac["name"] if fac else "Unassigned"
                result.append(c_dict)
            return result

    # ---------------------------------------------------------
    # Enrollments
    # ---------------------------------------------------------
    def enroll_student(
        self,
        student_id: str,
        course_id: str
    ) -> Dict[str, Any]:
        """Enroll a student in a course enforcing all 5 business rules.

        Rules:
        1. Student must exist.
        2. Course must exist.
        3. Duplicate enrollment is not allowed.
        4. Student semester must match course semester.
        5. A student cannot exceed 18 total credits in a semester.
        """
        s_id = str(student_id).strip()
        c_id = str(course_id).strip()

        with self.db._lock:
            # Rule 1: Student must exist
            student = self.db.students.get(s_id)
            if not student:
                raise NotFoundError(f"Student '{s_id}' not found")

            # Rule 2: Course must exist
            course = self.db.courses.get(c_id)
            if not course:
                raise NotFoundError(f"Course '{c_id}' not found")

            # Rule 3: Duplicate enrollment not allowed
            for enr in self.db.enrollments:
                if enr["student_id"] == s_id and enr["course_id"] == c_id:
                    raise DuplicateError(
                        f"Student '{s_id}' is already enrolled "
                        f"in course '{c_id}'"
                    )

            # Rule 4: Semester match
            if student["semester"] != course["semester"]:
                msg = (
                    f"Semester mismatch: Student semester "
                    f"({student['semester']}) does not match course semester "
                    f"({course['semester']})"
                )
                raise ValidationError(msg)

            # Rule 5: 18-credit limit for the semester
            current_credits = 0
            for enr in self.db.enrollments:
                if enr["student_id"] == s_id:
                    enr_course = self.db.courses.get(enr["course_id"])
                    if enr_course and (
                        enr_course["semester"] == course["semester"]
                    ):
                        current_credits += enr_course.get("credits", 0)

            total_credits = current_credits + course["credits"]
            if total_credits > 18:
                msg = (
                    f"Maximum 18 credits exceeded: Enrolling in '{c_id}' "
                    f"({course['credits']} credits) brings total to "
                    f"{total_credits} credits in semester "
                    f"{course['semester']} (current: {current_credits})"
                )
                raise ValidationError(msg)

            enrollment_record = {
                "student_id": s_id,
                "course_id": c_id,
                "semester": course["semester"]
            }
            self.db.enrollments.append(enrollment_record)
            return enrollment_record

    def get_student_enrollments(
        self,
        student_id: str
    ) -> List[Dict[str, Any]]:
        """Retrieve all course enrollments for a given student."""
        s_id = str(student_id).strip()
        with self.db._lock:
            if s_id not in self.db.students:
                raise NotFoundError(f"Student '{s_id}' not found")

            results = []
            for enr in self.db.enrollments:
                if enr["student_id"] == s_id:
                    course = self.db.courses.get(enr["course_id"], {})
                    fac = self.db.faculty.get(course.get("faculty_id"), {})
                    sem = enr.get("semester", course.get("semester", 0))
                    results.append({
                        "student_id": s_id,
                        "course_id": enr["course_id"],
                        "course_name": course.get("name", "Unknown"),
                        "credits": course.get("credits", 0),
                        "semester": sem,
                        "faculty_name": fac.get("name", "N/A")
                    })
            return results

    def get_all_enrollments(self) -> List[Dict[str, Any]]:
        """Retrieve all enrollments across platform with full metadata."""
        with self.db._lock:
            results = []
            for enr in self.db.enrollments:
                student = self.db.students.get(enr["student_id"], {})
                course = self.db.courses.get(enr["course_id"], {})
                results.append({
                    "student_id": enr["student_id"],
                    "student_name": student.get("name", "Unknown"),
                    "course_id": enr["course_id"],
                    "course_name": course.get("name", "Unknown"),
                    "credits": course.get("credits", 0),
                    "semester": enr.get("semester", course.get("semester", 0))
                })
            return results

    # ---------------------------------------------------------
    # Academic Marks & Grade Points
    # ---------------------------------------------------------
    @staticmethod
    def calculate_grade_point(marks: float) -> int:
        """Convert percentage marks (0-100) to grade points (0-10).

        Rules:
        90-100 = 10
        80-89 = 9
        70-79 = 8
        60-69 = 7
        50-59 = 6
        40-49 = 5
        0-39 = 0
        """
        if marks >= 90:
            return 10
        elif marks >= 80:
            return 9
        elif marks >= 70:
            return 8
        elif marks >= 60:
            return 7
        elif marks >= 50:
            return 6
        elif marks >= 40:
            return 5
        else:
            return 0

    def add_or_update_marks(
        self,
        student_id: str,
        course_id: str,
        marks_val: Any
    ) -> Dict[str, Any]:
        """Record or update academic marks for an enrolled student.

        Rules:
        1. Student must exist.
        2. Course must exist.
        3. Student must already be enrolled in the course.
        4. Marks must be between 0 and 100.
        5. Existing marks can be updated.
        """
        s_id = str(student_id).strip()
        c_id = str(course_id).strip()

        try:
            marks = float(marks_val)
        except (ValueError, TypeError):
            raise ValidationError("Marks must be a valid number")

        if marks < 0 or marks > 100:
            raise ValidationError("Marks must be between 0 and 100")

        with self.db._lock:
            # Rule 1: Student exists
            if s_id not in self.db.students:
                raise NotFoundError(f"Student '{s_id}' not found")

            # Rule 2: Course exists
            if c_id not in self.db.courses:
                raise NotFoundError(f"Course '{c_id}' not found")

            # Rule 3: Must already be enrolled
            is_enrolled = any(
                e["student_id"] == s_id and e["course_id"] == c_id
                for e in self.db.enrollments
            )
            if not is_enrolled:
                raise ValidationError(
                    f"Student '{s_id}' is not enrolled in course '{c_id}'"
                )

            grade_point = self.calculate_grade_point(marks)
            key = f"{s_id}_{c_id}"
            record = {
                "student_id": s_id,
                "course_id": c_id,
                "marks": round(marks, 2),
                "grade_point": grade_point
            }
            self.db.marks[key] = record
            return record

    def get_student_marks(self, student_id: str) -> List[Dict[str, Any]]:
        """Retrieve marks for a student with course and grade point details."""
        s_id = str(student_id).strip()
        with self.db._lock:
            if s_id not in self.db.students:
                raise NotFoundError(f"Student '{s_id}' not found")

            results = []
            for m in self.db.marks.values():
                if m["student_id"] == s_id:
                    course = self.db.courses.get(m["course_id"], {})
                    results.append({
                        "course_id": m["course_id"],
                        "course_name": course.get("name", "Unknown"),
                        "credits": course.get("credits", 0),
                        "marks": m["marks"],
                        "grade_point": m["grade_point"]
                    })
            return results

    # ---------------------------------------------------------
    # GPA Calculation
    # ---------------------------------------------------------
    def calculate_gpa(self, student_id: str) -> Dict[str, Any]:
        """Calculate weighted GPA using course credits.

        Formula:
        GPA = SUM(grade_point * course_credits) / SUM(course_credits)
        Round final GPA to 2 decimal places.
        If no marks: GPA = 0.0.
        Only calculate GPA using courses for which marks are available.
        """
        s_id = str(student_id).strip()
        with self.db._lock:
            if s_id not in self.db.students:
                raise NotFoundError(f"Student '{s_id}' not found")

            evaluated_courses = []
            total_weighted_points = 0.0
            total_evaluated_credits = 0

            for m in self.db.marks.values():
                if m["student_id"] == s_id:
                    course = self.db.courses.get(m["course_id"])
                    if course:
                        cr = course.get("credits", 0)
                        gp = m.get("grade_point", 0)
                        total_weighted_points += gp * cr
                        total_evaluated_credits += cr
                        evaluated_courses.append({
                            "course_id": m["course_id"],
                            "course_name": course.get("name", "Unknown"),
                            "credits": cr,
                            "marks": m["marks"],
                            "grade_point": gp
                        })

            if total_evaluated_credits == 0:
                gpa = 0.0
            else:
                gpa = round(total_weighted_points / total_evaluated_credits, 2)

            return {
                "student_id": s_id,
                "gpa": gpa,
                "total_credits": total_evaluated_credits,
                "courses": evaluated_courses
            }
