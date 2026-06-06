# -*- coding: utf-8 -*-
import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# تفعيل المفتاح بالطريقة الكلاسيكية المستقرة
genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
أنت DRaaS5.0 - مساعد بحثي مخصص لمساعدة الباحثة توحيدة موسى الحسن محمد في إنجاز بحث دبلومها العالي في علوم الحاسوب تحت إشراف د. هبة على ناصر.
عنوان البحث: "استخدام استراتيجية التعافي من الكوارث كخدمة (DRaaS) لجامعة أفريقيا العالمية: دراسة حالة"

قواعد الإجابة:
1. أجب دائماً باللغة العربية الفصحى وبصياغة أكاديمية رصينة ومقنعة (خطوط واضحة متناسقة عند النسخ).
2. عند إرسال الباحثة لمخططات (DFD أو Flowchart) أو صور لملاحظات الدكتورة، قم بتحليلها بدقة تقنية، واشرح النواقص (مثل ربط العمليات، المخرجات والمدخلات، أو التحليلات الأمنية) وصغ النصوص الأكاديمية الخاصة بها للفصل الثالث.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎓 مرحباً توحيدة! أنا مساعدك الأكاديمي الشامل المستقر DRaaS5.0. أرسلي لي النصوص أو صور المخططات الآن وسأقوم بتحليلها فوراً! 🚀")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    user_text = update.message.text or update.message.caption or ""
    
    try:
        # استدعاء النموذج المستقر والمجرب عالمياً في السيرفرات
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=SYSTEM_PROMPT
        )
        
        # إذا أرسلت الباحثة صورة (مخطط أو ملاحظات)
        if update.message.photo:
            photo_file = await update.message.photo[-1].get_file()
            photo_bytes = await photo_file.download_as_bytearray()
            
            image_info = {
                "mime_type": "image/jpeg",
                "data": bytes(photo_bytes)
            }
            
            if not user_text:
                user_text = "حلل هذا المخطط بدقة أكاديمية بما يتماشى مع سياق بحث جامعة أفريقيا العالمية وملاحظات الدكتورة."
                
            response = model.generate_content([user_text, image_info])
        else:
            # إذا أرسلت نصاً عادياً فقط
            response = model.generate_content(user_text)
            
        await update.message.reply_text(response.text)
        
    except Exception as e:
        print(f"Error encountered: {e}")
        await update.message.reply_text("⚠️ حدث خطأ أثناء معالجة الطلب، يرجى إعادة المحاولة بعد دقيقة.")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
