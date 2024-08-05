# FastAPI

## Overview

This repository contains a FastAPI application. The application handles user management for multiple projects and is designed to be deployed on Google Cloud Run. The project includes functionalities for creating, retrieving, updating, and deleting users, along with sending invitation emails. It utilizes Google Firestore as the database and is containerized using Docker.

## Features

- **User Management**: Create, update, retrieve, and delete user records.
- **Email Invitations**: Send invitation emails with links to API documentation and screenshots.
- **API Documentation**: Interactive API documentation via Swagger UI and reDoc.
- **Deployment**: Containerized using Docker and deployed on Google Cloud Run.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Docker
- Google Cloud SDK (for local development and deployment)
- FastAPI
- Firestore Database

### Setup

1. **Clone the Repository**

    ```bash
    git clone https://github.com/enjoyimkrsnna/Aviato-FastAPI.git
    cd Aviato-FastAPI
    ```

2. **Install Dependencies**

    Create a virtual environment and install the required Python packages:

    ```bash
    python -m venv env
    source env/bin/activate
    pip install -r requirements.txt
    ```

3. **Configure Environment Variables**

    Create a `.env` file in the root directory and add the following environment variables:

    ```env
    GOOGLE_APPLICATION_CREDENTIALS_JSON=<your_gcp_credentials_json>
    SENDER_EMAIL=<your_email>
    SENDER_PASSWORD=<your_email_password>
    ```

4. **Run the Application Locally**

    ```bash
    uvicorn main:app --reload
    ```

    Access the API at `http://127.0.0.1:8000`.

5. **Containerize the Application**

    Build the Docker image:

    ```bash
    docker build -t imkrsnna/aviato-consulting:1.0.0 .
    ```

    Run the Docker container locally:

    ```bash
    docker run -p 8000:8000 imkrsnna/aviato-consulting:1.0.0
    ```

6. **Deploy to Google Cloud Run**

    Push the Docker image to Docker Hub:

    ```bash
    docker push imkrsnna/aviato-consulting:1.0.0
    ```

    Deploy the image to Google Cloud Run using the Google Cloud Console.

## Acknowledgements

- FastAPI for building the APIs.
- Google Firestore for database services.
- Docker for containerization.
- Google Cloud Run for deployment.

## Documenation references:

1. **FastAPI Documentation**: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
2. **Google Firestore Documentation**: [https://firebase.google.com/docs/firestore](https://firebase.google.com/docs/firestore)
3. **Docker Documentation**: [https://docs.docker.com/](https://docs.docker.com/)
4. **Google Cloud Run Documentation**: [https://cloud.google.com/run/docs](https://cloud.google.com/run/docs)
5. **FastAPI Configuration Guide**: [https://fastapi.tiangolo.com/advanced/settings/](https://fastapi.tiangolo.com/advanced/settings/)
6. **FastAPI Running Docs**: [https://fastapi.tiangolo.com/deployment/](https://fastapi.tiangolo.com/deployment/)
7. **Docker Getting Started Guide**: [https://docs.docker.com/get-started/](https://docs.docker.com/get-started/)
8. **Google Cloud Run Deployment Guide**: [https://cloud.google.com/run/docs/deploying](https://cloud.google.com/run/docs/deploying)
