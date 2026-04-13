import os

from src.domain.portfolio import Portfolio


def lock_in():
    path = "src/simulator/portfolios/fintrdr_portfolio_core.json"
    if not os.path.exists(path):
        print("Portfolio not found.")
        return

    with open(path) as f:
        p = Portfolio.model_validate_json(f.read())

    # Transactions from report_2026-04-09
    # Executing at recommended quantities and current market prices
    p.buy("AAPL", 0.0576, 260.49, "Day 1 Journey Start")
    p.buy("SMAR", 0.1364, 110.00, "Day 1 Journey Start")
    p.buy("AMZN", 0.0642, 233.65, "Day 1 Journey Start")
    p.buy("JPM", 0.0483, 310.33, "Day 1 Journey Start (Risk Capped)")

    with open(path, "w") as f:
        f.write(p.model_dump_json(indent=4))

    print(f"Successfully locked in trades for {p.name}")
    print(f"Remaining Cash: ${p.cash:.2f}")
    print(f"Current Holdings: {list(p.holdings.keys())}")


if __name__ == "__main__":
    lock_in()
