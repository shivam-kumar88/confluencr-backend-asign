import os
import time
from celery import Celery
from pymongo import MongoClient
from datetime import datetime
# from upstash_redis import Redis



REDIS_URL = os.getenv("REDIS_URL", "rediss://default:AUgtAAIncDE0MWZiYWZmZDdlYjE0MTUxYjBmMWMyMWFlMDYzOGQwY3AxMTg0Nzc@busy-koi-18477.upstash.io:6379") #redis-cli --tls -u redis://default:AUgtAAIncDE0MWZiYWZmZDdlYjE0MTUxYjBmMWMyMWFlMDYzOGQwY3AxMTg0Nzc@busy-koi-18477.upstash.io:6379
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://user:user1234@confluencr.zfaihx7.mongodb.net/?appName=Confluencr")

# redis = Redis(url="https://busy-koi-18477.upstash.io", token="AUgtAAIncDE0MWZiYWZmZDdlYjE0MTUxYjBmMWMyMWFlMDYzOGQwY3AxMTg0Nzc")

# redis.set("foo", "bar")
# value = redis.get("foo")

celery_app = Celery("tasks", broker=REDIS_URL)

@celery_app.task(name="process_transaction")
def process_transaction_task(transaction_id: str):
    time.sleep(30)
    
    client = MongoClient(MONGO_URI)
    db = client.transaction_db
    
    db.transactions.update_one(
        {"transaction_id": transaction_id},
        {
            "$set": {
                "status": "PROCESSED", 
                "processed_at": datetime.utcnow() 
            }
        }
    )
    return f"Transaction {transaction_id} processed."