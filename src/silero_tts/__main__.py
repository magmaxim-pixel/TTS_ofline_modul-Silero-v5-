"""Запуск команды silero-tts из консоли."""

import argparse
import sys

from .cli import interactive_loop, run_tests_cli
from .core import OfflineSileroTTS


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="silero-tts")
    parser.add_argument(
        "command",
        nargs="?",
        choices=["run", "test"],
        default="run",
        help="Команда: run — интерактивный режим, test — выполнить тесты",
    )
    parser.add_argument("--device", default="auto", help="Устройство для инференса: cpu, cuda, mps или auto")
    parser.add_argument("--languages", default="ru,en", help="Языки через запятую")
    parser.add_argument("--speaker", default="aidar", help="Голос по умолчанию для интерактивного режима")

    args = parser.parse_args(argv)
    languages = [lang.strip() for lang in args.languages.split(",") if lang.strip()]

    if args.command == "run":
        tts = OfflineSileroTTS(languages=languages, device=args.device, optimize=True)
        interactive_loop(tts, speaker=args.speaker)
        return 0

    if args.command == "test":
        return run_tests_cli()

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
