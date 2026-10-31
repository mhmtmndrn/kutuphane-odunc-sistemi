# ADR-0011: Bina dışı yedeğin şifrelenmesi için cryptography tabanlı uygulama komutu

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 3, 3. tur. Kullanıcı soru penceresinden seçti.

## Bağlam

Haftalık dışa aktarma dosyası (ADR-0006) kişisel veri içerir ve bina dışına USB bellekle taşınır. Bellek kaybolursa veri okunamamalı. Felakette dosya başka bir makinede açılabilmeli.

## Değerlendirilen seçenekler

1. **cryptography kütüphanesiyle uygulama komutu** (seçildi): Parola türetimi scrypt, şifreleme AES-GCM. Şifreleme ve çözme management command ile yapılır, ek binary gerekmez.
2. **7-Zip AES-256 arşivi:** Uygulama olmadan da açılabilir ve tanıdıktır. Linux'ta p7zip binary'si gerekir ve iki platformda komutlar farklıdır.
3. **age CLI:** Modern ve basit. Ek binary gerektirir ve personel için yabancı bir araçtır.

## Karar

- Dışa aktarma komutu, son günlük yedeği yönetici parolasından scrypt ile türetilen anahtarla AES-256-GCM kullanarak şifreler.
- Dosya başlığında biçim sürümü, salt ve nonce bulunur.
- Geri yükleme komutu bu dosyayı çözer ve geri yükler.
- Parola veritabanında saklanmaz. Zamanlanmış görev için parolanın nereden okunacağı faz 4'te karara bağlanır.
- Parolanın çevrimdışı saklanması kurulum belgesinde yazılır.

## Sonuçlar

- **Olumlu:** İki platformda tek komut. Şifreleme ve çözme otomatik testle doğrulanabilir.
- **Olumsuz / riskler:**
  - Yeni bağımlılık: cryptography.
  - Geri yüklemek için uygulamanın kurulu olması gerekir; zaten çalıştırmak için de gerekir.
  - Parola kaybı yedeği kalıcı olarak açılamaz hale getirir.

## İzlenebilirlik

- **Gereksinim:** FR-28; NFR-04; R-04
- **Bağlantılı:** ADR-0002, ADR-0006
