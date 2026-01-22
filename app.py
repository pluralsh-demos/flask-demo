import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

app = FastAPI()

# Database configuration
DATABASE_URL = os.environ.get("POSTGRES_URL")


def get_db_engine():
    """Create and return a database engine."""
    if not DATABASE_URL:
        return None
    # Use psycopg3 driver - convert postgres:// to postgresql+psycopg://
    db_url = DATABASE_URL
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return create_engine(db_url)


@app.get("/")
async def index():
    """Hello world endpoint."""
    return {"message": "Hello from FastAPI!", "status": "running"}


@app.get("/health")
async def health():
    """Health check endpoint that validates PostgreSQL connection."""
    health_status = {
        "status": "healthy",
        "database": "unknown"
    }
    
    if not DATABASE_URL:
        health_status["status"] = "unhealthy"
        health_status["database"] = "not_configured"
        health_status["error"] = "POSTGRES_URL environment variable not set"
        print('health check failed', health_status)
        return JSONResponse(content=health_status, status_code=503)
    
    try:
        engine = get_db_engine()
        with engine.connect() as connection:
            # Execute a simple query to verify the connection works
            result = connection.execute(text("SELECT 1 as health_check"))
            row = result.fetchone()
            if row and row[0] == 1:
                health_status["database"] = "connected"
            else:
                health_status["status"] = "unhealthy"
                health_status["database"] = "query_failed"
                print('health check failed', health_status)
                return JSONResponse(content=health_status, status_code=503)
    except SQLAlchemyError as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = "error"
        health_status["error"] = str(e)
        print('health check failed', health_status)
        return JSONResponse(content=health_status, status_code=503)
    
    return JSONResponse(content=health_status, status_code=200)


@app.get("/ready")
async def ready():
    """Readiness probe - checks if app can serve traffic."""
    return JSONResponse(content={"ready": True}, status_code=200)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
