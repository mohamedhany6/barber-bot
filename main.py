
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
import asyncio
import datetime
import config
import database

database.init_db()


# ================= UI =================
def main_menu():
    return ReplyKeyboardMarkup(
        [
            ["✂️ احجز الآن"],
            ["👨‍💼 لوحة الأدمن"]
        ],
        resize_keyboard=True
    )


def admin_menu():
    return ReplyKeyboardMarkup(
        [
            ["📅 حجز يوم", "💰 دخل يوم"],
            ["❌ إلغاء حجز"],
            ["🏠 الرئيسية"]
        ],
        resize_keyboard=True
    )


# ================= TIME =================
def parse_time_safe(t):

    try:

        parts = t.split(":")

        if len(parts) == 2:
            h, m = map(int, parts)

        else:
            h = int(parts[0])
            m = 0

        return datetime.time(hour=h, minute=m)

    except:
        return None


def to_12h(time_str):

    t = parse_time_safe(time_str)

    if not t:
        return "غير معروف"

    h = t.hour

    if h < 12:
        return f"{h} صباحاً"

    elif h == 12:
        return "12 مساءً"

    else:
        return f"{h - 12} مساءً"


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    text = f"""
💈 أهلاً بيك في {config.SHOP_NAME}

━━━━━━━━━━━━━━

🔹 Basic Look
• حلاقة شعر
• تنعيم دقن
• ماسك + حمام زيت
💵 160 جنيه

━━━━━━━━━━━━━━

🔹 Clean Style ⭐
• حلاقة شعر
• تنعيم دقن
• استشوار / ويفي / كيرلي
💵 180 جنيه

━━━━━━━━━━━━━━

🔹 Full Experience 👑
• حلاقة شعر
• تنعيم دقن
• جلسة تنظيف بشرة متكاملة
💵 280 جنيه

━━━━━━━━━━━━━━

⚠️ تدريج الدقن +40 جنيه

🕒 مواعيد العمل:
من 12 ظهراً إلى 11 مساءً

🚫 الأثنين أجازة

📲 احجز دلوقتي واستمتع بأحسن لوك ✂️
"""

    await update.message.reply_text(
        text,
        reply_markup=main_menu()
    )


# ================= MENU =================
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    # HOME
    if text == "🏠 الرئيسية":

        context.user_data.clear()

        await update.message.reply_text(
            "🏠 رجعناك للرئيسية",
            reply_markup=main_menu()
        )

        return

    # CUSTOMER
    if text == "✂️ احجز الآن":

        keyboard = [
    [
        InlineKeyboardButton(
            v,
            callback_data=f"service:{k}"
        )
    ]
    for k, v in config.SERVICES.items()
]

        await update.message.reply_text(
            "💇 اختر الباكدچ:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return

    # ADMIN
    if text == "👨‍💼 لوحة الأدمن":

        if update.effective_user.id != config.ADMIN_ID:

            await update.message.reply_text("❌ غير مسموح")

            return

        await update.message.reply_text(
            "👨‍💼 لوحة التحكم",
            reply_markup=admin_menu()
        )

        return


# ================= CALLBACK =================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query

    try:
        await q.answer()
    except:
        return

    data = q.data

    # ================= SERVICE =================
    if data.startswith("service:"):

        key = data.split(":")[1]

        service = config.SERVICES[key]

        context.user_data["service"] = service

        details = config.SERVICE_DETAILS.get(service, "")

        today = datetime.date.today()

        keyboard = [
            [
                InlineKeyboardButton(
    (today + datetime.timedelta(days=i)).isoformat(),
    callback_data=f"date:{i}"
                )
            ]
            for i in range(5)
        ]

        await q.message.reply_text(
            f"{details}\n\n📅 اختر اليوم:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


    # ================= DATE =================
    elif data.startswith("date:"):

        days = int(data.split(":")[1])

        date = datetime.date.today() + datetime.timedelta(days=days)

        if date.weekday() == 0:

            await q.message.reply_text(
                "🚫 الأثنين أجازة الصالون\n\nاختار يوم تاني ✂️"
            )

            return

        context.user_data["date"] = str(date)

        keyboard = [
            [
                InlineKeyboardButton(
                    f"🕐 {to_12h(t)}",
                    callback_data=f"time:{t}"
                )
            ]
            for t in config.WORKING_HOURS
        ]

        await q.message.reply_text(
            "⏰ اختر الوقت:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


    # ================= TIME =================
    elif data.startswith("time:"):

        selected_time = data.replace("time:", "", 1)

        date = context.user_data.get("date")

        today = datetime.date.today()

        now = datetime.datetime.now().time()

        selected_obj = parse_time_safe(selected_time)

        if not selected_obj:

            await q.message.reply_text("❌ وقت غير صالح")

            return

        # وقت فات
        if date == str(today) and selected_obj <= now:

            await q.message.reply_text(
                f"""❌ الوقت ده فات

⏰ اختيارك:
{to_12h(selected_time)}"""
            )

            return

        taken = database.get_taken_times(date)

        # محجوز
        if selected_time in taken:

            alternatives = []

            for t in config.WORKING_HOURS:

                if t in taken:
                    continue

                t_obj = parse_time_safe(t)

                if not t_obj:
                    continue

                if date == str(today) and t_obj <= now:
                    continue

                alternatives.append(t)

            alternatives = alternatives[:3]

            if not alternatives:

                await q.message.reply_text(
                    "❌ full اليوم كامل"
                )

                return

            keyboard = [
                [
                    InlineKeyboardButton(
                        f"🕐 {to_12h(t)}",
                        callback_data=f"time:{t}"
                    )
                ]
                for t in alternatives
            ]

            await q.message.reply_text(
                f"""❌ الميعاد محجوز

⏰ اختيارك:
{to_12h(selected_time)}

🔥 أقرب مواعيد متاحة:""",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

            return

        # AVAILABLE
        context.user_data["time"] = selected_time

        await q.message.reply_text(
            """✅ الميعاد متاح

📩 ابعت البيانات بالشكل ده:

الاسم
رقم الموبايل"""
        )


    # ================= CONFIRM =================
    elif data == "confirm":

        name = context.user_data.get("name")
        phone = context.user_data.get("phone")
        date = context.user_data.get("date")
        time = context.user_data.get("time")
        service = context.user_data.get("service")

        if not all([name, phone, date, time, service]):

            await q.message.reply_text("❌ بيانات ناقصة")

            return

        if database.is_slot_taken(date, time):

            await q.message.reply_text("❌ الميعاد اتحجز")

            return

        booking_id = database.add_booking(
            name,
            phone,
            date,
            time,
            service,
            update.effective_user.id
        )
                  

        # إشعار للحلاق فور الحجز
        try:

            await context.bot.send_message(
                chat_id=config.ADMIN_ID,
                text=f"""📥 حجز جديد

👤 {name}
📱 {phone}

📅 {date}
⏰ {to_12h(time)}

💇 {service}

🆔 {booking_id}"""
            )

        except:
            pass

        await q.message.reply_text(
            f"""✅ تم تأكيد الحجز

🆔 رقم الحجز:
{booking_id}

🏪 {config.SHOP_NAME}

📅 {date}
⏰ {to_12h(time)}

💇 {service}
💵 {config.PRICES.get(service, 0)} جنيه

🔥 مستنيينك تنورنا ✂️""",

            reply_markup=main_menu()
        )

        context.user_data.clear()


    # ================= CANCEL =================
    elif data == "cancel":

        context.user_data.clear()

        await q.message.reply_text(
            "❌ تم إلغاء الحجز",
            reply_markup=main_menu()
        )


# ================= MESSAGE =================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    # ================= BOOKINGS BY DATE =================
    if text == "📅 حجز يوم":

        if update.effective_user.id != config.ADMIN_ID:
            return

        await update.message.reply_text(
            """📅 ابعت التاريخ بالشكل ده:

2026-05-07"""
        )

        context.user_data["admin_mode"] = "bookings_by_date"

        return


    # ================= INCOME BY DATE =================
    if text == "💰 دخل يوم":

        if update.effective_user.id != config.ADMIN_ID:
            return

        await update.message.reply_text(
            """💰 ابعت التاريخ بالشكل ده:

2026-05-07"""
        )

        context.user_data["admin_mode"] = "income_by_date"

        return


    # ================= BOOKINGS MODE =================
    if context.user_data.get("admin_mode") == "bookings_by_date":

        date = text

        data = database.get_bookings_by_date(date)

        if not data:

            await update.message.reply_text(
                f"📭 مفيش حجوزات يوم {date}"
            )

            context.user_data.pop("admin_mode")

            return

        msg = f"📅 حجوزات يوم {date}\n"

        for bid, name, phone, date, time, service, chat_id in data:

            msg += f"""

━━━━━━━━━━━━━━
🆔 {bid}

👤 {name}
📱 {phone}

⏰ {to_12h(time)}

💇 {service}
💵 {config.PRICES.get(service, 0)} جنيه
"""

        await update.message.reply_text(msg)

        context.user_data.pop("admin_mode")

        return


    # ================= INCOME MODE =================
    if context.user_data.get("admin_mode") == "income_by_date":

     date = text

    income_data = database.get_today_income(date)

    total = income_data["total"]

    details = ""

    for row in income_data["details"]:

        details += f"""

💇 {row['service']}
💵 {row['price']} جنيه
────────────
"""

    if total == 0:

        await update.message.reply_text(
            f"💸 مفيش دخل يوم {date}"
        )

        context.user_data.pop("admin_mode")

        return

    await update.message.reply_text(
        f"""💰 دخل يوم {date}

{details}

━━━━━━━━━━━━━━
💵 الإجمالي: {total} جنيه"""
    )

    context.user_data.pop("admin_mode")

    return

    # ================= DELETE =================
    if text == "❌ إلغاء حجز":

        if update.effective_user.id != config.ADMIN_ID:
            return

        await update.message.reply_text(
            "📩 ابعت رقم الحجز (ID)"
        )

        context.user_data["admin_mode"] = "delete"

        return


    # ================= DELETE MODE =================
    if context.user_data.get("admin_mode") == "delete":

        try:
            booking_id = int(text)

        except:

            await update.message.reply_text("❌ لازم رقم صحيح")

            return

        deleted = database.delete_booking_by_id(booking_id)

        if deleted:

            await update.message.reply_text("✅ تم حذف الحجز")

        else:

            await update.message.reply_text("❌ الحجز غير موجود")

        context.user_data.pop("admin_mode")

        return


    # ================= CUSTOMER =================
    try:

        name, phone = text.split("\n")

    except:

        await update.message.reply_text(
            """❌ ابعت بالشكل ده:

الاسم
 رقم الموبايل"""
        )

        return

    date = context.user_data.get("date")
    time = context.user_data.get("time")
    service = context.user_data.get("service")

    if not all([date, time, service]):

        await update.message.reply_text(
            "❌ ابدأ الحجز الأول"
        )

        return

    context.user_data["name"] = name
    context.user_data["phone"] = phone

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ تأكيد",
                callback_data="confirm"
            ),

            InlineKeyboardButton(
                "❌ إلغاء",
                callback_data="cancel"
            )
        ]
    ]

    await update.message.reply_text(
        f"""📌 تأكيد الحجز

👤 الاسم:
{name}

📱 رقم الموبايل:
{phone}

📅 التاريخ:
{date}

⏰ الوقت:
{to_12h(time)}

💇 الخدمة:
{service}

💵 السعر:
{config.PRICES.get(service, 0)} جنيه

⚠️ تدريج الدقن +40 جنيه""",

        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= AUTO TASKS =================
async def auto_tasks(context):
    app = context.application

    try:
        # 🧹 حذف الحجوزات القديمة
        database.delete_old_bookings()

        tomorrow = str(
            datetime.date.today() +
            datetime.timedelta(days=1)
        )

        data = database.get_bookings_by_date(tomorrow)

        reminded = set()

        for bid, name, phone, date, time, service, chat_id in data:

            if bid in reminded:
                continue

            # 👤 تذكير العميل
            try:
                await app.bot.send_message(
                    chat_id=chat_id,
                    text=f"""🔔 تذكير بموعدك بكرة

👤 {name}
📅 {date}
⏰ {to_12h(time)}

💇 {service}

✂️ مستنيينك في الموعد"""
                )
            except:
                pass

            # 👨‍💼 تذكير الأدمن
            try:
                await app.bot.send_message(
                    chat_id=config.ADMIN_ID,
                    text=f"""🔔 تذكير بموعد عميل

👤 {name}
📱 {phone}

📅 {date}
⏰ {to_12h(time)}

💇 {service}"""
                )
            except:
                pass

            reminded.add(bid)

    except:
        pass
 # ================= RUN =================
async def post_init(app):
    app.job_queue.run_repeating(auto_tasks, interval=3600, first=10)


def main():

    app = ApplicationBuilder().token(config.TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))

    app.add_handler(MessageHandler(
        filters.Regex("^(✂️ احجز الآن|👨‍💼 لوحة الأدمن|🏠 الرئيسية)$"),
        menu
    ))

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    print("Bot running...")

    app.run_polling()

if __name__ == "__main__":
    main()