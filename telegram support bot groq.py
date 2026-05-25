"""
ربات پشتیبانی مشتری تلگرام با Groq AI (رایگان)
نصب: pip install python-telegram-bot groq
"""

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# ===== تنظیمات =====
TELEGRAM_TOKEN = 8651960573:AAE52bx7r5UKnvpS1aRvhl_8jgFi3xPiG7E "YOUR_TELEGRAM_BOT_TOKEN"   # توکن از BotFather
GROQ_API_KEY = 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 "YOUR_GROQ_API_KEY"           # کلید از console.groq.com

# شخصیت و اطلاعات کسب‌وکار خودت رو اینجا بنویس
BUSINESS_INFO = """


تو یک دستیار پشتیبانی مشتری گالری طلای آماندا هستی.
شماره تماس:۰۹۳۹۱۸۸۱۴۶۱
سیاست مرجوعی: تا ۱ روز امکان تعویض وجود دارد
ساعت کاری: شنبه تا پنجشنبه ۱۱ تا ۲۱
- مودب، صبور و حرفه‌ای باش
- اگر سوالی نمی‌دانی، صادقانه بگو و پیشنهاد بده با تیم انسانی تماس بگیرند
- پاسخ‌ها را کوتاه و مفید نگه دار
- همیشه به فارسی پاسخ بده
"""
# ===== پایان تنظیمات =====

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

client = Groq(api_key=GROQ_API_KEY)

# ذخیره تاریخچه مکالمه هر کاربر
conversation_history = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پیام خوش‌آمدگویی"""
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"سلام {user_name} عزیز! 👋\n"
        "به پشتیبانی خوش آمدید.\n"
        "چطور می‌تونم کمکتون کنم؟"
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع مکالمه جدید"""
    user_id = update.effective_user.id
    conversation_history[user_id] = []
    await update.message.reply_text("مکالمه جدید شروع شد. چطور می‌تونم کمک کنم؟ 🔄")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش پیام‌های کاربر"""
    user_id = update.effective_user.id
    user_message = update.message.text

    # نمایش وضعیت تایپ
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    # ایجاد یا بازیابی تاریخچه مکالمه
    if user_id not in conversation_history:
        conversation_history[user_id] = []

    # اضافه کردن پیام کاربر به تاریخچه
    conversation_history[user_id].append({
        "role": "user",
        "content": user_message
    })

    # محدود کردن تاریخچه به ۲۰ پیام آخر
    if len(conversation_history[user_id]) > 20:
        conversation_history[user_id] = conversation_history[user_id][-20:]

    try:
        # ارسال به Groq AI
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # مدل رایگان و قوی
            max_tokens=1000,
            messages=[
                {"role": "system", "content": BUSINESS_INFO},
                *conversation_history[user_id]
            ]
        )

        assistant_reply = response.choices[0].message.content

        # اضافه کردن پاسخ به تاریخچه
        conversation_history[user_id].append({
            "role": "assistant",
            "content": assistant_reply
        })

        await update.message.reply_text(assistant_reply)

    except Exception as e:
        logging.error(f"خطا: {e}")
        await update.message.reply_text(
            "متأسفم، مشکلی پیش آمد. لطفاً دوباره امتحان کنید یا /reset بزنید."
        )


def main():
    """اجرای ربات"""
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # دستورات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))

    # پیام‌های متنی
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ ربات در حال اجراست...")
    app.run_polling()


if __name__ == "__main__":
    main()
