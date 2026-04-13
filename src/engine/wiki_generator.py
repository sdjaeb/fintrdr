import os


class WikiGenerator:
    """
    Simulated Wiki Generator for the Karpathy-style knowledge base.
    Converts raw research into structured markdown (Obsidian compatible).
    """

    def __init__(self, research_dir: str = "research", kb_dir: str = "knowledge-base"):
        self.research_dir = research_dir
        self.kb_dir = kb_dir
        os.makedirs(self.kb_dir, exist_ok=True)

    def process_research(self):
        """
        Reads all files in research/ and generates summaries.
        """
        research_files = [
            f for f in os.listdir(self.research_dir) if os.path.isfile(os.path.join(self.research_dir, f))
        ]

        for rf in research_files:
            rf_path = os.path.join(self.research_dir, rf)
            with open(rf_path, encoding="utf-8") as f:
                content = f.read()

            # Simple summary logic - in a real scenario, this would be an LLM call
            title = rf.replace(".txt", "").replace("_", " ").title()
            kb_filename = rf.replace(".txt", ".md")
            kb_path = os.path.join(self.kb_dir, kb_filename)

            with open(kb_path, "w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n")
                f.write(f"[[Source: {rf_path}]]\n\n")
                f.write("## Automated Summary\n")
                f.write(f"This is an automated summary for {title}. (LLM integration pending)\n\n")
                f.write("## Raw Content Insights\n")
                # Grabbing the first 500 characters as a placeholder
                f.write(content[:500].strip() + "...\n\n")
                f.write("## Backlinks\n")
                f.write("- [[Wiki Index]]\n")

            print(f"Generated wiki entry: {kb_path}")

        self.generate_index()

    def generate_index(self):
        """
        Creates an index file for the knowledge base.
        """
        kb_files = [f for f in os.listdir(self.kb_dir) if f.endswith(".md") and f != "Wiki Index.md"]
        index_path = os.path.join(self.kb_dir, "Wiki Index.md")

        with open(index_path, "w", encoding="utf-8") as f:
            f.write("# Wiki Index\n\n")
            f.write("Welcome to the automated knowledge base.\n\n")
            f.write("## Research Entities\n")
            for kbf in kb_files:
                name = kbf.replace(".md", "").replace("_", " ").title()
                f.write(f"- [[{name}]]\n")

        print(f"Updated Wiki Index: {index_path}")


if __name__ == "__main__":
    generator = WikiGenerator()
    generator.process_research()
