# ADR-0052: Üretimde SMTP bağlantısına 10 saniyelik zaman aşımı konur

- **Durum:** Kabul edildi (2026-11-01)
- **Kaynak:** Kullanıcı, 2026-11-01'de `feature/notifications` (G13) açılış isteminden önce onayladı.

## Bağlam

- Hatırlatma e-postaları Django'nun SMTP backend'iyle kurum hesabından gönderilir (ADR-0004). Django'nun `EMAIL_TIMEOUT` varsayılanı `None`'dır; SMTP sunucusu bağlantıyı kabul edip yanıt vermezse soket süresiz bekler.
- Elle hatırlatma (`/gecikenler/hatirlat/`, FR-19) bir web isteği içinde gönderilir. waitress tek süreçte 8 iş parçacığıyla çalışır (ADR-0012, faz 4 küçük karar 2); takılan her istek bir iş parçacığını süresiz kilitler.
- Otomatik hatırlatma (`send_reminders`, FR-18) uygulama içi zamanlayıcının iş parçacığında çalışır (ADR-0007, KL-5). Takılırsa sonraki görevler (yedek, anonimleştirme, dışa aktarma) da çalışmaz ve `job_run` RUNNING'de kalır.
- E-posta sırasında veritabanı kilidi tutulmaz; kayıt e-postadan sonra kendi işleminde yazılır (data-design §5, architecture §10). SMTP hatası FAILED olarak kaydedilir ve pencere içinde yeniden denenir (faz 3 küçük karar 7).

## Değerlendirilen seçenekler

1. **`EMAIL_TIMEOUT = 10` (saniye), yalnız `prod.py`'de** (seçildi): Takılan SMTP en fazla birkaç kez 10 saniye bekletir. Zaman aşımı `smtplib`'den `OSError` (socket timeout) olarak gelir; hatırlatma servisi bunu FAILED kaydına çevirir ve kayıt pencere içinde yeniden denenir. Kurum SMTP'si normalde birkaç saniyede yanıt verir; 10 saniye yavaş bir sunucuya da pay bırakır.
2. **30 saniye:** Yavaş sunucuya daha çok pay bırakır, ama elle hatırlatmada personel yarım dakika bekler ve takılan bir sunucu waitress iş parçacıklarını daha uzun tutar.
3. **`LIBRARY_EMAIL_TIMEOUT` ortam değişkeni:** Kurulumda ayarlanabilir olur, ama architecture §6.4'e ve KL-43'teki zorunlu değişken listesine yeni bir değişken ekler; ihtiyaç kanıtlanmadan yapılandırma yüzeyi büyür.
4. **Varsayılanı (`None`) korumak:** Kod değişmez, ama yukarıdaki süresiz kilitlenme riski kalır.

## Karar

- `library_site/settings/prod.py`'de `EMAIL_TIMEOUT = 10` tanımlanır (saniye, sabit değer; ortam değişkeni yoktur).
- `dev` (konsol backend'i) ve `test` (bellek backend'i) ayarları değişmez; bu backend'ler ağa çıkmaz.
- Zaman aşımı hatası (`OSError`) hatırlatma servislerinde `smtplib.SMTPException` ile birlikte FAILED olarak yakalanır (plan §11, G13 küçük karar 5).
- `tests/test_prod_settings.py`'deki bir ayar testi üretim ayarlarını ayrı süreçte yükleyip `EMAIL_TIMEOUT == 10` olduğunu sabitler.
- G13'ün "Dosyalar" satırına `library_site/settings/prod.py` eklenir.

## Sonuçlar

- **Olumlu:** SMTP sorunu web isteğini ve zamanlayıcıyı süresiz kilitlemez; hata `reminder_log`'da FAILED olarak görünür ve yeniden denenir.
- **Olumsuz / riskler:**
  - 10 saniyeden yavaş yanıt veren bir SMTP sunucusunda gönderimler FAILED olur. Kurulumda (TC-232) gerçek sunucuyla denenir; gerekirse değer yeni bir ADR ile değiştirilir.
  - Elle hatırlatmada çok sayıda ödünç seçilir ve SMTP takılırsa istek uzun sürebilir: her ödünç ayrı bir SMTP bağlantısıyla gönderilir ve her biri 10 saniyelik zaman aşımına takılabilir.

## İzlenebilirlik

- **Gereksinim:** FR-18, FR-19; NFR-05. Plan G13, §11 (2026-11-01 G13 kararları).
- **Bağlantılı:** ADR-0004, ADR-0007, ADR-0012
