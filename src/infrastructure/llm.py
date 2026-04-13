import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


class OllamaLLMAdapter:
    """
    Adapter for a local Ollama instance.
    Defaults to using the gemma4:e4b model as requested.
    """

    def __init__(self, host: str = "http://localhost:11434", model: str = "gemma4:e4b"):
        self.host = host
        self.model = model
        self.generate_url = f"{self.host}/api/generate"

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(requests.exceptions.RequestException),
    )
    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """
        Calls the Ollama generate endpoint.
        """
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        if system_prompt:
            payload["system"] = system_prompt

        response = requests.post(self.generate_url, json=payload, timeout=60)
        response.raise_for_status()

        data = response.json()
        return data.get("response", "")
