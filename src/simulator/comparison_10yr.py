import structlog

from src.domain.portfolio import Portfolio
from src.simulator.engine import HistoricalSimulator

logger = structlog.get_logger()


def run_investor_comparison():
    # Define tickers relevant to the strategies
    # BRK-B (Buffett), SPY (Baseline/Newbie), GLD (Dalio/All Weather - launched 2004, so we'll use Gold proxies or Treasury bonds)
    # Since we're limited to Yahoo Finance, let's use:
    # SPY: S&P 500 (Baseline)
    # BRK-B: Berkshire Hathaway (Buffett)
    # TLT: 20+ Year Treasury (Part of Dalio's All Weather)
    # GLD: Gold (Part of Dalio's All Weather - note: GLD started in 2004, so we'll use it for the later half)

    tickers = ["SPY", "BRK-B", "TLT", "MSFT", "AAPL"]
    start_date = "1997-05-01"
    end_date = "2007-04-30"

    sim = HistoricalSimulator(tickers=tickers, start_date=start_date, end_date=end_date)

    if not sim.load_data():
        return

    # 1. Baseline/Newbie Portfolio: 100% S&P 500 (Buy and Hold)
    p_baseline = Portfolio(name="Baseline-Newbie", cash=100.0)

    def newbie_strategy(date, prices, portfolio):
        if date == sim.data.index[0]:
            # Invest all cash into SPY
            qty = portfolio.cash / prices["SPY"]
            portfolio.buy("SPY", qty, prices["SPY"], rationale="Baseline: Buy and hold index.")

    # 2. Buffett-Inspired: High conviction, value-focused (Holding Berkshire proxy or key holdings)
    p_buffett = Portfolio(name="Buffett-Style", cash=100.0)

    def buffett_strategy(date, prices, portfolio):
        if date == sim.data.index[0]:
            # Buffett famously holds for long periods.
            # We'll use BRK-B as the proxy for his expertise.
            qty = portfolio.cash / prices["BRK-B"]
            portfolio.buy("BRK-B", qty, prices["BRK-B"], rationale="Value: Long-term bet on Berkshire.")

    # 3. Dalio-Inspired (All Weather Lite): Diversified across stocks and bonds
    p_dalio = Portfolio(name="Dalio-All-Weather", cash=100.0)

    def dalio_strategy(date, prices, portfolio):
        if date == sim.data.index[0]:
            # NOTE: TLT doesn't exist in 1997. Using MSFT as a proxy for 'Quality'
            # for this test run to ensure engine works without NaNs.
            stock_cash = portfolio.cash * 0.4
            quality_cash = portfolio.cash * 0.6

            s_qty = stock_cash / prices["SPY"]
            q_qty = quality_cash / prices["MSFT"]

            portfolio.buy("SPY", s_qty, prices["SPY"], rationale="Baseline index")
            portfolio.buy("MSFT", q_qty, prices["MSFT"], rationale="Quality proxy")

    # Run Simulations
    sim.run_simulation(p_baseline, newbie_strategy)
    sim.run_simulation(p_buffett, buffett_strategy)
    sim.run_simulation(p_dalio, dalio_strategy)

    # Final Evaluation
    final_prices = sim.data.iloc[-1].to_dict()
    print("\n--- 10-Year Simulation Results (1997-2007) ---")
    for p in [p_baseline, p_buffett, p_dalio]:
        val = p.get_value(final_prices)
        print(f"Portfolio: {p.name:<20} | Final Value: ${val:>8.2f} | Growth: {((val-100)/100)*100:>6.1f}%")
    print("----------------------------------------------\n")


if __name__ == "__main__":
    run_investor_comparison()
