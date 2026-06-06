# -*- coding: utf-8 -*-
import os
import logging
from google import genai
from google.genai import types
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

# إعداد السجلات لمراقبة أداء البوت
logging.basicConfig(level=logging.INFO)

# جلب مفاتيح الاتصال والتشغيل
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# تشغيل عميل جيميناي الحديث
client = genai.Client(api_key=GEMINI_API_KEY)

# التوجيه الأكاديمي الشامل للبوت (مدمج به هيكل ومراحل البحث)
SYSTEM_PROMPT = """
أنت DRaaS5.0 - مساعد بحثي مخصص لمساعدة الباحثة توحيدة موسى الحسن محمد في إنجاز بحث دبلومها العالي في علوم الحاسوب تحت إشراف د. هبة على ناصر.
عنوان البحث: "استخدام استراتيجية التعافي من الكوارث كخدمة (DRaaS) لجامعة أفريقيا العالمية: دراسة حالة"

تفاصيل وإطار عمل البحث الأساسي:
- المشكلة الأساسية: عدم مرونة خطط استمرارية الأعمال التقليدية في مواجهة الكوارث الكاملة وانهيار البنية التحتية نتيجة الحروب والنزاعات.
- الحل المقترح: إطار عمل متكامل قائم على تقنيات الـ DRaaS لضمان حماية بيانات وأنظمة جامعة أفريقيا العالمية الحيوية.
- الطريقة المقترحة (5 مراحل): تتضمن (النسخ الاحتياطي Backup، النسخ المتماثل Replication، المراقبة Continuous Monitoring، الفشل الفجائي/المتبادل Failover، والاسترداد Recovery).
- المنهجية: نوعي (دراسة حالة) + وصفي تحليلي.
- الأدوات والتقنيات المدعومة: تقارير Gartner، حلول Veeam، معايير ISO 22301، حسابات RTO و RPO، وأدوات التخطيط مثل draw.io، مع بيئات AWS أو Azure.

القواعد الأكاديمية الصارمة للإجابة:
1. أجب دائماً باللغة العربية الفصحى الفائقة، وبأسلوب صياغة أكاديمية رصينة، متقنة ومقنعة تصلح لتقديمها مباشرة للمشرفين.
2. عند إرسال الباحثة لأي مخططات تقنية (DFD بمختلف مستوياتها، Flowcharts، جداول) أو صور لملاحظات الدكتورة، قم بتحليلها بدقة تقنية عالية، واشرح النواقص (مثل ربط العمليات، اتجاهات الأسهم، أو توضيح المخرجات والمدخلات والتحليلات الأمنية) وقدم الحلول وصغ النصوص الأكاديمية الخاصة بها لدمجها في الفصل الثالث أو بقية فصول البحث.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "🎓 مرحباً بكِ باحثة توحيدة!\n\n"
        "أنا مساعدكِ الأكاديمي DRaaS5.0 الشامل. لقد تم تحديثي بالكامل لأفهم كل ما ترسلينه:\n"
        "📝 نصوص وأسئلة عادية.\n"
        "📊 مخططات تقنية ورسومات (DFD, Flowcharts).\n"
        "📸 صور لملاحظات الدكتورة أو مستندات البحث.\n\n"
        "أنا جاهز تماماً الآن، أرسلي أي شيء وسأقوم بصياغته وتحليله فوراً! 🚀"
    )
    await update.message.reply_text(welcome_message)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # إظهار حالة "جاري الكتابة..." لتبدو الاستجابة تفاعلية وسريعة
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # جلب النص سواء كان رسالة عادية أو نصاً مصاحباً لصورة/ملف (Caption)
    user_text = update.message.text or update.message.caption or ""
    contents = []

    try:
        # التحقق التلقائي إذا كانت الرسالة تحتوي على صورة أو مخطط
        if update.message.photo:
            # جلب الصورة بأعلى دقة متوفرة أرسلتها الباحثة
            photo_file = await update.message.photo[-1].get_file()
            photo_bytes = await photo_file.download_as_bytearray()
            
            # تحويل ملف الصورة إلى بيانت متوافقة مع الذكاء الاصطناعي
            image_part = types.Part.from_bytes(
                data=bytes(photo_bytes),
                mime_type="image/jpeg"
            )
            contents.append(image_part)
            
            # إذا أرسلت صورة بدون كتابة، نضع توجيهاً افتراضياً ذكياً لتوليد التحليل
            if not user_text:
                user_text = "قم بتحليل هذا المخطط أو الصورة بدقة أكاديمية وربطها بسياق البحث وملاحظات المشرفة."

        # إضافة النص (سواء كان منفصلاً أو مصاحباً للصورة) إلى قائمة المعالجة
        contents.append(user_text)

        # استدعاء نموذج جيميناي المتطور لمعالجة النص والصورة معاً في نفس الوقت
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config={'system_instruction': SYSTEM_PROMPT}
        )
        
        # إرسال الإجابة الأكاديمية المصاغة مباشرة للتليجرام
        await update.message.reply_text(response.text)
        
    except Exception as e:
        print(f"Error encountered: {e}")
        await update.message.reply_text("⚠️ حدث خطأ أثناء معالجة الطلب، يرجى التحقق من استقرار الشبكة وإعادة الإرسال.")

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧹 تم مسح سجل المحادثة بنجاح، وجاهز لبدء جلسة بحثية جديدة! ✅")

def main():
    # بناء وتمرير التوكن وتشغيل البوت بالخيارات الشاملة (نصوص + وسائط)
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    
    # فلتر شامل يستقبل النصوص والصور والوسائط والعناوين في دالة واحدة
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.Document.ALL, handle_message))
    
    print("🚀 البوت النهائي الشامل شغال ومستعد لاستقبال كافة أنواع البيانات الأكاديمية...")
    app.run_polling()

if __name__ == "__main__":
    main()
