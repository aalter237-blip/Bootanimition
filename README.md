# M❤M Boot Animation

شاشة إقلاع رومانسية فاخرة — **أسود × ذهبي**  
**محمد ♥ مزن** · حبي · حياتي · شعار **M❤M**

![Preview](preview/frame_0021.png)

## تحميل الملف الجاهز

📦 **[Download bootanimation.zip](https://github.com/aalter237-blip/Bootanimition/releases/latest)**  
(Release asset — جاهز للتثبيت مباشرة)

## المواصفات

| | |
|---|---|
| الدقة | 720 × 1600 |
| الإطارات | 40 |
| السرعة | 5 fps |
| الضغط | Store (بدون ضغط) |
| الحجم | ≈ 132 MB |

## محتويات المستودع

```
desc.txt                     # وصف الأنيميشن
part0/frame_0001.bmp … 40    # الإطارات
generate_romantic_boot.py    # سكربت إعادة التوليد
INSTALL.txt                  # تعليمات التثبيت
preview/                     # معاينات PNG / GIF
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
