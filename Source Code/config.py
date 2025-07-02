# config.py

### Pengaturan Mouse ###
SMOOTHING_FACTOR = 5
SENSITIVITY = 10.0

### Pengaturan Gestur ###
# >>> THRESHOLD DIUBAH MENJADI NILAI RASIO (NORMALISASI) <<<
# Artinya, klik terdeteksi jika jarak pinch < 40% dari panjang telapak tangan
NORMALIZED_CLICK_THRESHOLD = 0.4 
CLICK_COOLDOWN = 0.5
# >>> PENGATURAN BARU UNTUK SCROLL <<<
# Menentukan seberapa banyak piksel gerakan tangan untuk satu "unit" scroll.
# Semakin kecil nilainya, semakin sensitif scroll-nya.
SCROLL_SENSITIVITY = 0.3
# >>> PENGATURAN SWIPE DIPERBARUI UNTUK LOGIKA BARU <<<
# Jarak (dalam piksel) untuk mengunci arah swipe (vertikal/horizontal).
SWIPE_ACTIVATION_DISTANCE = 40 
# Jarak (dalam piksel) untuk memicu aksi final (swipe vertikal atau navigasi horizontal).
SWIPE_TRIGGER_DISTANCE = 70 
# >>> PENGATURAN BARU UNTUK KONFIRMASI GESTUR <<<
# Durasi (dalam detik) gestur harus ditahan untuk mengubah mode.
GESTURE_CONFIRM_DURATION = 0.5 
# >>> PENGATURAN BARU UNTUK KONTROL MEDIA <<<
# Jarak pergerakan tangan untuk memicu aksi media (volume/seek).
MEDIA_CONTROL_THRESHOLD = 60 

### Pengaturan Deteksi Tangan ###
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.7