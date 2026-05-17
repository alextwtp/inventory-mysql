## Known Issue: Excel file lock detection under WSL

When running this project inside WSL and opening `inventory.xlsx` with Windows Excel,
the application may not reliably detect that the file is already open.

This is because Windows Excel file locking may not be visible to the Linux/WSL process.

File-in-use detection works as expected when running the application directly on Windows.
####
The GUI is a lightweight client that calls the FastAPI backend.
The main business logic is handled by the service layer and database layer.