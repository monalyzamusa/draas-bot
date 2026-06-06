"""
بوت تيليجرام - مساعد بحث DRaaS
الدارسة: توحيدة موسى الحسن محمد
"""

import anthropic
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# ==========================================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
# ==========================================

SYSTEM_PROMPT = """أنت مساعد أكاديمي متخصص لمساعدة الدارسة توحيدة موسى الحسن محمد في إنجاز بحث دبلومها العالي في علوم الحاسوب تحت إشراف د. هبه علي ناصر.

عنوان البحث: "استخدام استراتيجية التعافي من الكوارث كخدمة (DRaaS) لضمان استمرارية المؤسسات الأكاديمية في مناطق النزاع المسلح - دراسة حالة: جامعة أفريقيا العالمية"

تفاصيل البحث:
- المشكلة: خطط استمرارية الأعمال التقليدية غير مصممة لمواجهة انهيار كامل للبنية التحتية بسبب النزاعات
- الأهداف: تحليل المخاطر، دراسة DRaaS، اقتراح إطار عمل لجامعة أفريقيا
- المنهج: نوعي + دراسة حالة + وصفي تحليلي
- الأدوات: Gartner, Veeam, RTO/RPO, draw.io, AWS/Azure, ISO 22301
- هيكل البحث: 4 فصول

قواعد:
- أجب بالعربية دائماً
- أجوبة أكاديمية دقيقة ومفصلة
- استخدم المصطلحات التقنية مع شرحها
- اربط الإجابات بسياق جامعة أفريقيا العالمية"""

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# تخزين سجل المحادثة لكل مستخدم
user_history = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎓 مرحباً توحيدة!\n\n"
        "أنا مساعدك الأكاديمي لبحث الدبلوم عن DRaaS.\n\n"
        "يمكنك سؤالي عن:\n"
        "📖 الإطار النظري\n"
        "⏱️ مفاهيم RTO/RPO\n"
        "📚 المراجع الأكاديمية\n"
        "🏗️ إطار العمل المقترح\n"
        "✍️ صياغة فصول البحث\n\n"
        "اكتبي سؤالك وأنا جاهز! 🚀"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    # تهيئة سجل المحادثة
    if user_id not in user_history:
        user_history[user_id] = []

    # إضافة رسالة المستخدم
    user_history[user_id].append({
        "role": "user",
        "content": user_text
    })

    # إرسال "جاري الكتابة..."
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    try:
        response = client.messages.create(
       model="claude-3-5-sonnet-latest",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=user_history[user_id]
        )

        reply = response.content[0].text

        # إضافة رد البوت للسجل
        user_history[user_id].append({
            "role": "assistant",
            "content": reply
        })

        # الاحتفاظ بآخر 10 رسائل فقط لتوفير الذاكرة
        if len(user_history[user_id]) > 20:
            user_history[user_id] = user_history[user_id][-20:]

        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text(
            "⚠️ حدث خطأ، حاولي مرة أخرى."
        )
        print(f"Error: {e}")

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_history[user_id] = []
    await update.message.reply_text("✅ تم مسح سجل المحادثة.")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ البوت شغال...")
    app.run_polling()

if __name__ == "__main__":
    main()
