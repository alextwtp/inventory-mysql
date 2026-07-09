# Inventory MySQL

![CI](https://github.com/alextwtp/inventory-mysql/actions/workflows/ci.yml/badge.svg)

# Inventory Management System

A lightweight inventory management system for daily stock IN / OUT operations.

This project started as a small internal inventory tool for real operational use in a small business environment. The first working version was built with a GUI and Excel-based storage. It was later extended with FastAPI, MySQL, Docker Compose, automated tests, and GitHub Actions CI to make the backend workflow more maintainable and production-oriented.

---

## Features

* Inventory IN / OUT operations
* Excel-based inventory storage as the stable baseline
* GUI client for daily operation
* FastAPI backend APIs
* MySQL integration with SQLAlchemy
* Docker Compose environment for MySQL
* Service / repository separation
* API-layer tests with fake service objects
* Unit tests with pytest
* GitHub Actions CI for automated testing
* Docker Hub image publishing from the master branch
* Sample inventory file for testing and demo usage

---

## Project Structure

```text
inventory-mysql/
├── app/
│   ├── main.py
│   ├── db.py
│   ├── mysql_models.py
│   └── ...
├── core/
│   ├── inventory_service.py
│   ├── inventory_mysql_service.py
│   ├── item.py
│   └── exceptions.py
├── repository/
│   ├── excel_repository.py
│   └── mysql_repository.py
├── data/
│   └── sample_inventory.xlsx
├── scripts/
│   └── ...
├── tests/
│   ├── test_inventory_mysql_service.py
│   ├── test_inventory_mysql_api.py
│   └── ...
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .github/
│   └── workflows/
│       └── ci.yml
└── README.md
```

---

## Requirements

* Python 3.10+
* MySQL 8.x
* Docker
* Docker Compose
* pip

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file if running with MySQL or Docker Compose.

Example:

```env
DB_HOST=127.0.0.1
DB_PORT=3307
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=inventory_db
```

When running inside Docker Compose, MySQL uses port `3306` internally.

When connecting from the host machine or WSL, use the host-mapped port `3307`.

---

## Run MySQL with Docker Compose

Start the MySQL container:

```bash
docker compose up -d
```

Check running containers:

```bash
docker compose ps
```

Stop containers:

```bash
docker compose down
```

Remove containers and database volume:

```bash
docker compose down -v
```

---

## FastAPI + MySQL API Extension

This project includes a FastAPI + MySQL version as a backend API extension.

The goal of this extension is to demonstrate a layered backend design:

```text
FastAPI endpoint
→ Service layer
→ Repository layer
→ MySQL database
```

The original Excel-based version is kept as the stable baseline, while the MySQL API version demonstrates how the same inventory business rules can be moved toward a database-backed backend service.

### API entry point

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

Default API URL:

```text
http://127.0.0.1:8000
```

Interactive API docs:

```text
http://127.0.0.1:8000/docs
```

Root health check:

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

### API endpoints

```http
GET /item/{pid}
POST /inventory/in
POST /inventory/out
```

### Inventory-in example

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

### Inventory-out example

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

### Get item example

```bash
curl http://127.0.0.1:8000/item/A001
```

### Expected successful response

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

### MySQL connection notes

When running the FastAPI app from the host machine or WSL, use the host-mapped MySQL port:

```env
DB_HOST=127.0.0.1
DB_PORT=3307
```

When running inside Docker Compose, the app should connect to the MySQL service name and internal container port:

```env
DB_HOST=mysql
DB_PORT=3306
```

Workbench connection example:

```text
Host: 127.0.0.1
Port: 3307
User: root
Database: inventory_db
```

---

## Run GUI Client

The GUI version was the original daily-use interface and is kept as the stable Excel-based baseline.

Start the FastAPI server first if using the API-connected GUI flow:

```bash
uvicorn app.main:app --reload
```

Then run the GUI entry script used by the current branch.

Example:

```bash
python3 run_gui.py
```

---

## Manual Database Check Scripts

The project includes manual scripts for verifying MySQL connectivity, database setup, and ORM behavior.

Example commands:

```bash
python3 app/check_mysql_conn.py
python3 app/check_database.py
python3 app/check_inventory_orm.py
```

Expected result:

```text
Database connection successful
Table created or verified successfully
ORM operation completed successfully
```

---

## Run Official Tests

Run all tests:

```bash
pytest -q
```

Current local result on the FastAPI + MySQL feature branch:

```text
58 passed, 1 skipped
Required test coverage of 80% reached
Total coverage: 85.12%
```

Run tests with coverage:

```bash
pytest --cov=. --cov-report=term-missing
```

### Testing strategy

The MySQL API version includes API-layer tests using a fake service instead of a live MySQL database.

This keeps the normal pytest suite fast and stable while still testing:

```text
- FastAPI request / response behavior
- endpoint routing
- service-layer call wiring
- application error handling
- database error rollback behavior
```

The real MySQL repository can be verified with a running MySQL container and manual check scripts. Normal unit tests avoid depending on live database state.

---

## Sample Inventory File

A sample Excel file is provided for testing and demo usage:

```text
data/sample_inventory.xlsx
```

The sample file is safe to upload to GitHub because it does not contain private or sensitive data.

Some Excel-based tests may modify this sample file during local testing. Before committing, restore it if needed:

```bash
git restore data/sample_inventory.xlsx
```

---

## GitHub Actions CI

This project uses GitHub Actions to run automated tests.

The CI workflow currently runs on the `master` branch. Feature branches can be pushed normally, but they may not appear in the GitHub Actions run list unless the workflow is configured to trigger on that branch or the branch is merged into `master`.

Typical CI steps:

```text
1. Checkout source code
2. Set up Python
3. Install dependencies
4. Run pytest with coverage gate
5. Build and publish Docker image when applicable
```

Expected result:

```text
All tests passed
CI completed successfully
```

---

## Docker Hub Image Verification

The Docker image has been published to Docker Hub from the master branch:

```bash
docker pull alextwtpyeh/inventory-mysql:latest
```

Basic runtime verification:

```bash
docker run --rm alextwtpyeh/inventory-mysql:latest python --version
```

Run the project test suite inside the Docker image:

```bash
docker run --rm alextwtpyeh/inventory-mysql:latest pytest -q
```

Expected result may vary depending on whether the image was built from the master branch or a feature branch.

---

## CI/CD and Docker Hub Deployment

This project uses GitHub Actions for continuous integration and Docker image publishing.

On each push or pull request to the `master` branch, the workflow runs the test suite with coverage checks on Python 3.10 and Python 3.11.

When changes are pushed to the `master` branch and all tests pass, GitHub Actions builds the Docker image and pushes it to Docker Hub as:

```bash
alextwtpyeh/inventory-mysql:latest
```

Docker Hub credentials are not stored in the repository. They are stored securely as GitHub repository secrets:

* `DOCKERHUB_USERNAME`
* `DOCKERHUB_TOKEN`

The workflow references these secrets during the Docker Hub login step. This prevents sensitive credentials from being committed to source control.

---

## Security and Deployment Notes

This project does not commit real runtime credentials to the repository.

* Real environment variables are stored in `.env`, which is excluded by `.gitignore`.
* `.env.example` is provided as a safe template for local setup.
* Real Excel data files are ignored by default.
* `data/sample_inventory.xlsx` is included only as a safe sample file.
* Docker Hub credentials are stored as GitHub repository secrets and referenced by the GitHub Actions workflow.
* The Docker image build and push job runs only after tests pass and only on pushes to the `master` branch.

The deployment setup was verified with Docker Compose:

* Python app container build
* MySQL 8.4 container startup
* app-to-MySQL connection check
* basic database check
* ORM insert/query check
* pytest with coverage gate

---

## Current Status

* GUI-based inventory tool: completed and used as the initial working version
* Excel-based inventory storage: completed and kept as the stable baseline
* FastAPI backend API: completed
* GUI-to-API integration: completed
* MySQL repository extension: completed
* FastAPI + MySQL API path: completed
* API-layer tests with fake service: completed
* Docker Compose MySQL environment: completed
* GitHub Actions CI: completed on master branch
* Docker Hub image publishing: completed on master branch

---

## Technical Highlights

This project demonstrates a practical backend workflow based on a small real-world inventory use case.

Main engineering points include:

* Service / repository separation
* Dependency injection
* API request and response design
* Centralized error handling
* Unit testing with pytest
* API-layer tests without requiring a live database
* MySQL integration with SQLAlchemy
* Docker Compose for local database environment
* GitHub Actions for CI automation
* Docker Hub publishing with repository secrets
* Environment variable and sample-data safety controls

The goal is to keep the system lightweight while showing a clear path from a simple desktop tool to a more structured backend service.

---

## Future Improvements / Design Considerations

Beyond the current FastAPI + MySQL implementation, the project can be extended in the following directions. These items are listed as design considerations and future improvements, not as completed features.

- **Pagination and filtering:** Add pagination for large query results and inventory search responses to reduce memory usage and avoid loading too much data at once.
- **Redis cache layer:** Introduce a cache layer such as Redis for high-frequency, mostly read-only queries, with clear TTL and invalidation rules.
- **Database migration control:** Manage schema changes with a migration tool such as Alembic for SQLAlchemy/MySQL, or Flyway in a mixed-stack environment, so database changes are version-controlled and repeatable.
- **Transaction and concurrency control:** Keep stock IN/OUT updates inside database transactions, and consider optimistic or pessimistic locking when concurrent updates may affect the same item.
- **Schema design and indexing:** Keep the database schema normalized where practical, and add indexes for common lookup fields such as product ID to improve query performance.
- **Backup and recovery planning:** Define backup/restore procedures and business recovery targets such as RPO and RTO. At the database-engine level, REDO/UNDO logs are part of crash recovery concepts, while application-level recovery should focus on tested restore procedures.

---

## License

No license specified.

