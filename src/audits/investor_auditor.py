import json
import os


class InvestorAuditor:
    """
    Audits successful investors and correlates their moves with world events.
    """

    def __init__(self, audit_dir: str = "src/audits", events_dir: str = "src/events"):
        self.audit_dir = audit_dir
        self.events_dir = events_dir
        os.makedirs(self.audit_dir, exist_ok=True)
        os.makedirs(self.events_dir, exist_ok=True)

    def audit_investor(self, name: str, profile_data: dict):
        """
        Saves an investor's audit profile.
        """
        filename = f"{name.lower().replace(' ', '_')}_audit.json"
        filepath = os.path.join(self.audit_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(profile_data, f, indent=4)

        print(f"Audited: {name} -> {filepath}")

    def correlate_event(self, event_name: str, date: str, impact: str):
        """
        Saves a world event for correlation.
        """
        filename = f"{date}_{event_name.lower().replace(' ', '_')}.json"
        filepath = os.path.join(self.events_dir, filename)

        event_data = {"name": event_name, "date": date, "impact": impact}

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(event_data, f, indent=4)

        print(f"Recorded Event: {event_name} -> {filepath}")


if __name__ == "__main__":
    auditor = InvestorAuditor()

    auditor.audit_investor(
        "Warren Buffett",
        {
            "strategy": "Value Investing",
            "key_moves": [
                {
                    "date": "2008-09",
                    "move": "Invested in Goldman Sachs",
                    "rationale": "Confidence during crisis",
                },
                {
                    "date": "2016-05",
                    "move": "Started buying Apple",
                    "rationale": "Evolving view on tech moats",
                },
            ],
        },
    )

    # Example Event Correlation
    auditor.correlate_event("2008 Financial Crisis", "2008-09-15", "Lehman Brothers collapse, systemic risk.")
