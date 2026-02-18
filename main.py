import os
from fastapi import FastAPI, status, HTTPException
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from models import TransactionWebhook, TransactionResponse
from worker import celery_app

app = FastAPI()

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://user:user1234@confluencr.zfaihx7.mongodb.net/?appName=Confluencr")
client = AsyncIOMotorClient(MONGO_URI)
db = client.transaction_db

@app.get("/")
async def health_check():
    return {
        "status": "HEALTHY", 
        "current_time": datetime.utcnow().isoformat()
    }

@app.post("/v1/webhooks/transactions", status_code=status.HTTP_202_ACCEPTED) 
async def handle_webhook(webhook: TransactionWebhook):
    existing = await db.transactions.find_one({"transaction_id": webhook.transaction_id})
    
    if existing:
        return {"message": "Transaction already received"}

    txn_data = webhook.dict()
    txn_data.update({
        "status": "PROCESSING",
        "created_at": datetime.utcnow(), 
        "processed_at": None
    })
    await db.transactions.insert_one(txn_data)

    celery_app.send_task("process_transaction", args=[webhook.transaction_id])
    
    return {"message": "Accepted"} 

@app.get("/v1/transactions/{transaction_id}") 
async def get_transaction(transaction_id: str):
    txn = await db.transactions.find_one({"transaction_id": transaction_id})
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    txn.pop("_id", None)
    return txn