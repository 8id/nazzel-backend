# استخدام نسخة بايثون رسمية كنقطة بداية
FROM python:3.10-slim

# تحديد مجلد العمل داخل الحاوية
WORKDIR /app

# تثبيت ffmpeg وتبعيات النظام الأخرى
# نثبّت أولاً أدوات إدارة الحزم ثم ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-utils \
    ffmpeg \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# نسخ ملف المتطلبات
COPY requirements.txt .

# تثبيت مكتبات بايثون
# استخدام --no-cache-dir يقلل حجم الصورة
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# نسخ باقي كود التطبيق (كل الملفات والمجلدات في المجلد الحالي)
COPY . .

# تحديد الأمر الذي سيتم تشغيله عند بدء الحاوية
# Render يستخدم متغير البيئة $PORT لتحديد المنفذ الذي يجب أن يستمع عليه التطبيق
# Gunicorn يشغل تطبيق Flask المسمى 'app' داخل ملف 'app.py'
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "app:app"]