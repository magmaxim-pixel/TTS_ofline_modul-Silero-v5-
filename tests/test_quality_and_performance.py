from __future__ import annotations

import time
import warnings
from pathlib import Path

import numpy as np
import pytest

from silero_tts import OfflineSileroTTS
from silero_tts.utils import adjust_speed


# Suppress warnings from torch package
warnings.filterwarnings("ignore", category=SyntaxWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)


@pytest.fixture(scope="session")
def tts() -> OfflineSileroTTS:
    return OfflineSileroTTS(languages=["ru", "en"], device="cpu", optimize=False)


def test_synthesize_short_phrase(tts: OfflineSileroTTS) -> None:
    audio = tts.synthesize("Привет, это тест синтеза.", speaker="xenia")
    assert audio.ndim == 1
    assert audio.size > 0


def test_switch_language_and_english_synthesis(tts: OfflineSileroTTS) -> None:
    tts.switch_language("en")
    audio = tts.synthesize("Hello world from offline TTS.", speaker="en_0")
    assert audio.size > 0
    assert audio.dtype == np.float32 or audio.dtype == np.float64
    tts.switch_language("ru")


def test_latency_short_and_long_phrases(tts: OfflineSileroTTS) -> None:
    short_text = "Привет, это короткая проверка." 
    long_text = "Это длинная фраза для оценки латентности и стабильности синтеза. " * 5

    def measure(text: str) -> float:
        iterations = 2
        total = 0.0
        for _ in range(iterations):
            start = time.perf_counter()
            tts.synthesize(text, speaker="xenia")
            total += time.perf_counter() - start
        return total / iterations

    short_latency = measure(short_text)
    long_latency = measure(long_text)

    assert short_latency > 0
    assert long_latency > 0
    assert long_latency >= short_latency


def test_adjust_speed_effect() -> None:
    sample = np.sin(np.linspace(0, 10 * np.pi, 48000, dtype=np.float32))
    fast = adjust_speed(sample, speed=1.8)
    slow = adjust_speed(sample, speed=0.75)

    assert fast.shape[0] < sample.shape[0]
    assert slow.shape[0] > sample.shape[0]


def test_save_to_file_creates_audio(tts: OfflineSileroTTS, tmp_path: Path) -> None:
    output = tmp_path / "output_test.wav"
    path = tts.save_to_file("Тестовая запись для файла.", str(output), speaker="xenia")
    assert path.exists()
    assert path.stat().st_size > 0


@pytest.mark.longrun
def test_repeated_synthesis_load_scenario(tts: OfflineSileroTTS) -> None:
    for index in range(6):
        phrase = f"Повторный синтез, итерация {index}."
        audio = tts.synthesize(phrase, speaker="xenia")
        assert audio.size > 0
