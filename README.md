# Inventory MySQL

![CI](https://github.com/alextwtp/inventory-mysql/actions/workflows/ci.yml/badge.svg)


# Inventory Management System

A lightweight inventory management system for daily stock IN / OUT operations.

This project started as a small internal inventory tool for real operational use in a small business environment. The first working version was built with a GUI and Excel-based storage. It was later extended with FastAPI, MySQL, Docker Compose, automated tests, and GitHub Actions CI to make the backend workflow more maintainable and production-oriented.

---

## Features

* Inventory IN / OUT operations
* Excel-based inventory storage
* GUI client for daily operation
* FastAPI backend APIs
* MySQL integration with SQLAlchemy
* Docker Compose environment for MySQL
* Unit tests with pytest
* GitHub Actions CI for automated testing
* Sample inventory file for testing and demo usage

---

## Project Structure

```text
inventory-mysql/
├── app/
│   ├── fastapi_app.py
│   ├── gui_app.py
│   ├── inventory_service.py
│   ├── excel_repository.py
│   ├── mysql_models.py
│   ├── db.py
│   └── ...
├── tests/
│   ├── test_service.py
│   ├── test_api.py
│   └── ...
├── sample_inventory.xlsx
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
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
DB_HOST=localhost
DB_PORT=3307
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=inventory_db
```

When running inside Docker Compose, MySQL uses port `3306` internally.

When connecting from the host machine, use port `3307`.

---

## Run FastAPI Server

```bash
uvicorn app.fastapi_app:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

---

## API Endpoints

### Inventory IN

```http
POST /api/inventory/in
```

Example request:

```json
{
  "pid": "P001",
  "qty": 10,
  "shipper": "ABC Supplier"
}
```

### Inventory OUT

```http
POST /api/inventory/out
```

Example request:

```json
{
  "pid": "P001",
  "qty": 3,
  "receiver": "Customer A"
}
```

---

## Expected API Response

Successful response:

```json
{
  "success": true,
  "data": {
    "pid": "P001",
    "current_qty": 17
  },
  "error": null
}
```

Failed response example:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ITEM_NOT_FOUND",
    "message": "Item not found"
  }
}
```

---

## Run GUI Client

Start the FastAPI server first:

```bash
uvicorn app.fastapi_app:app --reload
```

Then run the GUI client:

```bash
python3 ui/gui_app.py
```

The GUI sends requests to the FastAPI backend.

---

## Run Official Tests

Run all tests:

```bash
pytest -q
```

Run tests with coverage:

```bash
pytest --cov=app --cov-report=term-missing
```

Expected result:

```text
All tests passed
```

---

## Run MySQL with Docker Compose

Start MySQL container:

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

## Manual Database Check Scripts

Run MySQL connection test:

```bash
python3 app/check_mysql_conn.py
```

Run database check:

```bash
python3 app/check_database.py
```

Run ORM check:

```bash
python3 app/check_inventory_orm.py
```

Expected result:

```text
Database connection successful
Table created or verified successfully
ORM operation completed successfully
```

---

## MySQL Connection Notes

For host machine connection:

```env
DB_HOST=localhost
DB_PORT=3307
```

For container-to-container connection:

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

## Sample Inventory File

A sample Excel file is provided for testing and demo usage:

```text
sample_inventory.xlsx
```

The sample file is safe to upload to GitHub because it does not contain private or sensitive data.

---

## GitHub Actions CI

This project uses GitHub Actions to run automated tests.

The CI workflow runs when code is pushed to GitHub or when a pull request is created.

Typical CI steps:

```text
1. Checkout source code
2. Set up Python
3. Install dependencies
4. Run pytest
```

Expected result:

```text
All tests passed
CI completed successfully
```

---

## Current Status

* GUI-based inventory tool: completed and used as the initial working version
* Excel-based inventory storage: completed
* FastAPI backend API: completed
* GUI-to-API integration: completed
* Unit tests: completed
* MySQL basic integration: completed
* Docker Compose MySQL environment: completed
* GitHub Actions CI: completed
* Dockerized application runtime: optional next step

---

## Technical Highlights

This project demonstrates a practical backend workflow based on a small real-world inventory use case.

Main engineering points include:

* Service / repository separation
* Dependency injection
* API request and response design
* Centralized error handling
* Unit testing with pytest
* MySQL integration with SQLAlchemy
* Docker Compose for local database environment
* GitHub Actions for CI automation

The goal is to keep the system lightweight while showing a clear path from a simple desktop tool to a more structured backend service.

---

## License

No license specified.
