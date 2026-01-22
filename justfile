# Test database configuration
export POSTGRES_URL := "postgresql://testuser:testpass@localhost:5432/testdb"

# Start the test PostgreSQL database
db-up:
    docker compose up -d postgres
    @echo "Waiting for PostgreSQL to be ready..."
    @until docker compose exec -T postgres pg_isready -U testuser -d testdb > /dev/null 2>&1; do \
        sleep 1; \
    done
    @echo "PostgreSQL is ready!"

# Stop the test database
db-down:
    docker compose down -v

# Run tests (assumes db is running)
test *ARGS:
    pytest tests/ -v {{ARGS}}

# Run tests with coverage
test-cov:
    pytest tests/ -v --cov=app --cov-report=xml --cov-report=term-missing

# Start db, run tests, stop db
test-all: db-up test-cov db-down

# Start db, run tests with coverage, stop db
ci: db-up test-cov db-down

# Install dependencies
deps:
    pip install -r requirements.txt

# Full setup: install deps and run tests
setup: deps db-up test-cov db-down

