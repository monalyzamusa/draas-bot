# -*- coding: utf-8 -*-
import os
import logging
from google import genai
from google.genai import types
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
أنت DRaaS5.0 - مساعد بحثي مخصص لمساعدة الباحثة توحيدة موسى الحسن محمد في إنجاز بحث دبلومها العالي في علوم الحاسوب تحت إشراف د. هبة على ناصر.
عنوان البحث: "استخدام استراتيجية التعافي من الكوارث كخدمة (DRaaS) لجامعة أفريقيا العالمية: دراسة حالة"

تفاصيل البحث:
- المشكلة: انهيار البنية التحتية التقليدية بسبب الحروب والنزاعات.
- الحل: إطار عمل DRaaS خماسي المراحل (النسخ الاحتياطي، النسخ المتماثل، المراقبة، الفشل المتبادل، الاسترداد).

قواعد الإجابة:
1. أجب باللغة العربية الفصحى وبصياغة أكاديمية رصينة ومقنعة.
2. عند إرسال مخططات تقنية (DFD أو Flowchart) أو صور، قم بتحليلها بدقة واشرح النواقص وصغ النصوص الخاصة بها للفصل الثالث.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎓 مرحباً توحيدة! أنا مساعدك الأكاديمي DRaaS5.0. أرسلي النصوص أو صور المخططات وسأقوم بتحليلها فوراً! 🚀")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    user_text = update.message.text or update.message.caption or ""
    contents = []
    try:
        if update.message.photo:
            photo_file = await update.message.photo[-1].get_file()
            photo_bytes = await photo_file.download_as_bytearray()
            image_part = types.Part.from_bytes(data=bytes(photo_bytes), mime_type="image/jpeg")
            contents.append(image_part)
            if not user_text:
                user_text = "قم بتحليل هذا المخطط بدقة أكاديمية وربطه بسياق البحث وملاحظات المشرفة."
        contents.append(user_text)
        response = client.models.generate_content(model='gemini-2.5-flash', contents=contents, config={'system_instruction': SYSTEM_PROMPT})
        await update.message.reply_text(response.text)
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("⚠️ حدث خطأ أثناء معالجة الطلب، يرجى إعادة الإرسال.")

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧹 تم مسح سجل المحادثة بنجاح ✅")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()

