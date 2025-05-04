from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def insert_tender_record(tender_id, s3_url):
    data = {
        "tender_id": tender_id,
        "s3_url": s3_url
    }

    try:
        response = supabase.table("tenders").insert(data).execute()
        print("✅ Inserted:", response.data)
        return response.data
    except Exception as e:
        print("❌ Error inserting data:", e)
        return None
