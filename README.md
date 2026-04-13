# fintrdr: Autonomous Wealth Generation Engine

`fintrdr` is an advanced agentic investment platform designed to navigate modern financial markets through a combination of **Domain-Driven Design (DDD)**, **Hexagonal Architecture**, and the **Karpathy Knowledge OS** philosophy.

## 🏗️ Architecture: Hexagonal & DDD

The project is built on strict software engineering principles to ensure long-term maintainability and modularity:

-   **Domain Layer (`src/domain/`)**: The core "heart" of the system. Contains pure business logic, entities (Portfolios, Trades), and **Ports** (interfaces) that define how the engine interacts with the world.
-   **Application Layer (`src/application/`)**: Orchestrates use cases. Contains services for strategy formulation, risk management, and the "Morning Review" loop.
-   **Infrastructure Layer (`src/infrastructure/`)**: Implements the Ports. Contains adapters for LLMs (Ollama), Storage (Filesystem), Market Data (yfinance), and Reporting.

## 🧠 Key Features

-   **Karpathy Knowledge OS**: An LLM-owned research wiki that automatically synthesizes raw data into structured Obsidian-compatible Markdown.
-   **Multi-Agent Intelligence**: Specialized agents (Economist, Day Trader, Risk Manager, Crypto Watchdog) collaborate to formulate strategies.
-   **Simons-Style Quant Signals**: Leverages mathematical indicators like **Z-Scores (Mean Reversion)** and **Market Regime Detection** to find statistical edges.
-   **Interactive Morning Review**: Generates a professional HTML report and leads you through an interactive terminal session to approve or defer trades.
-   **Strict Risk Protection**: Dynamic cash reserves and position limits enforced by an autonomous Chief Risk Officer.

## 🚀 Getting Started

### Prerequisites
- **Python 3.13+**
- **[uv](https://github.com/astral-sh/uv)** for dependency management.
- **[Ollama](https://ollama.com/)** running locally with the `gemma4:e4b` model.
- **[Obsidian](https://obsidian.md/)** (Optional) to visualize the Knowledge Base.

### Installation
```bash
git clone https://github.com/sdjaeb/fintrdr.git
cd fintrdr
uv sync
```

### Usage
Run the daily intelligence loop:
```bash
./review.sh
```

## 📚 Attributions & Frameworks

`fintrdr` is built upon the following foundational concepts and tools:

-   **[Andrej Karpathy's Knowledge Base Idea](https://x.com/karpathy)**: The "LLM-owned wiki" concept for structured research.
-   **[Agentic Baseline](https://github.com/google/gemini-cli)**: Orchestration and governance prompts.
-   **[feynman](https://github.com/getcompanion-ai/feynman)**: Research agent philosophies.
-   **[claude-code-setup](https://github.com/tomascortereal/claude-code-setup)**: Advanced agentic principles and hook-based governance.
-   **[graphify](https://github.com/safishamsi/graphify)**: Document-to-graph transformation concepts.

---
*Disclaimer: fintrdr is an experimental simulation engine. All trades are virtual. Invest real capital at your own risk.*
