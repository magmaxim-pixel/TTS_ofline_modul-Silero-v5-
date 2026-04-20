from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from time import perf_counter

from silero_tts import OfflineSileroTTS
from silero_tts.utils import adjust_speed

SHORT_TEXT = "Привет, это короткая фраза для оценки латентности."
LONG_TEXT = (
    "Это длинная фраза для оценки латентности и стабильности синтеза. "
    "Она содержит больше слов и служит для сравнения средних значений времени отклика. "
) * 4
BENCHMARK_OUTPUT = Path(__file__).resolve().parent / "benchmark_results.json"


def measure_latency(tts: OfflineSileroTTS, text: str, speaker: str, repeat: int = 3) -> float:
    timings = []
    for _ in range(repeat):
        start = perf_counter()
        tts.synthesize(text=text, speaker=speaker)
        timings.append(perf_counter() - start)
    return sum(timings) / len(timings)


def measure_speed_effect(text: str, speaker: str, tts: OfflineSileroTTS) -> dict[str, float]:
    base_audio = tts.synthesize(text=text, speaker=speaker)
    results: dict[str, float] = {}
    for speed in (0.7, 1.0, 1.3, 1.7):
        adjusted = adjust_speed(base_audio, speed=speed)
        results[f"speed_{speed}"] = len(adjusted) / len(base_audio)
    return results


def run_benchmark() -> None:
    print("Запуск бенчмарка качества Silero Offline TTS...")
    tts = OfflineSileroTTS(languages=["ru", "en"], device="cpu", optimize=False)

    summary = defaultdict(dict)
    summary["latency"]["short_phrase"] = measure_latency(tts, SHORT_TEXT, speaker="xenia", repeat=3)
    summary["latency"]["long_phrase"] = measure_latency(tts, LONG_TEXT, speaker="xenia", repeat=2)

    print("Измерение латентности завершено.")
    summary["speed_effect"] = measure_speed_effect(SHORT_TEXT, speaker="xenia", tts=tts)

    output = {
        "short_phrase_text": SHORT_TEXT,
        "long_phrase_text": LONG_TEXT,
        "reference": {
            "system": "Silero V5 (RU)",
            "instructions": "Добавьте альтернативные MOS для сравнения вручную."
        },
        "benchmarks": summary,
    }

    with BENCHMARK_OUTPUT.open("w", encoding="utf-8") as handler:
        json.dump(output, handler, ensure_ascii=False, indent=2)

    print(f"Сохранено в: {BENCHMARK_OUTPUT}")
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    run_benchmark()
