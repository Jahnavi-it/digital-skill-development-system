import os
import re
from urllib.parse import urlparse
import pymysql
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("DATABASE_URL")

if database_url:
    parsed = urlparse(database_url.replace("mysql://", "mysql+pymysql://", 1).replace("mysql+pymysql://", "mysql://", 1))
    DB_HOST = parsed.hostname
    DB_PORT = parsed.port or 3306
    DB_USER = parsed.username
    DB_PASSWORD = parsed.password
    DB_NAME = parsed.path.lstrip("/")
else:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "dsds_db")

print(f"Connecting to {DB_HOST}:{DB_PORT} as {DB_USER}, database '{DB_NAME}'...")

conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)

with open("schema.sql", "r", encoding="utf-8") as f:
    sql_text = f.read()

sql_text = re.sub(r"--.*", "", sql_text)
statements = [s.strip() for s in sql_text.split(";") if s.strip()]

print(f"Found {len(statements)} statements to run...")

with conn.cursor() as cursor:
    for i, stmt in enumerate(statements, 1):
        try:
            cursor.execute(stmt)
            print(f"[{i}/{len(statements)}] OK: {stmt[:60].splitlines()[0]}...")
        except Exception as e:
            print(f"[{i}/{len(statements)}] FAILED: {stmt[:60].splitlines()[0]}...")
            print(f"    Error: {e}")

conn.commit()
conn.close()
print("Done. Schema import finished.")