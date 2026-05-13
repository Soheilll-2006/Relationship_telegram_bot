"""Per-user scheduler.

Uses APScheduler's BackgroundScheduler to fire a tick every minute and
deliver each user's daily message at *their* configured local time, while
also doing one birthday/anniversary check per day per user.
"""

from __future__ import annotations

import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from .bot import LoveBot
from .database import Database
from .utils import get_tz

logger = logging.getLogger(__name__)


class DailyScheduler:
    def __init__(self, bot: LoveBot, db: Database) -> None:
        self.bot = bot
        self.db = db
        # When we last sent to a user (YYYY-MM-DD in their tz). Prevents dupes.
        self._sent_today: dict[int, str] = {}
        self._birthday_done: dict[int, str] = {}
        self._scheduler = BackgroundScheduler(timezone="UTC")

    def start(self) -> None:
        # Run the tick every minute. The tick figures out whether each user's
        # local clock just crossed their scheduled minute.
        self._scheduler.add_job(self._tick, "interval", minutes=1, id="lovebot-tick",
                                 max_instances=1, coalesce=True)
        self._scheduler.start()
        logger.info("DailyScheduler started — tick every minute.")

    def stop(self) -> None:
        self._scheduler.shutdown(wait=False)

    # ------------------------------------------------------------ tick

    def _tick(self) -> None:
        users = self.db.list_active_users()
        for user in users:
            try:
                self._maybe_send_daily(user)
                self._maybe_send_birthday(user)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Tick error for user %s: %s", user.get("user_id"), exc)

    def _maybe_send_daily(self, user: dict) -> None:
        tz = get_tz(user.get("timezone") or "UTC")
        local = datetime.now(tz)
        today = local.date().isoformat()
        user_id = int(user["user_id"])

        # Already sent today?
        if self._sent_today.get(user_id) == today:
            return

        hour = int(user.get("daily_hour") or 9)
        minute = int(user.get("daily_minute") or 0)

        # Fire if we're at the configured minute *or later* in the day, and
        # we haven't yet sent. This makes the bot robust to small downtime
        # (if it was down at exactly 09:00, it will still send when it comes
        # back up).
        if (local.hour, local.minute) >= (hour, minute):
            self.bot.send_daily_to(user)
            self._sent_today[user_id] = today

    def _maybe_send_birthday(self, user: dict) -> None:
        tz = get_tz(user.get("timezone") or "UTC")
        today = datetime.now(tz).date()
        today_str = today.isoformat()
        user_id = int(user["user_id"])

        if self._birthday_done.get(user_id) == today_str:
            return

        md = f"{today.month:02d}-{today.day:02d}"
        if user.get("user_birthday") == md or user.get("partner_birthday") == md:
            # The bot helper already greets both partners as needed.
            self.bot.check_and_send_birthdays()
            self._birthday_done[user_id] = today_str
