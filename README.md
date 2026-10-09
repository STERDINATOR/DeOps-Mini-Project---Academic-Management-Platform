# Enterprise Student Record & Academic Management Platform

A clean, transparent, and beginner-friendly Academic Management System built as a university DevOps assignment project. The platform demonstrates modular software architecture, business-rule validation, RESTful API design, automated test coverage, Docker containerization, Kubernetes orchestration, and a declarative Jenkins CI/CD pipeline.

---

## 1. Project Overview

The **Enterprise Student Record & Academic Management Platform** is a web-based college administrative portal designed for managing foundational academic records:
- **Students**: Student registration, department mapping, and semester tracking.
- **Faculty**: Faculty directory and department affiliations.
- **Courses**: Curriculum courses with credit weightings and assigned faculty.
- **Course Enrollments**: Validated course registrations enforcing semester alignment and credit caps.
- **Academic Marks**: Exam score entry (0–100 scale) with automatic grade point mapping (0–10).
- **GPA Calculation**: Real-time credit-weighted grade point average computation.

---

## 2. Problem Statement

University academic administration often requires dependable record management where business policies (such as semester limits and credit overload prevention) must be rigorously enforced. Furthermore, modern software engineering curricula require practical demonstrations of how an application progresses from local development through automated testing, containerization, and orchestration in a DevOps lifecycle.

This project solves this by delivering an understandable, production-grade application free from excessive third-party dependencies, complex frameworks, or external cloud databases.

---

## 3. Objectives

- **Simplicity & Transparency**: Keep the codebase clean, readable, and easy to explain during a university viva or practical examination.
- **Strict Business Validation**: Enforce rules such as unique identifiers, semester matching, the strict **18-credit semester limit**, and valid marks ranges.
- **Service-Oriented Architecture**: Maintain a clean separation between data storage, domain business logic (Service Layer), HTTP routing (Flask Blueprints), and presentation (Jinja2 templates).
- **Automated Quality Assurance**: Deliver 100% automated test coverage for core business logic with JUnit-compatible XML test reporting.
- **DevOps Readiness**: Provide out-of-the-box Dockerfiles, Kubernetes manifests for Minikube, and a Jenkinsfile for CI/CD automation.

---

## 4. Key Features

- **Intuitive Web Portal**: Responsive, uncluttered interface designed like a real college portal with simple tables and cards.
- **Thread-Safe In-Memory Database**: Singleton in-memory database using Python dictionaries and `threading.Lock()` for concurrency protection without external database overhead.
- **Clean Initial State**: Starts with an empty database ready for student, faculty, course, and enrollment creation.
- **RESTful API**: Standardized JSON endpoints with appropriate HTTP status codes (`200`, `201`, `400`, `404`, `409`).
- **Health Check Endpoint**: `/api/health` providing readiness and liveness signals for container platforms.
- **DevOps Artifacts**: Docker container image, Kubernetes Deployment and Service definitions, and automated Jenkins CI pipeline.

---

## 5. Technology Stack

- **Backend**: Python 3.11, Flask 3.0.3, Werkzeug 3.0.3
- **WSGI / Production Server**: Gunicorn 22.0.0
- **Frontend**: HTML5, Semantic CSS3, Vanilla JavaScript, Jinja2 Templates
- **Testing & Coverage**: Pytest 8.2.1, Pytest-Cov 5.0.0
- **Code Quality / Linter**: Flake8 7.0.0 (PEP 8 compliance)
- **Database**: Thread-safe in-memory Python singleton (no external database required)
- **Containerization**: Docker (base image: `python:3.11-slim`)
- **Orchestration**: Kubernetes / Minikube (v1.x)
- **CI/CD Automation**: Jenkins Declarative Pipeline

---

## 6. Project Structure

```text
student-academic-platform/
│
├── app/
│   ├── __init__.py              # Flask application factory (create_app)
│   ├── models/                  # Domain entity definitions and validation
│   │   ├── __init__.py
│   │   ├── student.py
│   │   ├── faculty.py
│   │   └── course.py
│   ├── services/                # Business logic and validation rules
│   │   ├── __init__.py
│   │   └── student_service.py
│   ├── routes/                  # Thin HTTP controllers
│   │   ├── __init__.py
│   │   ├── api.py               # JSON REST endpoints
│   │   └── web.py               # Jinja2 template controllers
│   ├── templates/               # Minimalist academic UI templates
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── students.html
│   │   ├── student_details.html
│   │   ├── faculty.html
│   │   ├── courses.html
│   │   ├── enrollments.html
│   │   └── marks.html
│   └── static/                  # Vanilla CSS and JavaScript
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── app.js
│
├── database/                    # In-memory thread-safe singleton
│   ├── __init__.py
│   └── db.py
│
├── tests/                       # Pytest automated test suite
│   ├── __init__.py
│   ├── test_student_service.py  # Student, faculty, course, and enrollment tests
│   ├── test_marks_mgmt.py       # Marks range, grading scale, and GPA tests
│   └── test_api_endpoints.py    # REST API and web page rendering tests
│
├── reports/                     # JUnit XML test results and coverage output
│
├── k8s/                         # Kubernetes manifests
│   ├── deployment.yaml          # 3-replica Deployment with probes
│   └── service.yaml             # NodePort Service (Port 30090)
│
├── Dockerfile                   # Multi-stage production container build
├── Jenkinsfile                  # 6-stage CI/CD pipeline
├── requirements.txt             # Exact pinned Python dependencies
├── run.py                       # Application execution entry point
├── .gitignore                   # Version control ignore rules
├── .dockerignore                 # Docker context ignore rules
└── README.md                    # Project documentation
```

---

## 7. Local Setup & Installation

### Prerequisites
- Python 3.11 installed
- pip (Python package manager)
- Git

### Step-by-Step Instructions

1. **Clone or navigate into the repository**:
   ```bash
   cd /path/to/student-academic-platform
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv .venv
   ```

3. **Activate the virtual environment**:
   - On Linux / macOS:
     ```bash
     source .venv/bin/activate
     ```
   - On Windows (PowerShell):
     ```powershell
     .venv\Scripts\Activate.ps1
     ```

4. **Install pinned dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## 8. Running the Application

### Running with Python (Development Server)
```bash
python run.py
```
By default, the server listens on `0.0.0.0:5000`. You can configure a custom port via the `PORT` environment variable:
```bash
PORT=3000 python run.py
```
Open your web browser and navigate to:
```text
http://localhost:5000
```

### Running with Gunicorn (Production WSGI Server)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

---

## 9. Academic Business Rules

### 1. Student Rules
- `student_id` must be unique.
- `name`, `email`, `department`, and `semester` are required.
- `semester` must be a positive integer ($> 0$).
- Deleting a student cascades to remove their enrollments and marks.

### 2. Faculty Rules
- `faculty_id` must be unique.
- `name`, `email`, and `department` are required.

### 3. Course Rules
- `course_id` must be unique.
- `credits` must be a positive integer ($> 0$).
- `faculty_id` must reference an existing faculty member.
- `semester` must be a valid positive integer.

### 4. Course Enrollment Rules
1. Student must exist in the database.
2. Course must exist in the database.
3. Duplicate enrollment in the same course is strictly prohibited.
4. **Semester Matching**: Student semester must match course semester.
5. **18-Credit Limit Rule**: A student cannot exceed **18 total credits** in a semester. Any enrollment that causes total registered credits to exceed 18 is rejected with HTTP 400.

### 5. Marks & Grading Scale
- Student must already be enrolled in the course to enter marks.
- Marks must be between **0 and 100**. Existing marks can be updated.
- **Grade Point Conversion**:
  | Marks Range | Grade Point | Note |
  | :--- | :--- | :--- |
  | 90 – 100 | **10** | Outstanding |
  | 80 – 89 | **9** | Excellent |
  | 70 – 79 | **8** | Very Good |
  | 60 – 69 | **7** | Good |
  | 50 – 59 | **6** | Above Average |
  | 40 – 49 | **5** | Pass |
  | 0 – 39 | **0** | Fail |

### 6. GPA Calculation Formula
Weighted GPA is computed using only courses with recorded marks:
$$\text{GPA} = \frac{\sum (\text{Grade Point} \times \text{Course Credits})}{\sum \text{Course Credits}}$$
- Rounded to 2 decimal places.
- If a student has no graded courses: $\text{GPA} = 0.0$.

---

## 10. REST API Documentation

| Method | Endpoint | Description | Status Codes |
| :--- | :--- | :--- | :--- |
| **GET** | `/api/health` | Service health status check | `200` |
| **GET** | `/api/students` | List all registered students | `200` |
| **POST** | `/api/students` | Register a new student | `201`, `400`, `409` |
| **GET** | `/api/students/<student_id>` | Get student by ID | `200`, `404` |
| **DELETE** | `/api/students/<student_id>` | Delete student record | `200`, `404` |
| **GET** | `/api/faculty` | List all faculty members | `200` |
| **POST** | `/api/faculty` | Register a new faculty member | `201`, `400`, `409` |
| **GET** | `/api/faculty/<faculty_id>` | Get faculty by ID | `200`, `404` |
| **GET** | `/api/courses` | List all curriculum courses | `200` |
| **POST** | `/api/courses` | Register a new course | `201`, `400`, `409` |
| **GET** | `/api/courses/<course_id>` | Get course by ID | `200`, `404` |
| **POST** | `/api/enroll` | Enroll student in a course | `201`, `400`, `404`, `409` |
| **GET** | `/api/students/<id>/enrollments`| Get courses student enrolled in | `200`, `404` |
| **GET** | `/api/enrollments` | List all platform enrollments | `200` |
| **POST** | `/api/marks` | Add or update exam marks | `200`, `400`, `404` |
| **GET** | `/api/students/<id>/gpa` | Get student GPA and credit summary | `200`, `404` |

### Sample Requests & Responses

#### Health Check
`GET /api/health`
```json
{
  "status": "UP",
  "service": "Enterprise Student Record & Academic Management Platform",
  "version": "1.0.0"
}
```

#### Enroll Student
`POST /api/enroll`
```json
{
  "student_id": "STU003",
  "course_id": "CSE101"
}
```

#### Record Marks
`POST /api/marks`
```json
{
  "student_id": "STU003",
  "course_id": "CSE101",
  "marks": 87.5
}
```
Response:
```json
{
  "student_id": "STU003",
  "course_id": "CSE101",
  "marks": 87.5,
  "grade_point": 9
}
```

---

## 11. Automated Testing & Code Quality

### Running the Test Suite
Execute the exact university test command with code coverage and XML reporting:
```bash
pytest -v --cov=app --cov-report=term-missing --junitxml=reports/test-results.xml tests/
```

### Running the Linter (Flake8)
Verify PEP 8 code quality standards:
```bash
flake8 app/ database/ tests/ run.py
```

---

## 12. Docker Containerization

### Build Docker Image
```bash
docker build -t student-academic-platform:v1.0.0 .
```

### Run Docker Container
```bash
docker run -d -p 5000:5000 --name student-platform student-academic-platform:v1.0.0
```

### Verify Container Health
```bash
docker ps
curl http://localhost:5000/api/health
```

### View Logs and Stop Container
```bash
docker logs -f student-platform
docker stop student-platform && docker rm student-platform
```

---

## 13. Kubernetes & Minikube Deployment

The manifests in `k8s/` define a highly-available Deployment (3 replicas) with HTTP health probes and a NodePort service.

### 1. Start Minikube
```bash
minikube start
```

### 2. Load Image into Minikube (Local Build)
```bash
minikube image load student-academic-platform:v1.0.0
```

### 3. Apply Kubernetes Manifests
```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### 4. Check Deployment Status
```bash
kubectl rollout status deployment/student-deployment
kubectl get pods -l app=student-platform
kubectl get svc student-service
```

### 5. Access the Platform on Minikube
```bash
minikube service student-service --url
```
Or open directly:
```bash
minikube service student-service
```

---

## 14. Jenkins CI/CD Pipeline

The `Jenkinsfile` in the project root defines an automated 6-stage pipeline:

1. **SCM Checkout**: Checks out Git source repository.
2. **Environment Setup & Dependencies**: Creates virtual environment and installs dependencies from `requirements.txt`.
3. **Code Linting & Syntax Gate**: Runs `flake8` to prevent syntax or style regressions.
4. **Automated Unit & Integration Tests**: Runs `pytest` with coverage, generating `reports/test-results.xml` which is published via the Jenkins JUnit plugin.
5. **Build Docker Artifact**: Builds Docker image `student-academic-platform:v1.0.0`.
6. **Kubernetes Minikube Deployment**: Deploys manifests to Kubernetes and verifies zero-downtime rollout completion.

---

## 15. Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `Address already in use: 5000` | Another process is using port 5000. | Specify a different port: `PORT=5001 python run.py`. |
| `Student semester does not match course semester` | Enrolling across different semesters. | Ensure student's enrolled semester equals course's semester. |
| `Maximum 18 credits exceeded` | Student has exceeded 18 credits in that semester. | Drop a course or enroll in fewer credits. |
| `ModuleNotFoundError` | Virtual environment is not active. | Run `source .venv/bin/activate`. |
| `ImagePullBackOff in Kubernetes` | Kubernetes cannot find local image. | Run `minikube image load student-academic-platform:v1.0.0`. |

---

## 16. Limitations & Future Scope

- **In-Memory Storage**: Current storage is retained in memory for academic assignment simplicity. Restarting the server resets records to the initial seed state.
- **Authentication**: User authentication and role-based permissions are intentionally omitted per the assignment specification.
- **Future Enhancements**: Relational PostgreSQL database integration with Alembic migrations, student attendance tracking, and student fee reconciliation.
