# URL Shortener

A fast and scalable URL shortener built with FastAPI and PostgreSQL. This application provides a simple API to shorten long URLs and track visit statistics.

## Features

- **URL Shortening**: Convert long URLs into short, memorable codes
- **Visit Tracking**: Track the number of visits for each shortened URL
- **Statistics API**: Get detailed statistics about shortened URLs
- **Request Logging**: Comprehensive logging with IP tracking and timestamps
- **Database Migrations**: Alembic-based database schema management
- **Load Testing**: Built-in Locust configuration for performance testing

## How to Use

### Running with Docker

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd url-shortener
   ```

2. **Start the services**:
   ```bash
   cd docker
   docker compose -f ./docker/docker-compose.yml up -d
   ```

   This will start:
   - PostgreSQL database on port 5432
   - pgAdmin on port 5555 (admin@admin.com / admin)
   - Main FastAPI application

   The application will be available at `http://localhost:8000`.
   
   pgAdmin will be available at `http://localhost:5555`.

### Running without Docker

1. **Install PostgreSQL** and create a database named `shortener`

2. **Set up environment variables** (create a `.env` file):
   ```env
   DATABASE_URI=postgresql+asyncpg://postgres:postgres@localhost:5432/shortener
   DEFAULT_DOMAIN=http://localhost:8000
   SHORT_URL_LENGTH=6
   ```

3. **Install dependencies using uv**:
   ```bash
   # Install uv
   pip install uv

   # Install project dependencies
   uv sync

   # Install development dependencies (optional)
   uv sync --group dev

   # Install test dependencies (optional)
   uv sync --group test
   ```

4. **Run database migrations**:
   ```bash
   python src/migrate.py upgrade head
   ```

5. **Start the application**:
   ```bash
   python src/main.py
   ```

### API Usage

#### Shorten a URL
```bash
curl -X POST "http://localhost:8000/api/v1/link/shorten" \
     -H "Content-Type: application/json" \
     -d '{"target_url": "https://www.example.com"}'
```

Response:
```json
{
  "shortened_url": "http://localhost:8000/abc123",
  "target_url": "https://www.example.com"
}
```

#### Get URL Statistics
```bash
curl "http://localhost:8000/api/v1/link/stats/abc123"
```

Response:
```json
{
  "short_url": "http://localhost:8000/abc123",
  "target_url": "https://www.example.com",
  "visits_count": 5,
  "created_at": "2024-01-15T10:30:00"
}
```

#### Access Shortened URL
Simply visit the shortened URL in your browser:
```
http://localhost:8000/abc123
```

This will redirect you to the original URL and increment the visit counter.

## Database Design

### Tables and Relationships

The application uses two main tables with a one-to-many relationship:

#### Link Table
```sql
CREATE TABLE link (
    id INTEGER PRIMARY KEY,
    target TEXT NOT NULL,           -- Original URL to redirect to
    code TEXT NOT NULL UNIQUE,      -- Short code (indexed)
    created_at DATETIME NOT NULL,   -- When the link was created
    visits_count INTEGER DEFAULT 0  -- Cached visit count for performance
);
```

#### Visit Table
```sql
CREATE TABLE visit (
    id INTEGER PRIMARY KEY,
    link_id INTEGER NOT NULL,       -- Foreign key to link.id
    utm TEXT,                       -- UTM parameters (optional)
    visited_at DATETIME NOT NULL    -- When the visit occurred
);
```

### Database Relationships

- **Link → Visit**: One-to-Many relationship
- Each `Link` can have multiple `Visit` records
- `Visit.link_id` references `Link.id`
- The `visits_count` field in `Link` is maintained for performance optimization

### Migration Management

#### Migration Files Location
Database migrations are located in:
```
src/database/revisions/versions/
├── 1755184061_.py                    # Initial schema creation
├── 1755249632_add_visits_count_field.py  # Added visits_count field
```

#### Migration Configuration
- **Alembic config**: `src/database/revisions/alembic.ini`
- **Environment setup**: `src/database/revisions/env.py`

#### Creating and Applying Migrations

**Create a new migration**:
```bash
python src/migrate.py revision --autogenerate -m "description of changes"
```

**Apply migrations**:
```bash
# Upgrade to latest
python src/migrate.py upgrade head

# Upgrade to specific revision
python src/migrate.py upgrade <revision_id>

# Downgrade one revision
python src/migrate.py downgrade -1
```

**Check migration status**:
```bash
python src/migrate.py current
python src/migrate.py history
```

## Project Structure

### Folder Organization

```
url-shortener/
├── src/                          # Main application source
│   ├── config/                   # Configuration management
│   │   ├── __init__.py
│   │   └── conf.py              # Settings and environment variables
│   ├── database/                 # Database layer
│   │   ├── __init__.py
│   │   ├── core.py              # Database engine and session management
│   │   └── revisions/           # Alembic migration files
│   │       ├── alembic.ini      # Alembic configuration
│   │       ├── env.py           # Migration environment setup
│   │       └── versions/        # Migration scripts
│   ├── link/                     # Link domain module
│   │   ├── api/                 # API layer
│   │   │   └── v1/              # API version 1
│   │   │       ├── routers.py   # FastAPI route handlers
│   │   │       └── schemas.py   # Pydantic models for API
│   │   ├── models.py            # SQLModel database models
│   │   ├── repo.py              # Database repository layer
│   │   └── service.py           # Business logic layer
│   ├── logger.py                # Logging configuration and decorators
│   ├── main.py                  # FastAPI application entry point
│   ├── migrate.py               # Migration script wrapper
│   └── routers.py               # Main router configuration
├── test/                         # Test files
│   └── load_test.py             # Locust load testing
├── docker/                       # Docker configuration
│   └── docker-compose.yml       # Docker services definition
└── pyproject.toml               # Project dependencies and configuration
```

### Application Architecture

The application follows a **layered architecture** pattern:

#### 1. **API Layer** (`src/link/api/v1/`)
- **FastAPI routers** handle HTTP requests and responses
- **Pydantic schemas** validate input/output data
- Route handlers delegate to service layer

#### 2. **Service Layer** (`src/link/service.py`)
- **Business logic** for URL shortening and visit tracking
- **URL code generation** using Base62 encoding with UUID
- **Coordination** between different repositories

#### 3. **Repository Layer** (`src/link/repo.py`)
- **Data access** abstraction over SQLModel/SQLAlchemy
- **Database operations** for Link and Visit entities
- **Query optimization** for statistics and aggregations

#### 4. **Model Layer** (`src/link/models.py`)
- **SQLModel definitions** for database tables
- **Relationships** between Link and Visit entities
- **Field validation** and constraints

#### 5. **Configuration Layer** (`src/config/`)
- **Environment-based settings** using Pydantic Settings
- **Database connection** parameters
- **Application configuration** (domain, URL length, etc.)

### API Architecture Details

#### Route Structure
```
/                           # Root router (redirects)
├── /{short_code}          # Redirect to original URL
└── /api/                  # API routes
    └── /v1/               # Version 1 API
        └── /link/         # Link operations
            ├── /shorten   # POST: Create short URL
            └── /stats/{code} # GET: Get URL statistics
```

#### Service Dependencies
- **ShortenerService**: Handles URL shortening logic
- **VisitService**: Manages visit tracking
- **LinkRepo**: Database operations for links
- **VisitRepo**: Database operations for visits

## Logging

### Implementation

The application uses a **decorator-based logging system** implemented in `src/logger.py`:

```python
@log_request_info
async def redirect_to_url(request: Request, short_code: str, ...):
    # Route handler logic
```

### Features

- **Request logging**: Captures IP address, timestamp, HTTP method, and path
- **Proxy support**: Handles `X-Forwarded-For` and `X-Real-IP` headers
- **Error logging**: Logs exceptions with stack traces
- **Structured format**: Consistent log format across the application

### Log Configuration

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
```

### Log Output Examples

```
2024-01-15 10:30:15,123 - src.routers - INFO - Request GET /abc123 from IP: 192.168.1.100 at 2024-01-15T10:30:15
2024-01-15 10:30:15,456 - src.routers - ERROR - Error updating visits: 123
```

### Log Storage

- **Default**: Logs are output to **console/stdout**
- **Production**: Configure additional handlers for file logging or external services
- **Customization**: Modify `src/logger.py` to add file handlers, rotation, or external integrations

## Testing

### Load Testing with Locust

The project includes load testing capabilities using Locust.

#### Running Load Tests

1. **Install test dependencies**:
   ```bash
   uv sync --group test
   ```

2. **Start the application**:
   ```bash
   python src/main.py
   ```

3. **Run Locust load tests**:
   ```bash
   # Basic load test
   locust -f test/load_test.py --host=http://localhost:8000

   # Headless mode with specific parameters
   locust -f test/load_test.py --host=http://localhost:8000 \
          --users 50 --spawn-rate 5 --run-time 60s --headless
   ```

4. **Access Locust Web UI** (if not using headless mode):
   ```
   http://localhost:8089
   ```

#### Load Test Configuration

The load test simulates realistic user behavior:

- **URL Creation**: Users create shortened URLs
- **URL Access**: Users visit shortened URLs (higher frequency)
- **Statistics**: Users check URL statistics
- **Realistic delays**: Includes think time between requests

#### Expected Performance

With proper database indexing and connection pooling:

- **URL Creation**: ~100-500 requests/second
- **URL Redirects**: ~1000-2000 requests/second
- **Statistics API**: ~500-1000 requests/second

### Unit Testing

To add unit tests, create test files in the `test/` directory:

```bash
# Install pytest
uv add pytest pytest-asyncio httpx --group test

# Run tests
pytest test/
```

Example test structure:
```python
# test/test_shortener.py
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_create_short_url():
    response = client.post(
        "/api/v1/link/shorten",
        json={"target_url": "https://example.com"}
    )
    assert response.status_code == 201
    assert "shortened_url" in response.json()
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_URI=postgresql+asyncpg://postgres:postgres@localhost:5432/shortener
DATABASE_ENGINE_POOL_TIMEOUT=30
DATABASE_ENGINE_POOL_RECYCLE=3600
DATABASE_ENGINE_POOL_SIZE=10
DATABASE_ENGINE_MAX_OVERFLOW=20
DATABASE_ENGINE_POOL_PING=true

# Application Configuration
DEFAULT_DOMAIN=http://localhost:8000
SHORT_URL_LENGTH=6
```

### Configuration Options

- **DATABASE_URI**: PostgreSQL connection string
- **DEFAULT_DOMAIN**: Base domain for shortened URLs
- **SHORT_URL_LENGTH**: Length of generated short codes
- **Pool settings**: Database connection pool configuration

## Development

### Code Quality

The project uses **Ruff** for linting and formatting:

```bash
# Install dev dependencies
uv sync --group dev

# Run linter
ruff check src/

# Auto-fix issues
ruff check --fix src/

# Format code
ruff format src/
```

### Pre-commit Hooks

```bash
# Install pre-commit
uv sync --group dev

# Set up hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## License

This project is open source and available under the [MIT License](LICENSE).
