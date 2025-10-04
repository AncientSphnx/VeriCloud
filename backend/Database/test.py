# atlas_test.py
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from pymongo import MongoClient, errors
from datetime import datetime

load_dotenv()

# Option A: use single MONGODB_URI env var if you put the full URI there
MONGODB_URI = "mongodb+srv://Numan_admin:Smg1947%40%23@cluster0.xefwuvx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Option B: or build the URI from separate vars (safe encoding)
MONGO_USER = "Numan_admin"
MONGO_PASS = "Smg1947%40%23"
MONGO_HOST = "cluster0.xefwuvx.mongodb.net"   # e.g. cluster0.abcd.mongodb.net
MONGO_DB   = "LieDetection"

if not MONGODB_URI:
    if not (MONGO_USER and MONGO_PASS and MONGO_HOST):
        raise SystemExit("Set MONGODB_URI or MONGO_USER / MONGO_PASS / MONGO_HOST in .env")
    MONGODB_URI = f"mongodb+srv://{quote_plus(MONGO_USER)}:{quote_plus(MONGO_PASS)}@{MONGO_HOST}/{MONGO_DB}?retryWrites=true&w=majority"

print("Using URI:", MONGODB_URI.replace(quote_plus(MONGO_PASS), "*****") if MONGO_PASS else "from env var")

try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    # Ping to check connection
    client.admin.command("ping")
    print("✅ Connected to Atlas (ping ok).")

    db = client[MONGO_DB]
    # Insert a sample user (safe to run multiple times)
    user = {"name": "Test User", "email": "test@example.com", "createdAt": datetime.utcnow()}
    res = db.users.insert_one(user)
    print("Inserted sample user id:", res.inserted_id)

    # Query back
    doc = db.users.find_one({"_id": res.inserted_id})
    print("Found document:", doc)

except errors.ServerSelectionTimeoutError as e:
    print("❌ Server selection timeout — check Network Access (IP whitelist) and your internet.")
    print(str(e))
except errors.OperationFailure as e:
    print("❌ Authentication / operation failure — check username/password and roles.")
    print(str(e))
except Exception as e:
    print("❌ Unexpected error:", str(e))
