# Project References & Attributions

`fintrdr` is an autonomous investment engine built on the shoulders of giants in the AI and Finance communities.

## Core Concepts & Frameworks

### Andrej Karpathy's "The System"
The **Karpathy Knowledge OS** implemented here is based on Andrej Karpathy's philosophy of using LLMs to build and maintain a personal research wiki. 
- **Concept:** Raw data ingestion -> LLM Synthesis -> Structured Wiki -> Self-Improving Loop.
- **Implementation:** See `src/application/services.py` (`WikiMaintenanceService`).

### Hexagonal Architecture (Ports & Adapters)
The codebase structure follows the Hexagonal Architecture pattern to decouple business logic from infrastructure.
- **Port Definitions:** `src/domain/ports.py`
- **Adapters:** `src/infrastructure/`

### Jim Simons (Renaissance Technologies)
Quantitative techniques like **Mean Reversion (Z-Scores)** and **Market Regime Detection** are inspired by the success of the Medallion Fund.
- **Implementation:** `src/infrastructure/predictive.py`.

### Agentic Governance
Orchestration and risk rules are derived from principles found in modern agentic frameworks.
- **[google/gemini-cli](https://github.com/google/gemini-cli)**: Baseline prompts and coordination logic.
- **[tomascortereal/claude-code-setup](https://github.com/tomascortereal/claude-code-setup)**: Deterministic hooks and frontmatter-based discovery.

## Libraries & Tools
- **[uv](https://github.com/astral-sh/uv)**: Blazing fast Python package management.
- **[yfinance](https://github.com/ranaroussi/yfinance)**: Real-time and historical market data.
- **[Ollama](https://ollama.com/)**: Local LLM execution for privacy and cost-efficiency.
- **[scikit-learn](https://scikit-learn.org/)**: Lightweight ML trajectories.
- **[Polars](https://pola.rs/)**: High-performance data manipulation.
- **[Obsidian](https://obsidian.md/)**: Visual interface for the Knowledge Base.

---
*fintrdr is a community-driven experiment in autonomous compounding.*
