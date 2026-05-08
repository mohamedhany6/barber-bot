import os

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

SHOP_NAME = "Amr Salon ✂️🔥"

SERVICES = {
    "1": "🔹 Basic Look",
    "2": "🔹 Clean Style ⭐",
    "3": "🔹 Full Experience 👑"
}


PRICES = {
    "🔹 Basic Look": 160,
    "🔹 Clean Style ⭐": 180,
    "🔹 Full Experience 👑": 280
}


SERVICE_DETAILS = {

    "🔹 Basic Look — 160 جنيه":
"""🔹 Basic Look ✂️

• حلاقة شعر
• تنعيم دقن
• ماسك + حمام زيت

💰 السعر: 160 جنيه""",

    "🔹 Clean Style ⭐ — 180 جنيه":
"""🔹 Clean Style ⭐

• حلاقة شعر
• تنعيم دقن
• استشوار / ويفي / كيرلي

💰 السعر: 180 جنيه

🔥 الأكثر طلباً""",

    "🔹 Full Experience 👑 — 280 جنيه":
"""🔹 Full Experience 👑

• حلاقة شعر
• تنعيم دقن
• جلسة تنظيف بشرة متكاملة

💰 السعر: 280 جنيه"""
}


WORKING_HOURS = [
    "12:00",
    "13:00",
    "14:00",
    "15:00",
    "16:00",
    "17:00",
    "18:00",
    "19:00",
    "20:00",
    "21:00",
    "22:00",
    "23:00"
]


OFF_DAY = "Monday"