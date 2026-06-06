# -*- coding: utf-8 -*-
import os
import logging
from google import genai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

# إعداد السجلات (Logging)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# جلب التوكنات من المتغيرات البيئية للمشروع
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# إعداد مكتبة جيميناي الحديثة
client = genai.Client(api_key=GEMINI_API_KEY)

# التوجيه الأساسي والنظامي للمساعد الأكاديمي (System Prompt)
SYSTEM_PROMPT = """
أنت DRaaS5.0 - مساعد بحثي مخصص لمساعدة الباحثة توحيدة موسى الحسن محمد في إنجاز بحث دبلومها العالي في علوم الحاسوب تحت إشراف د. هبة على ناصر.
عنوان البحث: "استخدام استراتيجية التعافي من الكوارث كخدمة (DRaaS) لجامعة أفريقيا العالمية: دراسة حالة"

تفاصيل البحث الأساسية:
- المشكلة: خطط استمرارية الأعمال التقليدية غير مصممة لمواجهة انهيار كامل البنية التحتية بسبب النزاعات والحروب.
- المقترح: إطار عمل متكامل لجامعة أفريقيا العالمية قائم على تقنيات الـ DRaaS لحماية البيانات واستمرارية الأنظمة الحيوية.
- المنهج: نوعي - دراسة حالة + وصفي تحليلي.
- الأدوات والتقنيات: Gartner, Veeam, RTO/RPO, draw.io, AWS/Azure, ISO 22301.
- هيكل البحث: 4 فصول.

القواعد الصارمة لإجاباتك:
1. أجب دائماً باللغة العربية الفصحى وبصياغة أكاديمية رصينة ومتقنة ومقنعة.
2. استخدم المصطلحات التقنية مع شرحها بوضوح وربطها بسياق جامعة أفريقيا العالمية عند الحاجة.
3. ساعد الباحثة في صياغة وهيكلة فصول البحث (خاصة الفصل الثالث والتعديلات المطلوبة من المشرفة والدكتورة) وتقديم مقترحات ذكية لتقليل RTO و RPO.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🎓 مرحباً توحيدة!\n\n"
        "أنا مساعدك الأكاديمي DRaaS5.0 لبحث الدبلوم عن DRaaS.\n\n"
        "يمكنك سؤالي عن كل ما يخص البحث وصياغة الفصول. أرسلي سؤالكِ الآن! 🚀"
    )
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    # إظهار حالة "جاري الكتابة..." في تليجرام
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        # استدعاء نموذج جيميناي الحديث وإرسال الرسالة مباشرة
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_text,
            config={'system_instruction': SYSTEM_PROMPT}
        )
        reply = response.text

        # إرسال الرد للباحثة في تليجرام
        await update.message.reply_text(reply)

    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("⚠️ حدث خطأ أثناء معالجة الطلب، حاولي مرة أخرى.")

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧹 تم مسح سجل المحادثة بنجاح ✅")

def main():
    # بناء وتشغيل البوت بالتوكن المحدث
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ البوت شغال ومستعد لاستقبال الرسائل عبر ميزات جوجل الحديثة...")
    app.run_polling()

if __name__ == "__main__":
    main()

