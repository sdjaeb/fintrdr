import json
import os
from datetime import datetime

import structlog

from src.domain.ports import LLMPort, WikiStoragePort
from src.domain.research import WikiArticle

logger = structlog.get_logger()


class ProgressiveLearningService:
    """
    Analyzes simulated performance and elite investor audits to generate
    'Lessons Learned' for the Strategy Orchestrator.
    """

    def __init__(self, storage: WikiStoragePort, llm: LLMPort):
        self.storage = storage
        self.llm = llm

    def audit_performance(self) -> None:
        """
        Gathers data and synthesizes lessons. Implements a 4-hour cooldown.
        """
        filename = f"strategy_retrospective_{datetime.now().strftime('%Y%m%d')}.md"
        # This is a leak of kb_dir, ideally storage port handles path checking
        filepath = os.path.join("knowledge-base", filename)

        if os.path.exists(filepath):
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            if (datetime.now() - file_mod_time).total_seconds() < 14400:
                logger.info("Skipping Learning Audit: Recent retrospective exists.")
                return

        logger.info("Starting Progressive Learning Audit")

        # 1. Gather Simulated Data
        sim_data = []
        portfolio_dir = "src/infrastructure/data/portfolios"
        if os.path.exists(portfolio_dir):
            for f in os.listdir(portfolio_dir):
                if f.endswith(".json"):
                    with open(os.path.join(portfolio_dir, f)) as pfile:
                        sim_data.append(json.load(pfile))

        # 2. Gather Elite Investor Data
        investor_data = []
        audit_dir = "src/infrastructure/data/audits"
        if os.path.exists(audit_dir):
            for f in os.listdir(audit_dir):
                if f.endswith(".json"):
                    with open(os.path.join(audit_dir, f)) as afile:
                        investor_data.append(json.load(afile))

        # 3. Synthesize 'The Winning Pattern'
        prompt = (
            f"You are a Senior Strategic Auditor. Review our performance data:\n\n"
            f"SIMULATED PORTFOLIOS:\n{json.dumps(sim_data)[:2000]}\n\n"
            f"ELITE INVESTOR AUDITS:\n{json.dumps(investor_data)[:2000]}\n\n"
            "Identify what is working and what is not. "
            "Compare the 'Day Trader' high-risk moves to 'Buffett' value moves. "
            "Write a 'Strategic Retrospective' article for our Wiki. "
            "Format your response as a JSON object with 'title', 'summary', 'content', 'sources', 'backlinks'."
        )

        try:
            response = self.llm.generate(prompt, system_prompt="You return only a JSON WikiArticle.")

            # Robust Cleaning
            cleaned = response.strip()
            if "```" in cleaned:
                if "```json" in cleaned:
                    cleaned = cleaned.split("```json")[-1].split("```")[0]
                else:
                    cleaned = cleaned.split("```")[-1].split("```")[0]

            # Find actual JSON boundaries
            start_idx = cleaned.find("{")
            end_idx = cleaned.rfind("}")
            if start_idx != -1 and end_idx != -1:
                cleaned = cleaned[start_idx : end_idx + 1]

            data = json.loads(cleaned)

            def to_str(val):
                if isinstance(val, dict | list):
                    return json.dumps(val, indent=2)
                return str(val)

            article = WikiArticle(
                title=to_str(data.get("title", "Strategic Retrospective")),
                summary=to_str(data.get("summary", "Analysis of past performance.")),
                content=to_str(data.get("content", "No content provided.")),
                sources=["Simulator", "Investor Audits"],
                backlinks=["Wiki Index", "Warren Buffett", "Day Trader"],
            )

            # Save to Wiki
            self.storage.write_wiki_article(article, filename)
            logger.info("Learning synthesized into Wiki", filename=filename)

        except Exception as e:
            logger.error("Learning synthesis failed catastrophically", error=str(e))
