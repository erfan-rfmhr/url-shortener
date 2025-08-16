# URL Shortener Tests

This directory contains comprehensive tests for the URL shortener application's link module.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Shared fixtures and configuration
├── test_models.py              # Tests for Link and Visit models
├── test_repo.py                # Tests for repository classes
├── test_service.py             # Tests for service classes
├── load_test.py                # Load testing with Locust
└── README.md                   # This file
```

## Test Categories

### Unit Tests

#### Model Tests (`test_models.py`)
- **Link Model Tests**: Creation, validation, database operations, unique constraints, relationships
- **Visit Model Tests**: Creation, validation, database operations, relationships, foreign key constraints

#### Repository Tests (`test_repo.py`)
- **LinkRepo Tests**: CRUD operations, statistics, visit count updates, error handling
- **VisitRepo Tests**: Visit creation, relationships, constraints

#### Service Tests (`test_service.py`)
- **ShortenerService Tests**: URL shortening, code generation, Base62 encoding, link retrieval
- **VisitService Tests**: Visit creation and tracking
- **Integration Tests**: Full workflow testing

### Load Tests (`load_test.py`)
- Simulates multiple users creating short URLs
- Tests URL redirection performance
- Tests statistics endpoint performance
- Uses Locust framework for load testing

## Running Tests

### Prerequisites

Install test dependencies:

```bash
uv sync --group test
```

### Run All Tests
```bash
# Using pytest directly
pytest
```

### Run Load Tests
```bash
# Start the application first, then run:
locust -f tests/load_test.py --host=http://localhost:8000
```
