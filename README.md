# fintrdr

**fintrdr** is an automated financial investment engine and platform designed to grow capital from $100 to high-growth targets. It utilizes a multi-agent AI framework for deep research, automated knowledge management, and event-correlated investment strategies.

## Key Features
- **LLM-Owned Knowledge Base:** An automated, human-read-only wiki built from raw research.
- **Agentic Research Pipeline:** Deep investigation of financial markets, whitepapers, and portfolios.
- **Investor Auditing System:** Correlation of past successful moves with global events (e.g., Warren Buffett).
- **Automated Trading Engine:** Strategy formulation and execution based on synthesized intelligence.

## Getting Started
- See [docs/ROADMAP.md](docs/ROADMAP.md) for current progress and future plans.
- See [docs/DESIGN.md](docs/DESIGN.md) for system architecture details.
- See [docs/REFERENCES.md](docs/REFERENCES.md) for a summary of foundational tools and concepts.

## Project Structure
- `docs/`: Design documents, roadmaps, and references.
- `research/`: Raw research material (papers, articles, images, repos).
- `knowledge-base/`: LLM-generated wiki (Obsidian compatible).
- `src/`: Core logic for the engine, strategies, and audits.
- `tests/`: Project-specific test suites.

## 🛠️ Recommended Tools
To interact with the intelligence this system generates, the following tools are highly recommended:
1.  **[Obsidian](https://obsidian.md/):** (Free) Point Obsidian to the `knowledge-base/` folder to use the **Graph View** visualizer. This is your "Mission Control."
2.  **[VS Code](https://code.visualstudio.com/):** Best for reviewing the Python source code and running the `./review.sh` script.
3.  **[Ollama](https://ollama.com/):** Must be running locally (`ollama serve`) to power the agents.
