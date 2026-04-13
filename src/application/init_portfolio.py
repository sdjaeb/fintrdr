import os

from src.domain.portfolio import Portfolio


def init_new_portfolio():
    # Per user instruction: Initial portfolio balance is $100
    p = Portfolio(name="fintrdr-core-portfolio", cash=100.0)

    # Save the new portfolio state
    path = os.path.join("src/simulator/portfolios", "fintrdr_portfolio_core.json")
    with open(path, "w", encoding="utf-8") as f:
        f.write(p.model_dump_json(indent=4))

    print(f"Initialized new portfolio: {p.name} with ${p.cash}")
    return p


if __name__ == "__main__":
    init_new_portfolio()
