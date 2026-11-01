# ADR-0054: Geri yükleme mevcut veritabanını silmez, koruma kopyası olarak bırakır

- **Durum:** Kabul edildi (2026-11-01)
- **Kaynak:** Kullanıcı, 2026-11-01'de `feature/operations` (G14–G16) açılış isteminde onayladı.

## Bağlam

- Plan G14'teki `restore_backup` davranışının 5. adımı, mevcut veritabanının `-wal` ve `-shm` dosyalarını silip yeni dosyayı `os.replace` ile yerine koyuyordu. Bu adımdan sonra mevcut veritabanı geri alınamaz.
- Geri yükleme bir felaket yordamıdır (FR-28, NFR-04, AC-28) ve elle çalıştırılır. Yanlış dosya seçilmesi (ör. bir haftalık dışa aktarma yerine eski bir yedek) ya da yanlış veritabanına geri yükleme, son yedekten bu yana girilen bütün işlemleri kaybettirir.
- WAL modunda (ADR-0002) son işlemler `-wal` dosyasında olabilir; ana dosya tek başına güncel durumu taşımaz. Bu yüzden `-wal` ve `-shm` dosyaları ana dosyayla birlikte korunmalıdır.
- Mevcut veritabanı bozuk olduğu için geri yükleme yapılıyor olabilir; koruma adımı bozuk dosyada da çalışmalıdır.

## Değerlendirilen seçenekler

1. **Yeniden adlandırarak koruma kopyası bırakmak** (seçildi): Mevcut dosyalar silinmez, zaman damgalı bir adla yeniden adlandırılır. Ek kopyalama ve ek disk okuması yoktur; dosya bozuk olsa da adım çalışır. Yanlış bir geri yükleme, kopyanın adını geri vererek düzeltilebilir.
2. **Kopya bırakmamak (plandaki):** En basit yol; ama yanlış bir geri yükleme son yedekten sonraki bütün veriyi kalıcı olarak kaybettirir.

## Karar

- `restore_backup` doğrulamadan (plan G14 4. adım) sonra mevcut veritabanı dosyasını ve varsa `-wal`/`-shm` dosyalarını silmez. Onları `<db>.pre-restore-YYYYMMDD-HHMMSS`, `<db>.pre-restore-YYYYMMDD-HHMMSS-wal` ve `<db>.pre-restore-YYYYMMDD-HHMMSS-shm` olarak yeniden adlandırır (yerel saat). Ardından doğrulanmış geçici dosya `os.replace` ile veritabanının yerine konur.
- Adım, mevcut dosyanın içeriğine bakmaz; dosya bozuk olsa da çalışır. Veritabanı dosyası yoksa (ör. silinmişse) koruma kopyası oluşmaz.
- Koruma kopyasının yolu komut çıktısına yazılır. Kopya otomatik silinmez.
- Doğrulama başarısız olursa hiçbir dosya yeniden adlandırılmaz; mevcut veritabanı olduğu gibi kalır.
- **KVKK notu:** Koruma kopyası saklama kuralının (FR-25, ADR-0018) dışında kalan bir kişisel veri kopyasıdır; anonimleştirme görevi ona ulaşmaz. Kopya, geri yüklemenin doğru olduğu kontrol edildikten sonra elle silinmelidir. Not G19'da kurulum belgesinin geri yükleme yordamına yazılır.
- Plan G14 davranışındaki 5. adım buna göre değişir.

## Sonuçlar

- **Olumlu:** Yanlış geri yükleme geri alınabilir. Bozuk veritabanı da incelenmek üzere elde kalır.
- **Olumsuz / riskler:**
  - Her geri yükleme veritabanı boyutunda bir dosya bırakır; disk alanı ve KVKK yükümlülüğü yöneticinin elle silmesine bağlıdır.
  - Koruma kopyası `LIBRARY_DB_PATH`'in klasöründe kalır; günlük yedek ve dışa aktarma ona dokunmaz.

## İzlenebilirlik

- **Gereksinim:** FR-28, NFR-04, NFR-08; AC-28. Plan G14, G19, §11 (G14–G16 açılış kararları).
- **Bağlantılı:** ADR-0002, ADR-0006, ADR-0011, ADR-0018
