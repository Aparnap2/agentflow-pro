#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print section headers
section() {
    echo -e "\n${YELLOW}==> ${1}${NC}"
}

# Check if Python 3.10+ is installed
section "Checking Python version"
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3.10 or later."
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [[ "$PYTHON_VERSION" < "3.10" ]]; then
    echo "Python 3.10 or later is required, but found Python ${PYTHON_VERSION}"
    exit 1
fi
echo "✓ Python ${PYTHON_VERSION} is installed"

# Check if Docker is running
section "Checking Docker"
if ! docker info &> /dev/null; then
    echo "Docker is not running. Please start Docker and try again."
    exit 1
fi
echo "✓ Docker is running"

# Start services with Docker Compose
section "Starting services with Docker Compose"
docker-compose up -d

# Create and activate virtual environment
section "Setting up Python virtual environment"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Created virtual environment"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
section "Installing Python dependencies"
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Installed dependencies"

# Initialize the database
section "Initializing database"
python scripts/init_db.py

# Seed the database with test data
section "Seeding database with test data"
python scripts/seed_agents.py

# List all agents
section "Listing all agents"
python scripts/list_agents.py

# Run the FastAPI server
section "Starting FastAPI server"
echo -e "\n${GREEN}Starting the FastAPI server...${NC}"
echo -e "${GREEN}The API will be available at http://localhost:8000${NC}"
echo -e "${GREEN}API documentation will be available at http://localhost:8000/api/docs${NC}"
echo -e "${GREEN}Press Ctrl+C to stop the server${NC}\n"

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
