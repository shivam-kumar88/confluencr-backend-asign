
import os
import time
from celery import Celery
from pymongo import MongoClient
from datetime import datetime

REDIS_URL = os.getenv("REDIS_URL", "rediss://default:AUgtAAIncDE0MWZiYWZmZDdlYjE0MTUxYjBmMWMyMWFlMDYzOGQwY3AxMTg0Nzc@busy-koi-18477.upstash.io:6379")
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://user:user1234@confluencr.zfaihx7.mongodb.net/?appName=Confluencr")

mongo_client = MongoClient(
    MONGO_URI,
    minPoolSize=3,
    maxPoolSize=10,
    serverSelectionTimeoutMS=2000,
    connectTimeoutMS=5000,
    socketTimeoutMS=10000,
    maxIdleTimeMS=60000,  
    retryWrites=True
)
db = mongo_client.transaction_db

# Warm on startup
db.command("ping")
print("MongoDB worker connection ready")

celery_app = Celery("tasks", broker=REDIS_URL, worker_pool="solo")  

@celery_app.task(name="process_transaction")
def process_transaction_task(transaction_id: str):
    time.sleep(30)  
    
    db.transactions.update_one(
        {"transaction_id": transaction_id},
        {"$set": {
            "status": "PROCESSED", 
            "processed_at": datetime.utcnow() 
        }}
    )
    return f"Transaction {transaction_id} processed."
