#!/bin/bash
# RIK Quick Start Script
# ======================
#
# Usage:
#   ./start.sh                  # Start in development mode
#   ./start.sh prod             # Start in production mode
#   ./start.sh docker           # Start with Docker
#   ./start.sh stop             # Stop all services
#

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  RIK - Recursive Intelligence Kernel                    ║"
echo "║  Version 5.4.0                                           ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

MODE=${1:-dev}

case $MODE in
  dev|development)
    echo -e "${GREEN}Starting RIK in DEVELOPMENT mode...${NC}"

    # Check if .env exists
    if [ ! -f .env ]; then
      echo -e "${YELLOW}No .env file found, using development defaults${NC}"
      cp config/development.env .env
    fi

    # Check dependencies
    if ! python3 -c "import fastapi" 2>/dev/null; then
      echo -e "${YELLOW}Installing dependencies...${NC}"
      pip3 install -r requirements.txt -r requirements-demo.txt -q
    fi

    echo -e "${GREEN}✅ Starting RIK API...${NC}"
    echo ""
    echo "  API:  http://localhost:8000"
    echo "  Docs: http://localhost:8000/docs"
    echo ""
    echo "Press Ctrl+C to stop"
    echo ""

    python3 rik_api.py
    ;;

  prod|production)
    echo -e "${GREEN}Starting RIK in PRODUCTION mode...${NC}"

    # Check if .env exists
    if [ ! -f .env ]; then
      echo -e "${YELLOW}⚠️  No .env file found!${NC}"
      echo "Copy config/production.env to .env and configure:"
      echo "  cp config/production.env .env"
      echo "  nano .env"
      exit 1
    fi

    # Check for required production settings
    if grep -q "CHANGEME" .env; then
      echo -e "${YELLOW}⚠️  .env file contains CHANGEME placeholders!${NC}"
      echo "Update your .env file with real values:"
      echo "  nano .env"
      exit 1
    fi

    echo -e "${GREEN}✅ Starting RIK API (production mode)...${NC}"
    echo ""
    echo "  API:  http://0.0.0.0:8000"
    echo "  Docs: http://0.0.0.0:8000/docs"
    echo ""

    # Start with uvicorn + multiple workers
    uvicorn rik_api:app \
      --host 0.0.0.0 \
      --port 8000 \
      --workers 4 \
      --no-access-log
    ;;

  docker)
    echo -e "${GREEN}Starting RIK with Docker Compose...${NC}"

    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
      echo -e "${YELLOW}❌ Docker not found. Install Docker first.${NC}"
      exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
      echo -e "${YELLOW}❌ docker-compose not found. Install docker-compose first.${NC}"
      exit 1
    fi

    echo -e "${GREEN}✅ Building and starting containers...${NC}"
    docker-compose up -d

    echo ""
    echo -e "${GREEN}✅ RIK is running!${NC}"
    echo ""
    echo "  API:  http://localhost:8000"
    echo "  Docs: http://localhost:8000/docs"
    echo ""
    echo "View logs:   docker-compose logs -f rik-api"
    echo "Stop:        docker-compose down"
    echo ""

    # Show logs
    echo -e "${BLUE}Showing logs (Ctrl+C to detach):${NC}"
    docker-compose logs -f rik-api
    ;;

  stop)
    echo -e "${YELLOW}Stopping RIK services...${NC}"

    # Stop Docker if running
    if docker ps | grep -q rik-api; then
      echo "Stopping Docker containers..."
      docker-compose down
    fi

    # Kill any Python processes running rik_api.py
    if pgrep -f "python.*rik_api.py" > /dev/null; then
      echo "Stopping Python processes..."
      pkill -f "python.*rik_api.py"
    fi

    echo -e "${GREEN}✅ All RIK services stopped${NC}"
    ;;

  test)
    echo -e "${GREEN}Testing RIK deployment...${NC}"

    # Wait for API to be ready
    echo "Waiting for API to start..."
    for i in {1..30}; do
      if curl -s http://localhost:8000/health/live > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API is alive!${NC}"
        break
      fi
      sleep 1
      echo -n "."
    done
    echo ""

    # Test health endpoints
    echo "Testing health endpoints..."
    curl -s http://localhost:8000/health/live | jq .
    curl -s http://localhost:8000/health/ready | jq .

    # Test version
    echo ""
    echo "API Version:"
    curl -s http://localhost:8000/version | jq .

    echo ""
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "View API docs: http://localhost:8000/docs"
    ;;

  bench|benchmark)
    echo -e "${GREEN}Running performance benchmarks...${NC}"

    # Check if API is running
    if ! curl -s http://localhost:8000/health/live > /dev/null 2>&1; then
      echo -e "${YELLOW}❌ API not running. Start it first:${NC}"
      echo "  ./start.sh docker"
      exit 1
    fi

    python3 benchmarks/performance_test.py
    ;;

  *)
    echo "Usage: $0 {dev|prod|docker|stop|test|benchmark}"
    echo ""
    echo "  dev        - Start in development mode (local Python)"
    echo "  prod       - Start in production mode (uvicorn + workers)"
    echo "  docker     - Start with Docker Compose"
    echo "  stop       - Stop all RIK services"
    echo "  test       - Test deployment"
    echo "  benchmark  - Run performance benchmarks"
    echo ""
    exit 1
    ;;
esac
