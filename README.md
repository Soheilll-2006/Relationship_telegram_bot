<div align="center">

# 💕 LoveBot

### *A bilingual Telegram bot for couples — your daily relationship companion*

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Telegram-pyTelegramBotAPI-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram"/>
  <img src="https://img.shields.io/badge/Languages-FA%20%7C%20EN-EC4899?style=for-the-badge" alt="Languages"/>
  <img src="https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge" alt="License"/>
</p>

<p align="center">
  <strong>🇮🇷 فارسی</strong> · <strong>🇬🇧 English</strong>
</p>

<sub>200+ love quotes &nbsp;·&nbsp; 100+ daily-life tips &nbsp;·&nbsp; 80+ couple challenges &nbsp;·&nbsp; 100+ compliments<br/>per language — **never repeats** until the whole catalogue is seen.</sub>

</div>

---

## 🇮🇷 فارسی

### 🌹 این ربات چی هست؟

**LoveBot** یک ربات تلگرامی *دو زبانه* و *تک‌کاربره* برای زوج‌هاست. هر کاربر:
- زبان خودش رو انتخاب می‌کنه (فارسی یا انگلیسی).
- اسم خودش و پارتنرش، تاریخ شروع رابطه، تولدها، ساعت پیام روزانه و منطقه‌ی زمانی رو وارد می‌کنه.
- هر روز رأس ساعتی که گفته، یه پیام عاشقانه‌ی غافلگیر‌کننده (با کوت، توصیه، و در روزای خاص جشن) دریافت می‌کنه.

### ✨ فیچرها

| | |
| --- | --- |
| 🌐 **دو زبانه** | همه‌چی در دو زبان: فارسی + انگلیسی |
| 🧭 **Onboarding تعاملی** | با /start ربات قدم‌به‌قدم همه چی رو می‌پرسه |
| 💝 **۲۰۰+ کوت عاشقانه** | هیچ‌وقت تا کل لیست تموم نشده، تکرار نمی‌شن |
| 💡 **۱۰۰+ توصیه‌ی رابطه** | کاربردی، کوتاه، قشنگ |
| 🎯 **۸۰+ چالش روزانه** | کارهای کوچیک برای محکم‌تر کردن رابطه |
| 🌟 **۱۰۰+ تعریف آماده** | بفرست به پارتنرت، آماده‌ی کپی |
| 📅 **روزشمار و سالگرد** | روز چندم رابطه، نقطه‌ی عطف بعدی، شمارش معکوس |
| 🎂 **تبریک تولد خودکار** | تولد خودت و پارتنرت رو فراموش نکن |
| 📌 **رویدادهای دلخواه** | هر مناسبتی رو اضافه کن، ربات شمارش معکوس می‌گیره |
| 😊 **حال‌و‌هوای روزانه** | ثبت کن چه حسی داری و تاریخچه رو ببین |
| ❤️ **امتیاز عشق + استریک** | بازی‌سازی برای انگیزه‌ی فعال موندن |
| ⏰ **ساعت دلخواه + منطقه‌ی زمانی** | پیام دقیقاً ساعتی که می‌خوای، به وقت محلیت |
| 🔔 **خاموش/روشن پیام روزانه** | کنترل کامل |
| ⚙️ **تنظیمات شفاف** | همه چی قابل ویرایشه، حتی حذف کامل داده |

### 🧰 دستورات اصلی

| دستور | کار |
| ----- | --- |
| `/start` | شروع/راه‌اندازی |
| `/menu` | منوی اصلی با دکمه‌ها |
| `/quote` | جمله‌ی عاشقانه (بدون تکرار) |
| `/advice` | توصیه‌ی روز |
| `/challenge` | چالش امروز |
| `/compliment` | یه تعریف آماده برای پارتنرت |
| `/milestone` | روزشمار رابطه |
| `/countdown` | شمارش معکوس مناسبت‌ها |
| `/mood` | ثبت حال امروز |
| `/lovescore` | امتیاز و استریک شما |
| `/settings` | تنظیمات (زبان، نام، تاریخ، ساعت...) |
| `/help` | راهنما |
| `/skip` | رد کردن سؤال جاری |
| `/cancel` | لغو عملیات جاری |

### 🚀 نصب و راه‌اندازی

```bash
# ۱) کلون
git clone https://github.com/Soheilll-2006/telegram-relationship-bot.git
cd telegram-relationship-bot

# ۲) ساخت محیط مجازی
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# ۳) نصب کتابخونه‌ها
pip install -r requirements.txt

# ۴) ساخت فایل .env
cp .env.example .env
# و BOT_TOKEN رو از @BotFather بگیر و توش بگذار

# ۵) اجرا
python main.py
```

### 🌍 دیپلوی روی Replit / Railway / Render

ربات هیچ نیازی به دیتابیس بیرونی نداره؛ از SQLite استفاده می‌کنه. اگر روی هاست رایگانی هستی که سرویس رو می‌خوابونه، توی فایل `.env` این رو بگذار:

```env
KEEP_ALIVE=true
KEEP_ALIVE_PORT=5000
```

تا یه وب‌سرور Flask کوچیک هم کنارش بالا بیاد.

### 📁 ساختار پروژه

```
telegram-relationship-bot/
├── main.py                # نقطه‌ی شروع
├── requirements.txt
├── pyproject.toml
├── .env.example
└── lovebot/
    ├── __init__.py
    ├── config.py          # خوندن env
    ├── database.py        # SQLite (یوزر، کوت‌های دیده‌شده، …)
    ├── bot.py             # کلاس ربات + onboarding + همه‌ی handlerها
    ├── scheduler.py       # تیک هر دقیقه برای پیام روزانه
    ├── keep_alive.py      # وب‌سرور اختیاری Flask
    ├── keyboards.py       # کیبوردهای inline
    ├── content_picker.py  # انتخاب کوت بدون تکرار
    ├── i18n.py            # متن‌های UI به دو زبان
    ├── utils.py           # تاریخ، عدد فارسی، …
    └── content/
        ├── quotes.py      # 200+ کوت در هر زبان
        ├── advice.py      # 100+ توصیه در هر زبان
        ├── challenges.py  # 80+ چالش در هر زبان
        ├── compliments.py # 100+ تعریف در هر زبان
        └── greetings.py   # سلام‌ها و خداحافظی‌های صبحانه
```

### 🆚 از قبلی چی عوض شد؟

| قبلاً | الان |
| ---- | --- |
| ۳ تا فایل bot تکراری | یک کلاس واحد و تمیز |
| Hard-code فارسی | دو زبانه، انتخاب کاربر |
| فقط env vars | onboarding تعاملی + SQLite |
| یک گروه ثابت | هر کاربر مستقل، در private chat |
| ۳۵ کوت | ۲۰۰+ کوت در هر زبان، بدون تکرار |
| بدون استریک/امتیاز/مود | همه هست + رویدادهای دلخواه |
| Schedule لایبرری قدیمی | APScheduler با per-user timezone |

---

## 🇬🇧 English

### 🌹 What is this?

**LoveBot** is a *bilingual*, *per-user* Telegram bot for couples. Each user:
- Picks their preferred language (Persian or English).
- Enters their and their partner's names, the relationship start date, birthdays, daily-message time and timezone.
- Receives a sweet daily love note at the exact time they chose — with quotes, advice, milestone celebrations and birthday surprises.

### ✨ Features

| | |
| --- | --- |
| 🌐 **Bilingual** | Every UI string in Persian + English |
| 🧭 **Interactive onboarding** | `/start` walks the user through every setting |
| 💝 **200+ love quotes** | Never repeats until the full catalog is seen |
| 💡 **100+ relationship tips** | Practical, kind, short |
| 🎯 **80+ daily challenges** | Tiny activities that strengthen your bond |
| 🌟 **100+ ready-to-send compliments** | Copy & send to your partner |
| 📅 **Milestone tracker** | Days together, next big day, countdowns |
| 🎂 **Auto birthday wishes** | Yours *and* your partner's |
| 📌 **Custom events** | Add any date — get its countdown |
| 😊 **Daily mood log** | Track feelings over time |
| ❤️ **Love score + streak** | Light gamification keeps you engaged |
| ⏰ **Personal time + timezone** | Message at your local time, anywhere |
| 🔔 **Toggle daily** | Full control |
| ⚙️ **Transparent settings** | Edit everything; delete your data anytime |

### 🧰 Commands

| Command | Action |
| ------- | ------ |
| `/start` | Start or restart |
| `/menu` | Main menu (inline buttons) |
| `/quote` | A love quote (never repeats) |
| `/advice` | Daily advice |
| `/challenge` | Today's challenge |
| `/compliment` | A compliment for your partner |
| `/milestone` | Days together |
| `/countdown` | Upcoming events |
| `/mood` | Log today's mood |
| `/lovescore` | Score & streak |
| `/settings` | Change language, names, dates, time… |
| `/help` | Help |
| `/skip` | Skip the current question |
| `/cancel` | Cancel current action |

### 🚀 Getting started

```bash
# 1) Clone
git clone https://github.com/Soheilll-2006/telegram-relationship-bot.git
cd telegram-relationship-bot

# 2) Create a virtualenv
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate

# 3) Install dependencies
pip install -r requirements.txt

# 4) Configure environment
cp .env.example .env
# Then edit .env and paste your BOT_TOKEN from @BotFather

# 5) Run
python main.py
```

### 🌍 Free-tier hosts (Replit / Render / Railway)

LoveBot uses SQLite locally — no external DB needed. To keep the bot alive on free hosts that sleep idle processes, enable the lightweight Flask keep-alive:

```env
KEEP_ALIVE=true
KEEP_ALIVE_PORT=5000
```

Then ping the public URL (Replit/Render do this automatically when you give them an HTTP service).

### 🔐 Configuration reference (`.env`)

| Variable | Required | Default | Description |
| -------- | -------- | ------- | ----------- |
| `BOT_TOKEN` | ✅ | — | Telegram bot token from @BotFather |
| `DB_PATH` | ❌ | `lovebot.db` | SQLite file path |
| `KEEP_ALIVE` | ❌ | `false` | Run a tiny Flask server alongside the bot |
| `KEEP_ALIVE_PORT` | ❌ | `5000` | Port for the keep-alive server |
| `LOG_LEVEL` | ❌ | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |

### 🧠 How "no-repeat" quotes work

Every category (quotes, advice, challenges, compliments) is a stable list. Each shown item is recorded by user + category in `seen_items`. The picker excludes seen items and only resets the history once the user has truly seen them all. This means a couple can use LoveBot for *months* before hitting a repeat.

### 🤝 Contributing

PRs welcome! Especially:
- More quotes / advice / challenges (please keep them culturally inclusive and PG).
- New languages — drop a `lovebot/content/quotes_de.py` etc. and wire it in `i18n.py`.
- Tests for the SQLite layer and content picker.

### 📜 License

MIT — see `LICENSE` (or the header in `pyproject.toml`).

---

<div align="center">

**Made with 💕 for partners, by partners.**

*If LoveBot makes your relationship smile, give the repo a ⭐ — it really helps!*

</div>
