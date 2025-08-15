# Build stage
FROM python:3.13-slim AS builder

# Set working directory
WORKDIR /src

# Install system dependencies needed for building
RUN apt-get update 

# Copy requirements file
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.13-slim AS runner

# Set working directory
WORKDIR /src

# Install runtime dependencies
RUN apt-get update

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy source code
COPY src/ .

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run the application
CMD ["fastapi", "run"]
