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
                echo 'Checking out source code repository...'
                checkout scm
            }
        }

        stage('2. Environment Setup & Dependencies') {
            steps {
                echo 'Setting up Python virtual environment and installing dependencies...'
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('3. Code Linting & Syntax Gate') {
            steps {
                echo 'Executing Flake8 code quality verification and PEP 8 check...'
                sh '''
                    . .venv/bin/activate
                    flake8 app/ database/ tests/ run.py
                '''
            }
        }

        stage('4. Automated Unit & Integration Tests') {
            steps {
                echo 'Running Pytest test suite with code coverage and generating XML report...'
                sh '''
                    mkdir -p reports
                    . .venv/bin/activate
                    pytest -v --cov=app --cov-report=term-missing --junitxml=reports/test-results.xml tests/
                '''
            }
            post {
                always {
                    junit testResults: 'reports/test-results.xml', allowEmptyResults: false
                }
            }
        }

        stage('5. Build Docker Artifact') {
            steps {
                echo "Building Docker container image: ${IMAGE_NAME}:${IMAGE_TAG}..."
                sh """
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                """
            }
        }

        stage('6. Kubernetes Minikube Deployment') {
            steps {
                echo 'Deploying application to Kubernetes cluster and validating rollout status...'
                sh '''
                    kubectl apply -f k8s/deployment.yaml
                    kubectl apply -f k8s/service.yaml
                    kubectl rollout status deployment/student-deployment --timeout=120s
                '''
            }
        }
    }

    post {
        success {
            echo 'DevOps CI/CD pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Please inspect stage logs for details.'
        }
    }
}
