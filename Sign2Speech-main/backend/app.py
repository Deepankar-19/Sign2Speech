import json
import os
import re
import shutil
import uuid

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from gtts import gTTS

from inference import predict_video


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


UPLOAD_DIR = "uploads"
AUDIO_DIR = os.path.join(UPLOAD_DIR, "tts")

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)
os.makedirs(
    AUDIO_DIR,
    exist_ok=True
)

app.mount(
    "/tts",
    StaticFiles(directory=AUDIO_DIR),
    name="tts"
)


def generate_prediction_audio(label: str, language: str):
    label = (label or "").strip()
    if not label:
        return None

    lang_map = {
        "english": "en",
        "hindi": "hi",
        "tamil": "ta"
    }

    lang_code = lang_map.get(language.lower(), "en")
    safe_label = re.sub(r"[^\w\s\-]", "", label, flags=re.UNICODE)
    safe_label = re.sub(r"\s+", " ", safe_label).strip()

    if not safe_label:
        return None

    file_name = f"{safe_label.lower().replace(' ', '_')}_{uuid.uuid4().hex}.mp3"
    audio_path = os.path.join(AUDIO_DIR, file_name)

    try:
        tts = gTTS(
            text=label,
            lang=lang_code,
            slow=False
        )
        tts.save(audio_path)
        return f"/tts/{file_name}"
    except Exception:
        return None


@app.get("/label-map/{language}")
def get_label_map(language: str):
    allowed_languages = {"english", "tamil", "hindi"}
    language = language.lower().strip()

    if language not in allowed_languages:
        return {"error": "Unsupported language"}

    label_path = os.path.join(
        os.path.dirname(__file__),
        f"label_map_{language}.json"
    )

    with open(label_path, "r", encoding="utf-8") as f:
        label_map = json.load(f)

    return label_map


@app.get("/speak")
def speak_label(text: str = "", language: str = "english"):
    language = (language or "english").lower().strip()

    if not text or language not in {"english", "tamil", "hindi"}:
        return {"error": "Missing text or unsupported language"}

    audio_url = generate_prediction_audio(text, language)
    if not audio_url:
        return {"error": "Could not generate audio"}

    return {"audio_url": audio_url}


@app.get("/")
def root():
    return {
        "message": "ISL Sign2Speech Backend is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    language: str = Form("english")
):

    allowed_languages = {
        "english",
        "tamil",
        "hindi"
    }

    language = language.lower().strip()

    if language not in allowed_languages:
        return {
            "error": "Unsupported language",
            "supported_languages": list(allowed_languages)
        }

    file_extension = os.path.splitext(
        file.filename
    )[1]

    if not file_extension:
        file_extension = ".mp4"

    filename = (
        f"{uuid.uuid4()}"
        f"{file_extension}"
    )

    video_path = os.path.join(
        UPLOAD_DIR,
        filename
    )

    try:

        with open(
            video_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        result = predict_video(
            video_path,
            language
        )

        audio_url = generate_prediction_audio(
            result.get("label", ""),
            result.get("language", "english")
        )

        if audio_url:
            result["audio_url"] = audio_url

        return result

    except Exception as e:

        return {
            "error": str(e)
        }

    finally:

        if os.path.exists(video_path):
            os.remove(video_path)