import httpx


class TTSService:
    def __init__(self, base_url: str = "http://127.0.0.1:8001"):
        self.base_url = base_url.rstrip("/")

    def synthesize(self, text: str) -> bytes:
        text = text.strip()

        if not text:
            raise ValueError("Le texte ne peut pas être vide.")

        response = httpx.post(
            f"{self.base_url}/tts",
            json={"text": text},
            timeout=60.0,
        )

        response.raise_for_status()

        return response.content
