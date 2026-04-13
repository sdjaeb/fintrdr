import os
from datetime import datetime


class WikiVisualizer:
    """
    Generates a single-page HTML 'Map' of the entire Knowledge Base.
    """

    def __init__(self, kb_dir: str = "knowledge-base", output_dir: str = "docs"):
        self.kb_dir = kb_dir
        self.output_dir = output_dir

    def generate_map(self):
        kb_files = [f for f in os.listdir(self.kb_dir) if f.endswith(".md")]

        articles = []
        for f in kb_files:
            path = os.path.join(self.kb_dir, f)
            with open(path, encoding="utf-8") as file:
                content = file.read()
                # Simple extraction of title and links
                title = f.replace(".md", "").replace("_", " ").title()
                links = [link.split("[[")[-1].split("]]")[0] for link in content.split("\n") if "[[" in link]
                articles.append({"title": title, "filename": f, "links": links})

        # Create HTML
        html_path = os.path.join(self.output_dir, "wiki_map.html")

        css = """
        <style>
            body { font-family: sans-serif; max-width: 1000px; margin: 40px auto; background: #f0f2f1; padding: 20px; }
            .card { background: white; padding: 20px; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .link-tag { background: #3498db; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; margin-right: 5px; text-decoration: none; }
            h1 { color: #2c3e50; }
            h2 { margin: 0; color: #2980b9; }
        </style>
        """

        html_content = f"<!DOCTYPE html><html><head><title>Wiki Map</title>{css}</head><body>"
        html_content += "<h1>🧠 Intelligence Map (Knowledge Base)</h1>"
        html_content += f"<p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>"

        for a in sorted(articles, key=lambda x: x["title"]):
            html_content += "<div class='card'>"
            html_content += f"<h2>{a['title']}</h2>"
            html_content += f"<p style='color: #7f8c8d;'>File: {a['filename']}</p>"
            if a["links"]:
                html_content += "<div>"
                for link in a["links"]:
                    html_content += f"<span class='link-tag'>Linked to: {link}</span>"
                html_content += "</div>"
            html_content += "</div>"

        html_content += "</body></html>"

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return html_path


if __name__ == "__main__":
    viz = WikiVisualizer()
    print(f"Wiki Map generated at: {viz.generate_map()}")
