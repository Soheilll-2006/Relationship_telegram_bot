"""Runtime configuration loaded from environment variables / .env file."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv is optional at runtime
    pass


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Settings:
    """Immutable application settings."""

    bot_token: str
    db_path: str = "lovebot.db"
    keep_alive: bool = False
    keep_alive_port: int = 5000
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Settings":
        token = os.getenv("BOT_TOKEN", "").strip()
        if not token:
            raise RuntimeError(
                "BOT_TOKEN is not set. Create a bot with @BotFather, then export "
                "BOT_TOKEN=<your_token> (or set it in a .env file)."
            )

        return cls(
            bot_token=token,
            db_path=os.getenv("DB_PATH", "lovebot.db").strip() or "lovebot.db",
            keep_alive=os.getenv("KEEP_ALIVE", "false").strip().lower() == "true",
            keep_alive_port=int(os.getenv("KEEP_ALIVE_PORT", "5000")),
            log_level=os.getenv("LOG_LEVEL", "INFO").strip().upper(),
        )
