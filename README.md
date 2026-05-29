# Inventory Management API

A Python-based inventory management project built with FastAPI, SQLAlchemy, MySQL, Docker Compose, and pytest.

This project demonstrates a layered backend design with API, service, repository, and database layers. It supports stock-in and stock-out operations, business-rule error handling, and automated testing.

## Features

- FastAPI REST API
- MySQL database integration
- SQLAlchemy ORM
- Docker Compose environment
- Stock-in and stock-out inventory operations
- Business-rule error handling
- Automated tests with pytest
- Basic GUI client for demonstration purposes

## Architecture

```text
GUI Client
    ↓
FastAPI API Layer
    ↓
Service Layer
    ↓
Repository Layer
    ↓
MySQL Database / Excel File
```

## Project Structure

```text
inventory-mysql/
├── api/                 # FastAPI API layer
├── app/                 # Application entry point
├── config/              # Configuration files
├── core/                # Business logic and domain models
├── data/                # Excel data files
├── repository/          # Database and Excel repository layer
├── tests/               # Test cases using pytest
├── ui/                  # GUI-related files
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── run_api.py
├── run_gui.py
└── README.md
```

## Requirements

For local development:
- Python 3.10+
- MySQL
- pip

For Docker-based execution:
- Docker
- Docker Compose

## Environment Setup

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run Tests

```bash
pytest -q
```

Current test status:
```text
All tests are currently passing. 
```

## Run API Locally

```bash
python run_api.py
```
Then open:
```text
http://127.0.0.1:8000/docs
```

## API Endpoints

### Stock In

```text
POST /api/inventory/in
```

### Stock Out

```text
POST /api/inventory/out
```

## Run GUI

```bash
python run_gui.py
```
The GUI is a lightweight client that calls the FastAPI backend.
The main business logic is handled by the service and repository layers.

## Run with Docker Compose

```bash
docker compose up --build
```
To stop services:
```bash
docker compose down
```

## Platform Notes
Tests avoid relying on complete platform-specific error messages because Windows and Linux may return slightly different system-level messages.

### Known Issue: Excel File Lock Detection under WSL

When running this project inside WSL while `inventory.xlsx` is open in Windows Excel, the application may not reliably detect that the file is already in use.
This is because Windows Excel file locking may not be visible to the Linux/WSL process.
File-in-use detection works as expected when the application is run directly on Windows.

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- MySQL
- PyMySQL
- Docker Compose
- pytest

## Sample Data

A sample Excel file is provided for testing:

```text
data/sample_inventory.xlsx
```

This file contains demo inventory records only and does not include confidential data.

## Test Coverage

Current test coverage is about 87%.

## Future Improvements

- Add Docker Hub image publishing
- Add AWS S3 file storage support
- Add GitLab CI/CD pipeline
- Improve GUI design