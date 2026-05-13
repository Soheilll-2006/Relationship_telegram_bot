"""Random morning greetings and closings used in the daily message."""

GREETINGS_FA: list[str] = [
    "🌅 صبح بخیر عزیزدلم!",
    "☀️ سلام به قشنگ‌ترین آدمِ امروز!",
    "🌸 صبحت پر از مهربونی!",
    "💫 یه روز قشنگ دیگه، در راه!",
    "🌺 صبحی پر از عشق و امید!",
    "🌼 امروز هم به اسم تو شروع شد.",
    "💖 صبح‌ت بخیر و دلت عاشقانه!",
    "🌷 لبخندت رو فراموش نکن، روز قشنگه!",
    "✨ صبح بخیر! کاش هر روز با تو شروع بشه.",
    "🦋 یه روز نو، یه ماجراجویی نو با تو.",
    "🌞 سلام آدم خاص! صبح بخیر.",
    "🌹 صبح‌ت پر از گل، روزت پر از عشق.",
    "💐 سلام به همراهِ مسیر زندگیم!",
    "🌟 صبح بخیر، ستاره‌ی روزها.",
]

GREETINGS_EN: list[str] = [
    "🌅 Good morning, my love!",
    "☀️ Hello to today's most beautiful soul!",
    "🌸 May your morning be full of softness!",
    "💫 Another beautiful day, just ahead!",
    "🌺 A morning rich in love and hope!",
    "🌼 Today begins with your name.",
    "💖 Good morning — and may your heart smile!",
    "🌷 Don't forget your smile, today is lovely!",
    "✨ Good morning! May every day start with you.",
    "🦋 A new day, a new adventure with you.",
    "🌞 Hello, special one — good morning.",
    "🌹 Flowers for your morning, love for your day.",
    "💐 Hello to my life's companion!",
    "🌟 Good morning, star of my days.",
]


CLOSINGS_FA: list[str] = [
    "🌹 با عشق، ربات همراهت.",
    "💖 روزِ قشنگی داشته باشی!",
    "💕 امروز رو بساز، عاشقانه!",
    "💞 لحظه‌هاتون پر از مهربونی!",
    "🥰 با تمام قلب، ربات شما.",
    "✨ هر چی می‌خوای، براتون آرزو می‌کنم.",
    "🌟 دوستون داشته باشید — همیشه!",
    "💝 یادتون نره: قدر هم رو بدونید.",
    "🌷 با عشق و آرامش.",
    "🤗 یه بغل گرم بهش بدی، یادت نره!",
]

CLOSINGS_EN: list[str] = [
    "🌹 With love, your companion bot.",
    "💖 Have a lovely day!",
    "💕 Make today romantic!",
    "💞 May your moments brim with kindness!",
    "🥰 With all my heart, your bot.",
    "✨ Wishing you everything beautiful.",
    "🌟 Love each other — always!",
    "💝 Don't forget to cherish each other today.",
    "🌷 With love and calm.",
    "🤗 Don't forget to give them a warm hug!",
]


def greeting(lang: str) -> list[str]:
    return GREETINGS_FA if lang == "fa" else GREETINGS_EN


def closing(lang: str) -> list[str]:
    return CLOSINGS_FA if lang == "fa" else CLOSINGS_EN
