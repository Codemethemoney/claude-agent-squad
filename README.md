# Claude Agent Squad

A sophisticated multi-agent orchestration system powered by semantic engineering principles. This system enables dynamic agent creation, intelligent task routing, and collaborative AI workflows.

## 🚀 Features

- **Dynamic Agent Generation**: AI-powered spec generation with semantic engineering principles
- **Multi-Agent Orchestration**: Supervisor agent intelligently routes tasks to specialized agents
- **Robust Error Handling**: Retry logic, validation, and graceful fallbacks
- **FastAPI Backend**: High-performance async API for agent management
- **ClaudeAgent Integration**: Full integration with the agent_squad library
- **Extensible Architecture**: Easy to add new agents and capabilities

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key (or Claude API key)
- Node.js (for MCP bridge, optional)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/Codemethemoney/claude-agent-squad.git
cd claude-agent-squad
```

2. Set up Python environment:
```bash
cd python_agent_squad
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## 🏃‍♂️ Running the System

### Start the Spec Generator Service:
```bash
cd python_agent_squad
uvicorn generator:app --reload --port 8001
```

### Start the Agent Squad API:
```bash
cd python_agent_squad
uvicorn main:app --reload --port 8000
```

## 🧪 Testing

Run the test suite to verify the installation:
```bash
cd python_agent_squad
python test_agent_creation.py
```

## 📚 API Endpoints

- `POST /run_squad` - Execute a request through the agent squad
- `GET /agents` - List all active agents
- `POST /add_agent` - Dynamically add a new agent
- `GET /health` - Health check endpoint

## 🤖 Default Agents

1. **Researcher**: Analyzes data and summarizes information
   - Tools: filesystem.readFile, rag-web-browser, web_search

2. **Writer**: Crafts high-quality prose and documentation
   - Tools: filesystem.writeFile, filesystem.readFile

3. **Coder**: Writes clean, efficient code
   - Tools: command-runner, filesystem.writeFile, filesystem.readFile

## 🏗️ Architecture

```
claude-agent-squad/
├── python_agent_squad/        # Core Python services
│   ├── main.py               # Agent Squad API
│   ├── generator.py          # Spec generation service
│   └── requirements.txt      # Python dependencies
├── mcp_bridge/               # MCP integration (optional)
└── agents/                   # Generated agent profiles
```

## 🔧 Configuration

Environment variables in `.env`:
- `OPENAI_API_KEY`: General API key
- `OPENAI_API_KEY_[AGENT]`: Agent-specific API keys
- `GENERATOR_PORT`: Spec generator port (default: 8001)
- `SQUAD_API_PORT`: Squad API port (default: 8000)

## 📖 Documentation

See [IMPLEMENTATION_COMPLETE.md](python_agent_squad/IMPLEMENTATION_COMPLETE.md) for detailed implementation notes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.
