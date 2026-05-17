# Inventory Management API
A Python inventory management project using FastAPI, SQLAlchemy, MySQL, Docker Compose, and pytest.
This project demonstrates a layered backend design with API, service, repository, and database layers. It supports inventory stock-in and stock-out operations, business error handling, and automated tests.

## Features
- FastAPI REST API
- MySQL database integration
- SQLAlchemy ORM
- Docker Compose environment
- Inventory stock-in and stock-out operations
- Business error handling
- Automated tests with pytest
- Basic GUI client for demonstration

## Project Structure
```text
inventory-mysql/
├── api/                 # FastAPI API layer
├── app/                 # Application entry point
├── config/              # Configuration files
├── core/                # Business logic and domain models
├── data/                # Excel data files
├── repository/          # Database / Excel repository layer
├── tests/               # pytest test cases
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
38 passed
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
The main business logic is handled by the service layer and database layer.

## Run with Docker Compose
```bash
docker compose up --build
```
To stop services:
```bash
docker compose down
```

## Platform Notes
Tests avoid relying on full platform-specific error message text because Windows and Linux may return slightly different system-level messages.

### Known Issue: Excel file lock detection under WSL
When running this project inside WSL and opening `inventory.xlsx` with Windows Excel, the application may not reliably detect that the file is already open.
This is because Windows Excel file locking may not be visible to the Linux/WSL process.
File-in-use detection works as expected when running the application directly on Windows.

## Tech Stack
- Python
- FastAPI
- SQLAlchemy
- MySQL
- PyMySQL
- Docker Compose
- pytest