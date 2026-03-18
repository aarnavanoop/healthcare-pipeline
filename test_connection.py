import psycopg2
import os

print("Script started", flush=True)

try:
    conn = psycopg2.connect(
        host="db",
        port=5432,
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )
    print("Connected successfully.", flush=True)
    conn.close()

except Exception as e:
    print(f"Connection failed: {e}", flush=True)

print("Script finished", flush=True)