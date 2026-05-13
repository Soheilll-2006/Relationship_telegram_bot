"""Inline & reply keyboards for the bot UI.

Callback data uses the convention ``"<scope>:<action>[:<param>]"`` so handlers
can dispatch with a simple ``data.split(":")``.
"""

from __future__ import annotations

from telebot import types

from .i18n import (
    COMMON_TIMEZONES,
    LANGUAGE_LABELS,
    MOOD_OPTIONS,
    SUPPORTED_LANGUAGES,
    t,
)
from .utils import chunked


# ---------------------------------------------------------- onboarding pickers


def language_keyboard(prefix: str = "lang") -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        *[
            types.InlineKeyboardButton(LANGUAGE_LABELS[code], callback_data=f"{prefix}:{code}")
            for code in SUPPORTED_LANGUAGES
        ]
    )
    return kb


def time_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    """Preset times every 2 hours, plus a 'manual' hint button."""
    kb = types.InlineKeyboardMarkup(row_width=4)
    times = ["07:00", "08:00", "09:00", "10:00",
            "12:00", "18:00", "20:00", "21:00"]
    kb.add(
        *[types.InlineKeyboardButton(tm, callback_data=f"time:set:{tm}") for tm in times]
    )
    return kb


def timezone_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        *[types.InlineKeyboardButton(tz, callback_data=f"tz:set:{tz}") for tz in COMMON_TIMEZONES]
    )
    return kb


def skip_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(t(lang, "btn_skip"), callback_data="onboard:skip"))
    return kb


# ---------------------------------------------------------------- main menu


def main_menu(lang: str) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton(t(lang, "btn_quote"), callback_data="menu:quote"),
        types.InlineKeyboardButton(t(lang, "btn_advice"), callback_data="menu:advice"),
    )
    kb.add(
        types.InlineKeyboardButton(t(lang, "btn_milestone"), callback_data="menu:milestone"),
        types.InlineKeyboardButton(t(lang, "btn_challenge"), callback_data="menu:challenge"),
    )
    kb.add(
        types.InlineKeyboardButton(t(lang, "btn_compliment"), callback_data="menu:compliment"),
        types.InlineKeyboardButton(t(lang, "btn_mood"), callback_data="menu:mood"),
    )
    kb.add(
        types.InlineKeyboardButton(t(lang, "btn_love_score"), callback_data="menu:lovescore"),
        types.InlineKeyboardButton(t(lang, "btn_countdown"), callback_data="menu:countdown"),
    )
    kb.add(
        types.InlineKeyboardButton(t(lang, "btn_settings"), callback_data="menu:settings"),
        types.InlineKeyboardButton(t(lang, "btn_help"), callback_data="menu:help"),
    )
    return kb


def close_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(t(lang, "btn_close"), callback_data="ui:close"))
    return kb


def back_to_menu_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton(t(lang, "btn_back"), callback_data="menu:home"),
        types.InlineKeyboardButton(t(lang, "btn_close"), callback_data="ui:close"),
    )
    return kb


# ----------------------------------------------------------------- features


def quote_again_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🔁 " + t(lang, "btn_quote"), callback_data="menu:quote"),
        types.InlineKeyboardButton(t(lang, "btn_advice"), callback_data="menu:advice"),
    )
    kb.add(types.InlineKeyboardButton(t(lang, "btn_back"), callback_data="menu:home"))
    return kb


def advice_again_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🔁 " + t(lang, "btn_advice"), callback_data="menu:advice"),
        types.InlineKeyboardButton(t(lang, "btn_quote"), callback_data="menu:quote"),
    )
    kb.add(types.InlineKeyboardButton(t(lang, "btn_back"), callback_data="menu:home"))
    return kb


def challenge_again_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🔁 " + t(lang, "btn_challenge"), callback_data="menu:challenge"),
        types.InlineKeyboardButton(t(lang, "btn_compliment"), callback_data="menu:compliment"),
    )
    kb.add(types.InlineKeyboardButton(t(lang, "btn_back"), callback_data="menu:home"))
    return kb


def compliment_again_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🔁 " + t(lang, "btn_compliment"), callback_data="menu:compliment"),
        types.InlineKeyboardButton(t(lang, "btn_quote"), callback_data="menu:quote"),
    )
    kb.add(types.InlineKeyboardButton(t(lang, "btn_back"), callback_data="menu:home"))
    return kb


def mood_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(labels[lang], callback_data=f"mood:log:{mid}")
        for mid, labels in MOOD_OPTIONS
    ]
    for row in chunked(buttons, 2):
        kb.row(*row)
    kb.add(types.InlineKeyboardButton(t(lang, "btn_back"), callback_data="menu:home"))
    return kb


def love_score_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton(t(lang, "btn_checkin"), callback_data="score:checkin"))
    kb.add(types.InlineKeyboardButton(t(lang, "btn_back"), callback_data="menu:home"))
    return kb


def settings_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton(t(lang, "btn_change_language"), callback_data="settings:lang"),
        types.InlineKeyboardButton(t(lang, "btn_change_names"), callback_data="settings:names"),
    )
    kb.add(
        types.InlineKeyboardButton(t(lang, "btn_change_dates"), callback_data="settings:dates"),
        types.InlineKeyboardButton(t(lang, "btn_change_time"), callback_data="settings:time"),
    )
    kb.add(
        types.InlineKeyboardButton(t(lang, "btn_change_tz"), callback_data="settings:tz"),
        types.InlineKeyboardButton(t(lang, "btn_toggle_daily"), callback_data="settings:toggle"),
    )
    kb.add(
        types.InlineKeyboardButton(t(lang, "btn_custom_events"), callback_data="settings:events"),
        types.InlineKeyboardButton(t(lang, "btn_reset_quotes"), callback_data="settings:reset"),
    )
    kb.add(types.InlineKeyboardButton(t(lang, "btn_delete_data"), callback_data="settings:delete"))
    kb.add(types.InlineKeyboardButton(t(lang, "btn_back"), callback_data="menu:home"))
    return kb


def dates_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton(t(lang, "btn_date_start"), callback_data="dates:start"))
    kb.add(types.InlineKeyboardButton(t(lang, "btn_date_user_bday"), callback_data="dates:user_bday"))
    kb.add(types.InlineKeyboardButton(t(lang, "btn_date_partner_bday"), callback_data="dates:partner_bday"))
    kb.add(types.InlineKeyboardButton(t(lang, "btn_back"), callback_data="menu:settings"))
    return kb


def confirm_delete_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton(t(lang, "btn_yes_delete"), callback_data="delete:confirm"),
        types.InlineKeyboardButton(t(lang, "btn_cancel"), callback_data="menu:settings"),
    )
    return kb


def events_list_keyboard(lang: str, items: list[dict]) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=1)
    for it in items:
        kb.add(
            types.InlineKeyboardButton(
                f"🗑 {it['title']} ({it['target']})",
                callback_data=f"events:delete:{it['id']}",
            )
        )
    kb.add(types.InlineKeyboardButton(t(lang, "btn_add_event"), callback_data="events:add"))
    kb.add(types.InlineKeyboardButton(t(lang, "btn_back"), callback_data="menu:settings"))
    return kb
