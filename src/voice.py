
import os
import json
from pathlib import Path

from dotenv import load_dotenv
from gnani.stt import GnaniSTTClient
from gnani.tts import GnaniTTSClient

from src.agent import VoiceOpsAgent

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

stt = GnaniSTTClient(api_key=os.getenv("GNANI_API_KEY"))
tts = GnaniTTSClient(api_key=os.getenv("GNANI_API_KEY"))

agent = VoiceOpsAgent()


def process_audio(audio_path):
    audio_path = Path(audio_path)

    # 1. Convert customer audio to text using Gnani STT.
    transcription = stt.transcribe(
        str(audio_path),
        language_code="en-IN",
    )
    transcript = transcription.get("transcript", "").strip()

    if not transcript:
        raise RuntimeError(
            f"Gnani returned no transcript for {audio_path.name}: "
            f"{transcription}"
        )

    # 2. Generate the customer-support reply.
    reply = agent.respond(transcript)

    # 3. Convert the reply to audio using Gnani TTS.
    audio_output = OUTPUT_DIR / f"{audio_path.stem}_reply.wav"
    tts.synthesize(
        reply,
        voice="Pranav",
        model="timbre-v2.5",
        language="en-IN",
        output_file=str(audio_output),
    )

    # 4. Save transcript, reply, and retrieved knowledge chunks.
    transcript_file = OUTPUT_DIR / f"{audio_path.stem}_transcript.txt"
    reply_file = OUTPUT_DIR / f"{audio_path.stem}_reply.txt"
    chunks_file = OUTPUT_DIR / f"{audio_path.stem}_chunks.json"

    transcript_file.write_text(transcript, encoding="utf-8")
    reply_file.write_text(reply, encoding="utf-8")
    chunks_file.write_text(
        json.dumps(agent.last_chunks, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return {
        "input_audio": str(audio_path),
        "transcript": transcript,
        "reply": reply,
        "reply_audio": str(audio_output),
        "chunks_file": str(chunks_file),
    }
