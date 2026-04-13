import os

from src.domain.portfolio import Portfolio


def lock_in() -> None:
    path = "src/infrastructure/data/portfolios/fintrdr_portfolio_core.json"
    if not os.path.exists(path):
        print("Portfolio not found.")
        return

    with open(path) as f:
        p = Portfolio.model_validate_json(f.read())

    # Transactions from latest report - This is typically manual or passed as args
    # For now, we'll keep the example buys as a template
    # p.buy('AAPL', 0.0576, 260.49, 'Day 1 Journey Start')

    with open(path, "w", encoding="utf-8") as f:
        f.write(p.model_dump_json(indent=4))

    print(f"Successfully locked in trades for {p.name}")
    print(f"Remaining Cash: ${p.cash:.2f}")
    print(f"Current Holdings: {list(p.holdings.keys())}")


if __name__ == "__main__":
    lock_in()
