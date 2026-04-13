# fintrdr System Design

## Overview
`fintrdr` is an automated financial investment engine and platform designed to grow capital from $100 to high-growth targets. It leverages multi-agent AI research, automated knowledge management (LLM-owned wiki), and event-correlated strategy formulation.

## Core Components

### 1. Knowledge Base (LLM-Owned Wiki)
- **Role:** Central repository for all synthesized knowledge.
- **Goal:** Transform raw research (papers, articles, repos, images) into a structured markdown wiki.
- **Ownership:** Fully owned and edited by an LLM agent; human-read-only.
- **Format:** Obsidian-compatible markdown with summaries, concept articles, and backlinks.
- **Workflow:**
  - Raw research ingestion (`fintrdr/research/`).
  - LLM synthesis and wiki generation (`fintrdr/knowledge-base/`).
  - Automated linking and backlinking.

### 2. Research Pipeline
- **Role:** Collecting and processing external data.
- **Sources:** Financial whitepapers, news articles, codebases, market data APIs.
- **Process:** Fetch, clean, and store raw research for the Knowledge Base agent.

### 3. Investment Engine
- **Role:** Formulate and execute trading strategies.
- **Modules:**
  - **Strategy Formulator:** Develops trading strategies based on the Knowledge Base.
  - **Risk Manager:** Ensures trades align with safety and growth goals (especially the $100 starting point).
  - **Execution Engine:** Connects to brokers/exchanges to place trades.

### 4. Audit & Correlation System
- **Role:** Learn from past successes and correlate with global events.
- **Audit:** Analyze portfolios and moves of investors like Warren Buffett.
- **Correlation:** Link past successful moves to the world events that prompted them.
- **Data:** Historical market data, news archives, economic indicators.

## Architecture

```
[Raw Research] -> [Research Pipeline] -> [LLM Knowledge Agent] -> [Structured Wiki (Obsidian)]
                                                                           |
                                                                           v
[Market Data] -> [Investment Engine] <- [Strategy Formulator] <- [Audit System]
                         |
                         v
                [Execution Engine] -> [Broker/Exchange]
```

## Technology Stack
- **Language:** Python (backend, research, data science).
- **AI/LLM:** Gemini, Claude, OpenAI (via various agents).
- **Database:** SQLite/ChromaDB (memory and structured data).
- **Knowledge Base:** Obsidian (markdown-based).
- **Infrastructure:** Local/Cloud-based containers.
