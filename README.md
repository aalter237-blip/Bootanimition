# M❤M Boot Animation

شاشة إقلاع رومانسية فاخرة — **أسود × ذهبي**  
**محمد ♥ مزن** · حبي · حياتي · شعار **M❤M**

![Preview](preview/frame_0021.png)

## 🎬 فيديو الإقلاع

| الملف | المدة | الحجم | الوصف |
|--------|--------|--------|--------|
| **[boot_animation.mp4](https://github.com/aalter237-blip/Bootanimition/raw/arena/01a03b16-bootanimition/boot_animation.mp4)** | 24 ثانية | ≈ 24 MB | 3 دورات — معاينة كاملة |
| **[boot_animation_once.mp4](https://github.com/aalter237-blip/Bootanimition/raw/arena/01a03b16-bootanimition/boot_animation_once.mp4)** | 8 ثوانٍ | ≈ 8 MB | دورة واحدة |
| [boot_animation_preview.webm](https://github.com/aalter237-blip/Bootanimition/raw/arena/01a03b16-bootanimition/boot_animation_preview.webm) | 8 ثوانٍ | ≈ 0.6 MB | نسخة خفيفة للويب |

- الدقة: **720 × 1600** (عمودي / شاشة هاتف)
- الجودة: H.264 · 30 fps · CRF 17

## 📦 تحميل ملف التثبيت

**[bootanimation.zip](https://github.com/aalter237-blip/Bootanimition/raw/arena/01a03b16-bootanimition/bootanimation.zip)** — جاهز للتثبيت على أندرويد (≈ 46 MB)

## المواصفات

| | |
|---|---|
| الدقة | 720 × 1600 |
| الإطارات | 40 (PNG) |
| السرعة | 5 fps |
| الضغط | Store (بدون ضغط) |
| الحجم | ≈ 46 MB |

## محتويات المستودع

```
bootanimation.zip            # حزمة التثبيت
boot_animation.mp4           # فيديو 24ث (3 دورات)
boot_animation_once.mp4      # فيديو 8ث (دورة واحدة)
desc.txt                     # وصف الأنيميشن
part0/frame_0001.png … 40    # الإطارات
generate_romantic_boot.py    # سكربت إعادة التوليد
INSTALL.txt                  # تعليمات التثبيت
preview/                     # معاينات
```

## التثبيت (Root)

```bash
# نسخة احتياطية
adb shell cp /system/media/bootanimation.zip /sdcard/bootanimation_backup.zip

# تثبيت
adb root
adb remount
adb push bootanimation.zip /system/media/bootanimation.zip
adb shell chmod 644 /system/media/bootanimation.zip
adb reboot
```

مسارات بديلة على بعض أجهزة HONOR / Huawei:

- `/system/product/media/bootanimation.zip`
- `/oem/media/bootanimation.zip`

## إعادة بناء الـ zip

```bash
zip -0 -r bootanimation.zip desc.txt part0/
```

## إعادة توليد الإطارات

```bash
python3 generate_romantic_boot.py
```

---

**M❤M** · محمد ♥ مزن · حبي · حياتي
