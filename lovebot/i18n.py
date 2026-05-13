"""Tiny i18n layer: language-keyed string tables + ``t(lang, key, **kw)``.

All user-facing UI strings live here. Persian (``fa``) is the primary
language, English (``en``) is fully supported.
"""

from __future__ import annotations

from typing import Any

SUPPORTED_LANGUAGES: tuple[str, ...] = ("fa", "en")

# Display names of each language (always shown in the language itself).
LANGUAGE_LABELS: dict[str, str] = {
    "fa": "🇮🇷 فارسی",
    "en": "🇬🇧 English",
}


STRINGS: dict[str, dict[str, str]] = {
    # ---------------------------------------------------------- welcome / start
    "welcome_pick_language": {
        "fa": (
            "💕 سلام و خوش اومدی به *LoveBot* — همراه روزانه‌ی رابطه‌ت!\n\n"
            "اول از همه، زبان مورد علاقه‌ت رو انتخاب کن:"
        ),
        "en": (
            "💕 Hi, and welcome to *LoveBot* — your daily relationship companion!\n\n"
            "First, pick your preferred language:"
        ),
    },
    "welcome_already": {
        "fa": (
            "🌹 سلام {name} عزیز! خوشحالم که برگشتی.\n"
            "همه چی آماده‌ست — از منوی پایین یا /menu استفاده کن. 💖"
        ),
        "en": (
            "🌹 Hi {name}! Great to see you again.\n"
            "Everything's set — use the menu below or /menu. 💖"
        ),
    },
    # --------------------------------------------------------------- onboarding
    "ask_user_name": {
        "fa": "🌸 اسمت چیه؟ (همون چیزی که دوست داری ربات صدات کنه)",
        "en": "🌸 What's your name? (How would you like me to call you?)",
    },
    "ask_partner_name": {
        "fa": "💝 حالا اسم پارتنرت چیه؟",
        "en": "💝 And what's your partner's name?",
    },
    "ask_start_date": {
        "fa": (
            "📅 تاریخ شروع رابطه‌تون رو وارد کن.\n"
            "فرمت: *YYYY-MM-DD* (مثلاً `2024-06-22`)"
        ),
        "en": (
            "📅 When did your relationship start?\n"
            "Format: *YYYY-MM-DD* (e.g. `2024-06-22`)"
        ),
    },
    "ask_user_birthday": {
        "fa": (
            "🎂 تاریخ تولد *خودت*؟\n"
            "فرمت: *MM-DD* (مثلاً `09-22` برای ۲۲ سپتامبر).\n"
            "اگر نمی‌خوای، بنویس «رد» یا /skip."
        ),
        "en": (
            "🎂 What's *your* birthday?\n"
            "Format: *MM-DD* (e.g. `09-22` for September 22).\n"
            "Type `skip` or /skip to leave it empty."
        ),
    },
    "ask_partner_birthday": {
        "fa": (
            "🎁 تاریخ تولد *پارتنرت*؟\n"
            "فرمت: *MM-DD* (مثلاً `11-05`).\n"
            "اگر نمی‌خوای، بنویس «رد» یا /skip."
        ),
        "en": (
            "🎁 What's *your partner's* birthday?\n"
            "Format: *MM-DD* (e.g. `11-05`).\n"
            "Type `skip` or /skip to leave it empty."
        ),
    },
    "ask_daily_time": {
        "fa": (
            "⏰ هر روز ساعت چند پیام عاشقانه برات بفرستم؟\n"
            "یکی از گزینه‌های پایین رو انتخاب کن یا خودت بنویس (مثلاً `08:30`)."
        ),
        "en": (
            "⏰ What time of day should I send you your daily love note?\n"
            "Pick one below or type your own (e.g. `08:30`)."
        ),
    },
    "ask_timezone": {
        "fa": (
            "🌍 منطقه زمانیت کجاست؟\n"
            "از لیست انتخاب کن یا اسمش رو بنویس (مثلاً `Europe/London`)."
        ),
        "en": (
            "🌍 What's your timezone?\n"
            "Pick from the list or type the name (e.g. `Europe/London`)."
        ),
    },
    "onboarding_done": {
        "fa": (
            "🎉 تمومه {name} جان! همه چی ست شد.\n\n"
            "👤 تو: *{user_name}*\n"
            "💞 پارتنر: *{partner_name}*\n"
            "📅 شروع رابطه: *{start_date}*\n"
            "⏰ پیام روزانه: *{time}* به وقت *{tz}*\n\n"
            "از منوی پایین یا /menu استفاده کن. هر وقت خواستی تنظیمات رو از /settings تغییر بده. 💖"
        ),
        "en": (
            "🎉 All done, {name}! Everything is set.\n\n"
            "👤 You: *{user_name}*\n"
            "💞 Partner: *{partner_name}*\n"
            "📅 Started: *{start_date}*\n"
            "⏰ Daily note: *{time}* in *{tz}*\n\n"
            "Use the menu below or /menu. Tweak anything from /settings. 💖"
        ),
    },
    "onboarding_done_group_hint": {
        "fa": (
            "💡 *نکته:* پیام‌های روزانه پیش‌فرض به همین چت خصوصی میان.\n"
            "اگه می‌خوای به جاش به یه گروه مشترک با پارتنرت برن:\n\n"
            "1️⃣ ربات (@{bot}) رو به گروهتون اضافه کن.\n"
            "2️⃣ توی همون گروه دستور `/linkhere` رو بزن.\n\n"
            "هر وقت بخوای می‌تونی با `/unlinkhere` برگردونیش به پی‌وی."
        ),
        "en": (
            "💡 *Tip:* daily messages go to this private chat by default.\n"
            "Want them to go to a shared group with your partner instead?\n\n"
            "1️⃣ Add @{bot} to your group.\n"
            "2️⃣ In that group, send `/linkhere`.\n\n"
            "You can revert anytime with `/unlinkhere`."
        ),
    },
    # ----------------------------------------------------------- group linking
    "link_not_onboarded": {
        "fa": (
            "👋 سلام! اول لازمه توی پی‌وی من `/start` بزنی و راه‌اندازی رو "
            "کامل کنی، بعد می‌تونی توی این گروه `/linkhere` بزنی."
        ),
        "en": (
            "👋 Hi! Please /start me in private first and finish setup, "
            "then come back here and send /linkhere."
        ),
    },
    "link_must_be_group": {
        "fa": "ℹ️ این دستور رو *داخل گروهی* که می‌خوای پیام‌ها بهش بره بزن.",
        "en": "ℹ️ Send this command *inside the group* you want messages delivered to.",
    },
    "link_already": {
        "fa": "ℹ️ پیام‌های روزانه‌ی {name} از قبل به این گروه می‌اومد.",
        "en": "ℹ️ {name}'s daily messages already come to this group.",
    },
    "link_success": {
        "fa": (
            "✅ از این به بعد پیام‌های روزانه‌ی *{name}* به این گروه می‌رسه! 💖\n"
            "برای برگردوندنش به پی‌وی: `/unlinkhere`"
        ),
        "en": (
            "✅ From now on, *{name}*'s daily messages will be delivered here! 💖\n"
            "Revert anytime with `/unlinkhere`."
        ),
    },
    "unlink_success": {
        "fa": "🔄 برگشت به پی‌وی. پیام‌های روزانه دوباره مستقیم برای {name} می‌رسه.",
        "en": "🔄 Reverted to private chat. {name}'s daily messages will arrive privately again.",
    },
    "unlink_nothing": {
        "fa": "ℹ️ چیزی برای unlink کردن نیست — پیام‌ها از همون اول به پی‌وی می‌رسه.",
        "en": "ℹ️ Nothing to unlink — messages were already going to your private chat.",
    },
    "bot_added_to_group": {
        "fa": (
            "👋 سلام! من *LoveBot* هستم 💕\n"
            "اگه می‌خوای پیام‌های روزانه‌ت اینجا برسه، توی پی‌وی من `/start` بزن، "
            "بعد توی همین گروه `/linkhere` رو بزن."
        ),
        "en": (
            "👋 Hi, I'm *LoveBot* 💕\n"
            "If you'd like your daily messages here, /start me in private first, "
            "then send /linkhere in this group."
        ),
    },
    "delivery_private": {"fa": "پی‌وی", "en": "private"},
    "delivery_group": {"fa": "گروه {id}", "en": "group {id}"},
    "settings_delivery_label": {"fa": "📨 مقصد پیام", "en": "📨 Delivery"},
    # ------------------------------------------------------------------ errors
    "err_bad_date": {
        "fa": "❌ این تاریخ معتبر نیست. دوباره با فرمت *YYYY-MM-DD* وارد کن.",
        "en": "❌ That's not a valid date. Try again as *YYYY-MM-DD*.",
    },
    "err_bad_birthday": {
        "fa": "❌ این تاریخ تولد معتبر نیست. فرمت *MM-DD* (مثل `09-22`) یا /skip.",
        "en": "❌ Invalid birthday. Use *MM-DD* (e.g. `09-22`) or /skip.",
    },
    "err_bad_time": {
        "fa": "❌ ساعت معتبر نیست. فرمت *HH:MM* (مثل `09:00`).",
        "en": "❌ Invalid time. Use *HH:MM* (e.g. `09:00`).",
    },
    "err_future_date": {
        "fa": "❌ تاریخ شروع نمی‌تونه آینده باشه!",
        "en": "❌ The start date can't be in the future!",
    },
    "err_empty": {
        "fa": "❌ خالی نمی‌تونه باشه. دوباره امتحان کن.",
        "en": "❌ It can't be empty. Try again.",
    },
    # -------------------------------------------------------------------- menu
    "main_menu_title": {
        "fa": "💖 منوی اصلی — چی می‌خوای؟",
        "en": "💖 Main menu — what would you like?",
    },
    "btn_quote": {"fa": "💝 جمله عاشقانه", "en": "💝 Love quote"},
    "btn_advice": {"fa": "💡 توصیه روز", "en": "💡 Daily advice"},
    "btn_milestone": {"fa": "📅 روزشمار", "en": "📅 Milestone"},
    "btn_challenge": {"fa": "🎯 چالش امروز", "en": "🎯 Today's challenge"},
    "btn_compliment": {"fa": "🌟 تعریف‌ای از پارتنرت", "en": "🌟 Compliment partner"},
    "btn_mood": {"fa": "😊 حال امروز", "en": "😊 Mood check-in"},
    "btn_love_score": {"fa": "❤️ امتیاز عشق", "en": "❤️ Love score"},
    "btn_countdown": {"fa": "⏳ شمارش معکوس", "en": "⏳ Countdown"},
    "btn_settings": {"fa": "⚙️ تنظیمات", "en": "⚙️ Settings"},
    "btn_help": {"fa": "❓ راهنما", "en": "❓ Help"},
    "btn_back": {"fa": "↩️ بازگشت", "en": "↩️ Back"},
    "btn_close": {"fa": "✖️ بستن", "en": "✖️ Close"},
    "btn_skip": {"fa": "رد کردن", "en": "Skip"},
    # ----------------------------------------------------------- daily message
    "daily_header": {
        "fa": (
            "{greeting}\n\n"
            "💕 امروز *روز {days}* از داستان شما با {partner} است!"
        ),
        "en": (
            "{greeting}\n\n"
            "💕 Today is *day {days}* of your story with {partner}!"
        ),
    },
    "daily_quote_label": {"fa": "💝 جمله امروز:", "en": "💝 Today's quote:"},
    "daily_advice_label": {"fa": "💡 توصیه امروز:", "en": "💡 Today's advice:"},
    "daily_challenge_label": {"fa": "🎯 چالش امروز:", "en": "🎯 Today's challenge:"},
    "daily_closing": {
        "fa": "{closing}",
        "en": "{closing}",
    },
    # -------------------------------------------------------------- milestone
    "milestone_title": {
        "fa": "📅 *روزشمار عشق*",
        "en": "📅 *Relationship milestone*",
    },
    "milestone_body": {
        "fa": (
            "💕 امروز *روز {days}* از رابطه‌ت با {partner} است.\n"
            "📆 یعنی {humanised}.\n\n"
            "⏳ تا نقطه‌ی عطف بعدی ({next_m} روز) فقط *{remaining} روز* مونده!"
        ),
        "en": (
            "💕 You're on *day {days}* with {partner}.\n"
            "📆 That's {humanised}.\n\n"
            "⏳ Only *{remaining} days* until your next milestone ({next_m} days)!"
        ),
    },
    "milestone_special": {
        "fa": "🎉 *امروز یه روز خاصه!* {emoji}",
        "en": "🎉 *Today is a milestone!* {emoji}",
    },
    # --------------------------------------------------------------- countdown
    "countdown_title": {
        "fa": "⏳ *شمارش معکوس‌ها*",
        "en": "⏳ *Countdowns*",
    },
    "countdown_next_anniv": {
        "fa": "💞 سالگرد بعدی: *{days} روز* دیگه ({date})",
        "en": "💞 Next anniversary: *{days} days* away ({date})",
    },
    "countdown_next_user_bday": {
        "fa": "🎂 تولد خودت: *{days} روز* دیگه ({date})",
        "en": "🎂 Your birthday: *{days} days* away ({date})",
    },
    "countdown_next_partner_bday": {
        "fa": "🎁 تولد پارتنر: *{days} روز* دیگه ({date})",
        "en": "🎁 Partner's birthday: *{days} days* away ({date})",
    },
    "countdown_next_milestone": {
        "fa": "✨ نقطه‌ی عطف بعدی: روز *{m}* — *{days} روز* دیگه",
        "en": "✨ Next milestone: day *{m}* — *{days} days* away",
    },
    "countdown_custom_header": {
        "fa": "📌 رویدادهای دلخواه شما:",
        "en": "📌 Your custom events:",
    },
    "countdown_custom_item": {
        "fa": "• {title} — *{days} روز* ({date})",
        "en": "• {title} — *{days} days* ({date})",
    },
    # ---------------------------------------------------------------- birthday
    "birthday_user": {
        "fa": (
            "🎂🎉 *تولدت مبارک {name}!* 🎉🎂\n\n"
            "💖 یه سال دیگه از این آدم خاص و دوست‌داشتنی گذشت.\n"
            "🌟 امیدوارم این سال، پر از لحظه‌های قشنگ و عاشقانه باشه!"
        ),
        "en": (
            "🎂🎉 *Happy birthday, {name}!* 🎉🎂\n\n"
            "💖 Another year of this beautiful, loved person.\n"
            "🌟 May this year overflow with love and joy!"
        ),
    },
    "birthday_partner": {
        "fa": (
            "🎂🎉 *تولد {partner} عزیز مبارکه!* 🎉🎂\n\n"
            "🌹 یه روز خاص برای آدم خاص زندگیت.\n"
            "💝 یادت نره امروز پارتنرت رو غافلگیر کنی!"
        ),
        "en": (
            "🎂🎉 *Happy birthday to {partner}!* 🎉🎂\n\n"
            "🌹 A special day for the special person in your life.\n"
            "💝 Don't forget to surprise them today!"
        ),
    },
    # ------------------------------------------------------------- love score
    "love_score_body": {
        "fa": (
            "❤️ *امتیاز عشق:* {score}\n"
            "🔥 *روزهای پیاپی فعال:* {streak}\n\n"
            "هر روز که با ربات تعامل کنی، یا چالش رو انجام بدی، امتیازت بیشتر می‌شه! 💪"
        ),
        "en": (
            "❤️ *Love score:* {score}\n"
            "🔥 *Active streak:* {streak} days\n\n"
            "Earn more points by checking in daily and completing challenges! 💪"
        ),
    },
    "btn_checkin": {"fa": "✅ امروز چک‌این", "en": "✅ Check in today"},
    "checkin_done": {
        "fa": "🎉 ثبت شد! +{points} امتیاز. استریک: *{streak}* روز 🔥",
        "en": "🎉 Logged! +{points} points. Streak: *{streak}* days 🔥",
    },
    "checkin_already": {
        "fa": "💡 امروز قبلاً چک‌این کردی! فردا یادت نره.",
        "en": "💡 You've already checked in today! See you tomorrow.",
    },
    # -------------------------------------------------------------------- mood
    "mood_prompt": {
        "fa": "😊 امروز چه حسی نسبت به رابطه‌ت داری؟",
        "en": "😊 How do you feel about your relationship today?",
    },
    "mood_recorded": {
        "fa": "💖 ثبت شد: *{mood}*\n+{points} امتیاز عشق",
        "en": "💖 Logged: *{mood}*\n+{points} love points",
    },
    "mood_history_title": {
        "fa": "📊 *حال‌و‌هوای اخیر تو:*",
        "en": "📊 *Your recent mood:*",
    },
    "mood_history_empty": {
        "fa": "هنوز حالی ثبت نکردی. از /mood شروع کن!",
        "en": "No moods logged yet. Try /mood!",
    },
    # ------------------------------------------------------------- compliment
    "compliment_prompt": {
        "fa": (
            "🌟 یه تعریف قشنگ برای *{partner}*:\n\n"
            "_{text}_\n\n"
            "💡 می‌تونی همین رو کپی کنی و بفرستی!"
        ),
        "en": (
            "🌟 A lovely compliment for *{partner}*:\n\n"
            "_{text}_\n\n"
            "💡 Feel free to copy & send!"
        ),
    },
    # -------------------------------------------------------------- settings
    "settings_title": {
        "fa": "⚙️ *تنظیمات* — چی می‌خوای تغییر بدی؟",
        "en": "⚙️ *Settings* — what would you like to change?",
    },
    "btn_change_language": {"fa": "🌐 زبان", "en": "🌐 Language"},
    "btn_change_names": {"fa": "👥 نام‌ها", "en": "👥 Names"},
    "btn_change_dates": {"fa": "📅 تاریخ‌ها", "en": "📅 Dates"},
    "btn_change_time": {"fa": "⏰ ساعت پیام", "en": "⏰ Daily time"},
    "btn_change_tz": {"fa": "🌍 منطقه زمانی", "en": "🌍 Timezone"},
    "btn_toggle_daily": {"fa": "🔔 خاموش/روشن پیام روزانه", "en": "🔔 Toggle daily"},
    "btn_custom_events": {"fa": "📌 رویدادهای دلخواه", "en": "📌 Custom events"},
    "btn_reset_quotes": {"fa": "🔄 ریست تاریخچه‌ی کوت‌ها", "en": "🔄 Reset quote history"},
    "btn_delete_data": {"fa": "🗑 حذف داده‌های من", "en": "🗑 Delete my data"},
    "daily_toggled_on": {"fa": "🔔 پیام روزانه روشن شد.", "en": "🔔 Daily messages enabled."},
    "daily_toggled_off": {"fa": "🔕 پیام روزانه خاموش شد.", "en": "🔕 Daily messages disabled."},
    "quotes_reset": {
        "fa": "🔄 تاریخچه‌ی کوت‌ها پاک شد. حالا دوباره از اول کوت‌های جدید می‌بینی!",
        "en": "🔄 Quote history cleared. You'll see fresh quotes again!",
    },
    "data_deleted": {
        "fa": "🗑 همه‌ی داده‌های شما حذف شد. هر وقت خواستی با /start دوباره شروع کن.",
        "en": "🗑 All your data has been deleted. Use /start any time to begin again.",
    },
    "confirm_delete": {
        "fa": "⚠️ مطمئنی می‌خوای *همه‌ی داده‌هات* حذف بشه؟",
        "en": "⚠️ Are you sure you want to delete *all your data*?",
    },
    "btn_yes_delete": {"fa": "✅ بله، حذف کن", "en": "✅ Yes, delete"},
    "btn_cancel": {"fa": "↩️ بی‌خیال", "en": "↩️ Cancel"},
    # ----------------------------------------------------- custom milestones UI
    "custom_events_title": {
        "fa": (
            "📌 *رویدادهای دلخواه*\n\n"
            "می‌تونی هر مناسبتی (سالگرد آشنایی، اولین قرار، سفر، …) رو اضافه کنی "
            "تا ربات روزشمارش رو نشونت بده."
        ),
        "en": (
            "📌 *Custom events*\n\n"
            "Add any meaningful date (first date, trip, anniversary…) and the bot "
            "will keep a countdown for you."
        ),
    },
    "btn_add_event": {"fa": "➕ افزودن", "en": "➕ Add"},
    "add_event_ask_title": {
        "fa": "📝 اسم این مناسبت چی باشه؟ (مثل «اولین قرار»)",
        "en": "📝 What's the name of this event? (e.g. \"First date\")",
    },
    "add_event_ask_date": {
        "fa": "📅 تاریخش رو وارد کن (*YYYY-MM-DD*).",
        "en": "📅 Enter the date (*YYYY-MM-DD*).",
    },
    "event_added": {
        "fa": "✅ مناسبت *{title}* تو تاریخ {date} اضافه شد!",
        "en": "✅ Event *{title}* on {date} added!",
    },
    "event_deleted": {"fa": "🗑 مناسبت حذف شد.", "en": "🗑 Event deleted."},
    "event_empty": {"fa": "📭 هیچ مناسبتی ثبت نشده.", "en": "📭 No custom events yet."},
    # ----------------------------------------------------------- generic flow
    "generic_back": {"fa": "↩️ به منوی اصلی برگشتیم.", "en": "↩️ Back to main menu."},
    "generic_cancelled": {"fa": "❎ لغو شد.", "en": "❎ Cancelled."},
    "generic_pick_language": {"fa": "🌐 یه زبان انتخاب کن:", "en": "🌐 Pick a language:"},
    "language_set": {"fa": "✅ زبان روی فارسی تنظیم شد.", "en": "✅ Language set to English."},
    "names_update_user": {
        "fa": "👤 اسم جدید *خودت* رو بنویس:",
        "en": "👤 Type your new name:",
    },
    "names_update_partner": {
        "fa": "💞 اسم جدید *پارتنرت* رو بنویس:",
        "en": "💞 Type your partner's new name:",
    },
    "names_updated": {"fa": "✅ اسم‌ها بروز شدن.", "en": "✅ Names updated."},
    "dates_pick": {
        "fa": "📅 کدوم تاریخ رو می‌خوای تغییر بدی؟",
        "en": "📅 Which date do you want to change?",
    },
    "btn_date_start": {"fa": "💞 شروع رابطه", "en": "💞 Relationship start"},
    "btn_date_user_bday": {"fa": "🎂 تولد خودم", "en": "🎂 My birthday"},
    "btn_date_partner_bday": {"fa": "🎁 تولد پارتنر", "en": "🎁 Partner's birthday"},
    "date_updated": {"fa": "✅ تاریخ بروز شد.", "en": "✅ Date updated."},
    "time_updated": {"fa": "✅ ساعت پیام بروز شد.", "en": "✅ Daily time updated."},
    "tz_updated": {"fa": "✅ منطقه‌ی زمانی بروز شد.", "en": "✅ Timezone updated."},
    "tz_invalid": {
        "fa": "❌ این منطقه‌ی زمانی شناخته شده نیست.",
        "en": "❌ Unknown timezone.",
    },
    # ------------------------------------------------------------------- help
    "help_text": {
        "fa": (
            "📖 *راهنمای LoveBot*\n\n"
            "🔸 /start — شروع/راه‌اندازی مجدد\n"
            "🔸 /menu — منوی اصلی\n"
            "🔸 /quote — جمله‌ی عاشقانه‌ی تصادفی (بدون تکرار!)\n"
            "🔸 /advice — توصیه‌ی روز\n"
            "🔸 /challenge — چالش امروز\n"
            "🔸 /compliment — یه تعریف برای پارتنرت\n"
            "🔸 /milestone — روزشمار رابطه\n"
            "🔸 /countdown — شمارش معکوس مناسبت‌ها\n"
            "🔸 /mood — ثبت حال امروز\n"
            "🔸 /lovescore — امتیاز عشق و استریک\n"
            "🔸 /settings — تنظیمات (زبان، تاریخ، ساعت…)\n"
            "🔸 /linkhere — *داخل گروه:* مقصد پیام روزانه رو همین گروه کن\n"
            "🔸 /unlinkhere — برگردوندن مقصد به پی‌وی\n"
            "🔸 /skip — رد کردن سؤال جاری\n"
            "🔸 /cancel — لغو عملیات جاری\n\n"
            "💡 *نکته:* کوت‌ها هیچ‌وقت تکرار نمی‌شن تا کل لیست رو ببینی، "
            "بعد از اول شروع می‌شن. ✨"
        ),
        "en": (
            "📖 *LoveBot help*\n\n"
            "🔸 /start — start or restart\n"
            "🔸 /menu — main menu\n"
            "🔸 /quote — a random love quote (never repeats!)\n"
            "🔸 /advice — daily advice\n"
            "🔸 /challenge — today's challenge\n"
            "🔸 /compliment — a compliment for your partner\n"
            "🔸 /milestone — relationship milestone\n"
            "🔸 /countdown — upcoming events\n"
            "🔸 /mood — log today's mood\n"
            "🔸 /lovescore — your love score & streak\n"
            "🔸 /settings — settings (language, dates, time…)\n"
            "🔸 /linkhere — *inside a group:* deliver daily messages there\n"
            "🔸 /unlinkhere — revert delivery to your private chat\n"
            "🔸 /skip — skip the current question\n"
            "🔸 /cancel — cancel the current action\n\n"
            "💡 *Tip:* quotes never repeat until the whole catalogue is seen, "
            "then it loops with fresh randomness. ✨"
        ),
    },
}


# ---------------------------------------------------------------- mood labels

MOOD_OPTIONS: list[tuple[str, dict[str, str]]] = [
    ("blissful", {"fa": "😍 فوق‌العاده", "en": "😍 Blissful"}),
    ("happy",    {"fa": "😊 خوب",        "en": "😊 Happy"}),
    ("okay",     {"fa": "🙂 معمولی",     "en": "🙂 Okay"}),
    ("sad",      {"fa": "😔 ناراحت",     "en": "😔 Sad"}),
    ("missing",  {"fa": "🥺 دلتنگ",      "en": "🥺 Missing them"}),
    ("grateful", {"fa": "🙏 ممنون",      "en": "🙏 Grateful"}),
    ("excited",  {"fa": "🥳 هیجان‌زده",   "en": "🥳 Excited"}),
    ("anxious",  {"fa": "😟 نگران",      "en": "😟 Anxious"}),
]


# ---------------------------------------------------------- common timezones

COMMON_TIMEZONES: list[str] = [
    "Asia/Tehran",
    "Asia/Dubai",
    "Asia/Istanbul",
    "Europe/London",
    "Europe/Berlin",
    "Europe/Moscow",
    "America/New_York",
    "America/Los_Angeles",
    "Asia/Tokyo",
    "UTC",
]


def t(lang: str, key: str, **fmt: Any) -> str:
    """Translate ``key`` into ``lang``; falls back to Persian then English."""
    lang = lang if lang in SUPPORTED_LANGUAGES else "fa"
    bundle = STRINGS.get(key, {})
    value = bundle.get(lang) or bundle.get("fa") or bundle.get("en") or key
    if fmt:
        try:
            value = value.format(**fmt)
        except (KeyError, IndexError):
            pass
    return value


def mood_label(mood_id: str, lang: str) -> str:
    for mid, labels in MOOD_OPTIONS:
        if mid == mood_id:
            return labels.get(lang, labels["fa"])
    return mood_id
