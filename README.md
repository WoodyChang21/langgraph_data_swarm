# 🛫 LangGraph Airport AI Agent Swarm

A sophisticated multi-agent system built with [LangGraph](https://langchain-ai.github.io/langgraph/) for analyzing Kaohsiung Airport data. This AI-powered system combines SQL search capabilities with data visualization through coordinated agent handoffs.

## 🎯 Choose Your Implementation

This repository offers **two different implementations** to suit your needs:

| | 🚀 LangGraph CLI | 🎨 Open WebUI |
|---|---|---|
| **Branch** | [`langgraph-server`](https://github.com/WoodyChang21/langgraph-data-swarm/tree/langgraph-server) | [`openai_api`](https://github.com/WoodyChang21/langgraph-data-swarm/tree/openai_api) |
| **Best For** | Fast prototyping, Demos, Development | Production, Robust UX, Full-featured |
| **Setup Time** | ⚡ ~5 minutes | 🔧 ~15 minutes |
| **Frontend** | Agent Chat UI (Vercel) | Open WebUI (Self-hosted) |
| **Commands** | `langgraph up` | `docker-compose up` |
| **Dependencies** | Python, OpenAI | Docker, Redis, Optional Ollama |
| **Chat Interface** | Minimal, Clean | Rich, Feature-packed |
| **Local LLM Support** | ❌ OpenAI only | ✅ Ollama integration |
| **Memory** | PostgreSQL (auto) | Redis + Checkpointing |
| **Authentication** | None | ✅ Built-in user auth |
| **Deployment** | Simple | Docker Compose stack |

---

## 🚀 LangGraph CLI Implementation

**Perfect for: Quick demos, rapid prototyping, development**

### Key Features
- ⚡ **Instant Setup**: Get running in 2 commands
- 🔄 **Hot Reload**: Code changes apply automatically
- 🎯 **Minimal Dependencies**: Just Python and OpenAI
- 💻 **Clean Interface**: Agent Chat UI via Vercel
- 📊 **Built-in Observability**: LangSmith integration

### Quick Start

```bash
# Clone and switch to branch
git clone https://github.com/WoodyChang21/langgraph-data-swarm.git
cd langgraph-data-swarm
git checkout langgraph-server

# Configure environment
cp .env.example .env
# Edit .env with your OpenAI and AWS credentials

# Install dependencies
pip install uv
uv pip install -r requirements.txt

# Launch server
langgraph up
```

**Access the demo at**: [https://agentchat.vercel.app/](https://agentchat.vercel.app/)
- API URL: `http://localhost:2024`
- Graph ID: `agent`

### When to Use
✅ Quick demonstrations and POCs  
✅ Rapid development and iteration  
✅ Learning LangGraph fundamentals  
✅ Minimal infrastructure requirements  

### Documentation
👉 [Full Setup Guide](https://github.com/WoodyChang21/langgraph-data-swarm/tree/langgraph-server#readme)

---

## 🎨 Open WebUI Implementation

**Perfect for: Production deployments, full-featured applications, robust UX**

### Key Features
- 🎨 **Rich Chat Interface**: Full-featured Open WebUI with markdown, code highlighting
- 🔐 **User Authentication**: Built-in auth system with roles and permissions
- 🤖 **Local LLM Support**: Integrated Ollama for offline/private deployments
- 💾 **Robust Memory**: Redis-based checkpointing with RedisInsight
- 📊 **Monitoring**: RedisInsight UI for debugging and monitoring
- 🐳 **Production Ready**: Complete Docker Compose stack

### Architecture

```
┌─────────────────────────────────────────────────┐
│              Open WebUI (Port 3000)             │
│         Full-featured Chat Interface            │
└──────────────────┬──────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────┐
│         FastAPI Agent API (Port 8001)           │
│     SQL Agent + Plot Agent + Swarm Logic        │
└─────┬────────────────────────────────────┬──────┘
      │                                    │
      ↓                                    ↓
┌─────────────┐                    ┌──────────────┐
│   Redis     │                    │   Ollama     │
│ (Optional)  │                    │  (Optional)  │
└─────────────┘                    └──────────────┘
```

### Quick Start

```bash
# Clone and switch to branch
git clone https://github.com/WoodyChang21/langgraph-data-swarm.git
cd langgraph-data-swarm
git checkout openai_api

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Launch entire stack
docker-compose up --build
```

**Access your deployment**:
- **Open WebUI**: http://localhost:3000
- **API**: http://localhost:8001
- **RedisInsight**: http://localhost:8004

### Services Included
- **App**: FastAPI agent system (Port 8001)
- **Open WebUI**: Full-featured chat interface (Port 3000)
- **Redis**: Memory and session storage (Port 6381)
- **RedisInsight**: Monitoring UI (Port 8004)
- **Ollama**: Local LLM server (Port 11434) - Optional

### When to Use
✅ Production deployments  
✅ Need user authentication and management  
✅ Want local LLM support (offline/private)  
✅ Require persistent memory across sessions  
✅ Need full-featured chat interface  
✅ Docker-based infrastructure  

### Documentation
👉 [Full Setup Guide](https://github.com/WoodyChang21/langgraph-data-swarm/tree/openai_api#readme)

---

## 🌟 Common Features (Both Implementations)

Both implementations share the same core AI capabilities:

### Multi-Agent Architecture
- **SQL Search Agent**: Natural language to SQL with context-aware querying
- **Plot Agent**: Dynamic visualization with Plotly, Matplotlib, Seaborn
- **Intelligent Handoffs**: Seamless agent coordination using LangGraph Swarm

### Smart Capabilities
- 🔍 **Airport/Airline Lookup**: Chinese language support with IATA code mapping
- 📊 **SQL Query Generation**: Converts natural language to optimized SQL
- 📈 **Auto Visualization**: Detects when plots are needed and generates them
- ☁️ **Cloud Storage**: Auto-upload CSV/HTML to AWS S3
- 🧠 **Memory**: Conversation history and context retention

### Example Queries
```
👤 "Search all flights to Tokyo in October 2024"
🤖 [SQL Agent] → Returns data + CSV download link

👤 "Show me a plot of flight counts by airline"
🤖 [SQL Agent] → [Plot Agent] → Interactive Plotly chart

👤 "Analyze on-time rate for EVA Air and create a visualization"
🤖 [SQL + Plot Agents] → Data analysis + Chart
```

---

## 🔧 Prerequisites

### For LangGraph CLI Branch
- Python 3.11+
- OpenAI API Key
- AWS S3 credentials (for file storage)

### For Open WebUI Branch
- Docker & Docker Compose
- OpenAI API Key
- AWS S3 credentials
- (Optional) NVIDIA GPU for Ollama

---

## 📚 Project Structure

Both branches contain:

```
langgraph_data_swarm/
├── agents/
│   ├── sql_search_agent/      # SQL query generation
│   ├── plot_agent/             # Data visualization
│   └── swarm/                  # Agent coordination
├── database/
│   └── airport_data.db         # Kaohsiung Airport data
├── api/                        # FastAPI endpoints (openai_api branch)
├── langgraph_server.py         # LangGraph entry (langgraph-server branch)
└── requirements.txt
```

---

## 🚦 Getting Started

### 1. Choose Your Implementation

**Quick Demo?** → Use [`langgraph-server`](https://github.com/WoodyChang21/langgraph-data-swarm/tree/langgraph-server)  
**Production App?** → Use [`openai_api`](https://github.com/WoodyChang21/langgraph-data-swarm/tree/openai_api)

### 2. Clone and Switch Branch

```bash
git clone https://github.com/WoodyChang21/langgraph-data-swarm.git
cd langgraph-data-swarm

# For LangGraph CLI
git checkout langgraph-server

# OR for Open WebUI
git checkout openai_api
```

### 3. Follow Branch-Specific Setup

Each branch has its own detailed README with complete setup instructions.

---

## 🎓 Learn More

- **LangGraph Documentation**: [https://langchain-ai.github.io/langgraph/](https://langchain-ai.github.io/langgraph/)
- **LangGraph CLI**: [https://langchain-ai.github.io/langgraph/concepts/langgraph_cli/](https://langchain-ai.github.io/langgraph/concepts/langgraph_cli/)
- **LangGraph Swarm**: [https://langchain-ai.github.io/langgraph-swarm/](https://langchain-ai.github.io/langgraph-swarm/)
- **Agent Chat UI**: [https://github.com/langchain-ai/agent-chat-ui](https://github.com/langchain-ai/agent-chat-ui)
- **Open WebUI**: [https://github.com/open-webui/open-webui](https://github.com/open-webui/open-webui)

---

## 📊 Database Schema

Both implementations use the same SQLite database with Kaohsiung Airport flight data:

- **departure_flights**: Outbound flights from Kaohsiung
- **arrival_flights**: Inbound flights to Kaohsiung

**Fields**: FlightNumber, Airline, Origin/Destination, ScheduledTime, ActualTime, Status, Date, Terminal, Gate

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request to either branch.

---

## 📝 License

[Add your license information here]

---

**Built with ❤️ using LangGraph, LangChain, and OpenAI**

**Choose your path and start building intelligent AI agents today! 🚀**
