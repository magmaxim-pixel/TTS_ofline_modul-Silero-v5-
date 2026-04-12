
"""Точка входа в приложение."""

from silero_tts import OfflineSileroTTS
from silero_tts.cli import interactive_loop
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def main():
    print("🚀 Silero TTS — RU + EN (чистый, быстрый, плавный конец)")
    tts = OfflineSileroTTS(languages=["ru", "en"], device="auto", optimize=True)
    interactive_loop(tts, speaker="xenia")


if __name__ == "__main__":
    main()