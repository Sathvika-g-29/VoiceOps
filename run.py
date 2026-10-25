
import argparse
from pathlib import Path

from src.voice import process_audio

SUPPORTED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac", ".ogg"}


def main():
    parser = argparse.ArgumentParser(
        description="Process a folder of customer audio files with VoiceOps."
    )
    parser.add_argument(
        "audio_folder",
        help="Folder containing customer audio files",
    )
    args = parser.parse_args()

    audio_folder = Path(args.audio_folder)

    if not audio_folder.is_dir():
        parser.error(f"Folder not found: {audio_folder}")

    audio_files = sorted(
        file for file in audio_folder.iterdir()
        if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not audio_files:
        parser.error("No supported audio files found in the folder.")

    for audio_file in audio_files:
        print(f"\nProcessing: {audio_file.name}")
        try:
            result = process_audio(audio_file)
            print("Transcript:", result["transcript"])
            print("Reply:", result["reply"])
            print("Reply audio:", result["reply_audio"])
            print("Retrieved chunks:", result["chunks_file"])
        except Exception as exc:
            print(f"Failed to process {audio_file.name}: {exc}")


if __name__ == "__main__":
    main()
