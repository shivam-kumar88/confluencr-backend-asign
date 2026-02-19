import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, status, HTTPException, BackgroundTasks
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from models import TransactionWebhook, TransactionResponse
from worker import celery_app


MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://user:user1234@confluencr.zfaihx7.mongodb.net/?appName=Confluencr")
client = AsyncIOMotorClient(
    MONGO_URI,
    minPoolSize=5,          
    maxPoolSize=20,         
    serverSelectionTimeoutMS=2000,
    connectTimeoutMS=5000,
    socketTimeoutMS=5000,
    maxIdleTimeMS=30000,    
    retryWrites=True
)
db = client.transaction_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await client.admin.command("ping")
        print("MongoDB connection healthy")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
    yield
    client.close()

app = FastAPI(lifespan=lifespan) 

@app.get("/")
async def health_check():
    return {
        "status": "HEALTHY", 
        "current_time": datetime.utcnow().isoformat()
    }

@app.post("/v1/webhooks/transactions", status_code=status.HTTP_202_ACCEPTED) 
async def handle_webhook(webhook: TransactionWebhook, background_tasks: BackgroundTasks):
    
    existing = await db.transactions.find_one(
        {"transaction_id": webhook.transaction_id},
        projection={"_id": 1}  
    )
    
    if existing:
        return {"message": "Transaction already received"}

    # txn_data = webhook.dict()
    # txn_data.update({
    #     "status": "PROCESSING",
    #     "created_at": datetime.utcnow(), 
    #     "processed_at": None
    # })
    
    # await db.transactions.insert_one(txn_data)
    # celery_app.send_task("process_transaction", args=[webhook.transaction_id])

    async def process_in_bg():
        txn_data = webhook.dict()
        txn_data.update({
            "status": "PROCESSING",
            "created_at": datetime.utcnow(),
            "processed_at": None
        })
        await db.transactions.insert_one(txn_data)
        celery_app.send_task("process_transaction", args=[webhook.transaction_id])

    
    background_tasks.add_task(process_in_bg)
    return {"message": "Accepted"} 

@app.get("/v1/transactions/{transaction_id}") 
async def get_transaction(transaction_id: str):
    txn = await db.transactions.find_one({"transaction_id": transaction_id})
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    txn.pop("_id", None)
    return txn
