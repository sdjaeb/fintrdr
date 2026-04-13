# fintrdr Operational Guide

This document provides technical and strategic guidance for running and extending the `fintrdr` autonomous investment engine.

## 🏗️ The Intelligence Loop

The core of `fintrdr` is the **Morning Review Pipeline**, triggered by `./review.sh`. This pipeline orchestrates several domain-specific services:

1.  **Ingestion (`ResearchIngestionService`)**: Polls real-time headlines and specified research URLs.
2.  **Synthesis (`WikiMaintenanceService`)**: Uses the Karpathy Loop to summarize raw research into the Knowledge Base.
3.  **Discovery (`TickerDiscoveryService`)**: Identifies emerging tickers and manages the Active Universe vs. Watchlist.
4.  **Prediction (`TrajectoryPredictor`)**: Calculates linear regression slopes and R-squared confidence.
5.  **Quant Analysis (`QuantSignalProcessor`)**: Calculates Z-Scores for mean reversion and detects Volatility Regimes.
6.  **Strategy (`StrategyOrchestrator`)**: Formulates trade rules based on agent personas and wiki intelligence.
7.  **Risk (`RiskManager`)**: Vets trades against position limits, crypto caps, and dynamic cash reserves.

---

## 📈 Understanding the Signals

### Trajectories & ML
The system uses lightweight machine learning to identify the "direction" of an asset:
- **UPWARD**: Positive slope with statistical significance.
- **DOWNWARD**: Negative slope (potential shorting target).
- **FLAT**: No clear trend; often indicates consolidation.

### Quant Signals (Simons-style)
- **Z-Score**: A measure of how "stretched" a price is. 
    - `Z > 2.0`: Mathematically overbought. High probability of a pullback.
    - `Z < -2.0`: Mathematically oversold. Potential rebound entry.
- **Market Regimes**:
    - **HIGH_VOLATILITY**: The "Simons Playground." Profitable but requires tight risk controls.
    - **LOW_VOLATILITY**: Ideal for steady, "Buffett-style" compounding.

---

## 🛡️ Risk Management Policies

- **Maximum Position Size**: Default is 15% of total portfolio value.
- **Crypto Exposure**: Hard-capped at 5% total exposure per user mandate.
- **Dynamic Cash Reserve**: 
    - Increases to 25%+ during Bearish regimes to protect capital.
    - Decreases to 5% during Bullish regimes to maximize alpha.

---

## 🚀 Future Extensions

`fintrdr` is designed for extensibility via its **Hexagonal Architecture**:

1.  **Adding a New Source**: Implement a new adapter in `src/infrastructure/scraper.py` and register it in the application service.
2.  **Adding an Agent**: Create a new `.md` file in `.github/agents/` with proper YAML frontmatter. The `StrategyOrchestrator` will automatically find it.
3.  **Advanced ML**: Replace the `TrajectoryPredictor` with a more complex model (e.g., Random Forest or LSTM) by updating the `predictive.py` adapter.

---

## 🛠️ Git Standards (Conventional Commits)

To maintain a clean and searchable history, this project enforces the **Conventional Commits** standard. Every commit must follow this format:
`<type>(scope): description`

**Common Types:**
- `feat`: A new feature (e.g., a new specialist agent).
- `fix`: A bug fix (e.g., fixing a JSON parse error).
- `refactor`: A code change that neither fixes a bug nor adds a feature.
- `docs`: Documentation only changes.
- `test`: Adding missing tests or correcting existing tests.
- `chore`: Changes to the build process or auxiliary tools.

---
*fintrdr Strategic Review — Empowering autonomous wealth generation through intelligence.*
