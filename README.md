# Inventory MySQL

![CI](https://github.com/alextwtp/inventory-mysql/actions/workflows/ci.yml/badge.svg)

## Inventory Management System

A lightweight inventory management system for daily stock IN / OUT operations.

This project started as a small internal inventory tool for real operational use in a small business environment. The first working version used a Tkinter GUI with Excel-based storage.

It was later extended with FastAPI, MySQL, SQLAlchemy, Docker Compose, automated testing, GitHub Actions CI, and Docker Hub publishing to demonstrate a more maintainable and production-oriented backend workflow.

---

## Features

* Inventory IN / OUT operations
* Excel-based inventory storage as the stable baseline
* Tkinter GUI for daily operation
* FastAPI backend APIs
* MySQL integration with SQLAlchemy
* Service and repository layer separation
* Dependency injection
* Business-rule validation and error handling
* Docker Compose environment
* Automated tests with pytest
* Coverage enforcement in CI
* GitHub Actions CI/CD
* Docker Hub image publishing
* Safe sample inventory data

---

## Architecture

The project contains two related execution paths.

### Excel-Based GUI Baseline

```text
run_gui.py
    ↓
Tkinter GUI
    ↓
InventoryService
    ↓
ExcelRepository
    ↓
Excel File
```

### FastAPI + MySQL Backend

```text
HTTP Client / Swagger UI
    ↓
FastAPI Endpoint
    ↓
InventoryMySQLService
    ↓
MySQLRepository
    ↓
SQLAlchemy
    ↓
MySQL Database
```

The Excel-based GUI is retained as the stable original implementation. The FastAPI + MySQL path demonstrates how the same inventory business rules can be moved into a database-backed backend service.

---

## Project Structure

Key project files and directories:

```text
inventory-mysql/
├── api/
│   ├── __init__.py
│   └── fastapi_app.py
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── db.py
│   ├── mysql_models.py
│   ├── check_mysql_conn.py
│   ├── check_database.py
│   └── check_inventory_orm.py
├── config/
│   ├── __init__.py
│   └── constants.py
├── core/
│   ├── __init__.py
│   ├── exceptions.py
│   ├── inventory_service.py
│   ├── inventory_mysql_service.py
│   └── item.py
├── data/
│   └── sample_inventory.xlsx
├── repository/
│   ├── __init__.py
│   ├── excel_repository.py
│   └── mysql_repository.py
├── scripts/
│   └── create_tables.py
├── tests/
│   ├── conftest.py
│   ├── test_fastapi.py
│   ├── test_repository.py
│   ├── test_service.py
│   ├── test_inventory_mysql_api.py
│   └── test_inventory_mysql_service.py
├── ui/
│   ├── __init__.py
│   └── gui_app.py
├── .github/
│   └── workflows/
│       └── ci.yml
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── pytest.ini
├── requirements.txt
├── run_api.py
├── run_gui.py
└── README.md
```

Generated cache files, local environment files, database data, test artifacts, and private Excel files are intentionally omitted from this structure.

---

## Requirements

### Local Development

* Python 3.10+
* pip
* MySQL 8.x for the database-backed API

### Container-Based Execution

* Docker
* Docker Compose

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a local `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Example host configuration:

```env
DB_HOST=127.0.0.1
DB_PORT=3307
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=inventory_db
```

The real `.env` file is excluded by `.gitignore` and must not be committed.

### MySQL Port Mapping

When connecting from the host machine or WSL:

```env
DB_HOST=127.0.0.1
DB_PORT=3307
```

When the application connects to MySQL inside Docker Compose:

```env
DB_HOST=mysql
DB_PORT=3306
```

Example MySQL Workbench connection:

```text
Host: 127.0.0.1
Port: 3307
User: root
Database: inventory_db
```

---

## Run the Excel-Based GUI

The GUI version is the original stable implementation and uses the Excel repository.

Run the GUI from the project root:

```bash
python3 run_gui.py
```

On Windows, this can also be run as:

```powershell
python run_gui.py
```

The GUI entry script creates the Tkinter application and injects the Excel repository and inventory service.

The MySQL FastAPI server is not required when running this direct Excel-based GUI path.

---

## Run MySQL with Docker Compose

Start the configured services:

```bash
docker compose up -d
```

Check service status:

```bash
docker compose ps
```

View service logs:

```bash
docker compose logs
```

Stop the services:

```bash
docker compose down
```

Remove the services and the MySQL data volume:

```bash
docker compose down -v
```

> Warning: `docker compose down -v` removes the database volume and its stored data.

---

## Run the FastAPI + MySQL API

Start MySQL first:

```bash
docker compose up -d
```

Then start the FastAPI server from the project root:

```bash
uvicorn app.main:app --reload
```

Default API URL:

```text
http://127.0.0.1:8000
```

Interactive Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

## FastAPI + MySQL Endpoints

### Health Check

```http
GET /
```

Example response:

```json
{
  "status": "ok",
  "message": "Inventory MySQL API is running"
}
```

### Get an Item

```http
GET /item/{pid}
```

Example:

```bash
curl http://127.0.0.1:8000/item/A001
```

### Inventory IN

```http
POST /inventory/in
```

Example request:

```bash
curl -X POST http://127.0.0.1:8000/inventory/in \
  -H "Content-Type: application/json" \
  -d '{
    "pid": "A001",
    "name": "Mouse",
    "qty": 5,
    "receiver": "",
    "shipper": "Vendor A"
  }'
```

### Inventory OUT

```http
POST /inventory/out
```

Example request:

```bash
curl -X POST http://127.0.0.1:8000/inventory/out \
  -H "Content-Type: application/json" \
  -d '{
    "pid": "A001",
    "name": "Mouse",
    "qty": 2,
    "receiver": "Customer A",
    "shipper": ""
  }'
```

---

## Expected MySQL API Response

Example successful response:

```json
{
  "status": "success",
  "message": "Item found",
  "item": {
    "pid": "A001",
    "name": "Mouse",
    "current_qty": 10,
    "buyer": "",
    "shipper": ""
  }
}
```

Application-level errors are converted into appropriate HTTP responses.

Unexpected SQLAlchemy errors trigger a database rollback and return an HTTP 500 database error response.

---

## Manual Database Checks

The project includes manual scripts for verifying MySQL connectivity, table setup, and ORM behavior.

Run the MySQL connection check:

```bash
python3 app/check_mysql_conn.py
```

Run the database check:

```bash
python3 app/check_database.py
```

Run the ORM check:

```bash
python3 app/check_inventory_orm.py
```

Typical expected results:

```text
Database connection successful
Table created or verified successfully
ORM operation completed successfully
```

These scripts are intended for manual integration verification and are separate from the normal unit-test suite.

---

## Run Official Tests

Run the complete test suite:

```bash
pytest -q
```

Run tests with coverage details:

```bash
pytest --cov=. --cov-report=term-missing
```

Last verified local result for the FastAPI + MySQL extension:

```text
58 passed, 1 skipped
Required test coverage of 80% reached
Total coverage: 85.12%
```

### Testing Strategy

The test suite covers:

* Inventory business rules
* Inventory IN and OUT operations
* Invalid quantity handling
* Insufficient-stock handling
* Item-not-found behavior
* Repository behavior
* FastAPI request and response behavior
* Endpoint routing
* Service dependency wiring
* Application error handling
* Database error rollback behavior

API-layer tests use fake service objects where appropriate. This keeps the normal test suite fast and stable without requiring a live MySQL database for every test run.

The real MySQL path is verified separately through Docker Compose and the manual database-check scripts.

---

## Sample Inventory Data

A safe sample Excel file is included for testing and demonstration:

```text
data/sample_inventory.xlsx
```

The sample file contains demonstration data only and does not contain confidential business information.

Some Excel-based tests may modify the sample file locally. Restore it before committing when necessary:

```bash
git restore data/sample_inventory.xlsx
```

Real operational Excel files are excluded from source control.

---

## GitHub Actions CI

The project uses GitHub Actions for automated testing and Docker image publishing.

The CI workflow runs on the `master` branch and performs the following general steps:

```text
1. Checkout source code
2. Set up Python 3.10 and Python 3.11
3. Install project dependencies
4. Run pytest
5. Enforce the coverage threshold
6. Build the Docker image after successful tests
7. Publish the image to Docker Hub when applicable
```

The configured minimum test coverage is:

```text
80%
```

A failed test or failed coverage check prevents the deployment stage from continuing.

---

## Docker Hub Image

The published Docker image is available as:

```text
alextwtpyeh/inventory-mysql
```

Pull the versioned release:

```bash
docker pull alextwtpyeh/inventory-mysql:v2.0.0
```

Pull the latest image:

```bash
docker pull alextwtpyeh/inventory-mysql:latest
```

Basic image verification:

```bash
docker run --rm alextwtpyeh/inventory-mysql:v2.0.0 python --version
```

Run the packaged test suite:

```bash
docker run --rm alextwtpyeh/inventory-mysql:v2.0.0 pytest -q
```

---

## CI/CD and Docker Hub Deployment

On a successful push to the `master` branch:

```text
Source Push
    ↓
GitHub Actions
    ↓
pytest and Coverage Gate
    ↓
Docker Image Build
    ↓
Docker Hub Login
    ↓
Docker Image Push
```

Docker Hub credentials are not stored in the repository.

They are configured as GitHub repository secrets:

* `DOCKERHUB_USERNAME`
* `DOCKERHUB_TOKEN`

The GitHub Actions workflow references these secrets during the Docker Hub login step.

---

## Security and Data-Safety Controls

The project follows several basic source-control and deployment safety practices:

* Real runtime credentials are stored in `.env`.
* `.env` is excluded by `.gitignore`.
* `.env.example` contains only safe placeholder values.
* Real operational Excel files are excluded from Git.
* Only safe sample inventory data is committed.
* Docker Hub credentials are stored as GitHub repository secrets.
* Docker images are published only after automated tests pass.
* The coverage threshold is enforced before deployment.
* Database connection settings are passed through environment variables.
* Private credentials are not hard-coded in the source code.

---

## Platform Notes

### Excel File Lock Detection under WSL

When the Excel-based version runs inside WSL while an Excel file is open in Windows Excel, the Linux process may not reliably detect the Windows file lock.

This is caused by differences between Windows and Linux file-lock behavior.

File-in-use detection works more reliably when the Excel-based application runs directly on Windows.

### Host and Container Ports

MySQL uses:

```text
3306 inside the Docker network
3307 from the host machine
```

The FastAPI server normally uses:

```text
8000
```

---

## Current Status

Current stable release:

```text
v2.0.0
```

Completed components:

* Excel-based inventory tool
* Tkinter GUI
* Inventory IN / OUT business rules
* Service and repository separation
* FastAPI backend
* MySQL repository
* SQLAlchemy ORM integration
* FastAPI + MySQL API path
* Dependency injection
* Application error handling
* Unit and API testing
* Docker Compose environment
* Coverage enforcement
* GitHub Actions CI
* Docker Hub image publishing
* Versioned Docker image
* Safe environment-variable handling
* Safe sample-data handling

---

## Technical Highlights

This project demonstrates the modernization of a small operational desktop tool into a structured backend system.

Main engineering concepts include:

* Layered architecture
* Service and repository separation
* Dependency injection
* Domain-oriented business rules
* REST API design
* Pydantic request validation
* SQLAlchemy ORM
* MySQL integration
* Transaction rollback on database errors
* Unit testing with pytest
* API testing with fake dependencies
* Docker Compose
* GitHub Actions CI/CD
* Coverage enforcement
* Docker Hub publishing
* Environment-variable security
* Sample-data isolation

---

## Future Improvements and Design Considerations

The following items are future design considerations and are not presented as completed features.

### Pagination and Filtering

Add pagination and filtering for larger inventory result sets to avoid loading excessive data into memory.

### Redis Cache Layer

Introduce Redis for selected high-frequency read operations, with explicit TTL and cache invalidation rules.

Potential cache risks to consider include:

* Cache penetration
* Cache breakdown
* Cache avalanche
* Stale-data handling

### Database Migration Control

Introduce Alembic for version-controlled SQLAlchemy schema migrations.

A migration workflow would make database changes repeatable across development, testing, and deployment environments.

### Transaction and Concurrency Control

Keep stock updates inside database transactions.

For concurrent updates to the same product, possible strategies include:

* Optimistic locking
* Pessimistic locking
* Appropriate transaction isolation levels

### Schema Design and Indexing

Maintain normalized data structures where practical and add indexes for frequently searched fields such as product ID.

### Backup and Recovery

Define database backup and restore procedures and establish recovery targets such as:

* Recovery Point Objective (RPO)
* Recovery Time Objective (RTO)

Database-engine REDO and UNDO logs support crash recovery, while application-level recovery requires tested backup and restore procedures.

### Scaling Considerations

For larger deployments, evaluate the trade-offs between:

* Vertical scaling
* Horizontal scaling
* Read replicas
* Connection pooling
* Stateless API deployment

---

## License

No license specified.
