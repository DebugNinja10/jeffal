import tempfile
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from TTS.utils.synthesizer import Synthesizer

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "kiriku_tts" / "model.pth"
CONFIG_PATH = BASE_DIR / "kiriku_tts" / "config.json"

app = FastAPI(title="JËFAL Kiriku TTS")

print("[TTS] Chargement de Kiriku...")
synthesizer = Synthesizer(
    tts_checkpoint=str(MODEL_PATH),
    tts_config_path=str(CONFIG_PATH),
)
print("[TTS] Kiriku TTS chargé.")


class TTSRequest(BaseModel):
    text: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "kiriku-tts"}


@app.post("/tts")
def generate_tts(request: TTSRequest):
    text = request.text.strip()

    if not text:
        return {"error": "Le texte ne peut pas être vide."}

    wav = synthesizer.tts(text=text)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        output_path = tmp.name

    synthesizer.save_wav(wav, output_path)

    audio = Path(output_path).read_bytes()
    Path(output_path).unlink(missing_ok=True)

    return StreamingResponse(
        iter([audio]),
        media_type="audio/wav",
        headers={
            "Content-Disposition": 'inline; filename="response.wav"'
        },
    )
