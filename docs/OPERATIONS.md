# fintrdr Operational Guide & Next Steps

Welcome to your automated financial investment engine. This document explains how the system works, how to interpret its findings, and how to extend it toward the high-growth targets goal.

---

## 🏗️ How it Works: The Intelligence Pipeline

The system operates in a closed loop called the **Morning Review**:

1.  **Ingestion:** The system scrapes live headlines (CNBC/Yahoo) and research URLs.
2.  **Synthesis (Karpathy Wiki):** A local LLM reads the raw data and maintains a structured Markdown Wiki. It "learns" about new companies and events without human intervention.
3.  **Discovery:** The system scans the Wiki to find stock tickers and crypto assets. It manages a "Ticker Universe" by promoting winners and demoting underperformers.
4.  **Learning:** An ML layer (scikit-learn) calculates price trajectories (UP/DOWN/FLAT) and an LLM auditor reviews past trades to extract "Lessons Learned."
5.  **Strategy:** A specialized agent correlates today's news with historical data (Buffett, Dalio, etc.) to formulate a plan.
6.  **Risk Management:** A "Chief Risk Officer" agent vets the plan, enforces position limits (15%), and ensures a dynamic cash reserve (5-50%).
7.  **Reporting:** A deduplicated, diversified trade ticket is generated and opened in your browser.

---

## 📈 Understanding Statuses & Recommendations

### Ticker Trajectories (ML Model)
- **UPWARD:** Strong positive momentum. Model fits the trend with high confidence.
- **DOWNWARD:** Bearish trend. Potential shorting opportunity or "do not buy" signal.
- **FLAT:** Sideways movement. High noise or consolidation.
- **STABLE (Mock):** Fallback state when live data is unavailable.

### Recommendation Timing
- **[IMMEDIATE]:** Actions to take **TODAY**. These are budgeted to fit your current cash.
- **[CONTINGENT]:** Future "If/Then" triggers. These are not part of today's budget but are stored in your strategy playbook.

---

## 💰 Financial Instruments Explained

### 1. Short Selling
- **What it is:** Profit from a stock's price *falling*. You borrow shares, sell them now, and hope to buy them back later at a lower price (covering).
- **In fintrdr:** The system automatically recommends shorts when it detects a "DOWNWARD" trajectory in an overvalued asset.

### 2. Fractional Shares
- **What it is:** Buying a portion of a share (e.g., 0.0576 of Apple). 
- **In fintrdr:** Critical for our $100 start. It allows you to own high-priced stocks (like Berkshire @ $400k+) with just a few dollars.

### 3. Tax Shelters & Trusts
- **What it is:** Legal structures (GRATs, CRUTs, LLCs) to minimize tax liability and protect wealth.
- **In fintrdr:** These are handled by the **Wealth Strategist** agent. They are "locked" until your portfolio hits $5,000,000 to keep the focus on aggressive early-stage compounding.

---

## 📅 Maintenance & Run Frequency

- **Frequency:** Run `./review.sh` **once every morning** when the market opens (or whenever you are at your laptop).
- **Debouncing:** The system has a **4-hour cooldown**. Running it multiple times in an hour will reuse cached data to prevent polluting your Wiki with redundant articles.
- **Weekend Runs:** Market data won't move on weekends, but running the review can help the agents perform "Deep Audits" and "Wiki Linting" to prepare for Monday.

---

## 🚀 Future Extensions (How to Grow fintrdr)

To make the system more robust, you could consider adding these components:

1.  **Sentiment Analysis MCP:** Connect an "X (Twitter) or Reddit" scraper to the Ingestor. Let the agents see "Social Momentum" alongside "Price Momentum."
2.  **Live Broker Integration:** Connect to the **Alpaca** or **Robinhood** API. Change the "Lock-In" script to actually place the orders in your account.
3.  **Advanced ML (LSTM):** Replace the current Linear Regression with a Long Short-Term Memory (LSTM) network for better time-series forecasting.
4.  **Visual Dashboard:** Use `Streamlit` or `Obsidian Dataview` to create a live dashboard of your $100 -> high-growth progress.
5.  **Multi-Language Research:** Allow the Ingestor to read financial reports in other languages (e.g., Japanese or Chinese markets) to find global arbitrage opportunities.

---
*This guide is maintained by the fintrdr Framework.*
