# -*- coding: utf-8 -*-
import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
أنت DRaaS5.0 - مساعد بحثي مخصص لمساعدة الباحثة توحيدة موسى الحسن محمد في إنجاز بحث دبلومها العالي في علوم الحاسوب تحت إشراف د. هبة على ناصر.
عنوان البحث: "استخدام استراتيجية التعافي من الكوارث كخدمة (DRaaS) لجامعة أفريقيا العالمية: دراسة حالة"
أجب دائماً باللغة العربية الفصحى وبصياغة أكاديمية رصينة ومقنعة. حلل المخططات والصور المرفقة بدقة تامة.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎓 مرحباً توحيدة! أنا مساعدك الأكاديمي الشامل DRaaS5.0 جاهز لاستقبال أسئلتكِ وصوركِ بأمان الآن! 🚀")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    user_text = update.message.text or update.message.caption or ""
    
    try:
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=SYSTEM_PROMPT
        )
        
        # إذا أرسلت الباحثة صورة، نستخرج رابطها مباشرة دون تحميلها في السيرفر
        if update.message.photo:
            photo_file = await update.message.photo[-1].get_file()
            # استخدام الرابط المباشر المخزن في سيرفرات تليجرام لحماية ذاكرة السيرفر
            photo_url = photo_file.file_path
            
            import requests
            from PIL import Image
            from io import BytesIO
            
            response_img = requests.get(photo_url)
            img = Image.open(BytesIO(response_img.content))
            
            if not user_text:
                user_text = "حلل هذا المخطط بدقة أكاديمية يتماشى مع بحث جامعة أفريقيا العالمية وملاحظات الدكتورة."
                
            response = model.generate_content([user_text, img])
        else:
            response = model.generate_content(user_text)
            
        await update.message.reply_text(response.text)
        
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("⚠️ حدث خطأ، جربي إرسال رسالة نصية أولاً للتأكد، أو أعيدي إرسال الصورة بحجم أصغر.")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
