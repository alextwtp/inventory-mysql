import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


load_dotenv()

DB_USER = os.getenv("MYSQL_USER")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD")
DB_NAME = os.getenv("MYSQL_DATABASE")

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@127.0.0.1:3307/{DB_NAME}"
)

engine = create_engine(DATABASE_URL, echo=True)

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1 AS test_value"))
    row = result.fetchone()
    print("Connection OK:", row.test_value)
    #print("URL", DATABASE_URL)
    #URL mysql+pymysql://appuser:app1234@127.0.0.1:3307/inventory_db