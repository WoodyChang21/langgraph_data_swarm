#!/bin/bash
# start.sh - Start all services for Airport AI Agent

set -e

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Export PROJECT_DIR for docker-compose volume substitution
export PROJECT_DIR=$(basename "$SCRIPT_DIR")

echo "=========================================="
echo "Starting Airport AI Agent Services"
echo "=========================================="

# Start HTTP file server in background
echo "📁 Starting file server on port 8080..."
cd "$SCRIPT_DIR/agents"
python3 -m http.server 8080 --bind 0.0.0.0 > /tmp/fileserver.log 2>&1 &
FILE_SERVER_PID=$!
echo "   ✅ File server running (PID: $FILE_SERVER_PID)"
echo "   📊 CSV files: http://localhost:8080/sql_search_agent/csv/"
echo "   📈 Plots: http://localhost:8080/plot_agent/plots/"

# Return to project root
cd "$SCRIPT_DIR"

# Start LangGraph server (foreground - keeps script running)
echo ""
echo "🚀 Starting LangGraph server..."
echo "   API: http://localhost:8123"
echo ""
echo "Press Ctrl+C to stop all services"
echo "=========================================="

# Trap Ctrl+C to cleanup
trap "echo ''; echo 'Stopping services...'; kill $FILE_SERVER_PID 2>/dev/null; langgraph down; echo 'Done!'; exit 0" INT TERM

# Start LangGraph (this blocks until Ctrl+C)
# langgraph up
# Start LangGraph with volume mounts
langgraph up -d volumes.yml