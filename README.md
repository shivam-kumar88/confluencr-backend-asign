## Tech Stack
- ** Framework: FastAPI — Chosen for its high performance and native asynchronous support, making it the most suitable framework for high-throughput webhook ingestion.

- ** Background Worker: Celery with Redis — Used for reliable background task management to ensure the API remains responsive while tasks run in the background.


- ** Database: MongoDB — Utilized for this assessment due to its ease of deployment for demonstration purposes  however, PostgreSQL remains the preferred choice for long-term production use to ensure ACID compliance.


## Installation & Setup

### 1. Environment Setup
It is recommended to use a virtual environment:
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate # Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt


### 1. Running the Service
The project requires both the FastAPI application and the Celery worker to be running simultaneously.

# Start the Celery Worker:
celery -A worker.celery_app worker --loglevel=info

# Start the FastAPI Server:
uvicorn main:app --reload


The project will be accessible at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)


# FastAPI over Django: 
FastAPI was selected because it is lightweight and handles asynchronous requests more efficiently than Django for specific microservices like this assessment.


# Worker Pattern: 
By offloading the 30-second delay to Celery , the service guarantees high availability and responsiveness even under heavy load.

# Automatic Documentation: 
Interactive Swagger documentation is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)



## Deployments 

- For FastAPI project I am using Railway to deploy beacuse it support worker and FastAPI to run Simultaneously in it (unlike vercel)
- for Redis upstash [https://upstash.com/](upstash)
- For database Serverless mongoDb is alredy being used  
