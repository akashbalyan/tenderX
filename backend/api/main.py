from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Optional CORS setup if you’ll access from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT", 5432)
    )

@app.get("/tenders")
def get_tenders():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT tender_id, s3_url FROM tenders;")
        rows = cursor.fetchall()
        tenders = [{"tender_id": row[0], "s3_url": row[1]} for row in rows]
        cursor.close()
        conn.close()
        return {"tenders": tenders}
    except Exception as e:
        return {"error": str(e)}
