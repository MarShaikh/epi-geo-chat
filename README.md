# Epi-Geo Chat: AI-Powered Geospatial Data Query System

An intelligent chat interface for querying geospatial climate data (CHIRPS rainfall, MODIS temperature) to support epidemiological research in Nigeria.

**Status:** Pre-Phase 1 Planning Complete 

---

## Project Goal

Build a ChatGPT-like interface where researchers can ask natural language questions about climate data:

> "Show me rainfall in Lagos for February 2024"
> "What's the temperature trend in Kano over the last year?"
> "Generate a rainfall analysis for Port Harcourt 2020-2024"

The system will:
1. Parse the natural language query
2. Search your Azure GeoCatalog STAC catalog
3. Return relevant data with visualizations
4. Generate and execute analysis code when requested

---

## 📁 Documentation Index

**Start here if you're new:**

| Document | Purpose | Read This When... |
|----------|---------|-------------------|
| **README.md** | This file - quick overview | You're starting the project |
| **IMPLEMENTATION_ROADMAP.md** | Executive summary & timeline | You want the big picture |
| **PRE_PHASE_1_AF.md** | ✨ **Main plan (Agent Framework)** | You're ready to start coding |
| **QUICK_START_AF.md** | ✨ **Day-by-day checklist** | You want a daily task list |
| **EARTH_COPILOT_ANALYSIS.md** | Architecture decisions & lessons | Understanding design patterns |
| **MCP_SERVER_ANALYSIS.md** | Why not MCP for MVP | Wondering about Model Context Protocol |

---

## 🏗️ Architecture Overview

### Tech Stack

**Backend:**
- Python 3.12+ with FastAPI
- **Microsoft Agent Framework** (multi-agent orchestration)
- Azure OpenAI (GPT-4 for LLM)
- ChromaDB (vector store for RAG)
- Docker (sandboxed code execution)

**Frontend:**
- React 18 + TypeScript
- Azure Maps SDK v2
- Vite build system

**Data Layer:**
- Azure GeoCatalog (STAC API)
- Azure Blob Storage (COG assets)
- Azure Maps (geocoding)

### Multi-Agent Architecture

The system uses **4 specialized AI agents** orchestrated by **Microsoft Agent Framework**:

1. **Query Parser Agent** - Extracts intent, collections, location, datetime
2. **Geocoding & Temporal Agent** - Resolves locations and dates (multi-strategy fallback)
3. **STAC Query Coordinator Agent** - Executes searches and optimizes results
4. **Response Synthesizer Agent** - Generates natural language responses or Python code

**Framework:** Microsoft Agent Framework (graph-based multi-agent orchestration)
**Inspired by:** Microsoft Earth Copilot (simplified from 13 agents to 4)

---

## 📅 Timeline

### Pre-Phase 1: Foundation (2.5 weeks) - **YOU ARE HERE**
Build the core infrastructure before implementing the chat interface.

- **Week 0:** Project setup, Azure OpenAI, STAC access, geocoding
- **Week 1:** 4-agent pipeline, sample query dataset
- **Week 2:** RAG pipeline, security design, evaluation framework
- **Week 3:** Unit tests, integration tests, documentation

### Phase 1: MVP Development (4 weeks)
Build the actual chat application.

- **Week 1:** FastAPI backend + query parsing
- **Week 2:** React frontend + map visualization
- **Week 3:** RAG integration
- **Week 4:** Code generation + execution

**Total Timeline:** ~6.5 weeks to production-ready MVP

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Azure subscription with:
  - Azure OpenAI (GPT-4 deployment)
  - Azure GeoCatalog instance
  - Azure Maps subscription key
- Docker Desktop
- Node.js 18+ (for frontend, later)

### Setup (5 minutes)

```bash
# 1. Clone repository (or use existing directory)
cd /Users/lshms102/Documents/epi-geo-chat

# 2. Create virtual environment
conda create -n epi-geo-chat python=3.11 -y
conda activate epi-geo-chat

# 3. Install dependencies (once requirements.txt is created)
pip install -r requirements/base.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your Azure credentials

# 5. Verify setup
python scripts/test_agent_framework.py  # Test Agent Framework + Azure OpenAI
python scripts/test_stac.py             # Test GeoCatalog access
python scripts/test_geocoding.py        # Test geocoding
```

### What to Do Next

**Option 1: Start Pre-Phase 1 immediately**
1. Open `PRE_PHASE_1_AF.md`
2. Read through Week 0, Day 1
3. Follow the tasks step by step
4. Use `QUICK_START_AF.md` for daily reference

**Option 2: Understand the architecture first**
1. Read `IMPLEMENTATION_ROADMAP.md` (executive summary)
2. Read `EARTH_COPILOT_ANALYSIS.md` (architecture decisions)
3. Then start Pre-Phase 1

---

## 📊 Project Structure

```
epi-geo-chat/
├── src/
│   ├── agents/              # Agent Framework agents
│   │   ├── kernel_config.py
│   │   ├── query_parser.py
│   │   ├── geocoding_temporal.py
│   │   ├── stac_coordinator.py
│   │   ├── response_synthesizer.py
│   │   └── orchestrator.py
│   ├── stac/                # STAC catalog client
│   │   ├── catalog_client.py
│   │   └── geocoding.py
│   ├── rag/                 # Vector store (RAG)
│   │   └── vector_store.py
│   ├── code_executor/       # Sandboxed execution
│   │   └── validator.py
│   ├── api/                 # FastAPI backend (Phase 1)
│   └── utils/               # Shared utilities
│
├── tests/
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   ├── fixtures/            # Sample queries, STAC items
│   └── evaluation/          # Evaluation scripts
│
├── docs/
│   ├── ARCHITECTURE.md      # System architecture
│   ├── SETUP.md             # Setup guide
│   ├── STAC_INVENTORY.md    # STAC collection documentation
│   ├── EVALUATION_METRICS.md
│   └── SANDBOX_DESIGN.md
│
├── configs/
│   ├── prompts/             # LLM prompt templates
│   └── schemas/             # JSON schemas
│
├── scripts/                 # Setup/utility scripts
│   ├── test_kernel.py
│   ├── test_stac.py
│   ├── test_geocoding.py
│   ├── inventory_stac.py
│   └── index_stac_metadata.py
│
├── notebooks/               # Jupyter notebooks (exploration)
│
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
│
├── .env.example             # Environment variables template
├── .gitignore
├── README.md                # This file
├── IMPLEMENTATION_ROADMAP.md
├── PRE_PHASE_1_AF.md
├── QUICK_START_AF.md
├── EARTH_COPILOT_ANALYSIS.md
└── MCP_SERVER_ANALYSIS.md
```

---

## 🎓 Key Decisions & Rationale

### Why Microsoft Agent Framework?
- **Next-gen orchestration** - Evolution beyond Semantic Kernel, built for multi-agent systems
- **Graph-based workflows** - Native support for complex agent pipelines with streaming and checkpointing
- **Built-in observability** - OpenTelemetry integration for distributed tracing
- **Azure integration** - Native support for Azure OpenAI and Azure services
- **DevUI included** - Interactive developer interface for testing and debugging
- **Python-first** - Modern Python implementation with async support
- **Production-ready** - Used in Microsoft's latest AI agent solutions

### Why 4 Agents (Not 13 like Earth Copilot)?
- Earth Copilot serves general geospatial use cases (military, disaster response, etc.)
- We have a focused domain (epidemiology in Nigeria)
- 4 agents are sufficient for MVP, can expand later
- Simpler = faster development + easier debugging

### Why Not MCP Server?
- MCP is for **reusable tools across multiple LLM apps**
- We're building **one domain-specific chat app**
- MCP adds 1-2 weeks of development time
- Can add MCP in v2.0 if users request Claude Desktop integration

See `MCP_SERVER_ANALYSIS.md` for full analysis.

### Why ChromaDB (Not Azure AI Search)?
- **MVP:** ChromaDB is simpler, free, runs locally
- **v2.0:** Migrate to Azure AI Search for production scale
- Switching is easy - same vector search API pattern

---

## 🧪 Testing Strategy

### Unit Tests
Test each agent individually with mocked dependencies:
- Query parser extracts correct parameters
- Geocoding handles edge cases
- STAC client constructs correct queries
- Code validator blocks dangerous operations

**Target:** >80% code coverage

### Integration Tests
Test the full agent pipeline with real Azure services:
- End-to-end query processing
- STAC search returns relevant results
- RAG enriches responses
- Generated code executes successfully

### Evaluation
Run 15-20 sample queries and measure:
- Intent classification accuracy (target: >90%)
- Parameter extraction accuracy (target: >85%)
- STAC search precision (target: >95%)
- Response quality (manual evaluation, target: >4/5)

---

## 📈 Success Criteria

### Pre-Phase 1 Complete When:
- [ ] Can process natural language queries end-to-end
- [ ] Multi-agent pipeline handles all 15+ test queries
- [ ] Geocoding accuracy >90% for Nigerian locations
- [ ] STAC search returns relevant results
- [ ] RAG provides useful context
- [ ] Unit test coverage >80%
- [ ] Documentation complete

### Phase 1 MVP Complete When:
- [ ] Users can chat and get STAC data results
- [ ] Map displays results correctly
- [ ] RAG improves response quality (measured)
- [ ] Code execution works for simple analyses
- [ ] System handles errors gracefully
- [ ] Response time <5 seconds (p95)

---

## 🔮 Future Roadmap (Post-MVP)

### v2.0 Features
1. **Epidemiology-Specific Analysis**
   - Lassa fever risk mapping
   - Vector habitat suitability
   - Disease outbreak correlation

2. **Multi-Catalog Support**
   - Add Microsoft Planetary Computer
   - Add NASA VEDA
   - Unified search

3. **Production Infrastructure**
   - Migrate to Azure AI Search
   - Add caching (Redis)
   - Monitoring (Application Insights)

4. **MCP Server** (if requested)
   - Expose tools to Claude Desktop
   - Enable community use

---

## 🆘 Getting Help

### Stuck? Check These Resources:

1. **Documentation:**
   - Review the relevant doc from the index above
   - Check `docs/TROUBLESHOOTING.md` (create during Pre-Phase 1)

2. **External Resources:**
   - [Microsoft Earth Copilot](https://github.com/microsoft/Earth-Copilot) - Reference implementation
   - [Semantic Kernel Docs](https://learn.microsoft.com/en-us/semantic-kernel/)
   - [Azure GeoCatalog Docs](https://learn.microsoft.com/en-us/azure/geocatalog/)
   - [STAC Specification](https://stacspec.org/)

3. **Debugging Tips:**
   - Test each agent individually before integration
   - Use Jupyter notebooks to explore STAC data
   - Check Azure portal for service health
   - Enable verbose logging during development

---

## 👥 Contributing

This is a research project. For now:
1. Follow the Pre-Phase 1 plan
2. Document learnings in `docs/`
3. Keep tests passing
4. Update README as you go

---

## 📝 Change Log

**2024-11-19:** Pre-Phase 1 planning complete
- Analyzed Microsoft Earth Copilot
- Chose Semantic Kernel for agent orchestration (4-agent architecture)
- Decided against MCP for MVP
- Created comprehensive implementation plan
- Ready to start Day 1 of Pre-Phase 1

---

## 📄 License

[Add your license here]

---

## 🙏 Acknowledgments

- **Microsoft Earth Copilot** - Architecture inspiration and best practices
- **Microsoft Planetary Computer** - STAC catalog patterns
- **Azure OpenAI** - LLM infrastructure
- **Semantic Kernel** - Agent orchestration framework

---