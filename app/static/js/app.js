/**
 * Enterprise Student Record & Academic Management Platform
 * Vanilla JavaScript UI Controller
 */

document.addEventListener("DOMContentLoaded", function () {
  // --------------------------------------------------------------------------
  // Helper: Display Flash Alert Messages
  // --------------------------------------------------------------------------
  function showAlert(containerId, message, type) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // type can be 'success', 'error', 'info'
    const alertDiv = document.createElement("div");
    alertDiv.className = `alert alert-${type === "error" ? "error" : "success"}`;
    alertDiv.innerHTML = `
      <span>${message}</span>
      <button type="button" class="btn btn-sm btn-secondary" style="padding: 2px 6px; font-size: 11px;" onclick="this.parentElement.remove()">✕</button>
    `;

    container.innerHTML = "";
    container.appendChild(alertDiv);

    // Auto-dismiss success after 5 seconds
    if (type === "success") {
      setTimeout(() => {
        if (alertDiv.parentElement) {
          alertDiv.remove();
        }
      }, 5000);
    }
  }

  // --------------------------------------------------------------------------
  // 1. Add Student Form
  // --------------------------------------------------------------------------
  const addStudentForm = document.getElementById("addStudentForm");
  if (addStudentForm) {
    addStudentForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      const formData = {
        student_id: document.getElementById("student_id").value.trim(),
        name: document.getElementById("name").value.trim(),
        email: document.getElementById("email").value.trim(),
        department: document.getElementById("department").value.trim(),
        semester: parseInt(document.getElementById("semester").value, 10)
      };

      try {
        const response = await fetch("/api/students", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(formData)
        });
        const result = await response.json();

        if (response.ok) {
          showAlert("studentAlerts", "Student added successfully.", "success");
          addStudentForm.reset();
          setTimeout(() => window.location.reload(), 1000);
        } else {
          showAlert("studentAlerts", result.error || "Failed to add student.", "error");
        }
      } catch (err) {
        showAlert("studentAlerts", "Network error occurred while adding student.", "error");
      }
    });
  }

  // --------------------------------------------------------------------------
  // 2. Delete Student Button
  // --------------------------------------------------------------------------
  const deleteButtons = document.querySelectorAll(".btn-delete-student");
  deleteButtons.forEach((btn) => {
    btn.addEventListener("click", async function () {
      const studentId = this.getAttribute("data-student-id");
      const studentName = this.getAttribute("data-student-name");

      if (!confirm(`Are you sure you want to delete student ${studentName} (${studentId})? This will also remove all associated enrollments and marks.`)) {
        return;
      }

      try {
        const response = await fetch(`/api/students/${studentId}`, {
          method: "DELETE"
        });
        const result = await response.json();

        if (response.ok) {
          showAlert("studentAlerts", `Student ${studentId} deleted successfully.`, "success");
          setTimeout(() => window.location.reload(), 800);
        } else {
          showAlert("studentAlerts", result.error || "Failed to delete student.", "error");
        }
      } catch (err) {
        showAlert("studentAlerts", "Network error occurred while deleting student.", "error");
      }
    });
  });

  // --------------------------------------------------------------------------
  // 3. Add Faculty Form
  // --------------------------------------------------------------------------
  const addFacultyForm = document.getElementById("addFacultyForm");
  if (addFacultyForm) {
    addFacultyForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      const formData = {
        faculty_id: document.getElementById("faculty_id").value.trim(),
        name: document.getElementById("faculty_name").value.trim(),
        email: document.getElementById("faculty_email").value.trim(),
        department: document.getElementById("faculty_department").value.trim()
      };

      try {
        const response = await fetch("/api/faculty", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(formData)
        });
        const result = await response.json();

        if (response.ok) {
          showAlert("facultyAlerts", "Faculty member added successfully.", "success");
          addFacultyForm.reset();
          setTimeout(() => window.location.reload(), 1000);
        } else {
          showAlert("facultyAlerts", result.error || "Failed to add faculty.", "error");
        }
      } catch (err) {
        showAlert("facultyAlerts", "Network error occurred while adding faculty.", "error");
      }
    });
  }

  // --------------------------------------------------------------------------
  // 4. Add Course Form
  // --------------------------------------------------------------------------
  const addCourseForm = document.getElementById("addCourseForm");
  if (addCourseForm) {
    addCourseForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      const formData = {
        course_id: document.getElementById("course_id").value.trim(),
        name: document.getElementById("course_name").value.trim(),
        credits: parseInt(document.getElementById("credits").value, 10),
        faculty_id: document.getElementById("course_faculty").value.trim(),
        semester: parseInt(document.getElementById("course_semester").value, 10)
      };

      try {
        const response = await fetch("/api/courses", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(formData)
        });
        const result = await response.json();

        if (response.ok) {
          showAlert("courseAlerts", "Course added successfully.", "success");
          addCourseForm.reset();
          setTimeout(() => window.location.reload(), 1000);
        } else {
          showAlert("courseAlerts", result.error || "Failed to add course.", "error");
        }
      } catch (err) {
        showAlert("courseAlerts", "Network error occurred while adding course.", "error");
      }
    });
  }

  // --------------------------------------------------------------------------
  // 5. Enroll Student Form
  // --------------------------------------------------------------------------
  const enrollForm = document.getElementById("enrollForm");
  if (enrollForm) {
    enrollForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      const studentId = document.getElementById("enroll_student_id").value.trim();
      const courseId = document.getElementById("enroll_course_id").value.trim();

      if (!studentId || !courseId) {
        showAlert("enrollAlerts", "Please select both a student and a course.", "error");
        return;
      }

      try {
        const response = await fetch("/api/enroll", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            student_id: studentId,
            course_id: courseId
          })
        });
        const result = await response.json();

        if (response.ok) {
          showAlert("enrollAlerts", "Enrollment successful.", "success");
          setTimeout(() => window.location.reload(), 1000);
        } else {
          showAlert("enrollAlerts", result.error || "Enrollment failed.", "error");
        }
      } catch (err) {
        showAlert("enrollAlerts", "Network error occurred during enrollment.", "error");
      }
    });
  }

  // --------------------------------------------------------------------------
  // 6. Record Marks Form
  // --------------------------------------------------------------------------
  const marksForm = document.getElementById("marksForm");
  if (marksForm) {
    const marksStudentSelect = document.getElementById("marks_student_id");
    const marksCourseSelect = document.getElementById("marks_course_id");

    // Dynamic course filtering based on student's enrollments
    if (marksStudentSelect && marksCourseSelect) {
      marksStudentSelect.addEventListener("change", async function () {
        const studentId = this.value;
        marksCourseSelect.innerHTML = '<option value="">Loading courses...</option>';

        if (!studentId) {
          marksCourseSelect.innerHTML = '<option value="">-- Select Student First --</option>';
          return;
        }

        try {
          const res = await fetch(`/api/students/${studentId}/enrollments`);
          if (res.ok) {
            const enrollments = await res.json();
            if (enrollments.length === 0) {
              marksCourseSelect.innerHTML = '<option value="">-- No Enrolled Courses --</option>';
            } else {
              marksCourseSelect.innerHTML = '<option value="">-- Select Enrolled Course --</option>';
              enrollments.forEach((enr) => {
                const opt = document.createElement("option");
                opt.value = enr.course_id;
                opt.textContent = `${enr.course_id} - ${enr.course_name} (${enr.credits} Credits)`;
                marksCourseSelect.appendChild(opt);
              });
            }
          } else {
            marksCourseSelect.innerHTML = '<option value="">Failed to load enrollments</option>';
          }
        } catch (err) {
          marksCourseSelect.innerHTML = '<option value="">Error loading courses</option>';
        }
      });

      // If a student is already preselected (e.g. browser cache), trigger course load
      if (marksStudentSelect.value) {
        marksStudentSelect.dispatchEvent(new Event("change"));
      }
    }

    marksForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      const studentId = document.getElementById("marks_student_id").value.trim();
      const courseId = document.getElementById("marks_course_id").value.trim();
      const marksVal = document.getElementById("marks_value").value.trim();

      if (!studentId || !courseId || marksVal === "") {
        showAlert("marksAlerts", "Please complete all fields.", "error");
        return;
      }

      const numMarks = parseFloat(marksVal);
      if (isNaN(numMarks) || numMarks < 0 || numMarks > 100) {
        showAlert("marksAlerts", "Marks must be between 0 and 100.", "error");
        return;
      }

      try {
        const response = await fetch("/api/marks", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            student_id: studentId,
            course_id: courseId,
            marks: numMarks
          })
        });
        const result = await response.json();

        if (response.ok) {
          showAlert("marksAlerts", "Academic marks recorded successfully.", "success");
          setTimeout(() => window.location.reload(), 1000);
        } else {
          showAlert("marksAlerts", result.error || "Failed to record marks.", "error");
        }
      } catch (err) {
        showAlert("marksAlerts", "Network error occurred while recording marks.", "error");
      }
    });
  }
});
