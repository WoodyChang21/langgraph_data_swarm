# 🛫 LangGraph Airport AI Agent Swarm

A sophisticated multi-agent system built with [LangGraph](https://langchain-ai.github.io/langgraph/) for analyzing Kaohsiung Airport data. This AI-powered system combines SQL search capabilities with data visualization through coordinated agent handoffs.

## 🌟 Features

- **🤖 Multi-Agent Architecture**: Coordinated SQL, Analysis, and Plot agents using LangGraph Swarm
- **📊 Intelligent Data Analysis**: Natural language to SQL query conversion with context-aware search
- **📈 Dynamic Visualizations**: Automatic plot generation using Plotly and Matplotlib
- **💬 Conversational Interface**: Chat-based interaction via LangGraph Studio
- **🔄 Agent Handoffs**: Seamless transitions between data retrieval, analysis, and visualization tasks
- **📁 Local File Server**: HTTP server for accessing generated CSV and plot files
- **🎯 Flexible LLM Backend**: Support for both OpenAI models and local Ollama models
- **🔍 Smart Mapping**: Airport and airline code lookups with Chinese language support
- **🐳 Docker Integration**: Containerized deployment with volume mounts for file persistence

## ⚡ Quick Start

```bash
# 1. Copy environment configuration
cp .env.example .env

# 2. Edit .env with your API keys (if using OpenAI)
# For Ollama: Set LOCAL_MODEL=True in agents/llm_model.py

# 3. Install dependencies
uv pip install -r requirements.txt

# 4. Make start script executable (if needed)
chmod +x start.sh

# 5. Start all services
./start.sh

# 6. Access LangGraph Studio
# Visit: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:8123
```

**Access Points:**
- 🚀 LangGraph API: `http://localhost:8123`
- 📁 File Server: `http://localhost:8080`
- 📊 API Docs: `http://localhost:8123/docs`

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│          LangGraph Swarm Router                 │
│       (Intelligent Agent Orchestration)         │
└────────────────┬────────────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼──────┐ ┌──▼─────┐ ┌───▼─────────┐
│   SQL    │ │Analysis│ │    Plot     │
│  Agent   │ │ Agent  │ │   Agent     │
│          │ │        │ │             │
│• Query DB│ │• Stats │ │• Plotly     │
│• CSV     │ │• Trends│ │• Matplotlib │
│• Mapping │ │• Report│ │• Seaborn    │
└────┬─────┘ └────────┘ └──────┬──────┘
     │                          │
     │    ┌──────────────┐      │
     └────►  Airport DB  ◄──────┘
          │  (SQLite)    │
          └──────────────┘
                 │
          ┌──────▼──────────┐
          │  Volume Mounts  │
          │  (Docker)       │
          └──────┬──────────┘
                 │
          ┌──────▼──────────┐
          │  HTTP Server    │
          │  (port 8080)    │
          │  • CSV files    │
          │  • HTML plots   │
          └─────────────────┘
```

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.11+** installed
- **Docker** and **Docker Compose** installed and running
- **Git** installed
- **LLM Backend** (choose one):
  - **OpenAI API Key** (for GPT-4o-mini) - Default option
  - **Ollama** (for local models like Granite 4, Llama 3.2, Qwen3) - Free, GPU-accelerated
- **(Optional)** LangSmith account for agent tracing and debugging
- **(Optional)** Conda/Virtualenv for Python environment management

## 🚀 Setup Process

### Step 0: Configure Environment Variables

First, copy the example environment file and fill in your credentials:

```bash
# Copy the example file
cp .env.example .env
```

Now edit the `.env` file with your actual values:

```bash
# Required: Database Path
SQL_DATABASE_PATH=database/airport_data.db

# LLM Configuration (choose one)
# Option 1: OpenAI (Default - set LOCAL_MODEL=False in agents/llm_model.py)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx

# Option 2: Local Ollama (set LOCAL_MODEL=True in agents/llm_model.py)
# No API key needed - uses local GPU via Ollama

# Optional: LangSmith (for agent tracing and debugging)
LANGSMITH_API_KEY=lsv2_pt_xxxxxxxxxxxxx
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=airport-agent-swarm
```

**🔐 Security Note**: Never commit your `.env` file to version control!

### Step 0.1: Choose Your LLM Backend

Edit `agents/llm_model.py` to select your preferred model:

```python
# For OpenAI (requires API key)
LOCAL_MODEL = False  # Uses GPT-4o-mini

# For local Ollama (free, GPU-accelerated)
LOCAL_MODEL = True   # Uses Granite 4 7B or other Ollama models
```

**Recommended local models** (sorted by performance):
- `granite4:7b-a1b-h` - Best for tool-calling (121 tok/s)
- `granite4:3b` - Fastest option (114 tok/s)
- `llama3.2:3b-instruct-q8_0` - Good balance (84 tok/s)

### Step 1: Install Dependencies

This project uses `uv` for fast, reliable Python package installation.

#### 1.1 Install uv Package Manager

```bash
pip install uv
```

**Why uv?** 
- ⚡ 10-100x faster than pip
- 🎯 Better dependency resolution
- 🔒 More reliable installs

#### 1.2 Install Project Dependencies

```bash
uv pip install -r requirements.txt
```

This will install:
- **LangChain** ecosystem (langchain, langchain-openai, langchain-ollama, langchain-community)
- **LangGraph** (v0.2.0+) with CLI tools
- **LangGraph Swarm** for agent coordination
- Database tools (SQLite, Pandas, SQLAlchemy)
- Visualization libraries (Plotly, Matplotlib, Seaborn, Kaleido)
- Web framework (FastAPI, Uvicorn)
- Utilities (boto3, requests, python-dateutil)

### Step 2: Start All Services

#### Option A: Quick Start (Recommended)

Use the provided startup script that launches both the LangGraph server and file server:

```bash
./start.sh
```

**What this does:**
- 🚀 Starts LangGraph server on `http://localhost:8123` (in Docker)
- 📁 Starts HTTP file server on `http://localhost:8080` (for CSV/plots)
- 🔧 Configures PostgreSQL checkpointer automatically
- 📦 Mounts volumes for file persistence between container and host
- 🔄 Enables graceful shutdown with Ctrl+C

**Expected output:**
```
==========================================
Starting Airport AI Agent Services
==========================================
📁 Starting file server on port 8080...
   ✅ File server running (PID: xxxxx)
   📊 CSV files: http://localhost:8080/sql_search_agent/csv/
   📈 Plots: http://localhost:8080/plot_agent/plots/

🚀 Starting LangGraph server...
   API: http://localhost:8123

Press Ctrl+C to stop all services
==========================================
Ready!
- API: http://localhost:8123
- Docs: http://localhost:8123/docs
- LangGraph Studio: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:8123
```

**Services Running:**
- **8123**: LangGraph API server (Docker container)
- **8080**: HTTP file server (Python http.server)
- **5432**: PostgreSQL (for checkpointing, internal)
- **6379**: Redis (for caching, internal)

#### Option B: Manual Start

If you prefer to start services individually:

```bash
# Terminal 1: Start file server
cd agents
python3 -m http.server 8080 --bind 0.0.0.0

# Terminal 2: Start LangGraph with volume mounts
langgraph up -d volumes.yml
```

#### 2.2 Access the Interface

Once the server is running, access it via:

1. **LangGraph Studio** (Recommended): 
   - Visit: [https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:8123](https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:8123)
   - Login with your LangSmith account (or create one for free)
   - Interactive interface with agent handoff visualization

2. **Direct API Access**:
   - API Docs: [http://localhost:8123/docs](http://localhost:8123/docs)
   - Test endpoint: `POST http://localhost:8123/runs/stream`

3. **File Downloads**:
   - CSV files: [http://localhost:8080/sql_search_agent/csv/](http://localhost:8080/sql_search_agent/csv/)
   - Plot files: [http://localhost:8080/plot_agent/plots/](http://localhost:8080/plot_agent/plots/)

#### 2.3 SSH Port Forwarding (If Running on Remote Server)

If you're running on an SSH server, forward the ports to your local machine:

```bash
# On your local machine
ssh -L 8123:localhost:8123 -L 8080:localhost:8080 user@<SSH_SERVER_IP>
```

Then access the services on your local browser as if they were running locally!

## 🎯 Usage Examples

Once connected to LangGraph Studio, try these queries:

### Data Retrieval with CSV Export
```
User: 查詢2025年長榮航空的離境航班數據並匯出CSV
Agent: [SQL Agent] 
  → Calls get_airline_code("長榮") → ['BR']
  → Generates SQL query
  → Executes and exports to CSV
  → Returns download link: http://localhost:8080/sql_search_agent/csv/...
```

### Visualization
```
User: 給我一個圖表顯示長榮航空的航班數量趨勢
Agent: [SQL Agent] Retrieves data 
  → [Handoff to Plot Agent] 
  → Generates interactive Plotly chart
  → Returns plot link: http://localhost:8080/plot_agent/plots/...
```

### Combined Analysis and Visualization
```
User: 分析過去三個月中華航空的準點率並提供圖表
Agent: [SQL Agent] Queries on-time data
  → [Analysis Agent] Calculates statistics
  → [Plot Agent] Creates visualization
  → Returns comprehensive analysis with charts
```

### Accessing Generated Files

All generated files are accessible via the HTTP file server:

- **CSV Data**: Browse to `http://localhost:8080/sql_search_agent/csv/`
- **Plot Charts**: Browse to `http://localhost:8080/plot_agent/plots/`
- Files are organized by session ID in subdirectories
- Direct download links are provided in agent responses

## 📁 Project Structure

```
langgraph_data_swarm/
├── agents/
│   ├── llm_model.py              # LLM configuration (OpenAI/Ollama)
│   ├── test_llm.py               # Performance benchmark script
│   ├── sql_search_agent/
│   │   ├── sql_agent.py          # SQL query agent with tools
│   │   ├── csv/                  # Generated CSV exports (volume-mounted)
│   │   ├── airport_airline_mapping/
│   │   │   ├── airport.json      # Airport IATA code mappings
│   │   │   └── airline.json      # Airline IATA code mappings
│   │   └── search_prompt/
│   │       ├── prompt.md         # SQL agent system prompt
│   │       └── database_context.md
│   ├── plot_agent/
│   │   ├── plot_agent.py         # Visualization agent
│   │   └── plots/                # Generated HTML plots (volume-mounted)
│   ├── analysis_agent/
│   │   ├── analysis_agent.py     # Statistical analysis agent
│   │   └── analysis_prompt/
│   └── swarm/
│       ├── swarm.py              # Agent coordination logic
│       ├── handoff_tool.py       # Tool for agent handoffs
│       ├── sql_agent_with_handoff.py
│       ├── plot_agent_with_handoff.py
│       └── analysis_agent_with_handoff.py
├── database/
│   └── airport_data.db           # SQLite database
├── langgraph_server.py           # LangGraph server entry point
├── langgraph.json                # LangGraph configuration
├── volumes.yml                   # Docker volume mounts configuration
├── start.sh                      # Startup script (LangGraph + file server)
├── .env                          # Environment variables (create from .env.example)
├── .env.example                  # Template for environment configuration
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🔧 Configuration

### LangGraph Configuration (`langgraph.json`)

```json
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./langgraph_server.py:graph"
  },
  "env": ".env",
  "python_version": "3.11"
}
```

### Volume Mounts (`volumes.yml`)

The `volumes.yml` file configures Docker volume mounts to sync generated files between the container and host:

```yaml
services:
  langgraph-api:
    extra_hosts:
      - "host.docker.internal:host-gateway"  # Enables container→host communication
    volumes:
      # CSV files: container path → host path
      - ./agents/sql_search_agent/csv:/deps/outer-${PROJECT_DIR}/${PROJECT_DIR}/agents/sql_search_agent/csv
      # Plot files: container path → host path  
      - ./agents/plot_agent/plots:/deps/outer-${PROJECT_DIR}/${PROJECT_DIR}/agents/plot_agent/plots
```

**Key Points:**
- `${PROJECT_DIR}` is automatically set by `start.sh` to the current directory name
- Files created in the container instantly appear on the host
- The HTTP file server serves these directories for easy browser access
- `host.docker.internal` allows the container to access host services (e.g., Ollama)

### HTTP File Server

The file server is started by `start.sh` using Python's built-in HTTP server:

```bash
python3 -m http.server 8080 --bind 0.0.0.0
```

**Features:**
- 📁 No installation required (uses Python standard library)
- 🌐 Accessible from any device on the network (`0.0.0.0` binding)
- 📂 Serves the entire `agents/` directory structure
- 🔗 Direct download links generated by SQL and Plot agents
- 🚀 Lightweight and fast for serving static files

## 🛠️ Development Commands

### Quick Commands

```bash
# Start all services (recommended)
./start.sh

# Stop all services
# Press Ctrl+C in the terminal running start.sh
# Or manually:
langgraph down
pkill -f "python3 -m http.server 8080"
```

### LangGraph CLI Commands

```bash
# Development mode (hot-reload enabled, without volumes)
langgraph dev

# Production with volume mounts
langgraph up -d volumes.yml

# Stop services
langgraph down

# Check configuration
langgraph config

# Build Docker image
langgraph build

# View logs
docker logs -f langgraph_data_swarm-langgraph-api-1
```

### Testing Model Performance

Benchmark the configured LLM model:

```bash
python -m agents.test_llm
```

This tests response time and token generation speed for your current model configuration.

## 🤖 Setting Up Ollama (Local Models)

If you want to use local models instead of OpenAI, follow these steps:

### 1. Install Ollama

```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# macOS
brew install ollama
```

### 2. Configure Ollama for Docker Access

Edit `/etc/systemd/system/ollama.service` and ensure it has:

```ini
Environment="OLLAMA_HOST=0.0.0.0:11434"
```

Then restart:

```bash
sudo systemctl restart ollama
```

### 3. Download Recommended Models

```bash
# Best performance (recommended)
ollama pull granite4:7b-a1b-h

# Alternative options
ollama pull granite4:3b
ollama pull llama3.2:3b-instruct-q8_0
```

### 4. Update Configuration

Edit `agents/llm_model.py`:

```python
LOCAL_MODEL = True  # Change from False to True
```

Choose your model (line 14):

```python
LLM = ChatOllama(
    model="granite4:7b-a1b-h",  # or granite4:3b, llama3.2:3b-instruct-q8_0
    temperature=0.1,
    base_url="http://host.docker.internal:11434"
)
```

### Performance Comparison

| Model | Speed | Response Time | Best For |
|-------|-------|---------------|----------|
| granite4:7b-a1b-h | 121 tok/s | 2.86s | Tool-calling, production |
| granite4:3b | 114 tok/s | 3.06s | Fast responses |
| llama3.2:3b | 84 tok/s | 3.78s | Lightweight |
| GPT-4o-mini (OpenAI) | N/A | ~2-3s | Most capable |

## 📊 Database Schema

The SQLite database (`database/airport_data.db`) contains:

- **departures**: Outbound flights from Kaohsiung (KHH)
- **arrivals**: Inbound flights to Kaohsiung (KHH)

**Key fields:**
- `FDate`, `FlightNumber`, `AirlineIATA`
- `DepartureAirportIATA` / `ArrivalAirportIATA`
- `ArrivalDateTime`, `amhsATA` (actual arrival time)
- `Passanger` (passenger count), `Cancel` (cancellation status)
- `SCHE_TYPE` (DOM_* for domestic, FOR_* for international)

**Date Range**: August 2024 - July 2025

## 📁 File Server & Volume Mounts

### How It Works

The system uses **Docker volume mounts** combined with a **Python HTTP server** to make generated files accessible:

1. **Agent generates file** → Written inside Docker container
   ```
   /deps/outer-langgraph_data_swarm/langgraph_data_swarm/agents/sql_search_agent/csv/session-id/data.csv
   ```

2. **Volume mount syncs** → File appears on host machine
   ```
   ./agents/sql_search_agent/csv/session-id/data.csv
   ```

3. **HTTP server serves** → Accessible via browser
   ```
   http://localhost:8080/sql_search_agent/csv/session-id/data.csv
   ```

### File Organization

```
agents/
├── sql_search_agent/csv/
│   └── <session-id>/
│       ├── data_20251111_095133_566.csv
│       └── data_20251111_095521_626.csv
└── plot_agent/plots/
    └── <session-id>/
        ├── plot_20251111_095206_526.html
        └── plot_20251111_095527_310.html
```

**Session IDs** are generated per user interaction, keeping files organized.

### Accessing Files

**Via Browser:**
- Navigate to `http://localhost:8080` (or `localhost:34163` if port is in use)
- Browse directory structure
- Click to download or view files

**Via wget/curl:**
```bash
wget http://localhost:8080/sql_search_agent/csv/session-id/data.csv
```

**Note**: The HTTP server binds to `0.0.0.0:8080`, making it accessible from:
- localhost
- LAN devices (if firewall permits)
- SSH tunnels (when running on remote server)

## 🧪 Testing

Test the agent system directly:

```python
from agents.swarm.swarm import AirportAgentSwarm

async def test():
    swarm = AirportAgentSwarm()
    app = await swarm.initialize()
    
    result = await app.ainvoke({
        "messages": [{"role": "user", "content": "查詢日本航線"}]
    })
    print(result)
```

## 🐛 Troubleshooting

### Issue: "Docker not running"

**Solution**: Start Docker and add your user to the docker group:
```bash
# Start Docker
sudo systemctl start docker

# Add user to docker group (then logout/login)
sudo usermod -aG docker $USER

# Quick fix (temporary)
sudo chmod 666 /var/run/docker.sock
```

### Issue: "Failed to connect to LangGraph server"

**Solution**: Ensure Docker is running and services are started:
```bash
# Check Docker status
docker ps

# Restart services
./start.sh
```

### Issue: "OpenAI API key not found" (when using OpenAI)

**Solution**: Verify your `.env` file and `llm_model.py`:
```bash
# Check .env file
cat .env | grep OPENAI_API_KEY

# Ensure LOCAL_MODEL = False in agents/llm_model.py
grep LOCAL_MODEL agents/llm_model.py
```

### Issue: "Cannot connect to Ollama" (when using local models)

**Solution**: Ensure Ollama is accessible from Docker container:
```bash
# Check if Ollama is listening on all interfaces
ss -tlnp | grep 11434
# Should show: *:11434 (not just 127.0.0.1:11434)

# Restart Ollama
sudo systemctl restart ollama

# Test connectivity from container
docker exec langgraph_data_swarm-langgraph-api-1 ping -c 1 host.docker.internal
```

### Issue: "Files not accessible via http://localhost:8080"

**Solution**: Check if the file server is running and volumes are mounted:
```bash
# Check file server
ps aux | grep "http.server 8080"

# Check if files exist on host
ls -la agents/sql_search_agent/csv/
ls -la agents/plot_agent/plots/

# Verify volume mounts in container
docker exec langgraph_data_swarm-langgraph-api-1 ls -la /deps/outer-langgraph_data_swarm/langgraph_data_swarm/agents/sql_search_agent/csv/
```

### Issue: "Database not found"

**Solution**: Ensure the database path is correct:
```bash
ls database/airport_data.db

# Check .env configuration
grep SQL_DATABASE_PATH .env
```

### Issue: "Port already in use"

**Solution**: Kill the process using the port:
```bash
# Find process using port 8080 or 8123
lsof -i :8080
lsof -i :8123

# Kill the process
kill <PID>
```

### Issue: "Permission denied" when running `./start.sh`

**Solution**: Make the script executable:
```bash
chmod +x start.sh
./start.sh
```

Alternatively, run with bash explicitly:
```bash
bash start.sh
```

## 🎓 Learn More

- **LangGraph Documentation**: [https://langchain-ai.github.io/langgraph/](https://langchain-ai.github.io/langgraph/)
- **LangGraph CLI Guide**: [https://langchain-ai.github.io/langgraph/concepts/langgraph_cli/](https://langchain-ai.github.io/langgraph/concepts/langgraph_cli/)
- **LangGraph Swarm Pattern**: [https://langchain-ai.github.io/langgraph-swarm/](https://langchain-ai.github.io/langgraph-swarm/)
- **Agent Chat UI**: [https://github.com/langchain-ai/agent-chat-ui](https://github.com/langchain-ai/agent-chat-ui)
- **LangSmith Tracing**: [https://smith.langchain.com/](https://smith.langchain.com/)


## 📧 Contact

[woodychang891121@gmail.com]

---

**Built with ❤️ using LangGraph, LangChain, and powered by OpenAI / Ollama**
