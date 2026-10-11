
pipeline {
    agent any

    environment {
        IMAGE_NAME = 'student-academic-platform'
        IMAGE_TAG = 'v1.0.0'
        PYTHONUNBUFFERED = '1'
    }

    stages {
        stage('1. SCM Checkout') {
            steps {
                checkout scm
                bat 'git --version'
            }
        }

        stage('2. Environment Setup & Dependencies') {
            steps {
                bat '''
                    if not exist reports mkdir reports
                    py -3.11 -m venv .venv
                    if errorlevel 1 exit /b 1

                    .venv\\Scripts\\python.exe -m pip install --upgrade pip
                    if errorlevel 1 exit /b 1

                    .venv\\Scripts\\python.exe -m pip install -r requirements.txt
                    if errorlevel 1 exit /b 1
                '''
            }
        }

        stage('3. Code Linting & Syntax Gate') {
            steps {
                bat '''
                    .venv\\Scripts\\python.exe -m flake8 app/ database/ tests/ run.py
                    if errorlevel 1 exit /b 1
                '''
            }
        }

        stage('4. Automated Unit & Integration Tests') {
            steps {
                bat '''
                    if not exist reports mkdir reports

                    .venv\\Scripts\\python.exe -m pytest -v --cov=app --cov-report=term-missing --junitxml=reports/test-results.xml tests/
                    if errorlevel 1 exit /b 1
                '''
            }

            post {
                always {
                    junit testResults: 'reports/test-results.xml',
                          allowEmptyResults: false
                }
            }
        }

        stage('5. Build Docker Artifact') {
            steps {
                bat 'docker build -t %IMAGE_NAME%:%IMAGE_TAG% .'
            }
        }

        stage('6. Kubernetes Minikube Deployment') {
            steps {
                bat '''
                    minikube status
                    if errorlevel 1 exit /b 1

                    minikube image load %IMAGE_NAME%:%IMAGE_TAG%
                    if errorlevel 1 exit /b 1

                    kubectl apply -f k8s\\deployment.yaml
                    if errorlevel 1 exit /b 1

                    kubectl apply -f k8s\\service.yaml
                    if errorlevel 1 exit /b 1

                    kubectl rollout status deployment/student-deployment --timeout=180s
                    if errorlevel 1 exit /b 1

                    kubectl get pods -l app=student-platform
                    kubectl get services
                '''
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: All six DevOps pipeline stages completed.'
        }

        failure {
            echo 'FAILURE: Inspect the console output for the first failed stage.'
        }

        always {
            echo 'Pipeline execution finished.'
        }
    }
}
