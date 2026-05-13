"""Main bot class — onboarding state machine + every command & feature.

The bot is fully bilingual (Persian / English), per-user (no shared group),
and remembers each user's preferences and content history in SQLite.
"""

from __future__ import annotations

import logging
import random
from datetime import date, datetime, timedelta
from typing import Any

import pytz
import telebot
from telebot import types
from telebot.apihelper import ApiException

from .content import greetings
from .content_picker import pick_unseen, progress
from .database import Database
from .i18n import COMMON_TIMEZONES, MOOD_OPTIONS, mood_label, t
from .keyboards import (
    advice_again_keyboard,
    back_to_menu_keyboard,
    challenge_again_keyboard,
    close_keyboard,
    compliment_again_keyboard,
    confirm_delete_keyboard,
    dates_keyboard,
    events_list_keyboard,
    language_keyboard,
    love_score_keyboard,
    main_menu,
    mood_keyboard,
    quote_again_keyboard,
    settings_keyboard,
    skip_keyboard,
    time_keyboard,
    timezone_keyboard,
)
from .utils import (
    days_between,
    format_number,
    get_tz,
    humanise_duration,
    is_special_milestone,
    next_milestone,
    now_in,
    parse_birthday,
    parse_date,
    parse_time,
)

logger = logging.getLogger(__name__)


# ---------- onboarding state names (also reused for in-settings prompts) ------

S_PICK_LANG          = "ob_lang"
S_USER_NAME          = "ob_user_name"
S_PARTNER_NAME       = "ob_partner_name"
S_START_DATE         = "ob_start_date"
S_USER_BDAY          = "ob_user_bday"
S_PARTNER_BDAY       = "ob_partner_bday"
S_TIME               = "ob_time"
S_TZ                 = "ob_tz"
S_READY              = "ready"

S_SET_LANG           = "set_lang"
S_SET_USER_NAME      = "set_user_name"
S_SET_PARTNER_NAME   = "set_partner_name"
S_SET_START_DATE     = "set_start_date"
S_SET_USER_BDAY      = "set_user_bday"
S_SET_PARTNER_BDAY   = "set_partner_bday"
S_SET_TIME           = "set_time"
S_SET_TZ             = "set_tz"

S_EVENT_TITLE        = "event_title"
S_EVENT_DATE         = "event_date"


# ----------------------------------------------------------- helpers


def _safe_edit(bot: telebot.TeleBot, chat_id: int, message_id: int, text: str,
               reply_markup: types.InlineKeyboardMarkup | None = None) -> None:
    try:
        bot.edit_message_text(
            text=text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=reply_markup,
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )
    except ApiException as exc:
        # Most common cause is "message is not modified" — safe to ignore.
        if "message is not modified" not in str(exc):
            logger.warning("edit_message_text failed: %s", exc)


def _user_lang(user: dict[str, Any] | None) -> str:
    return (user or {}).get("language") or "fa"


# ----------------------------------------------------------- LoveBot class


class LoveBot:
    """Pluggable Telegram bot for couples."""

    def __init__(self, token: str, db: Database) -> None:
        self.bot = telebot.TeleBot(token, parse_mode="Markdown")
        self.db = db
        # transient per-user data that doesn't need persistence (e.g. partial form values)
        self._scratch: dict[int, dict[str, Any]] = {}
        self._register()

    # =====================================================================
    # message + callback registration
    # =====================================================================

    def _register(self) -> None:
        b = self.bot

        # ----- commands -----
        @b.message_handler(commands=["start"])
        def _start(msg: types.Message) -> None:
            self._cmd_start(msg)

        @b.message_handler(commands=["menu"])
        def _menu(msg: types.Message) -> None:
            self._send_main_menu(msg.chat.id, msg.from_user.id)

        @b.message_handler(commands=["help"])
        def _help(msg: types.Message) -> None:
            user = self.db.get_user(msg.from_user.id)
            self.bot.send_message(
                msg.chat.id,
                t(_user_lang(user), "help_text"),
                reply_markup=back_to_menu_keyboard(_user_lang(user)),
            )

        @b.message_handler(commands=["cancel"])
        def _cancel(msg: types.Message) -> None:
            user = self.db.get_user(msg.from_user.id)
            if user and user["state"] not in (S_READY, "idle"):
                self.db.set_state(msg.from_user.id, S_READY if user.get("relationship_start") else "idle")
            self.bot.send_message(msg.chat.id, t(_user_lang(user), "generic_cancelled"))
            self._send_main_menu(msg.chat.id, msg.from_user.id)

        @b.message_handler(commands=["skip"])
        def _skip(msg: types.Message) -> None:
            self._handle_skip(msg.chat.id, msg.from_user.id)

        @b.message_handler(commands=["quote"])
        def _quote(msg: types.Message) -> None:
            self._send_quote(msg.chat.id, msg.from_user.id)

        @b.message_handler(commands=["advice"])
        def _advice(msg: types.Message) -> None:
            self._send_advice(msg.chat.id, msg.from_user.id)

        @b.message_handler(commands=["challenge"])
        def _challenge(msg: types.Message) -> None:
            self._send_challenge(msg.chat.id, msg.from_user.id)

        @b.message_handler(commands=["compliment"])
        def _compliment(msg: types.Message) -> None:
            self._send_compliment(msg.chat.id, msg.from_user.id)

        @b.message_handler(commands=["milestone"])
        def _milestone(msg: types.Message) -> None:
            self._send_milestone(msg.chat.id, msg.from_user.id)

        @b.message_handler(commands=["countdown"])
        def _countdown(msg: types.Message) -> None:
            self._send_countdown(msg.chat.id, msg.from_user.id)

        @b.message_handler(commands=["mood"])
        def _mood(msg: types.Message) -> None:
            self._send_mood_prompt(msg.chat.id, msg.from_user.id)

        @b.message_handler(commands=["lovescore"])
        def _score(msg: types.Message) -> None:
            self._send_love_score(msg.chat.id, msg.from_user.id)

        @b.message_handler(commands=["settings"])
        def _settings(msg: types.Message) -> None:
            self._send_settings(msg.chat.id, msg.from_user.id)

        # ----- text router (onboarding + free-form inputs) -----
        @b.message_handler(func=lambda m: True, content_types=["text"])
        def _text(msg: types.Message) -> None:
            self._route_text(msg)

        # ----- callback router -----
        @b.callback_query_handler(func=lambda c: True)
        def _cb(call: types.CallbackQuery) -> None:
            self._route_callback(call)

    # =====================================================================
    # /start
    # =====================================================================

    def _cmd_start(self, msg: types.Message) -> None:
        user = self.db.upsert_user(msg.from_user.id, msg.chat.id)
        if user["state"] == S_READY and user.get("relationship_start"):
            lang = _user_lang(user)
            self.bot.send_message(
                msg.chat.id,
                t(lang, "welcome_already", name=user.get("user_name") or ""),
            )
            self._send_main_menu(msg.chat.id, msg.from_user.id)
            return

        # Fresh onboarding.
        self.db.set_state(msg.from_user.id, S_PICK_LANG)
        self.bot.send_message(
            msg.chat.id,
            t("fa", "welcome_pick_language"),  # Use Persian until they pick
            reply_markup=language_keyboard(prefix="lang"),
        )

    # =====================================================================
    # text routing — handles state-machine inputs (names, dates, etc.)
    # =====================================================================

    def _route_text(self, msg: types.Message) -> None:
        user = self.db.get_user(msg.from_user.id)
        if not user:
            self._cmd_start(msg)
            return

        state = user["state"]
        text = (msg.text or "").strip()
        lang = _user_lang(user)

        # Allow exiting any flow.
        if text.lower() in {"/cancel", "cancel", "لغو"}:
            self.db.set_state(msg.from_user.id, S_READY if user.get("relationship_start") else "idle")
            self.bot.send_message(msg.chat.id, t(lang, "generic_cancelled"))
            self._send_main_menu(msg.chat.id, msg.from_user.id)
            return

        # ----- onboarding -----
        if state == S_USER_NAME:
            if not text:
                self.bot.send_message(msg.chat.id, t(lang, "err_empty"))
                return
            self.db.update_user(msg.from_user.id, user_name=text[:64])
            self.db.set_state(msg.from_user.id, S_PARTNER_NAME)
            self.bot.send_message(msg.chat.id, t(lang, "ask_partner_name"))
            return

        if state == S_PARTNER_NAME:
            if not text:
                self.bot.send_message(msg.chat.id, t(lang, "err_empty"))
                return
            self.db.update_user(msg.from_user.id, partner_name=text[:64])
            self.db.set_state(msg.from_user.id, S_START_DATE)
            self.bot.send_message(msg.chat.id, t(lang, "ask_start_date"))
            return

        if state == S_START_DATE:
            d = parse_date(text)
            if not d:
                self.bot.send_message(msg.chat.id, t(lang, "err_bad_date"))
                return
            if d > date.today():
                self.bot.send_message(msg.chat.id, t(lang, "err_future_date"))
                return
            self.db.update_user(msg.from_user.id, relationship_start=d.isoformat())
            self.db.set_state(msg.from_user.id, S_USER_BDAY)
            self.bot.send_message(
                msg.chat.id, t(lang, "ask_user_birthday"),
                reply_markup=skip_keyboard(lang),
            )
            return

        if state == S_USER_BDAY:
            if text.lower() in {"skip", "/skip", "رد"}:
                self._advance_from_user_bday(msg.chat.id, msg.from_user.id, lang)
                return
            bd = parse_birthday(text)
            if not bd:
                self.bot.send_message(msg.chat.id, t(lang, "err_bad_birthday"))
                return
            self.db.update_user(msg.from_user.id, user_birthday=bd)
            self._advance_from_user_bday(msg.chat.id, msg.from_user.id, lang)
            return

        if state == S_PARTNER_BDAY:
            if text.lower() in {"skip", "/skip", "رد"}:
                self._advance_from_partner_bday(msg.chat.id, msg.from_user.id, lang)
                return
            bd = parse_birthday(text)
            if not bd:
                self.bot.send_message(msg.chat.id, t(lang, "err_bad_birthday"))
                return
            self.db.update_user(msg.from_user.id, partner_birthday=bd)
            self._advance_from_partner_bday(msg.chat.id, msg.from_user.id, lang)
            return

        if state == S_TIME:
            tm = parse_time(text)
            if not tm:
                self.bot.send_message(msg.chat.id, t(lang, "err_bad_time"))
                return
            self.db.update_user(msg.from_user.id, daily_hour=tm[0], daily_minute=tm[1])
            self.db.set_state(msg.from_user.id, S_TZ)
            self.bot.send_message(
                msg.chat.id, t(lang, "ask_timezone"),
                reply_markup=timezone_keyboard(lang),
            )
            return

        if state == S_TZ:
            try:
                pytz.timezone(text)
                tz_value = text
            except pytz.UnknownTimeZoneError:
                self.bot.send_message(msg.chat.id, t(lang, "tz_invalid"))
                return
            self._finish_onboarding(msg.chat.id, msg.from_user.id, tz_value)
            return

        # ----- settings (text follow-ups) -----
        if state == S_SET_USER_NAME:
            if not text:
                self.bot.send_message(msg.chat.id, t(lang, "err_empty"))
                return
            self.db.update_user(msg.from_user.id, user_name=text[:64])
            self.db.set_state(msg.from_user.id, S_READY)
            self.bot.send_message(msg.chat.id, t(lang, "names_updated"))
            self._send_settings(msg.chat.id, msg.from_user.id)
            return

        if state == S_SET_PARTNER_NAME:
            if not text:
                self.bot.send_message(msg.chat.id, t(lang, "err_empty"))
                return
            self.db.update_user(msg.from_user.id, partner_name=text[:64])
            self.db.set_state(msg.from_user.id, S_READY)
            self.bot.send_message(msg.chat.id, t(lang, "names_updated"))
            self._send_settings(msg.chat.id, msg.from_user.id)
            return

        if state == S_SET_START_DATE:
            d = parse_date(text)
            if not d:
                self.bot.send_message(msg.chat.id, t(lang, "err_bad_date"))
                return
            if d > date.today():
                self.bot.send_message(msg.chat.id, t(lang, "err_future_date"))
                return
            self.db.update_user(msg.from_user.id, relationship_start=d.isoformat())
            self.db.set_state(msg.from_user.id, S_READY)
            self.bot.send_message(msg.chat.id, t(lang, "date_updated"))
            self._send_settings(msg.chat.id, msg.from_user.id)
            return

        if state == S_SET_USER_BDAY:
            bd = parse_birthday(text)
            if not bd:
                self.bot.send_message(msg.chat.id, t(lang, "err_bad_birthday"))
                return
            self.db.update_user(msg.from_user.id, user_birthday=bd)
            self.db.set_state(msg.from_user.id, S_READY)
            self.bot.send_message(msg.chat.id, t(lang, "date_updated"))
            self._send_settings(msg.chat.id, msg.from_user.id)
            return

        if state == S_SET_PARTNER_BDAY:
            bd = parse_birthday(text)
            if not bd:
                self.bot.send_message(msg.chat.id, t(lang, "err_bad_birthday"))
                return
            self.db.update_user(msg.from_user.id, partner_birthday=bd)
            self.db.set_state(msg.from_user.id, S_READY)
            self.bot.send_message(msg.chat.id, t(lang, "date_updated"))
            self._send_settings(msg.chat.id, msg.from_user.id)
            return

        if state == S_SET_TIME:
            tm = parse_time(text)
            if not tm:
                self.bot.send_message(msg.chat.id, t(lang, "err_bad_time"))
                return
            self.db.update_user(msg.from_user.id, daily_hour=tm[0], daily_minute=tm[1])
            self.db.set_state(msg.from_user.id, S_READY)
            self.bot.send_message(msg.chat.id, t(lang, "time_updated"))
            self._send_settings(msg.chat.id, msg.from_user.id)
            return

        if state == S_SET_TZ:
            try:
                pytz.timezone(text)
            except pytz.UnknownTimeZoneError:
                self.bot.send_message(msg.chat.id, t(lang, "tz_invalid"))
                return
            self.db.update_user(msg.from_user.id, timezone=text)
            self.db.set_state(msg.from_user.id, S_READY)
            self.bot.send_message(msg.chat.id, t(lang, "tz_updated"))
            self._send_settings(msg.chat.id, msg.from_user.id)
            return

        # ----- custom events -----
        if state == S_EVENT_TITLE:
            if not text:
                self.bot.send_message(msg.chat.id, t(lang, "err_empty"))
                return
            self._scratch.setdefault(msg.from_user.id, {})["event_title"] = text[:80]
            self.db.set_state(msg.from_user.id, S_EVENT_DATE)
            self.bot.send_message(msg.chat.id, t(lang, "add_event_ask_date"))
            return

        if state == S_EVENT_DATE:
            d = parse_date(text)
            if not d:
                self.bot.send_message(msg.chat.id, t(lang, "err_bad_date"))
                return
            title = (self._scratch.get(msg.from_user.id, {}).get("event_title")) or "Event"
            self.db.add_custom_milestone(msg.from_user.id, title, d.isoformat())
            self.db.set_state(msg.from_user.id, S_READY)
            self._scratch.get(msg.from_user.id, {}).pop("event_title", None)
            self.bot.send_message(
                msg.chat.id,
                t(lang, "event_added", title=title, date=d.isoformat()),
            )
            self._send_events(msg.chat.id, msg.from_user.id)
            return

        # ----- fallback: show menu hint if onboarded -----
        if state == S_READY:
            self._send_main_menu(msg.chat.id, msg.from_user.id)
        else:
            # in onboarding pick_lang state and user sent text — nudge them.
            self.bot.send_message(
                msg.chat.id, t(lang, "welcome_pick_language"),
                reply_markup=language_keyboard(prefix="lang"),
            )

    # =====================================================================
    # callbacks
    # =====================================================================

    def _route_callback(self, call: types.CallbackQuery) -> None:
        try:
            self.bot.answer_callback_query(call.id)
        except ApiException:
            pass

        data = call.data or ""
        user = self.db.upsert_user(call.from_user.id, call.message.chat.id)
        lang = _user_lang(user)

        try:
            # ---------- language during onboarding ----------
            if data.startswith("lang:") and user["state"] == S_PICK_LANG:
                code = data.split(":", 1)[1]
                if code not in {"fa", "en"}:
                    return
                self.db.update_user(call.from_user.id, language=code)
                self.db.set_state(call.from_user.id, S_USER_NAME)
                _safe_edit(self.bot, call.message.chat.id, call.message.message_id,
                           t(code, "language_set"))
                self.bot.send_message(call.message.chat.id, t(code, "ask_user_name"))
                return

            # ---------- language from settings ----------
            if data.startswith("lang_set:"):
                code = data.split(":", 1)[1]
                if code not in {"fa", "en"}:
                    return
                self.db.update_user(call.from_user.id, language=code)
                _safe_edit(self.bot, call.message.chat.id, call.message.message_id,
                           t(code, "language_set"))
                self._send_settings(call.message.chat.id, call.from_user.id)
                return

            # ---------- time presets (onboarding + settings) ----------
            if data.startswith("time:set:"):
                tm = parse_time(data.split(":", 2)[2])
                if not tm:
                    return
                self.db.update_user(call.from_user.id, daily_hour=tm[0], daily_minute=tm[1])
                if user["state"] == S_TIME:
                    self.db.set_state(call.from_user.id, S_TZ)
                    _safe_edit(self.bot, call.message.chat.id, call.message.message_id,
                               t(lang, "time_updated"))
                    self.bot.send_message(call.message.chat.id, t(lang, "ask_timezone"),
                                          reply_markup=timezone_keyboard(lang))
                else:
                    self.db.set_state(call.from_user.id, S_READY)
                    _safe_edit(self.bot, call.message.chat.id, call.message.message_id,
                               t(lang, "time_updated"))
                    self._send_settings(call.message.chat.id, call.from_user.id)
                return

            # ---------- timezone presets ----------
            if data.startswith("tz:set:"):
                tzname = data.split(":", 2)[2]
                try:
                    pytz.timezone(tzname)
                except pytz.UnknownTimeZoneError:
                    return
                if user["state"] == S_TZ:
                    self._finish_onboarding(call.message.chat.id, call.from_user.id, tzname,
                                            edit_msg_id=call.message.message_id)
                else:
                    self.db.update_user(call.from_user.id, timezone=tzname)
                    self.db.set_state(call.from_user.id, S_READY)
                    _safe_edit(self.bot, call.message.chat.id, call.message.message_id,
                               t(lang, "tz_updated"))
                    self._send_settings(call.message.chat.id, call.from_user.id)
                return

            # ---------- onboarding skip ----------
            if data == "onboard:skip":
                self._handle_skip(call.message.chat.id, call.from_user.id)
                return

            # ---------- menu navigation ----------
            if data == "menu:home":
                _safe_edit(self.bot, call.message.chat.id, call.message.message_id,
                           t(lang, "main_menu_title"), reply_markup=main_menu(lang))
                return

            if data == "ui:close":
                try:
                    self.bot.delete_message(call.message.chat.id, call.message.message_id)
                except ApiException:
                    pass
                return

            if data == "menu:quote":
                self._send_quote(call.message.chat.id, call.from_user.id,
                                 edit_msg_id=call.message.message_id)
                return
            if data == "menu:advice":
                self._send_advice(call.message.chat.id, call.from_user.id,
                                  edit_msg_id=call.message.message_id)
                return
            if data == "menu:challenge":
                self._send_challenge(call.message.chat.id, call.from_user.id,
                                     edit_msg_id=call.message.message_id)
                return
            if data == "menu:compliment":
                self._send_compliment(call.message.chat.id, call.from_user.id,
                                      edit_msg_id=call.message.message_id)
                return
            if data == "menu:milestone":
                self._send_milestone(call.message.chat.id, call.from_user.id,
                                     edit_msg_id=call.message.message_id)
                return
            if data == "menu:countdown":
                self._send_countdown(call.message.chat.id, call.from_user.id,
                                     edit_msg_id=call.message.message_id)
                return
            if data == "menu:mood":
                self._send_mood_prompt(call.message.chat.id, call.from_user.id,
                                       edit_msg_id=call.message.message_id)
                return
            if data == "menu:lovescore":
                self._send_love_score(call.message.chat.id, call.from_user.id,
                                      edit_msg_id=call.message.message_id)
                return
            if data == "menu:settings":
                self._send_settings(call.message.chat.id, call.from_user.id,
                                    edit_msg_id=call.message.message_id)
                return
            if data == "menu:help":
                _safe_edit(self.bot, call.message.chat.id, call.message.message_id,
                           t(lang, "help_text"),
                           reply_markup=back_to_menu_keyboard(lang))
                return

            # ---------- mood ----------
            if data.startswith("mood:log:"):
                mood_id = data.split(":", 2)[2]
                self.db.log_mood(call.from_user.id, mood_id)
                self._add_points(call.from_user.id, 5)
                _safe_edit(self.bot, call.message.chat.id, call.message.message_id,
                           t(lang, "mood_recorded", mood=mood_label(mood_id, lang), points=5),
                           reply_markup=back_to_menu_keyboard(lang))
                return

            # ---------- love score check-in ----------
            if data == "score:checkin":
                self._handle_checkin(call.message.chat.id, call.from_user.id,
                                     edit_msg_id=call.message.message_id)
                return

            # ---------- settings ----------
            if data == "settings:lang":
                _safe_edit(self.bot, call.message.chat.id, call.message.message_id,
                           t(lang, "generic_pick_language"),
                           reply_markup=language_keyboard(prefix="lang_set"))
                return

            if data == "settings:names":
                self.db.set_state(call.from_user.id, S_SET_USER_NAME)
                _safe_edit(self.bot, call.message.chat.id, call.message.message_id,
                           t(lang, "names_update_user"))
                return

            if data == "settings:dates":
                _safe_edit(self.bot, call.message.chat.id, call.message.message_id,
                           t(lang, "dates_pick"), reply_markup=dates_keyboard(lang))
                return

            if data == "settings:time":
                self.db.set_state(call.from_user.id, S_SET_TIME)
                _safe_edit(self.bot, call.message.chat.id, call.message.message_id,
                           t(lang, "ask_daily_time"),
                           reply_markup=time_keyboard(lang))
                return

            if data == "settings:tz":
                self.db.set_state(call.from_user.id, S_SET_TZ)
                _safe_edit(self.bot, call.message.chat.id, call.message.message_id,
                           t(lang, "ask_timezone"),
                           reply_markup=timezone_keyboard(lang))
                return

            if data == "settings:toggle":
                enabled = not bool(user["daily_enabled"])
                self.db.update_user(call.from_user.id, daily_enabled=1 if enabled else 0)
                msg_text = t(lang, "daily_toggled_on" if enabled else "daily_toggled_off")
                _safe_edit(self.bot, call.message.chat.id, call.message.message_id,
                           msg_text)
                self._send_settings(call.message.chat.id, call.from_user.id)
                return

            if data == "settings:reset":
                for cat in ("quotes", "advice", "challenges", "compliments"):
                    self.db.reset_category(call.from_user.id, cat)
                _safe_edit(self.bot, call.message.chat.id, call.message.message_id,
                           t(lang, "quotes_reset"))
                self._send_settings(call.message.chat.id, call.from_user.id)
                return

            if data == "settings:delete":
                _safe_edit(self.bot, call.message.chat.id, call.message.message_id,
                           t(lang, "confirm_delete"),
                           reply_markup=confirm_delete_keyboard(lang))
                return

            if data == "settings:events":
                self._send_events(call.message.chat.id, call.from_user.id,
                                  edit_msg_id=call.message.message_id)
                return

            # ---------- dates submenu ----------
            if data == "dates:start":
                self.db.set_state(call.from_user.id, S_SET_START_DATE)
                _safe_edit(self.bot, call.message.chat.id, call.message.message_id,
                           t(lang, "ask_start_date"))
                return

            if data == "dates:user_bday":
                self.db.set_state(call.from_user.id, S_SET_USER_BDAY)
                _safe_edit(self.bot, call.message.chat.id, call.message.message_id,
                           t(lang, "ask_user_birthday"))
                return

            if data == "dates:partner_bday":
                self.db.set_state(call.from_user.id, S_SET_PARTNER_BDAY)
                _safe_edit(self.bot, call.message.chat.id, call.message.message_id,
                           t(lang, "ask_partner_birthday"))
                return

            # ---------- custom events ----------
            if data == "events:add":
                self.db.set_state(call.from_user.id, S_EVENT_TITLE)
                _safe_edit(self.bot, call.message.chat.id, call.message.message_id,
                           t(lang, "add_event_ask_title"))
                return

            if data.startswith("events:delete:"):
                mid = int(data.split(":", 2)[2])
                self.db.delete_custom_milestone(call.from_user.id, mid)
                self._send_events(call.message.chat.id, call.from_user.id,
                                  edit_msg_id=call.message.message_id)
                return

            # ---------- account deletion ----------
            if data == "delete:confirm":
                with self.db.cursor() as c:
                    c.execute("DELETE FROM seen_items WHERE user_id = ?", (call.from_user.id,))
                    c.execute("DELETE FROM moods WHERE user_id = ?", (call.from_user.id,))
                    c.execute("DELETE FROM custom_milestones WHERE user_id = ?", (call.from_user.id,))
                    c.execute("DELETE FROM users WHERE user_id = ?", (call.from_user.id,))
                _safe_edit(self.bot, call.message.chat.id, call.message.message_id,
                           t(lang, "data_deleted"))
                return

        except Exception as exc:  # noqa: BLE001
            logger.exception("Callback error: %s", exc)

    # =====================================================================
    # onboarding helpers
    # =====================================================================

    def _handle_skip(self, chat_id: int, user_id: int) -> None:
        user = self.db.get_user(user_id)
        if not user:
            return
        lang = _user_lang(user)
        state = user["state"]
        if state == S_USER_BDAY:
            self._advance_from_user_bday(chat_id, user_id, lang)
        elif state == S_PARTNER_BDAY:
            self._advance_from_partner_bday(chat_id, user_id, lang)

    def _advance_from_user_bday(self, chat_id: int, user_id: int, lang: str) -> None:
        self.db.set_state(user_id, S_PARTNER_BDAY)
        self.bot.send_message(chat_id, t(lang, "ask_partner_birthday"),
                              reply_markup=skip_keyboard(lang))

    def _advance_from_partner_bday(self, chat_id: int, user_id: int, lang: str) -> None:
        self.db.set_state(user_id, S_TIME)
        self.bot.send_message(chat_id, t(lang, "ask_daily_time"),
                              reply_markup=time_keyboard(lang))

    def _finish_onboarding(self, chat_id: int, user_id: int, tz_value: str,
                           edit_msg_id: int | None = None) -> None:
        self.db.update_user(user_id, timezone=tz_value)
        self.db.set_state(user_id, S_READY)
        user = self.db.get_user(user_id) or {}
        lang = _user_lang(user)
        msg = t(
            lang, "onboarding_done",
            name=user.get("user_name") or "",
            user_name=user.get("user_name") or "—",
            partner_name=user.get("partner_name") or "—",
            start_date=user.get("relationship_start") or "—",
            time=f"{user['daily_hour']:02d}:{user['daily_minute']:02d}",
            tz=user.get("timezone") or "UTC",
        )
        if edit_msg_id:
            _safe_edit(self.bot, chat_id, edit_msg_id, msg)
        else:
            self.bot.send_message(chat_id, msg)
        self._send_main_menu(chat_id, user_id)

    # =====================================================================
    # main menu
    # =====================================================================

    def _send_main_menu(self, chat_id: int, user_id: int,
                        edit_msg_id: int | None = None) -> None:
        user = self.db.get_user(user_id) or {}
        lang = _user_lang(user)
        text = t(lang, "main_menu_title")
        kb = main_menu(lang)
        if edit_msg_id:
            _safe_edit(self.bot, chat_id, edit_msg_id, text, reply_markup=kb)
        else:
            self.bot.send_message(chat_id, text, reply_markup=kb)

    # =====================================================================
    # features
    # =====================================================================

    def _require_ready(self, chat_id: int, user_id: int) -> dict[str, Any] | None:
        user = self.db.get_user(user_id)
        if not user or user["state"] != S_READY:
            self._cmd_start(types.Message(
                message_id=0,
                from_user=types.User(id=user_id, is_bot=False, first_name=""),
                date=0,
                chat=types.Chat(id=chat_id, type="private"),
                content_type="text", options={}, json_string="",
            ))
            return None
        return user

    def _send_quote(self, chat_id: int, user_id: int, edit_msg_id: int | None = None) -> None:
        user = self.db.get_user(user_id)
        if not user:
            return self._cmd_start_fake(chat_id, user_id)
        lang = _user_lang(user)
        _, quote = pick_unseen(self.db, user_id, "quotes", lang)
        seen, total = progress(self.db, user_id, "quotes", lang)
        text = (
            f"{t(lang, 'daily_quote_label')}\n\n"
            f"_{quote}_\n\n"
            f"📚 {format_number(seen, lang)}/{format_number(total, lang)}"
        )
        self._send_or_edit(chat_id, edit_msg_id, text, quote_again_keyboard(lang))

    def _send_advice(self, chat_id: int, user_id: int, edit_msg_id: int | None = None) -> None:
        user = self.db.get_user(user_id)
        if not user:
            return self._cmd_start_fake(chat_id, user_id)
        lang = _user_lang(user)
        _, advice = pick_unseen(self.db, user_id, "advice", lang)
        text = f"{t(lang, 'daily_advice_label')}\n\n_{advice}_"
        self._send_or_edit(chat_id, edit_msg_id, text, advice_again_keyboard(lang))

    def _send_challenge(self, chat_id: int, user_id: int, edit_msg_id: int | None = None) -> None:
        user = self.db.get_user(user_id)
        if not user:
            return self._cmd_start_fake(chat_id, user_id)
        lang = _user_lang(user)
        _, ch = pick_unseen(self.db, user_id, "challenges", lang)
        text = f"{t(lang, 'daily_challenge_label')}\n\n_{ch}_"
        self._send_or_edit(chat_id, edit_msg_id, text, challenge_again_keyboard(lang))

    def _send_compliment(self, chat_id: int, user_id: int, edit_msg_id: int | None = None) -> None:
        user = self.db.get_user(user_id)
        if not user:
            return self._cmd_start_fake(chat_id, user_id)
        lang = _user_lang(user)
        _, c = pick_unseen(self.db, user_id, "compliments", lang)
        partner = user.get("partner_name") or ("پارتنرت" if lang == "fa" else "your partner")
        text = t(lang, "compliment_prompt", partner=partner, text=c)
        self._send_or_edit(chat_id, edit_msg_id, text, compliment_again_keyboard(lang))

    def _send_milestone(self, chat_id: int, user_id: int, edit_msg_id: int | None = None) -> None:
        user = self.db.get_user(user_id)
        if not user or not user.get("relationship_start"):
            return self._cmd_start_fake(chat_id, user_id)
        lang = _user_lang(user)
        days = days_between(user["relationship_start"])
        nm = next_milestone(days)
        body = t(
            lang, "milestone_body",
            days=format_number(days, lang),
            partner=user.get("partner_name") or "—",
            humanised=humanise_duration(days, lang),
            next_m=format_number(nm, lang),
            remaining=format_number(nm - days, lang),
        )
        header = t(lang, "milestone_title")
        special = ""
        if is_special_milestone(days):
            special = "\n\n" + t(lang, "milestone_special", emoji="🎉🎊🥳✨")
        text = f"{header}\n\n{body}{special}"
        self._send_or_edit(chat_id, edit_msg_id, text, back_to_menu_keyboard(lang))

    def _send_countdown(self, chat_id: int, user_id: int, edit_msg_id: int | None = None) -> None:
        user = self.db.get_user(user_id)
        if not user:
            return self._cmd_start_fake(chat_id, user_id)
        lang = _user_lang(user)
        today = date.today()
        lines = [t(lang, "countdown_title")]

        if user.get("relationship_start"):
            start = datetime.strptime(user["relationship_start"], "%Y-%m-%d").date()
            anniv = start.replace(year=today.year)
            if anniv < today:
                anniv = anniv.replace(year=today.year + 1)
            days = (anniv - today).days
            lines.append("")
            lines.append(t(lang, "countdown_next_anniv",
                           days=format_number(days, lang),
                           date=anniv.isoformat()))

            nm = next_milestone(days_between(user["relationship_start"]))
            remaining = nm - days_between(user["relationship_start"])
            lines.append(t(lang, "countdown_next_milestone",
                           m=format_number(nm, lang),
                           days=format_number(remaining, lang)))

        for field, key in (
            ("user_birthday", "countdown_next_user_bday"),
            ("partner_birthday", "countdown_next_partner_bday"),
        ):
            md = user.get(field)
            if not md:
                continue
            try:
                m, d = (int(p) for p in md.split("-"))
            except (ValueError, AttributeError):
                continue
            target = date(today.year, m, d)
            if target < today:
                target = date(today.year + 1, m, d)
            days = (target - today).days
            lines.append(t(lang, key,
                           days=format_number(days, lang),
                           date=target.isoformat()))

        events = self.db.list_custom_milestones(user_id)
        if events:
            lines.append("")
            lines.append(t(lang, "countdown_custom_header"))
            for ev in events:
                target = datetime.strptime(ev["target"], "%Y-%m-%d").date()
                days = (target - today).days
                if days < 0:
                    continue
                lines.append(t(lang, "countdown_custom_item",
                               title=ev["title"],
                               days=format_number(days, lang),
                               date=ev["target"]))

        text = "\n".join(lines)
        self._send_or_edit(chat_id, edit_msg_id, text, back_to_menu_keyboard(lang))

    def _send_mood_prompt(self, chat_id: int, user_id: int, edit_msg_id: int | None = None) -> None:
        user = self.db.get_user(user_id)
        if not user:
            return self._cmd_start_fake(chat_id, user_id)
        lang = _user_lang(user)
        recent = self.db.recent_moods(user_id, limit=5)
        lines = [t(lang, "mood_prompt")]
        if recent:
            lines += ["", t(lang, "mood_history_title")]
            for m in recent:
                stamp = m["logged_at"].split("T")[0]
                lines.append(f"• {stamp} — {mood_label(m['mood'], lang)}")
        text = "\n".join(lines)
        self._send_or_edit(chat_id, edit_msg_id, text, mood_keyboard(lang))

    def _send_love_score(self, chat_id: int, user_id: int, edit_msg_id: int | None = None) -> None:
        user = self.db.get_user(user_id) or {}
        lang = _user_lang(user)
        text = t(
            lang, "love_score_body",
            score=format_number(int(user.get("love_score", 0)), lang),
            streak=format_number(int(user.get("streak", 0)), lang),
        )
        self._send_or_edit(chat_id, edit_msg_id, text, love_score_keyboard(lang))

    def _handle_checkin(self, chat_id: int, user_id: int, edit_msg_id: int | None = None) -> None:
        user = self.db.get_user(user_id) or {}
        lang = _user_lang(user)
        today_s = date.today().isoformat()
        last = user.get("last_checkin")
        if last == today_s:
            _safe_edit(self.bot, chat_id, edit_msg_id, t(lang, "checkin_already"),
                       reply_markup=love_score_keyboard(lang))
            return

        # Streak logic.
        new_streak = int(user.get("streak") or 0)
        if last:
            try:
                last_date = datetime.strptime(last, "%Y-%m-%d").date()
                if (date.today() - last_date).days == 1:
                    new_streak += 1
                else:
                    new_streak = 1
            except ValueError:
                new_streak = 1
        else:
            new_streak = 1

        points = 10 + min(new_streak, 10)  # bonus up to +10 for long streaks
        new_score = int(user.get("love_score") or 0) + points
        self.db.update_user(
            user_id,
            love_score=new_score,
            streak=new_streak,
            last_checkin=today_s,
        )
        msg = t(lang, "checkin_done",
                points=format_number(points, lang),
                streak=format_number(new_streak, lang))
        _safe_edit(self.bot, chat_id, edit_msg_id, msg,
                   reply_markup=love_score_keyboard(lang))

    def _add_points(self, user_id: int, points: int) -> None:
        user = self.db.get_user(user_id) or {}
        new_score = int(user.get("love_score") or 0) + points
        self.db.update_user(user_id, love_score=new_score)

    def _send_settings(self, chat_id: int, user_id: int,
                       edit_msg_id: int | None = None) -> None:
        user = self.db.get_user(user_id) or {}
        lang = _user_lang(user)
        text = t(lang, "settings_title") + self._settings_summary(user, lang)
        self._send_or_edit(chat_id, edit_msg_id, text, settings_keyboard(lang))

    def _settings_summary(self, user: dict[str, Any], lang: str) -> str:
        rows = [
            f"👤 {user.get('user_name') or '—'}",
            f"💞 {user.get('partner_name') or '—'}",
            f"📅 {user.get('relationship_start') or '—'}",
            f"🎂 {user.get('user_birthday') or '—'}  /  🎁 {user.get('partner_birthday') or '—'}",
            f"⏰ {int(user.get('daily_hour') or 9):02d}:{int(user.get('daily_minute') or 0):02d} ({user.get('timezone') or 'UTC'})",
            f"🔔 {'on' if user.get('daily_enabled') else 'off'}",
        ]
        return "\n\n" + "\n".join(rows)

    def _send_events(self, chat_id: int, user_id: int,
                     edit_msg_id: int | None = None) -> None:
        user = self.db.get_user(user_id) or {}
        lang = _user_lang(user)
        events = self.db.list_custom_milestones(user_id)
        body = t(lang, "custom_events_title")
        if not events:
            body += "\n\n" + t(lang, "event_empty")
        kb = events_list_keyboard(lang, events)
        self._send_or_edit(chat_id, edit_msg_id, body, kb)

    def _cmd_start_fake(self, chat_id: int, user_id: int) -> None:
        """When a user calls a feature before onboarding — restart onboarding."""
        self.db.upsert_user(user_id, chat_id)
        self.db.set_state(user_id, S_PICK_LANG)
        self.bot.send_message(
            chat_id,
            t("fa", "welcome_pick_language"),
            reply_markup=language_keyboard(prefix="lang"),
        )

    def _send_or_edit(self, chat_id: int, edit_msg_id: int | None,
                      text: str, reply_markup) -> None:
        if edit_msg_id:
            _safe_edit(self.bot, chat_id, edit_msg_id, text, reply_markup)
        else:
            self.bot.send_message(chat_id, text, reply_markup=reply_markup,
                                  parse_mode="Markdown",
                                  disable_web_page_preview=True)

    # =====================================================================
    # daily broadcast (called by scheduler)
    # =====================================================================

    def send_daily_to(self, user: dict[str, Any]) -> None:
        """Send the daily love message to one user."""
        if not user.get("relationship_start"):
            return
        chat_id = int(user["chat_id"])
        user_id = int(user["user_id"])
        lang = _user_lang(user)

        days = days_between(user["relationship_start"])
        partner = user.get("partner_name") or ("پارتنرت" if lang == "fa" else "your partner")
        greeting = random.choice(greetings.greeting(lang))
        closing = random.choice(greetings.closing(lang))

        _, quote = pick_unseen(self.db, user_id, "quotes", lang)
        _, advice = pick_unseen(self.db, user_id, "advice", lang)

        special_block = ""
        if is_special_milestone(days):
            special_block = "\n\n" + t(lang, "milestone_special",
                                       emoji="🎉🎊🥳✨")

        text = (
            t(lang, "daily_header",
              greeting=greeting,
              days=format_number(days, lang),
              partner=partner)
            + special_block
            + f"\n\n{t(lang, 'daily_quote_label')}\n_{quote}_"
            + f"\n\n{t(lang, 'daily_advice_label')}\n_{advice}_"
            + f"\n\n{closing}"
        )
        try:
            self.bot.send_message(chat_id, text, parse_mode="Markdown",
                                  disable_web_page_preview=True,
                                  reply_markup=close_keyboard(lang))
        except ApiException as exc:
            logger.warning("Daily send failed for %s: %s", user_id, exc)

    def check_and_send_birthdays(self) -> None:
        """If today is a user's or their partner's birthday, send a greeting."""
        for user in self.db.list_active_users():
            lang = _user_lang(user)
            tz = get_tz(user.get("timezone") or "UTC")
            today = datetime.now(tz).date()
            md = f"{today.month:02d}-{today.day:02d}"

            if user.get("user_birthday") == md:
                try:
                    self.bot.send_message(
                        int(user["chat_id"]),
                        t(lang, "birthday_user", name=user.get("user_name") or ""),
                        parse_mode="Markdown",
                    )
                except ApiException as exc:
                    logger.warning("Birthday-user send failed: %s", exc)

            if user.get("partner_birthday") == md:
                try:
                    self.bot.send_message(
                        int(user["chat_id"]),
                        t(lang, "birthday_partner",
                          partner=user.get("partner_name") or ""),
                        parse_mode="Markdown",
                    )
                except ApiException as exc:
                    logger.warning("Birthday-partner send failed: %s", exc)

    # =====================================================================
    # bot lifecycle
    # =====================================================================

    def run(self) -> None:
        try:
            self.bot.remove_webhook()
        except ApiException:
            pass
        logger.info("LoveBot polling started.")
        self.bot.infinity_polling(
            timeout=20,
            long_polling_timeout=20,
            skip_pending=True,
            restart_on_change=False,
        )
