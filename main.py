"""Entry point — wire up settings, database, bot, scheduler, and (optional) keep-alive."""

from __future__ import annotations

import logging
import sys

from lovebot import __version__
from lovebot.bot import LoveBot
from lovebot.config import Settings
from lovebot.database import Database
from lovebot.keep_alive import start_keep_alive
from lovebot.scheduler import DailyScheduler


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(stream=sys.stdout),
            logging.FileHandler("lovebot.log", encoding="utf-8"),
        ],
    )


def main() -> None:
    try:
        settings = Settings.from_env()
    except RuntimeError as exc:
        print(f"\n❌ {exc}\n", file=sys.stderr)
        sys.exit(1)

    configure_logging(settings.log_level)
    log = logging.getLogger("lovebot.main")
    log.info("🚀 Starting LoveBot v%s", __version__)

    db = Database(settings.db_path)
    bot = LoveBot(token=settings.bot_token, db=db)
    scheduler = DailyScheduler(bot, db)
    scheduler.start()

    if settings.keep_alive:
        start_keep_alive(settings.keep_alive_port)

    try:
        bot.run()
    except KeyboardInterrupt:
        log.info("👋 Shutting down (Ctrl+C).")
    finally:
        scheduler.stop()
        db.close()


if __name__ == "__main__":
    main()
