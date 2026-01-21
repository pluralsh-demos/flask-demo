import os
from flask import Flask, jsonify
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)

# Database configuration
DATABASE_URL = os.environ.get("POSTGRES_URL")


def get_db_engine():
    """Create and return a database engine."""
    if not DATABASE_URL:
        return None
    return create_engine(DATABASE_URL)


@app.route("/")
def index():
    """Hello world endpoint."""
    return jsonify({"message": "Hello from Flask!", "status": "running"})


@app.route("/health")
def health():
    """Health check endpoint that validates PostgreSQL connection."""
    health_status = {
        "status": "healthy",
        "database": "unknown"
    }
    
    if not DATABASE_URL:
        health_status["status"] = "unhealthy"
        health_status["database"] = "not_configured"
        health_status["error"] = "POSTGRES_URL environment variable not set"
        return jsonify(health_status), 503
    
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
                return jsonify(health_status), 503
    except SQLAlchemyError as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = "error"
        health_status["error"] = str(e)
        return jsonify(health_status), 503
    
    return jsonify(health_status), 200


@app.route("/ready")
def ready():
    """Readiness probe - checks if app can serve traffic."""
    return jsonify({"ready": True}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
