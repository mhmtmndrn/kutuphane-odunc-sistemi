# Test planı: Kütüphane ödünç sistemi

- **Güncelleme:** 2026-11-01 (TC-340…TC-356: G17–G18 açılış kararları, ADR-0056…0058; G17 ve G18 TC'leri "Geçti"; TC-357…TC-358: PR #6 yerel doğrulamasında ADR-0059)
- **Test yaklaşımı:** TDD (faz 0 kararı, AGENTS.md). Her görevde §6'daki TC'lerin testi önce yazılır ve kırmızı görülür, sonra kod yazılır (plan §4.0).
- **Kaynak:** Faz 4 test tasarımı taslağı (TC-01…TC-234) ADR-0036…0047 ve KL-1…46'ya göre revize edildi; TC-235…TC-319 eklendi. TC-320…TC-339, G14–G16 açılışında kullanıcının onayladığı kararların (ADR-0053…0055, plan §11) yeni davranışları için eklendi (2026-11-01); TC-340…TC-356, G17–G18 açılışında onaylanan kararların (ADR-0056…0058, plan §11) yeni davranışları için eklendi (2026-11-01); TC-357…TC-358, PR #6'nın yerel doğrulamasında onaylanan ADR-0059 için eklendi (2026-11-01). Taslak, içeriği buraya alındıktan sonra kullanıcı kararıyla silindi (2026-10-31); açık soruları plan §8.2'de.

## 1. Kapsam

- **Test edilecekler:** Kapsam içindeki 35 FR (24 Must, 11 Should), 13 NFR, 35 AC, data-design değişmezleri I1–I6 ve plan §3'teki KL kararları. Her FR, NFR ve AC'nin en az bir TC'si var (plan §7).
- **Test edilmeyecekler ve nedeni:**
  - Won't gereksinimler FR-30…FR-36: kapsam dışı.
  - Üçüncü taraf kütüphanelerin iç davranışı (Django, django-axes, APScheduler, reportlab, cryptography): yalnız bizim kodumuzla birleştikleri yerde test edilir (ör. TC-07 kilit, TC-192 şifreleme biçimi).
  - Django admin paneli: üretimde yok (ADR-0024); yalnız 404 olduğu test edilir (TC-01).
- **Otomatik olarak yalnız kısmen doğrulananlar** (kalan kısım faz 6'da elle):
  - NFR-01, NFR-02: Betiğin karar mantığı birim testinde (TC-221, TC-222, TC-318); gerçek p95 ancak hedef donanımda, yük verisiyle ölçülür (TC-223). TLS yükü ölçüme girmez (ADR-0031); raporda not edilir.
  - NFR-04, AC-28: Sayıların eşitliği otomatik (TC-191). "1 saatten kısa" ve "belgedeki adımlarla" kısmı kronometreli provadır (TC-225).
  - FR-28 ("geri yükleme adımını belgelemeli"): Belge TC-225 provasında adım adım izlenir.
  - NFR-03: Günlük tetikleyici otomatik (TC-208); 24 saatlik RPO birkaç günlük çalışmayla gösterilir (TC-233).
  - NFR-08: LAN dışı erişim port taramasıyla elle (TC-229); veri minimizasyonu otomatik (TC-52, TC-206).
  - NFR-06: Hash biçimi otomatik (TC-03); HTTPS ve sertifika zinciri elle (TC-230).
  - NFR-09: Tarayıcı, ekran genişliği ve dil elle (TC-231); saat dilimi ve dil ayarı otomatik (TC-235).
  - NFR-11, AC-11: `autofocus`, form sırası ve 303 akışı otomatik (TC-128); "fare yok, en fazla 3 etkileşim" gerçek okuyucuyla (TC-227).
  - AC-06, AC-31: Çözücüyle okunabilirlik otomatik (TC-71, TC-74); baskı, hiza ve okuyucu elle (TC-228).
  - FR-18 (teslim edilebilirlik): Bellek backend'iyle otomatik; kurum SMTP'si elle (TC-232).
  - AC-29: Adların `seed/` listelerinden geldiği, telefonların "000" önekli sahte numara (ADR-0057) ve e-postaların `@example.invalid` olduğu otomatik (TC-217, TC-342, TC-351); gerçek kişiye denk gelmeme örneklem incelemesiyle (TC-234).
  - FR-37 (bina dışı yedek): Şifreleme ve geri yükleme otomatik; USB ile taşıma elle (TC-226).
  - Kullanıcı belgelerinin içeriği gözden geçirmeyle (TC-319).

## 2. Test seviyeleri

Görev tablosundaki "Seviye" sütunu bu satırlardan birini gösterir.

| Seviye | Neyi kapsar | Araç | Ne zaman çalışır |
|---|---|---|---|
| Birim (`birim`) | `*/domain.py` saf fonksiyonları, `money`, `libx`, `pdf/sheets.py`, betik yardımcıları; ORM ve saat yok | pytest | Her değişiklikte (TDD döngüsü) |
| Entegrasyon (`servis`, `komut`) | `services.py` fonksiyonları veritabanıyla; management command'lar `call_command` ile; eşzamanlılık (`servis (eşzamanlı)`) dosya tabanlı SQLite ve `django_db(transaction=True)` ile | pytest, pytest-django | Her görevin doğrulama komutunda ve `python -m pytest -q` ile |
| Sistem (`view`) | URL → view → servis → şablon zinciri, yetki (403), yönlendirme, form hataları | Django test istemcisi | Her görevin doğrulama komutunda |
| Yavaş (`slow`) | PDF üretimi ve barkod çözme, yük profili tohumu | pytest `-m slow` (pypdfium2, zxing-cpp) | Görev doğrulamasında ve `main`'e birleştirmeden önce |
| Kabul (`elle`) | Gerçek donanım ve ağ: okuyucu, yazıcı, SMTP, HTTPS, LAN, yük ölçümü, geri yükleme provası | Kontrol listesi, kronometre, `scripts/loadtest.py` | Faz 6, test ortamına kurulumdan sonra |

## 3. Teknikler

| Bileşen | Teknik | Örnek TC |
|---|---|---|
| Son tarih, gecikme günü, ceza (`circulation.domain`) | Sınır değer (ceza üst sınırı ve gecikme gününde üç değerli), denklik sınıfı, hata tahmini | TC-104…TC-113, TC-276, TC-277 |
| Ödünç ve uzatma engelleri | Karar tablosu (tek koşul ve birleşik engel satırları) | TC-114…TC-123, TC-280 |
| Nüsha durumu | Durum geçişi: geçerli geçişler, geçersiz geçişler (her durumdan), 1-switch dizileri | TC-159…TC-169, TC-291 |
| Borç defteri | Denklik sınıfı, sınır değer (borç, af, para iadesi tutarları), değişmez kontrolü (I1–I6) | TC-76…TC-103, TC-270…TC-275 |
| Türkçe normalizasyon | Denklik sınıfı, metamorfik ilişki (idempotans, büyük/küçük harf) | TC-34…TC-36 |
| ISBN | Denklik sınıfı, sınır değer (hane sayısı), hata tahmini | TC-37…TC-43, TC-253 |
| Üye alanı yorumlama | Denklik sınıfı ve sınır değer (8 hane ve baştaki 0, 10–11 hane) | TC-279 |
| Rıza olayları | Durum geçişi, sınır değer (bugün ve yarın) | TC-57…TC-59, TC-254…TC-258 |
| Yetki | Denklik sınıfı ve URL çözücüden üretilen tam tarama (NFR-07) | TC-31…TC-33 |
| Hatırlatma aday koşulu (S6) | Koşul başına elle MC/DC: her koşulun sonucu tek başına değiştirdiği bir case | TC-173…TC-176, TC-179 |
| Telafi ve görev kaydı | Sınır değer (saat), durum geçişi (RUNNING → SUCCESS/FAILED; saatlik telafi) | TC-210…TC-213, TC-310…TC-312, TC-336 |
| Yedek, dışa aktarma, geri yükleme | Hata tahmini (bozuk dosya, yanlış parola, kilit, yol, yarıda kalan yazım), sınır değer (saklama günleri), senaryo (koruma kopyası) | TC-186…TC-200, TC-299…TC-304, TC-320…TC-329 |
| Tohum veri | Denklik sınıfı (profil sayıları), değişmez kontrolü (defter, nüsha durumu), metamorfik ilişki (aynı tohum ve gün; bir gün sonrası), hata tahmini (eksik dosya, yarıda kalan yazım) | TC-214…TC-220, TC-315…TC-317, TC-340…TC-352, TC-357…TC-358 |
| Yük betiği | Sınır değer (p95 499/500 ms), denklik sınıfı (karışım, yüzdelik), durum geçişi (iş parçacığının ödünç havuzu), karar tablosu (koruma) | TC-221…TC-222, TC-318, TC-353…TC-356 |
| Eşzamanlılık | Hata tahmini: iki iş parçacığı aynı kaynağa | TC-103, TC-145…TC-148 |

## 4. Kapsam hedefleri

| Bileşen | Ölçüt | Hedef | Gerekçe | Nasıl ölçülür |
|---|---|---|---|---|
| `*/domain.py` (administration, catalog, circulation, billing, notifications, operations) | Dal | ≥ %90 (NFR-13) | Son tarih, ceza, engel, uzatma ve borç kuralları burada | `coverage run --branch -m pytest`, ardından `coverage report --include="*/domain.py" --fail-under=90` (TC-224) |
| `billing/services.py`, `circulation/services.py` | Dal | ≥ %85 | Para ve durum geçişlerinin ret dalları (I1, I5, `InvalidTransition`, `NoOpenDayError`, işlem geri alma) serviste | `coverage report --include="billing/services.py,circulation/services.py" --fail-under=85` |
| `accounts/permissions.py`, `accounts/middleware.py` | Dal | %100 | Güvenliğin tek kapısı (FR-22, NFR-07, FR-41); kaçan dal yetki açığıdır | `coverage report --include="accounts/permissions.py,accounts/middleware.py" --fail-under=100` |
| `operations` (yedek, dışa aktarma, geri yükleme, anonimleştirme, zamanlayıcı) | Dal | ≥ %80 | Veri kaybı hata dallarında olur; OS'a özgü birkaç dal testte üretilemez | `coverage report --include="operations/*" --fail-under=80` |
| `pdf/sheets.py` | Satır | ≥ %80 | Yerleşim kodu düz akışlı; asıl kanıt barkod çözme testleri (TC-70, TC-71, TC-74) | `slow` dahil koşuda `coverage report --include="pdf/*"` |
| `views.py` dosyaları | Sayısal hedef yok | — | View'lar ince; yetki için NFR-07 taraması, davranış için AC başına view testi | — |

Kapsam ölçümü otomatik ölçütlerin yerini almaz: NFR-13 hedefi her görevin doğrulamasında, diğerleri grup `main`'e birleştirilmeden önce kontrol edilir.

## 5. Ortam ve test verisi

- **Çalışma zamanı:** Python 3.11 (yerelde 3.11.9), Django 5.2 LTS, `requirements-dev.txt`'teki sabit sürümler (KL-18). Bulut oturumları Linux'ta, yerel ortam Windows 11'dedir; platforma özgü testler (TC-235, TC-302, TC-313) iki ortamda da koşulur ve grup `main`'e birleştirilmeden önce yerelde `python -m pytest -q` çalışır (R-15).
- **Ayarlar:** `DJANGO_SETTINGS_MODULE=library_site.settings.test`: bellek e-posta backend'i, hızlı parola hasher'ı. Argon2 testi (TC-03) `base` listesini okur. Üretim ayarı testleri (TC-01, TC-02, TC-236) ayarları ayrı bir süreçte yükler.
- **Varsayılan kurallar:** Aksi yazılmadıkça süre 14 gün, limit 3, günlük ceza 5,00 TL, üst sınır 150,00 TL, borç eşiği 50,00 TL, saklama 2 yıl, kapalı gün yok.
- **Zaman:** "Bugün" `administration.clock.today()` `monkeypatch` ile sabitlenerek verilir (küçük karar 9). Saat gerektiren testler (oturum süresi, kilit, yedek uyarısı) zamanı sabitleyen yardımcıyla çalışır; gerçek bekleme yoktur.
- **Test verisi:** `tests/support/factories.py`'daki düz fonksiyonlar (`make_staff`, `make_member`, `make_book`, `make_copy`, `make_loan`, `make_charge`) kurar; factory_boy yoktur (küçük karar 11). Kişisel veri sentetiktir.
- **Eşzamanlılık:** Dosya tabanlı geçici SQLite, `django_db(transaction=True)`, iki iş parçacığı ve bir `threading.Barrier`.
- **Dosya sistemi:** Yedek ve dışa aktarma testleri `tmp_path` altında çalışır; yol boşluk ve Türkçe karakter içerir (TC-189).
- **Ağ:** Testler ağa çıkmaz. TC-219 socket düzeyinde engeller; SMTP bellek backend'idir.
- **Gizli değerler:** Testlerde gerçek parola, anahtar ya da SMTP bilgisi bulunmaz; dışa aktarma parolası test içinde üretilen geçici dosyadır.

## 6. Test senaryoları

Sütunlar: Görev, TC'nin yazıldığı görev (plan §4); Seviye, §2'deki satır. "Durum" faz 5'te "Geçti" ya da "Kaldı" olarak güncellenir.

| ID | Gereksinim | Görev | Seviye | Teknik | Girdi veya koşul | Beklenen | Durum |
|---|---|---|---|---|---|---|---|
| TC-01 | FR-22 (ADR-0024) | G01 | view | Denklik sınıfı | `settings.prod` ile GET `/admin/` | 404 | Planlandı |
| TC-02 | Mimari §6.4, KL-43 | G01 | birim | Hata tahmini | `settings.prod`, `LIBRARY_SECRET_KEY` tanımsız; ayarlar ayrı süreçte yüklenir | Süreç `ImproperlyConfigured("Eksik ortam değişkeni: LIBRARY_SECRET_KEY")` ile durur | Planlandı |
| TC-03 | NFR-06 | G01 | servis | Denklik sınıfı | Personel parolası kaydedilir | `password` `argon2$argon2id$` önekiyle başlar; düz parola veritabanında geçmez | Planlandı |
| TC-04 | FR-27 | G02 | view | Denklik sınıfı | Oturumsuz GET `/odunc/` | 302 → `/giris/?next=/odunc/` | Geçti |
| TC-05 | FR-27 | G02 | view | Senaryo | Doğru bilgilerle giriş, POST `/cikis/`, ardından GET `/odunc/` | Giriş başarılı; çıkıştan sonra `/giris/`e yönlendirilir | Geçti |
| TC-06 | FR-27, AC-27 | G02 | view | Sınır değer (iki değerli) | "ali": 4 yanlış parola, sonra doğru; ardından yine 4 yanlış ve doğru | İki giriş de başarılı (başarılı girişte sayaç sıfırlanır) | Geçti |
| TC-07 | FR-27, AC-27 | G02 | view | Sınır değer (iki değerli) | "ali": 5 ardışık yanlış parola, 6. denemede doğru parola | Giriş reddedilir: HTTP 429, giriş şablonu ve kilit mesajı (ADR-0049) | Geçti |
| TC-08 | FR-27 (ADR-0009, ADR-0050) | G02 | view | Sınır değer (iki değerli) | Kilitli "ali", kilidi tetikleyen 5. hatalı denemeden 14 dk 59 sn ve (ayrı testte) 15 dk 01 sn sonra doğru parola | 14:59'da 429 ile reddedilir; 15:01'de giriş başarılı | Geçti |
| TC-09 | FR-27, AC-27 | G02 | view | Sınır değer (iki değerli) | Oturumlu görevli; son istekten 29 dk 59 sn ve (ayrı testte) 30 dk 01 sn sonra GET `/odunc/` | 29:59'da 200; 30:01'de `/giris/`e yönlendirilir | Geçti |
| TC-10 | FR-27 | G02 | view | Senaryo | Oturumlu görevli 25 dk arayla 3 istek yapar (toplam 75 dk) | Üçü de 200; her istek süreyi yeniler | Geçti |
| TC-11 | FR-22, NFR-07 | G02 | servis | Karar tablosu | `require_role(ADMIN)` ile korunan bir servis CLERK ve ADMIN aktörle çağrılır | CLERK: `PermissionDenied`, veri değişmez; ADMIN: işlem yapılır | Geçti |
| TC-12 | FR-21, FR-27 (küçük karar 9) | G02, G04 | servis | Sınır değer (iki değerli) | 9 ve 10 karakterli parola: G02'de `validate_password` ile, G04'te `create_staff` ve `reset_password` ile (plan §11, G02 (b)) | 9: doğrulama hatası, değişiklik yok; 10: kabul | Geçti |
| TC-13 | SRS §7, FR-12 | G03 | birim | Sınır değer (iki değerli) | Saat 2026-11-16T20:59:59Z ve 2026-11-16T21:00:00Z iken `clock.today()` | 2026-11-16 ve 2026-11-17 | Geçti |
| TC-14 | NFR-12 (ADR-0016) | G03 | birim | Denklik sınıfı | Ayrıştırma: "15,00", "0,01", "150,00"; biçimlendirme: 1500, 1, 0 | 1500, 1, 15000; "15,00 TL", "0,01 TL", "0,00 TL" | Geçti |
| TC-15 | NFR-12 (ADR-0016) | G03 | birim | Sınır değer | Ayrıştırma: "15,005" | Reddedilir (kuruştan küçük basamak) | Geçti |
| TC-16 | NFR-12 | G03 | birim | Denklik sınıfı | Geçersiz girdiler: "-5,00", "abc", "" (her biri ayrı test) | Her biri reddedilir | Geçti |
| TC-17 | NFR-12 | G03 | birim | Hata tahmini | parse("0,10") + parse("0,20") | Tam olarak 30, tipi `int` | Geçti |
| TC-18 | FR-23, FR-26 | G03 | servis | Denklik sınıfı | Yönetici ayarları günceller (süre 21, limit 4, ceza 7,50 TL, ad "Merkez Kütüphanesi") | `get_settings()` yeni değerleri döner; eski ve yeni değerleri içeren SETTINGS_CHANGED kaydı yazılır | Geçti |
| TC-19 | FR-23 | G03 | servis | Sınır değer (iki değerli) | `loan_period_days`, `max_open_loans`, `debt_threshold_kurus`, `retention_years` için 0 ve 1; günlük ceza ve üst sınır için 0 | İlk dört alanda 0 reddedilir, 1 kabul edilir; ceza ve üst sınırda 0 kabul edilir | Geçti |
| TC-20 | FR-23 (ADR-0035) | G03 | servis | Sınır değer (iki değerli) | `library_name` 80 karakter, 81 karakter, "" | 80 kabul; 81 ve boş reddedilir | Geçti |
| TC-21 | FR-22, AC-22 | G03 | view | Denklik sınıfı | Görevli oturumuyla doğrudan POST `/ayarlar/` (süre 21) | 403; ayar değişmez; denetim kaydı yazılmaz | Geçti |
| TC-22 | FR-24, FR-26 | G03 | servis | Denklik sınıfı | Yönetici pazarı haftalık kapalı gün, 2027-10-29'u kapalı tarih olarak ekler | `closed_day_predicate()` pazar ve 2027-10-29 için True, 2027-11-01 için False; CLOSED_DAY_CHANGED kaydı | Geçti |
| TC-23 | FR-24, AC-24 | G03 | view | Sınır değer (iki değerli) | Pazartesi–cumartesi kapalı (6 gün) kaydı; ardından pazar eklenir | 6 gün kabul edilir; 7. gün reddedilir, "En az bir gün açık kalmalı" görünür, satır sayısı 6 kalır | Geçti |
| TC-24 | FR-24 | G03 | servis | Hata tahmini | 2027-10-29 ikinci kez kapalı tarih olarak eklenir | Reddedilir; tek satır kalır | Geçti |
| TC-25 | FR-37, AC-30 (KL-14) | G03 | view | Sınır değer (iki değerli) | Yönetici ana sayfası; son SUCCESS EXPORT `job_run` kaydının `run_on` değeri bugünden 7 ve 8 gün önce | Tarih görünür; 7 günde uyarı yok; 8 günde "Bina dışı yedek 7 günden eski" görünür | Geçti |
| TC-26 | FR-26 | G03 | servis | Hata tahmini | Denetim kaydı yazan servis, kayıttan sonra istisna fırlatır | İşlem geri alınır; iş verisi de denetim kaydı da kalmaz | Geçti |
| TC-27 | FR-21, FR-26 | G04 | servis | Denklik sınıfı | Yönetici "ali"yi CLERK olarak oluşturur, sonra rolünü ADMIN yapar | Ali giriş yapar; rolü ADMIN olur; iki STAFF_CHANGED kaydı | Geçti |
| TC-28 | FR-21, AC-21 | G04 | view | Durum geçişi | Yönetici "ali"yi pasifleştirir; ali doğru parolayla giriş dener | Giriş reddedilir; STAFF_CHANGED kaydı | Geçti |
| TC-29 | FR-21 | G04 | servis | Denklik sınıfı | Yönetici ali'nin parolasını sıfırlar | Eski parola reddedilir, yeni parola kabul edilir | Geçti |
| TC-30 | FR-27 (ADR-0009) | G04 | view | Durum geçişi | Kilitli "ali"nin kilidini yönetici kaldırır; ali hemen doğru parolayla girer | Giriş 15 dk beklemeden başarılı | Geçti |
| TC-31 | NFR-07, FR-22 | G04 | view | Denklik sınıfı | URL çözücüden alınan, yönetici işaretli her view'a görevli oturumuyla GET ve POST | Her istek 403 alır; veri değişmez | Geçti |
| TC-32 | NFR-07 | G04 | view | Hata tahmini | TC-31'in bulduğu yönetici URL desenleri, testte sabit yazılmış beklenen kümeyle karşılaştırılır. Kümede plan §4.1'deki 19 yönetici yolunun hepsi var, sonraki görevlerin ekleyecekleri de: personel (6), ayarlar, kapalı günler (3), denetim, saklama listesi, kayıp, hasarlı, onarıldı, kayıttan düşme, af, para iadesi, elle iptal | `Role.ADMIN` ile korunan yollar = beklenen küme ∩ var olan yollar (sonradan ADMIN korumasız eklenen yönetici yolu testi düşürür); bulundu, aktifleştir ve `/parola/` kümede yok ve var olduklarında görevli rolüyle korunur | Geçti |
| TC-33 | NFR-07 | G04 | view | Denklik sınıfı | TC-31'deki view'lara yönetici oturumuyla GET | Hiçbiri 403 dönmez | Geçti |
| TC-34 | NFR-10 (ADR-0019) | G05 | birim | Denklik sınıfı | `normalize_tr`: "istanbul", "İstanbul", "İSTANBUL", "ISTANBUL" | Dördü de "istanbul" | Geçti |
| TC-35 | FR-01, FR-04 (ADR-0019) | G05 | birim | Denklik sınıfı | "Şefiller", "IŞIK ÇĞÖÜ", "Hâlâ", "Ayşe   Yılmaz", "" | "sefiller", "isik cgou", "hala", "ayse yilmaz", "" | Geçti |
| TC-36 | NFR-10 | G05 | birim | Metamorfik ilişki | Türkçe örnek metin kümesindeki her s | `normalize_tr(normalize_tr(s)) == normalize_tr(s)`; `normalize_tr(s.upper()) == normalize_tr(s.lower()) == normalize_tr(s)` | Geçti |
| TC-37 | FR-04 (ADR-0008) | G05 | birim | Denklik sınıfı | `parse_isbn`: "9786053609322", "978-605-360-932-2", "978 605 360 932 2" | Üçü de `IsbnOk("9786053609322")` | Geçti |
| TC-38 | FR-04 | G05 | birim | Denklik sınıfı | Geçerli ISBN-10: "0306406152", "080442957X" | `IsbnOk("9780306406157")`, `IsbnOk("9780804429573")` | Geçti |
| TC-39 | FR-04, AC-04 | G05 | birim | Denklik sınıfı | "6053609322" (ISBN-10 kontrol hanesi tutmuyor; "978" önekli hali geçerli) | `IsbnSuggest("9786053609322")` | Geçti |
| TC-40 | FR-04 | G05 | birim | Denklik sınıfı | "6053609321" (ISBN-10 olarak da "978" önekiyle de geçersiz) | `IsbnInvalid`; öneri yok | Geçti |
| TC-41 | FR-04 | G05 | birim | Denklik sınıfı | "9786053609321" (13 hane, kontrol hanesi yanlış) | `IsbnInvalid` | Geçti |
| TC-42 | FR-04 | G05 | birim | Sınır değer | 9, 11, 12 ve 14 haneli girişler | Hepsi `IsbnInvalid` | Geçti |
| TC-43 | FR-04 | G05 | birim | Hata tahmini | "978605360932X", "97860536O9322" (O harfi), "X053609322" | Hepsi `IsbnInvalid` | Geçti |
| TC-44 | FR-01, AC-01 | G06 | servis | Denklik sınıfı | "Ayşe Yılmaz", "0555 111 22 33", e-posta yok | Benzersiz `member_no`; `phone_digits` "05551112233"; `search_key` "ayse yilmaz" | Geçti |
| TC-45 | FR-01 (küçük karar 2) | G06 | servis | Sınır değer | Art arda iki üye kaydı | İkinci üyenin `member_no`'su birincininkinden 1 fazla | Geçti |
| TC-46 | FR-01 | G06 | servis | Denklik sınıfı | Ad soyad boş; telefon boş (ayrı testler) | Her biri reddedilir; üye oluşmaz | Geçti |
| TC-47 | FR-01, AC-01, NFR-10 | G06 | servis | Denklik sınıfı | `search_members("ayşe")`, "AYŞE", "ayse" | Üç arama da Ayşe Yılmaz'ı döndürür | Geçti |
| TC-48 | FR-01 (KL-10) | G06 | servis | Denklik sınıfı | Üye no ile arama ("1042"); "05551112233" ile arama | Üye no tam eşleşir; telefon araması aynı üyeyi bulur (tireli ve parantezli biçimler TC-261'de) | Geçti |
| TC-49 | FR-01 (ADR-0019) | G06 | servis | Hata tahmini | Ad "Ayşe Yılmaz" → "Ayşe Demir" olarak güncellenir | "demir" araması bulur; "yılmaz" araması bulmaz | Geçti |
| TC-50 | FR-01 | G06 | servis | Hata tahmini | Arama terimi "%" ve "_" | Joker karakter olarak yorumlanmaz; bütün üyeler dönmez | Geçti |
| TC-51 | FR-01 (data-design S7) | G06 | servis | Sınır değer (iki değerli) | Terimle 50 ve 51 üye eşleşir | İkisinde de 50 sonuç | Geçti |
| TC-52 | NFR-08, FR-01 | G06 | birim | Denklik sınıfı | `Member` modelinin alan listesi | Kişisel alanlar yalnız `full_name`, `phone`, `phone_digits`, `email`, `search_key`; diğerleri data-design §2.2'deki teknik alanlar | Geçti |
| TC-53 | FR-02 (KL-22) | G11 | servis | Karar tablosu | `deactivate_member`: açık ödünç yok, borç 0 | Üye pasifleşir; `deactivated_on` = bugün | Geçti |
| TC-54 | FR-02 (KL-22) | G11 | servis | Karar tablosu | `deactivate_member`: 1 açık ödünç (borç ve onay ne olursa olsun) | "Açık ödüncü olan üye pasifleştirilemez"; üye aktif kalır | Geçti |
| TC-55 | FR-02 (KL-22) | G11 | servis | Karar tablosu | `deactivate_member`: açık ödünç yok, borç 0,01 TL, `confirm_debt=False` | "Üyenin 0,01 TL borcu var; onaylayarak pasifleştirin"; üye aktif kalır | Geçti |
| TC-56 | FR-02 (KL-22) | G11 | servis | Karar tablosu | `deactivate_member`: açık ödünç yok, borç 20,00 TL, `confirm_debt=True` | Pasifleşir; borç değişmez | Geçti |
| TC-57 | FR-03, AC-03 | G06 | servis | Durum geçişi | Rızasız üyeye 2026-11-01'de GIVEN, 2026-12-01'de WITHDRAWN | İki `consent_event`; `has_email_consent` önce True, sonra False; üye sayfasında iki tarih görünür | Geçti |
| TC-58 | FR-03 (ADR-0022) | G06 | servis | Durum geçişi | GIVEN → WITHDRAWN → GIVEN | Üç olay; `has_email_consent` True; sayfada son verme ve son geri alma tarihleri | Geçti |
| TC-59 | FR-03 (küçük karar 8) | G06 | servis | Hata tahmini | `set_consent` olay eklendikten sonra istisna fırlatır | Ne olay ne `has_email_consent` değişir | Geçti |
| TC-60 | FR-04 | G07 | servis | Denklik sınıfı | Başlık, yazar, ISBN "978-605-360-932-2", yayınevi, yıl girilir; ikinci kitap ISBN'siz | Birincinin `isbn13` alanı "9786053609322"; ikincininki NULL | Geçti |
| TC-61 | FR-04 | G07 | servis | Denklik sınıfı | Başlık boş; yazar boş (ayrı testler) | Reddedilir | Geçti |
| TC-62 | FR-04, AC-04 | G07 | view | Senaryo | Kitap formuna "6053609322" girilir, sonra öneri onaylanır | İlk POST kayıt yapmaz ve "9786053609322" önerir; onaydan sonra kitap "9786053609322" ile kaydedilir | Geçti |
| TC-63 | FR-04 | G07 | view | Denklik sınıfı | Kitap formuna "6053609321" girilir | Kayıt yapılmaz; hata gösterilir, öneri yok | Geçti |
| TC-64 | FR-05, AC-05 | G07 | servis | Denklik sınıfı | `add_copies(book, 2)` | İki ayrı barkod, her biri `f"{id:08d}"`; ikisi de ON_SHELF | Geçti |
| TC-65 | FR-05 | G07 | servis | Sınır değer | Nüsha id 1, 42 ve 99999999 (dizi değeri ayarlanarak) | "00000001", "00000042", "99999999" | Geçti |
| TC-66 | FR-04, AC-04 | G07 | view | Denklik sınıfı | "Tutunamayanlar" kitabının "00000042" barkodlu nüshası; "00000042" ile arama | Sonuçta "Tutunamayanlar" ve "Rafta" görünür | Geçti |
| TC-67 | FR-04, NFR-10 | G07 | servis | Denklik sınıfı | "İstanbul Hatırası" / "Ahmet Ümit"; aramalar: "istanbul", "İSTANBUL", "İstanbul", "umit", "9786053609322" | İlk üç arama aynı sonucu verir; yazar ve ISBN aramaları kitabı bulur | Geçti |
| TC-68 | FR-04 | G07 | servis | Hata tahmini | Olmayan barkod "99999998" ile arama; başlığı güncellenen kitabın yeni başlıkla aranması | İlki hatasız boş sonuç verir; ikincisi kitabı bulur | Geçti |
| TC-69 | FR-06, FR-38 | G08 | birim | Sınır değer (iki değerli) | `render_sheet`, 3×8 yerleşim, 24 ve 25 öğe | 1 ve 2 sayfa | Geçti |
| TC-70 | FR-06 (ADR-0030) | G08 | birim | Denklik sınıfı | Bilinen yerleşimde 3 barkodlu test PDF'i; `decode_pdf_barcodes` | Değerler sayfa sırasıyla, yukarıdan aşağı ve soldan sağa döner | Geçti |
| TC-71 | FR-05, FR-06, AC-06 | G08 | servis (slow) | Senaryo | 30 nüsha seçilir; `label_pdf` | 2 sayfa (24 + 6); çözülen 30 değer seçilen barkodlarla aynı sırada; biçim Code 128 | Geçti |
| TC-72 | FR-06 (faz 4 küçük karar 3) | G08 | servis | Sınır değer (iki değerli) | 30 ve 31 karakterli başlık | Etikette kütüphane adı, 8 haneli kod ve başlığın ilk 30 karakteri bulunur; 31. karakter basılmaz | Geçti |
| TC-73 | FR-23 (ADR-0035) | G08 | servis | Sınır değer | `library_name` = "W" × 80, etiket ve kartta | Metin "…" ile kısaltılır | Geçti |
| TC-74 | FR-38, AC-31 | G08 | servis (slow) | Senaryo | 3 üye; `member_card_pdf` | 3 kart; çözülen değerler üyelerin `member_no` değerleri; PDF metninde ad yok, "Üye No" ve kütüphane adı var | Geçti |
| TC-75 | FR-38 (faz 4 küçük karar 4) | G08 | servis | Sınır değer (iki değerli) | 10 ve 11 üye | 1 ve 2 sayfa | Geçti |
| TC-76 | FR-17, AC-17 | G09 | birim | Denklik sınıfı | `balance`: FINE 1500, PAYMENT 500, WAIVER 500 | 500 | Geçti |
| TC-77 | FR-17 (ADR-0020) | G09 | birim | Hata tahmini | TC-76'ya REFUND 2000 eklenir, sonra CANCELLATION 300 eklenir | REFUND bakiyeyi değiştirmez (500); CANCELLATION'dan sonra 200 | Geçti |
| TC-78 | FR-13 (ADR-0017) | G09 | birim | Denklik sınıfı | `allocate_fifo([(c1,1500),(c2,1000)], 2000)` | [(c1,1500),(c2,500)] | Geçti |
| TC-79 | FR-13 | G09 | birim | Sınır değer | Aynı kalemlerle tutar 1, 2500, 2501 ve 0 | 1 → [(c1,1)]; 2500 → iki kalem de tam; 2501 ve 0 hata verir | Geçti |
| TC-80 | FR-13, AC-13 | G09 | servis | Denklik sınıfı | Borç 40,00 TL; görevli 15,00 TL ödeme alır | Borç 25,00 TL; kayıtta tutar, tarih ve görevlinin adı; PAYMENT denetim kaydı | Geçti |
| TC-81 | FR-13, I1 | G09 | servis | Sınır değer (iki değerli) | Borç 40,00 TL; önce 40,01 TL, sonra 40,00 TL ödeme | 40,01 reddedilir, hareket yazılmaz; 40,00 kabul edilir, borç 0 olur | Geçti |
| TC-82 | FR-13 | G09 | servis | Sınır değer (iki değerli) | 0,00 TL ve 0,01 TL ödeme | 0,00 reddedilir; 0,01 kabul edilir | Geçti |
| TC-83 | FR-13, I2, I3, I4 | G09 | servis | Denklik sınıfı | FINE 1500 (t1), FEE 1000 (t2); 2000 ödeme | Dağıtım FINE 1500, FEE 500; Σ dağıtım = 2000; hiçbir kalemde ödenen tutarı aşmaz; FEE'nin ödenmemiş kısmı 500 | Geçti |
| TC-84 | FR-13 (ADR-0017) | G09 | servis | Hata tahmini | Aynı `created_at` değerine sahip iki kalem; ödeme ilk kalemi kapatmaya yetmez | Ödeme küçük `id`'li kaleme düşer | Geçti |
| TC-85 | FR-13 (ADR-0017) | G09 | servis | Hata tahmini | FINE 1500 tamamen affedilmiş, FEE 1000; 500 ödeme | Dağıtım yalnız FEE'ye | Geçti |
| TC-86 | FR-14, AC-14 | G09 | view | Denklik sınıfı | Görevli oturumuyla af POST'u | 403; WAIVER yazılmaz | Geçti |
| TC-87 | FR-14, AC-14 | G09 | servis | Denklik sınıfı | Yönetici affı, gerekçe "" ve "   " | Af kaydedilmez; gerekçe istenir | Geçti |
| TC-88 | FR-14 (ADR-0021) | G09 | servis | Sınır değer (iki değerli) | 15,00 TL'lik kalemin 5,00'ı ödenmiş (ödenmemiş 10,00); önce 10,01, sonra 10,00 af | 10,01 reddedilir; 10,00 kabul edilir: ödenmemiş 0, o kaleme tek dağıtım | Geçti |
| TC-89 | FR-14 | G09 | servis | Denklik sınıfı | Aynı kaleme 3,00 TL kısmi af | Ödenmemiş 7,00 kalır; bakiye 3,00 azalır | Geçti |
| TC-90 | FR-14 (ADR-0021) | G09 | servis | Hata tahmini | Affın hedefi tamamen ödenmiş bir kalem; hedefi bir PAYMENT hareketi | İkisi de reddedilir | Geçti |
| TC-91 | FR-26, AC-26 | G09 | view | Senaryo | Yönetici "ayse.y" 5,00 TL'yi "Hastalık" gerekçesiyle affeder; `/denetim/` açılır | WAIVER kaydında işlem, 5,00 TL, gerekçe, "ayse.y" ve zaman damgası görünür | Geçti |
| TC-92 | FR-16, I5 (ADR-0020, ADR-0037) | G09 | servis | Denklik sınıfı | 120,00 TL bedel; ödüncü LOST ile kapanmış ve `copy_found_on` dolu (factory); 20,00'ı ödenmiş; `cancel_unpaid` | Bedele hedefli 100,00 CANCELLATION ve tek dağıtım; `refundable` 20,00 | Geçti |
| TC-93 | FR-16, FR-26 (ADR-0020, ADR-0027, ADR-0037) | G09 | servis | Denklik sınıfı | TC-92'den sonra yönetici 20,00 TL para iadesi yapar | REFUND kaydı; bakiye değişmez; `refundable` 0; REFUND denetim kaydı | Geçti |
| TC-94 | FR-16, I5 (ADR-0037) | G09 | servis | Sınır değer (iki değerli) | TC-92 kurulumu, `refundable` 20,00: 20,01; sonra 15,00; sonra 5,01; sonra 5,00 | 20,01 ve 5,01 "Para iadesi, ödenmiş ve henüz iade edilmemiş tutarı aşamaz" ile reddedilir; 15,00 ve 5,00 kabul edilir; toplam iade 20,00 | Geçti |
| TC-95 | FR-16, I5 (ADR-0037) | G09 | servis | Hata tahmini | REFUND hedefi: ödüncü LOST ile kapanmış ama `copy_found_on` NULL bedel (nüsha hâlâ kayıp); ayrı testte FINE kalemi | İkisi de reddedilir; bedelde mesaj "Para iadesi yalnız bulunan kayıp nüshanın bedeli için yapılabilir"; hareket yazılmaz | Geçti |
| TC-96 | FR-16, I5 (ADR-0037) | G09 | servis | Hata tahmini | 120,00 TL bedel (ödünç LOST, `copy_found_on` dolu); 20,00'ı ödenmiş, 10,00'ı affedilmiş; `cancel_unpaid` | CANCELLATION 90,00; `refundable` 20,00 (affedilen kısım iade edilmez) | Geçti |
| TC-97 | FR-16 (ADR-0020) | G09 | view | Denklik sınıfı | Görevli oturumuyla para iadesi POST'u | 403 | Geçti |
| TC-98 | FR-17, AC-17 | G09 | view | Senaryo | 15,00 ceza, 5,00 ödeme, 5,00 af; borç sayfası açılır | Güncel borç "5,00 TL"; üç hareket tarihleriyle listelenir | Geçti |
| TC-99 | FR-17 | G09 | view | Denklik sınıfı | Döküme CANCELLATION ve REFUND hareketleri eklenmiş | İkisi de listelenir; REFUND güncel borcu değiştirmez | Geçti |
| TC-100 | FR-13, I1 | G09 | servis | Senaryo | Sırayla ceza, kısmi ödeme, af, bedel, iptal, para iadesi | Her adımdan sonra domain `balance` = S3 SQL sonucu ≥ 0 | Geçti |
| TC-101 | FR-17, I6 | G09 | servis | Senaryo | TC-100'den önce ledger_entry ve allocation satırlarının anlık görüntüsü alınır | Önceki satırlar alan alan aynı kalır; yalnız yeni satırlar eklenir. I6'nın tek istisnası (saklama görevinin `loan_id` bağını koparması, ADR-0018) TC-202'de | Geçti |
| TC-102 | NFR-12 | G09 | servis | Hata tahmini | 3 × 5,00 TL ceza, 15,00 TL ödeme | Bakiye tam 0 (`int`), "0,00 TL" | Geçti |
| TC-103 | FR-13, I1 | G09 | servis (eşzamanlı) | Hata tahmini | Borç 10,00; iki iş parçacığı aynı anda 6,00 öder | Biri kabul edilir, diğeri borçtan fazla diye reddedilir; borç 4,00 | Geçti |
| TC-104 | FR-07 | G10 | birim | Denklik sınıfı | `due_date(2026-11-02, 14, kapalı gün yok)` | 2026-11-16 | Geçti |
| TC-105 | FR-07, AC-07 | G10 | birim | Denklik sınıfı | Süre 13, pazar kapalı, başlangıç 2026-11-02 | 2026-11-16 | Geçti |
| TC-106 | FR-24, AC-24 | G10 | birim | Denklik sınıfı | Pazar ve 2027-10-29 kapalı; 2027-10-15 + 14 | 2027-10-30 | Geçti |
| TC-107 | FR-07 | G10 | birim | Hata tahmini | Cumartesi ve pazar haftalık kapalı, 2026-11-16 tek tarih kapalı; 2026-10-31 + 14 | 2026-11-17 (salı) | Geçti |
| TC-108 | FR-07 | G10 | birim | Hata tahmini | 2028-02-20 + 14; 2026-12-25 + 14 | 2028-03-05; 2027-01-08 | Geçti |
| TC-109 | FR-07 (ADR-0028) | G10 | birim | Sınır değer | Aday + 0…365 kapalı, aday + 366 açık; ayrı testte aday + 0…366 kapalı | İlkinde aday + 366 döner; ikincisinde `NoOpenDayError` | Geçti |
| TC-110 | FR-12, AC-12 (ADR-0040) | G10 | birim | Sınır değer (üç değerli) | `late_days(2026-11-16, on, frozenset())`, on = 11-15, 11-16, 11-17 | 0, 0, 1 | Geçti |
| TC-111 | FR-12, AC-09 (ADR-0040) | G10 | birim | Denklik sınıfı | `late_days(2026-11-16, 2026-11-19, frozenset())` | 3 | Geçti |
| TC-112 | FR-12, AC-12 | G10 | birim | Sınır değer (üç değerli) | `fine(gün, 500, 15000)`, gün = 0, 29, 30, 31, 40 | 0, 14500, 15000, 15000, 15000 | Geçti |
| TC-113 | FR-12 | G10 | birim | Hata tahmini | Oran 0; üst sınır 0; 100000 gün | 0; 0; 15000 | Geçti |
| TC-114 | FR-08 | G10 | birim | Karar tablosu | Aktif üye, açık 2/limit 3, gecikme yok, borç 4999/eşik 5000, nüsha ON_SHELF | Engel yok | Geçti |
| TC-115 | FR-02, AC-02 | G10 | birim | Karar tablosu | Yalnız üye pasif | ["Üye pasif"] | Geçti |
| TC-116 | FR-08, AC-08 | G10 | birim | Karar tablosu | Yalnız açık 3/limit 3 (ve 4/limit 3) | ["Ödünç limiti dolu"] | Geçti |
| TC-117 | FR-08, AC-08 | G10 | birim | Karar tablosu | Yalnız gecikmiş ödünç var | ["Gecikmiş ödünç var"] | Geçti |
| TC-118 | FR-08, AC-08 | G10 | birim | Karar tablosu | Yalnız borç 5000/eşik 5000 (ve 5001) | ["Borç eşiği aşıldı"] | Geçti |
| TC-119 | FR-08, AC-08 | G10 | birim | Karar tablosu | Yalnız nüsha ON_LOAN, LOST, DAMAGED ya da WITHDRAWN (her biri ayrı) | ["Nüsha rafta değil"] | Geçti |
| TC-120 | FR-10 | G10 | birim | Karar tablosu | `renewed_on` boş, son tarih = bugün, borç 0 | Engel yok | Geçti |
| TC-121 | FR-10, AC-10 | G10 | birim | Karar tablosu | Yalnız `renewed_on` dolu | ["Uzatma hakkı kullanıldı"] | Geçti |
| TC-122 | FR-10 (KL-6) | G10 | birim | Karar tablosu | Yalnız son tarih = bugün − 1 | ["Ödünç gecikmiş"] | Geçti |
| TC-123 | FR-10, AC-10 | G10 | birim | Karar tablosu | Yalnız borç 200 (ve 1) kuruş | ["Ödenmemiş borç var"] | Geçti |
| TC-124 | FR-07, FR-08 (ADR-0023) | G11 | servis | Denklik sınıfı | Bugün 2026-11-02; aktif üye ve ON_SHELF nüshayla `check_out` | Ödünç son tarihi 2026-11-16; 500/15000 oran kopyası; `created_by` = aktör; nüsha ON_LOAN | Geçti |
| TC-125 | FR-08 | G11 | servis | Sınır değer (iki değerli) | Üyenin açık ödüncünün son tarihi bugün; ayrı testte dün | Bugün: ödünç verilir; dün: "Gecikmiş ödünç var" | Geçti |
| TC-126 | FR-02, FR-08, AC-02, AC-08 | G11 | servis | Denklik sınıfı | Veritabanı durumundan (S2, S3): pasif üye, AC-08'in üç örneği, Ödünçte nüsha | Her biri kendi nedeniyle reddedilir; ödünç satırı yazılmaz, nüsha durumu değişmez | Geçti |
| TC-127 | FR-08, AC-08 | G11 | view | Denklik sınıfı | Engeli olan üye için POST `/odunc/` | 200; form aynı ekranda neden metniyle gösterilir; ödünç yazılmaz | Geçti |
| TC-128 | FR-11, AC-11, NFR-11 | G11 | view | Senaryo | GET `/odunc/?uye=<no>`, nüsha önizlemesi, ardından POST (üye, barkod) | Üye ve engeller görünür, `autofocus` nüsha alanında; POST 303 → `/odunc/`, "Son tarih 16.11.2026", odak üye alanına döner | Geçti |
| TC-129 | FR-11 | G11 | view | Denklik sınıfı | Ödünç ekranında "ayşe" ile üye aranır, sonuçtan seçilir | Seçilen üyeye ödünç verilir | Geçti |
| TC-130 | FR-11 | G11 | view | Hata tahmini | Olmayan üye no "999999"; olmayan barkod "99999999"; " 00000042" (başında boşluk) | İlk ikisinde hata mesajı, ödünç yok; üçüncüsünde boşluk kırpılır ve nüsha bulunur | Geçti |
| TC-131 | FR-23, AC-23 | G11 | servis | Senaryo | Süre 14 iken verilen ödünç (son tarih 2026-11-16); süre 21 yapılır; 2026-11-02'de yeni ödünç | Yeni ödüncün son tarihi 2026-11-23; eskisi 2026-11-16 kalır | Geçti |
| TC-132 | FR-12 (ADR-0023) | G11 | servis | Senaryo | Ödünç günlük ceza 5,00 iken verilir; ceza 10,00 yapılır; 3 gün gecikmeli iade | Ceza 15,00 TL | Geçti |
| TC-133 | FR-07 (ADR-0028) | G11 | servis | Hata tahmini | Kapalı günler 366 gün içinde açık gün bırakmıyor; `check_out` | "Önümüzdeki 366 günde açık gün yok; kapalı gün ayarlarını kontrol edin"; ödünç yazılmaz, nüsha ON_SHELF kalır | Geçti |
| TC-134 | FR-09, AC-12 | G11 | servis | Sınır değer | Son tarih 2026-11-16, iade 2026-11-16 | Ödünç RETURNED olarak kapanır, `closed_on` 11-16; nüsha ON_SHELF; FINE yok | Geçti |
| TC-135 | FR-09, AC-09 | G11 | view | Denklik sınıfı | Son tarih 2026-11-16, günlük ceza 5,00; iade 2026-11-19 | Ödünç kapanır, nüsha ON_SHELF; ödünce ve üyeye bağlı 15,00 TL FINE; "İade alındı; 15,00 TL ceza yazıldı" | Geçti |
| TC-136 | FR-12, AC-12 | G11 | servis | Sınır değer | Günlük ceza 5,00, üst sınır 150,00; 40 gün gecikmeli iade | FINE 150,00 TL | Geçti |
| TC-137 | FR-12 | G11 | servis | Hata tahmini | Ödüncün oran kopyası 0; 5 gün gecikmeli iade | Ödünç kapanır; FINE yazılmaz | Geçti |
| TC-138 | FR-09 | G11 | servis | Hata tahmini | Raftaki nüshanın barkoduyla iade; olmayan barkodla iade | Hata döner; hiçbir kayıt değişmez | Geçti |
| TC-139 | FR-10 | G11 | servis | Denklik sınıfı | Son tarih 11-16, süre 14; 2026-11-10'da uzatma | Yeni son tarih 2026-11-30; `renewed_on` 11-10; oran kopyası aynı kalır | Geçti |
| TC-140 | FR-07, FR-10 (küçük karar 3) | G11 | servis | Denklik sınıfı | Süre 13, pazar kapalı; son tarihi 11-16 olan ödünç uzatılır | 11-29 pazar olduğu için 2026-11-30 | Geçti |
| TC-141 | FR-10, AC-10 | G11 | servis | Durum geçişi | Bir kez uzatılmış ödünç yeniden uzatılır | "Uzatma hakkı kullanıldı"; son tarih değişmez | Geçti |
| TC-142 | FR-10, AC-10 | G11 | servis | Denklik sınıfı | Üyenin 2,00 TL borcu var, ödünç gecikmemiş | "Ödenmemiş borç var" | Geçti |
| TC-143 | FR-10 (KL-6) | G11 | servis | Sınır değer (iki değerli) | Bugün = son tarih; bugün = son tarih + 1 | İlkinde uzatılır; ikincisinde "Ödünç gecikmiş" ile reddedilir | Geçti |
| TC-144 | FR-10 | G11 | servis | Hata tahmini | Kapanmış ödüncü uzatma; 366 gün içinde açık gün yokken uzatma | İkisi de reddedilir (ikincisi ADR-0028 mesajıyla); değişiklik olmaz | Geçti |
| TC-145 | FR-08 (data-design §5) | G11 | servis (eşzamanlı) | Hata tahmini | Dosya tabanlı SQLite; iki iş parçacığı aynı nüshayı aynı anda iki üyeye verir | Tek açık ödünç; diğer istek "Nüsha rafta değil" alır; 500 ya da `IntegrityError` dışarı sızmaz | Geçti |
| TC-146 | FR-08 | G11 | servis (eşzamanlı) | Hata tahmini | Üyenin 2/3 açık ödüncü var; iki farklı nüsha aynı anda verilir | Biri verilir, diğeri "Ödünç limiti dolu"; açık ödünç sayısı 3 | Geçti |
| TC-147 | FR-09 | G11 | servis (eşzamanlı) | Hata tahmini | 3 gün gecikmiş ödünce aynı anda iki iade | Tek kapanış ve tek 15,00 TL FINE; ikinci istek hata alır | Geçti |
| TC-148 | FR-10 | G11 | servis (eşzamanlı) | Hata tahmini | Aynı ödünce aynı anda iki uzatma | Son tarih bir kez ilerler; ikinci istek "Uzatma hakkı kullanıldı" alır | Geçti |
| TC-149 | FR-08 (data-design §2.4) | G11 | servis | Hata tahmini | ORM ile aynı nüshaya doğrudan ikinci açık ödünç eklenir | `IntegrityError` (kısmi benzersiz indeks) | Geçti |
| TC-150 | FR-15, AC-15 (KL-15, KL-44) | G12 | servis | Durum geçişi | 10 gün gecikmiş ödünç, günlük ceza 5,00, kapalı tarih yok; yönetici 120,00 TL bedelle kayıp işaretler | Ödünç LOST olarak kapanır, nüsha LOST; FINE 50,00 ve FEE 120,00; FEE denetim kaydı ve `details.fee_kurus = 12000` taşıyan COPY_LOST kaydı | Geçti |
| TC-151 | FR-15 (KL-15) | G12 | servis | Durum geçişi | Gecikmemiş ödünç; 50,00 TL bedelle hasarlı işaretlenir | Ödünç DAMAGED olarak kapanır, nüsha DAMAGED; yalnız FEE 50,00; FEE denetim kaydı ve COPY_DAMAGED kaydı | Geçti |
| TC-152 | FR-12, FR-15 | G12 | servis | Sınır değer | Kayıp işaretleme son tarihte, 1 gün sonra ve 40 gün sonra | FINE yok; 5,00; 150,00 | Geçti |
| TC-153 | FR-16, AC-16 (ADR-0037) | G12 | servis | Durum geçişi | Gecikmeden kaybolmuş nüshanın 120,00 bedelinin 20,00'ı ödenmiş (açık kalem yalnız bu bedel); görevli bulundu işaretler | Nüsha ON_SHELF; ödüncün `copy_found_on` = bugün; 100,00 CANCELLATION; `FoundResult(cancelled_kurus=10000, refundable_kurus=2000)`; COPY_FOUND | Geçti |
| TC-154 | FR-16 (ADR-0026) | G12 | servis | Durum geçişi | Raftayken kayıp işaretlenmiş (bedelsiz) nüsha bulunur | ON_SHELF; CANCELLATION yazılmaz | Geçti |
| TC-155 | FR-16, AC-16 (ADR-0037) | G12 | servis | Hata tahmini | Bedeli (120,00) tamamen ödenmiş kayıp nüsha bulunur | ON_SHELF; CANCELLATION yazılmaz; `copy_found_on` dolu; `FoundResult(cancelled_kurus=0, refundable_kurus=12000)` | Geçti |
| TC-156 | FR-16 (ADR-0018, ADR-0041) | G12 | servis | Hata tahmini | Kayıp ödüncün ve bedelinin bağı saklama görevince koparılmış (bedelin `loan_id` NULL); nüsha bulunur | ON_SHELF; ödüncün `copy_found_on` dolar; CANCELLATION yazılmaz, bedel kalır; `cancelled_kurus=0`, `refundable_kurus=0` | Geçti |
| TC-157 | FR-16, FR-26 | G12 | servis | Durum geçişi | Bedelli hasarlı nüshayı yönetici onarıldı işaretler | ON_SHELF; bedel değişmez; COPY_REPAIRED | Geçti |
| TC-158 | FR-16, FR-26 | G12 | servis | Durum geçişi | Bedelli hasarlı nüshayı yönetici kayıttan düşer | WITHDRAWN; bedel değişmez; COPY_WITHDRAWN | Geçti |
| TC-159 | FR-39, AC-32 | G12 | view | Durum geçişi | "00000042" Rafta; yönetici Kayıp işaretler | LOST; hiçbir üyenin borcu değişmez; ödünç oluşmaz; COPY_LOST kaydında `{"from": "ON_SHELF"}`, nüsha, yönetici ve zaman damgası | Geçti |
| TC-160 | FR-39 | G12 | servis | Durum geçişi | Rafta → Hasarlı; Rafta → Kayıttan düşmüş; Kayıp → Kayıttan düşmüş (notlu ve notsuz) | Durum değişir; ledger ve ödünç satırı oluşmaz; uygun COPY_* kaydı yazılır, varsa not ayrıntıda yer alır | Geçti |
| TC-161 | FR-39, AC-32 | G12 | view | Denklik sınıfı | Görevli, Raftaki "00000042" için Kayıttan düşmüş POST'u gönderir | 403; nüsha ON_SHELF kalır | Geçti |
| TC-162 | FR-15, FR-16 | G12 | view | Karar tablosu | Görevli bulundu POST'u ve onarıldı POST'u gönderir | Bulundu kabul edilir (303); onarıldı 403 alır | Geçti |
| TC-163 | FR-05 (mimari §5.1) | G12 | servis | Durum geçişi | ON_SHELF nüshada onarıldı ve bulundu; `check_in` | `InvalidTransition`; iade hata verir; nüsha ON_SHELF kalır | Geçti |
| TC-164 | FR-05 | G12 | servis | Durum geçişi | ON_LOAN nüshada `mark_shelf_copy` (LOST, DAMAGED, WITHDRAWN), onarıldı, bulundu; başka üyeye ödünç | `InvalidTransition`; ödünçte "Nüsha rafta değil"; açık ödünç ve durum aynı kalır | Geçti |
| TC-165 | FR-05 | G12 | servis | Durum geçişi | LOST nüshada onarıldı, hasarlı, yeniden kayıp; ödünç; iade | `InvalidTransition`; ödünçte "Nüsha rafta değil"; iade hata verir; nüsha LOST kalır | Geçti |
| TC-166 | FR-05 | G12 | servis | Durum geçişi | DAMAGED nüshada bulundu ve kayıp; ödünç | `InvalidTransition`; ödünçte "Nüsha rafta değil"; nüsha DAMAGED kalır | Geçti |
| TC-167 | FR-05 (ADR-0026) | G12 | servis | Durum geçişi | WITHDRAWN nüshada bulundu, onarıldı, kayıp, hasarlı, kayıttan düşme; ödünç | Hepsi reddedilir; nüsha WITHDRAWN kalır | Geçti |
| TC-168 | FR-05, FR-16 | G12 | servis | Durum geçişi (1-switch) | Rafta → Ödünçte → Kayıp → (bulundu) Rafta → başka üyeye Ödünçte | Son ödünç verilir; ilk ödüncün cezası kalır | Geçti |
| TC-169 | FR-05, FR-16 | G12 | servis | Durum geçişi (1-switch) | Ödünçte → Hasarlı (bedelli) → Rafta (onarıldı) → Ödünçte | Ödünç verilir; bedel kalır | Geçti |
| TC-170 | FR-26 (KL-30, KL-31) | G12 | servis | Denklik sınıfı | 14 eylemin her biri birer kez: PAYMENT, WAIVER, FEE, REFUND, CANCELLATION, COPY_LOST, COPY_DAMAGED, COPY_FOUND, COPY_REPAIRED, COPY_WITHDRAWN, MEMBER_REACTIVATED, SETTINGS_CHANGED, CLOSED_DAY_CHANGED, STAFF_CHANGED | Her biri için doğru `action`, `actor`, `occurred_at` ve KL-15'teki hedef; hiçbir ayrıntıda üye ve ödünç birlikte bulunmaz | Geçti |
| TC-171 | FR-20, AC-20 | G13 | view | Denklik sınıfı | Bugün 2026-11-20; 3 ve 10 gün gecikmiş birer ödünç, 1 gecikmemiş, 1 son tarihi bugün olan ödünç | Yalnız iki satır: üye, telefon, kitap, son tarih, 3/10 gün, 15,00/50,00 TL; son tarihe göre sıralı (10 günlük önce) | Geçti |
| TC-172 | FR-20 (ADR-0023) | G13 | servis | Sınır değer | 40 gün gecikmiş ödünç; oran kopyası 5,00, ayar sonradan 10,00 yapılmış | Birikmiş ceza 150,00 TL | Geçti |
| TC-173 | FR-18 | G13 | birim | Sınır değer | `due_reminder_kind(2026-11-16, bugün)`, bugün = 11-13, 11-14, 11-15, 11-16, 11-17, 11-23, 11-24 | None, DUE_SOON, DUE_SOON, DUE_SOON, OVERDUE_1, OVERDUE_1, None | Geçti |
| TC-174 | FR-18, AC-18 (ADR-0039) | G13 | servis | Senaryo | Son tarih 11-16; üyenin rızası ve e-postası var; `send_due_reminders(2026-11-14)` iki kez çalışır | İlk çalışmada 1 e-posta ve `due_on` = 11-16 olan DUE_SOON SENT kaydı; ikinci çalışmada e-posta yok | Geçti |
| TC-175 | FR-18, AC-18 | G13 | servis | Denklik sınıfı | Üyenin e-postası var, rızası yok | E-posta da kayıt da yok | Geçti |
| TC-176 | FR-18 | G13 | servis | Denklik sınıfı | Rızası var, e-postası yok; ayrı testte pencere içinde ama kapanmış ödünç | E-posta yok | Geçti |
| TC-177 | FR-03, AC-03 | G13 | servis | Senaryo | Rıza 2026-11-01'de verilmiş, 2026-12-01'de geri alınmış; son tarih 12-03; görev 12-01'de (geri almadan sonra) ve 12-02'de çalışır | E-posta gönderilmez | Geçti |
| TC-178 | NFR-05, FR-18 | G13 | servis | Senaryo | Son tarih 11-16; sunucu 11-14…11-16 kapalı; görev ilk kez 11-17'de çalışır | DUE_SOON gönderilmez; OVERDUE_1 gönderilir | Geçti |
| TC-179 | NFR-05 | G13 | servis | Senaryo | OVERDUE_1 11-17'de SENT; görev 11-18…11-23 arasında her gün çalışır | Ek e-posta yok | Geçti |
| TC-180 | FR-18 (küçük karar 7, KL-23) | G13 | komut | Hata tahmini | 11-14'te SMTP hata fırlatır; 11-15'te SMTP çalışır | 11-14: hata metniyle FAILED kaydı, çıkış kodu 1, `job_run` SUCCESS; 11-15: SENT; toplam 1 SENT | Geçti |
| TC-181 | FR-18 (data-design §5) | G13 | servis | Hata tahmini | Gönderimden sonra SENT kaydı benzersiz kısıta takılır (eşzamanlı çalışma) | İstisna fırlatılmaz; gönderilmiş sayılır; sonraki çalışmada e-posta yok | Geçti |
| TC-182 | FR-18, AC-18 (ADR-0039) | G13 | servis | Senaryo | Son tarih 11-16; DUE_SOON 11-14'te SENT; ödünç 11-15'te uzatılır (yeni son tarih 11-30); görev 11-28'de çalışır | Yeni son tarih için DUE_SOON gönderilir; iki SENT kaydı, `due_on` 11-16 ve 11-30 | Geçti |
| TC-183 | FR-19, AC-19 | G13 | view | Senaryo | Geciken listede biri rızalı, biri rızasız iki ödünç seçilir; "hatırlatma gönder" | Yalnız rızalı üyeye e-posta; rızasız üye için "rıza yok"; `triggered_by` dolu MANUAL kaydı | Geçti |
| TC-184 | FR-19 (KL-28) | G13 | servis | Sınır değer | Aynı ödünce iki kez elle hatırlatma; sonra otomatik OVERDUE_1 penceresi | İki MANUAL SENT kaydı (ikisinde de `due_on` dolu) ve iki e-posta; OVERDUE_1 yine gönderilir | Geçti |
| TC-185 | FR-18 (mimari §6.2) | G13 | komut | Denklik sınıfı | `send_reminders --date 2026-11-14`, SMTP sorunsuz | Çıkış 0; gönderilen, başarısız ve atlanan sayıları yazılır; verilen tarih kullanılır | Geçti |
| TC-186 | FR-28 | G14 | komut | Denklik sınıfı | `backup_db --date 2026-11-02` | `LIBRARY_BACKUP_DIR/library-20261102.sqlite3` oluşur; `integrity_check` ok; üye, nüsha ve ödünç sayıları kaynakla aynı; çıkış 0 | Geçti |
| TC-187 | FR-28 (KL-14) | G14 | komut | Sınır değer (iki değerli) | Bugün 2026-12-31; bugün − 30 ve bugün − 31 tarihli yedekler ile `notlar.txt` var; yedek başarılı | −31 silinir; −30 ve `notlar.txt` kalır | Geçti |
| TC-188 | FR-28 | G14 | komut | Hata tahmini | Yedek klasörü yok ya da yazılamaz; eski yedekler var | Çıkış 1; eski dosyalar silinmez | Geçti |
| TC-189 | FR-28 | G14 | komut | Hata tahmini | Yedek ve dışa aktarma yolunda boşluk ve Türkçe karakter var ("Yedek Klasörü Ğüş") | Çıkış 0; dosya doğru yerde | Geçti |
| TC-190 | FR-28, NFR-03 | G14 | komut | Hata tahmini | Yedek alınırken başka bir iş parçacığında açık yazma işlemi var | Yedek tamamlanır; içeriği commit edilmiş bir duruma eşit; `integrity_check` ok | Geçti |
| TC-191 | FR-28, AC-28 | G14 | komut | Senaryo | Yedek alınır, test veritabanı silinir, `restore_backup <yedek>.sqlite3 --yes` | Çıkış 0; üye, nüsha ve ödünç sayıları yedek anındakiyle aynı | Geçti |
| TC-192 | FR-37 (mimari §6.3) | G14 | komut | Denklik sınıfı | `export_backup --passphrase-file F` | `library-export-YYYYMMDD.libx`; başlık `LIBX`, `0x01`, büyük endian n=2^17, r=8, p=1, 16 bayt salt, 12 bayt nonce | Geçti |
| TC-193 | FR-37, AC-30 | G14 | komut | Senaryo | TC-192'nin dosyası doğru parolayla boş test ortamına geri yüklenir | Çıkış 0; sayılar aynı | Geçti |
| TC-194 | FR-37, AC-30 | G14 | komut | Denklik sınıfı | Yanlış parolayla geri yükleme | Çıkış 1; veritabanı değişmez | Geçti |
| TC-195 | FR-37 (ADR-0011) | G14 | komut | Hata tahmini | Başlıkta (salt ya da kdf alanında) bir bayt değiştirilir; ayrı testte şifreli metinde bir bayt | İkisinde de doğrulama hatası, çıkış 1; veritabanı değişmez | Geçti |
| TC-196 | FR-37 (mimari §6.3) | G14 | komut | Hata tahmini | Sürüm baytı `0x02`; magic "LIBY"; başlıktan kısa dosya | Hepsi reddedilir, çıkış 1 | Geçti |
| TC-197 | FR-37 | G14 | komut | Hata tahmini | Aynı yedekten iki dışa aktarma | Salt, nonce ve şifreli metin farklı | Geçti |
| TC-198 | FR-37 | G14 | komut | Hata tahmini | Günlük yedek yok; ayrı testte parola dosyası yok | Çıkış 1; `.libx` oluşmaz | Geçti |
| TC-199 | FR-28 (KL-4, R-13) | G14 | komut | Durum geçişi | Uygulama kilidi başka bir süreçte tutulurken `restore_backup ... --yes` | "Uygulama çalışıyor; önce servisi durdurun", çıkış 1; veritabanı değişmez | Geçti |
| TC-200 | FR-28 (faz 4 küçük karar 6) | G14 | komut | Denklik sınıfı | PATH'siz ve `--yes`'siz `restore_backup` | Çıkış 2; veritabanı değişmez | Geçti |
| TC-201 | FR-25, AC-25 | G15 | komut | Sınır değer (iki değerli) | Saklama 2 yıl; borçsuz üye 2026-11-01'de pasifleştirilmiş; görev 2028-11-01 ve 2028-11-02'de çalışır | 11-01: değişiklik yok. 11-02: ad, telefon, `phone_digits` ve e-posta NULL, `search_key` "", `has_email_consent` False, `anonymized_at` dolu, rıza olayları silinmiş; borç hareketleri ve tutarlar kalır | Geçti |
| TC-202 | FR-25, AC-25 (ADR-0018) | G15 | komut | Sınır değer (iki değerli) | Ödünç 2026-11-01'de iade edilmiş; görev 2028-11-01 ve 2028-11-02'de çalışır | 11-01: bağ kalır. 11-02: `member_id` NULL, `member_unlinked_at` dolu, `archived_loan_count` +1; bağlı hareketlerde `loan_id` NULL, `member_id` aynı | Geçti |
| TC-203 | FR-25, AC-25 | G15 | komut | Metamorfik ilişki | Görevden önce ve sonra üyenin bağlı ödünç sayısı + `archived_loan_count` | Toplam değişmez; ödünç ve nüsha satırları silinmez | Geçti |
| TC-204 | FR-25 (ADR-0018) | G15 | komut | Hata tahmini | Görev aynı gün ikinci kez çalışır | 0 üye, 0 ödünç işlenir; sayaç değişmez | Geçti |
| TC-205 | FR-25 | G15 | komut | Denklik sınıfı | Aktif üyenin 3 yıl önce iade edilmiş ödüncü; 3 yıl önce verilmiş ama hâlâ açık ödünç; 1 yıl önce pasifleşmiş üye | İlkinin bağı kopar, üye anonimleşmez; açık ödünç bağlı kalır; 1 yıllık pasif üye anonimleşmez | Geçti |
| TC-206 | FR-25, NFR-08 | G15 | servis | Hata tahmini | Anonimleşen üyenin eski adı ve telefonuyla arama | Bulunmaz; `search_key` boş metin | Geçti |
| TC-207 | FR-25 (data-design §5) | G15 | komut | Hata tahmini | İkinci ödünç işlenirken istisna fırlatılır | Hatalı kayıtta bağ ve sayaç birlikte geri alınır; önceki kayıt işlenmiş kalır; çıkış 1 | Geçti |
| TC-208 | FR-18, FR-25, FR-28, FR-37 (küçük karar 13) | G16 | servis | Denklik sınıfı | `LIBRARY_SCHEDULER_ENABLED=1` ile `start_scheduler()` | Europe/Istanbul saatiyle BACKUP 02:00, ANONYMIZE 02:30, REMINDERS 09:00, EXPORT pazartesi 03:00 | Geçti |
| TC-209 | NFR-05 (ADR-0007) | G16 | servis | Denklik sınıfı | `LIBRARY_SCHEDULER_ENABLED` tanımsız ya da 0; ayrıca bir management command çalıştırılır | Zamanlayıcı başlamaz | Geçti |
| TC-210 | NFR-05 | G16 | servis | Sınır değer (iki değerli) | Son REMINDERS SUCCESS dün; uygulama 08:59'da ve 09:01'de açılır | 08:59: telafi yok; 09:01: görev bir kez çalışır | Geçti |
| TC-211 | NFR-05 | G16 | servis | Durum geçişi | Son REMINDERS SUCCESS bugün; ayrı testte dünkü çalışma FAILED ve bugün SUCCESS yok (saat geçmiş) | İlkinde çalışmaz; ikincisinde çalışır | Geçti |
| TC-212 | NFR-05 | G16 | servis | Senaryo | Telafi 10:00'da çalışır; uygulama aynı gün yeniden açılır | İkinci açılışta çalışmaz; ek e-posta yok | Geçti |
| TC-213 | NFR-05 (data-design §2.6) | G16 | servis | Durum geçişi | Görev başarıyla biter; ayrı testte istisna fırlatır | job_run RUNNING → SUCCESS (`run_on`, `finished_at`, sayımlar) ya da FAILED (hata metniyle) | Geçti |
| TC-214 | FR-29 (ADR-0033) | G17 | birim | Denklik sınıfı | Başlığı ya da yazarı boş kayıt; başlıkta ya da yazarda "¿", "Ã", "Å", "�" geçen kayıt | Atılır (kural 1 ve 2) | Geçti |
| TC-215 | FR-29 (ADR-0033) | G17 | birim | Denklik sınıfı | Türkçe harf içermeyen kayıt; `parse_isbn` ile geçersiz ISBN | Atılır (kural 3 ve 4) | Geçti |
| TC-216 | FR-29 (ADR-0033) | G17 | birim | Sınır değer | Aynı ISBN'li iki kayıt; filtreden geçen 301 kayıt | İlk kayıt tutulur; ilk 300 yazılır; `_meta` kaynak, sorgu, çekim tarihi, lisans ve filtre sürümünü içerir | Geçti |
| TC-217 | FR-29, AC-29 (ADR-0038, KL-16) | G17 | komut | Senaryo | Boş veritabanında aktif "demo" personeliyle `load_seed_data --profile demo --actor demo --seed 42` | Çıkış 0; 300 kitap, kitap başına 1–3 nüsha, 200 üye, 150 açık ödünç (10'u gecikmiş); OL kitaplarında `source_ol_id`; üye adları `seed/` listelerinden | Geçti |
| TC-218 | FR-29 | G17 | komut | Hata tahmini | İki ayrı boş veritabanında `--actor demo --seed 42` | Üye, kitap, nüsha ve ödünç içerikleri birebir aynı | Geçti |
| TC-219 | FR-29 (ADR-0033) | G17 | komut | Hata tahmini | JSON'da 280 kayıt; ağ erişimi socket düzeyinde engelli; `--actor demo` | 20 sentetik kitap eklenir ve çıktıda bildirilir; ağ çağrısı yapılmaz | Geçti |
| TC-220 | NFR-02 (ADR-0031, KL-16) | G17 | komut (slow) | Denklik sınıfı | `--profile load --actor demo --seed 42` | 15.000 kitap, 20.000 nüsha, 5.000 üye, 100.000 ödünç (3.000'i açık, 300'ü gecikmiş) | Geçti |
| TC-221 | NFR-01 (ADR-0031) | G18 | birim | Sınır değer (iki değerli) | Rapor mantığı: bir türde p95 499 ms ve 500 ms; hata sayısı 0 ve 1; ayrıca istek yapılmamış bir tür | 499 ms ve 0 hata: çıkış 0; 500 ms, 1 hata ya da istek yapılmamış tür: çıkış 1; rapor `istek, p50, p95, hata` sütunlarını ve sonuç satırını içerir | Geçti |
| TC-222 | NFR-01 | G18 | birim | Denklik sınıfı | Bir türde 96 × 100 ms ve 4 × 900 ms | p95 = 100 ms; istek sayısı 100 | Geçti |
| TC-223 | NFR-01, NFR-02 | G18 | elle | Senaryo | Faz 6: sunucuda `--profile load`, ardından `scripts/loadtest.py --workers 5 --duration 120` | Bütün türlerde p95 < 500 ms, hata 0, çıkış 0; `EXPLAIN QUERY PLAN` S1–S3'te indeks kullanır | Planlandı |
| TC-224 | NFR-13 | G01 (her görevde) | komut | Denklik sınıfı | `coverage run --branch -m pytest`, ardından `coverage report --include="*/domain.py" --fail-under=90` | Çıkış 0; dal kapsamı ≥ %90 | Planlandı |
| TC-225 | FR-28, NFR-04, AC-28 | G19 | elle | Senaryo | Faz 6 test ortamı: veritabanı silinir, kurulum belgesindeki adımlarla son yedek geri yüklenir; süre ölçülür | Sayılar aynı; toplam süre < 1 saat | Planlandı |
| TC-226 | FR-37, AC-30 | G19 | elle | Senaryo | `.libx` USB ile başka makineye taşınır ve belgeye göre geri yüklenir | Sayılar aynı; parola olmadan açılmaz | Planlandı |
| TC-227 | FR-11, AC-11, NFR-11 | G19 | elle | Senaryo | Gerçek USB okuyucuyla üye kartı ve nüsha etiketi okutulur, Enter'a basılır | Ödünç kaydedilir; en fazla 3 etkileşim; fare kullanılmaz | Planlandı |
| TC-228 | FR-06, FR-38, AC-06, AC-31 | G19 | elle | Senaryo | Etiket ve kart PDF'leri gerçek etiket kağıdına basılır, okuyucuyla taranır | Her barkod doğru kodu verir; etiketler kağıda hizalı | Planlandı |
| TC-229 | NFR-08 | G19 | elle | Senaryo | LAN dışından 443, 80 ve 8000 portlarına bağlantı denenir; sunucuda dinlenen portlar listelenir | Erişim yok; waitress yalnız 127.0.0.1:8000'i dinler | Planlandı |
| TC-230 | NFR-06, NFR-08 (ADR-0005) | G19 | elle | Senaryo | Personel bilgisayarından `http://` ile erişim; sertifika kontrolü | HTTPS'e yönlendirilir; sertifika uyarısı çıkmaz | Planlandı |
| TC-231 | NFR-09 | G19 | elle | Senaryo | Chrome, Edge ve Firefox güncel sürümleri, 1366 px genişlik, bütün ekranlar | Yatay kaydırma yok; işlevler çalışır; arayüz yalnız Türkçe | Planlandı |
| TC-232 | FR-18 | G19 | elle | Senaryo | Kurum SMTP hesabıyla test üyesine gerçek hatırlatma gönderilir | E-posta gelen kutusuna ulaşır; Türkçe karakterler doğru | Planlandı |
| TC-233 | NFR-03, NFR-05 | G19 | elle | Senaryo | Hazırlık ortamı birkaç gün çalışır; bir gece servis durdurulur | Her gün için bir yedek var; servisin kapalı kaldığı gecenin ertesindeki açılışta telafi job_run'ı var | Planlandı |
| TC-234 | FR-29, AC-29 | G19 | elle | Senaryo | Tohum üyelerden örneklem alınır (ad, telefon, e-posta) | Gerçek bir kişiyi gösteren kayıt yok | Planlandı |
| TC-235 | NFR-09, R-10 | G01 | birim | Sınır değer (iki değerli) | `settings.base` yüklü; `zoneinfo.ZoneInfo("Europe/Istanbul")`; an 2026-11-16T20:59:59Z ve 21:00:00Z iken `timezone.localdate()`; `requirements.txt` okunur | `ZoneInfoNotFoundError` yok; 2026-11-16 ve 2026-11-17; `tzdata==` satırı var | Planlandı |
| TC-236 | Mimari §6.4, KL-43 | G01 | birim | Denklik sınıfı | `settings.prod`; KL-43'teki her zorunlu değişken için ayrı süreçte o değişken silinir; ayrıca yalnız `LIBRARY_SCHEDULER_ENABLED` silinir | Her zorunlu değişkende adını taşıyan `ImproperlyConfigured`; `LIBRARY_SCHEDULER_ENABLED` eksikken ayarlar yüklenir ve değeri "0" olur | Planlandı |
| TC-237 | FR-21, FR-27 (KL-45) | G04 | view | Durum geçişi | "ali" oturum açmış; yönetici ali'yi pasifleştirir; ali aynı oturumla GET `/odunc/` | 302 → `/giris/?next=/odunc/` | Geçti |
| TC-238 | NFR-12 (KL-3) | G03 | birim | Denklik sınıfı | `parse_tl`: "15", "15,5", "15,50", "1.250,00", "1250" | 1500, 1550, 1550, 125000, 125000 | Geçti |
| TC-239 | NFR-12 (KL-3) | G03 | birim | Denklik sınıfı | `format_tl`: 125000, 100000000, 5; şablonda `{{ 125000\|tl }}` | "1.250,00 TL", "1.000.000,00 TL", "0,05 TL"; şablon çıktısı "1.250,00 TL" | Geçti |
| TC-240 | NFR-12 (KL-3) | G03 | birim | Hata tahmini | `parse_tl`: "15.00", "1.25", "1,250.00", "12.50,00" | Her biri `ValueError` (binlik ayırıcı yalnız 3 haneli gruplarda) | Geçti |
| TC-241 | FR-42 (ADR-0044) | G03 | birim | Karar tablosu | `backup_warning(last_success_at, last_finished_failed, now)`: (None, False); (None, True); (now − 1 sa, True); (now − 26 sa, False); (now − 26 sa 1 sn, False); (now − 1 sa, False) | "Günlük yedek henüz alınmadı"; "Son günlük yedek başarısız oldu"; "Son günlük yedek başarısız oldu"; None; "Günlük yedek 26 saatten eski"; None | Geçti |
| TC-242 | FR-42, AC-35 | G03 | view | Denklik sınıfı | Son biten BACKUP `job_run` FAILED; yönetici ve görevli ana sayfayı açar | Yönetici "Son günlük yedek başarısız oldu" görür; görevli görmez | Geçti |
| TC-243 | FR-42, AC-35 (KL-33) | G03 | view | Senaryo | Son SUCCESS BACKUP 2026-11-15 02:05'te bitmiş; ondan sonra başlamış RUNNING bir BACKUP var; yönetici ana sayfayı 2026-11-16 04:06'da açar | "Günlük yedek 26 saatten eski" görünür (RUNNING kayıt "son biten" sayılmaz) | Geçti |
| TC-244 | FR-37 (KL-14) | G03 | view | Denklik sınıfı | Hiç SUCCESS EXPORT yok; ayrı testte 2 gün önceki SUCCESS'ten sonra bugün FAILED EXPORT | İlkinde "Bina dışı yedek henüz alınmadı"; ikincisinde uyarı yok ve tarih 2 gün önceki `run_on` | Geçti |
| TC-245 | FR-37, FR-42 (KL-33) | G03 | view | Denklik sınıfı | Hem yedek hem dışa aktarma uyarısı geçerli | İki uyarı alt alta: önce yedek, sonra dışa aktarma | Geçti |
| TC-246 | FR-12, FR-24 (ADR-0040, KL-29) | G03 | servis | Denklik sınıfı | Pazar haftalık kapalı; 2027-10-29 ve 2027-10-31 (pazar) kapalı tarih; `closed_dates()` | `frozenset({2027-10-29, 2027-10-31})`; haftalık günler kümede yok | Geçti |
| TC-247 | FR-26 (KL-30, KL-31) | G03 | birim | Denklik sınıfı | `AuditAction` değerleri | Tam olarak faz 4 küçük karar 8'deki 12 değer ile `CANCELLATION` ve `MEMBER_REACTIVATED`; toplam 14 | Geçti |
| TC-248 | FR-41, AC-34 (ADR-0043) | G04 | view | Senaryo | Yönetici görevlinin parolasını sıfırlar; görevli bu parolayla girer, GET `/odunc/`; `/parola/` ile değiştirir; yeniden GET `/odunc/` | İlk GET 302 → `/parola/`; değişiklikten sonra "Parolanız değiştirildi", `/`'e yönlendirme; ikinci GET 200 | Geçti |
| TC-249 | FR-41, AC-34 (KL-32) | G04 | view | Denklik sınıfı | Görevli `/parola/`'ya doğru mevcut parola ve geçerli yeni parola girer; ayrı testte yanlış mevcut parola | Doğru: yeni parola geçerli, oturum açık (sonraki istek 200), aktörü görevlinin kendisi olan `STAFF_CHANGED` (`password_changed`); yanlış: form hatası, parola ve bayrak değişmez | Geçti |
| TC-250 | FR-41 (ADR-0043) | G04 | servis | Denklik sınıfı | `create_staff`, `reset_password`, `createsuperuser` ile hesaplar; bayrağı True oturumla `/parola/`, POST `/cikis/`, `STATIC_URL` altındaki bir yol | `must_change_password` sırasıyla True, True, False; muaf üç yol yönlendirilmez | Geçti |
| TC-251 | FR-41 (KL-9, KL-32) | G04 | view | Sınır değer (iki değerli) | Bayrağı True görevli `/parola/`'da 9 ve 10 karakterli yeni parola girer | 9: hata, bayrak True kalır; 10: kabul, bayrak False | Geçti |
| TC-252 | FR-21 (KL-8) | G04 | servis | Karar tablosu | Tek aktif yönetici kendini görevliye çevirir; iki aktif yöneticiden A, B'yi görevliye çevirir; yönetici kendini pasifleştirir | İlki "En az bir aktif yönetici kalmalı"; ikincisi kabul; üçüncüsü "Kendi hesabınızı pasifleştiremezsiniz"; reddedilenlerde değişiklik ve denetim kaydı yok | Geçti |
| TC-253 | FR-04 (KL-40) | G05 | birim | Denklik sınıfı | `parse_isbn("080442957x")` | `IsbnOk("9780804429573")` | Geçti |
| TC-254 | FR-03, AC-03 (ADR-0047) | G06 | servis | Senaryo | Rızalı ve e-postalı üye; bugün 2026-11-10; görevli `update_member(email=None)` | Aynı işlemde `effective_on` 2026-11-10, `recorded_by` görevli olan WITHDRAWN olayı; `has_email_consent` False | Geçti |
| TC-255 | FR-03, AC-03 (ADR-0047, KL-12) | G06 | servis | Sınır değer (iki değerli) | Bugün 2026-11-01; rıza `on` = 2026-11-05, 2026-11-02 ve 2026-11-01 | 11-05 ve 11-02 "Rıza tarihi gelecekte olamaz" ile reddedilir, olay yazılmaz; 11-01 kabul edilir | Geçti |
| TC-256 | FR-03 (ADR-0047, KL-36) | G06 | servis | Durum geçişi | Rızalı üyeye GIVEN; olayı olmayan üyeye WITHDRAWN | "Üyenin rızası zaten var"; "Üyenin rızası zaten yok"; olay ve denetim kaydı yazılmaz | Geçti |
| TC-257 | FR-03 (ADR-0047) | G06 | servis | Hata tahmini | GIVEN 11-10 kayıtlı; WITHDRAWN `on` = 11-05 eklenir. Ayrı testte GIVEN 11-10, ardından WITHDRAWN 11-10 | İlkinde olay kabul edilir, `has_email_consent` True kalır; ikincisinde `recorded_at` sonra olan WITHDRAWN geçerli, `has_email_consent` False | Geçti |
| TC-258 | FR-03 | G06 | servis | Denklik sınıfı | E-postası olmayan üyeye rıza verilir | "Rıza için e-posta adresi gerekli"; olay yazılmaz | Geçti |
| TC-259 | FR-40, FR-26, AC-33 (ADR-0042, KL-31) | G06 | view | Durum geçişi | 42 no'lu pasif, anonimleştirilmemiş üye; görevli üye ayrıntısında "Aktifleştir"i görür ve POST `/uyeler/42/aktif/` gönderir | `is_active` True, `deactivated_on` NULL; aktörü görevli, hedefi üye, `details` `{"member_no": 42}` olan MEMBER_REACTIVATED kaydı | Geçti |
| TC-260 | FR-40, AC-33 (ADR-0042) | G06 | servis | Karar tablosu | `reactivate_member`: anonimleştirilmiş üye; aktif üye. Üye ayrıntısı: aktif üye, anonim üye | "Anonimleştirilmiş üye aktifleştirilemez"; "Üye zaten aktif"; iki ayrıntıda da "Aktifleştir" düğmesi yok | Geçti |
| TC-261 | FR-01 (KL-10) | G06 | servis | Denklik sınıfı | `search_members`: "0555-111-2233", "(0555) 111 22 33", "Ayşe Yılmaz" | İlk ikisi telefonla aynı üyeyi bulur; üçüncüsü ad aramasıdır ve aynı üyeyi bulur | Geçti |
| TC-262 | FR-05 (KL-19) | G07 | servis | Sınır değer (iki değerli) | `add_copies(book, n)`, n = 0, 1, 50, 51 | 0 ve 51 reddedilir, nüsha oluşmaz; 1 ve 50 kabul edilir | Geçti |
| TC-263 | FR-05 (KL-42) | G07 | servis | Sınır değer | Nüsha dizisi 99999999'a ayarlanmış; `add_copies(book, 2)` | "Barkod aralığı doldu"; işlem geri alınır, nüsha oluşmaz | Geçti |
| TC-264 | FR-04 (KL-10) | G07 | servis | Denklik sınıfı | `isbn13` "9780306406157" olan kitap; aramalar "0306406152", "978-0-306-40615-7"; başka kitabın nüshası "00000042"; 60 kitapta geçen sözcük | İki ISBN araması kitabı bulur; barkod araması o nüshanın kitabını bulur; sözcük araması 50 sonuç döner | Geçti |
| TC-265 | FR-06 (ADR-0036, KL-25) | G08 | servis | Denklik sınıfı | Nüshalar 00000010…00000015; 00000012 yok, 00000013 WITHDRAWN; `copies_for_labels(None, "00000010", "00000015")` | id'ler 10, 11, 14, 15 artan sırayla | Geçti |
| TC-266 | FR-06, FR-38 (KL-25) | G08 | servis | Sınır değer (iki değerli) | Aralık başlangıcı bitişten büyük; aralık genişliği 240 ve 241; 241 öğelik `copy_ids` listesi; bütün öğeleri hariç kalan aralık | "Başlangıç bitişten büyük olamaz"; 240 kabul, 241 ve 241'lik liste "En fazla 240 öğe seçilebilir"; "Aralıkta basılacak nüsha yok" | Geçti |
| TC-267 | FR-06 (KL-25) | G08 | servis | Karar tablosu | Aralık ve `copy_ids` birlikte; ikisi de boş; içinde WITHDRAWN nüsha bulunan `copy_ids` | "Aralık ya da seçim kutuları kullanın, ikisini birden değil"; "En az bir nüsha seçin"; WITHDRAWN nüsha sunucuda atlanır | Geçti |
| TC-268 | FR-38 (ADR-0036, KL-25) | G08 | servis | Denklik sınıfı | Üye no 1…6; 3 pasif, 4 anonim; `members_for_cards(None, 1, 6)`; `members_for_cards([5, 2], None, None)`; yalnız pasif ve anonim üyeleri kapsayan aralık; ikisi de boş | [1, 2, 5, 6]; [2, 5]; "Aralıkta basılacak üye yok"; "En az bir üye seçin" | Geçti |
| TC-269 | FR-06, FR-38 (ADR-0036) | G08 | view | Denklik sınıfı | GET `/nushalar/etiket/` ve `/uyeler/kart/`; geçerli seçimle POST; kitap ayrıntısı (bir nüsha WITHDRAWN); üye arama sonuçları (bir üye pasif) | GET'lerde aralık formu; POST'larda 200, `application/pdf`, `inline; filename="etiketler.pdf"` ve `"uye-kartlari.pdf"`; WITHDRAWN nüshada ve pasif üyede seçim kutusu yok | Geçti |
| TC-270 | FR-16 (KL-26) | G09 | servis | Denklik sınıfı | Bulunan kayıp nüshanın bedeline 50,00 ve 30,00 ödeme dağıtılmış; sonra 30,00 para iadesi; ayrı testte `copy_found_on` NULL | `refundable` 80,00, iadeden sonra 50,00; ön koşulsuz bedelde 0 | Geçti |
| TC-271 | FR-16, I5 (ADR-0037) | G09 | servis | Karar tablosu | REFUND hedefi: ödüncü DAMAGED ile kapanmış bedel; `loan_id` NULL bedel | İkisi de "Para iadesi yalnız bulunan kayıp nüshanın bedeli için yapılabilir"; hareket yazılmaz | Geçti |
| TC-272 | FR-16, AC-16 (ADR-0037) | G09 | servis | Sınır değer (iki değerli) | Tamamı ödenmiş 120,00 bedel; ödünç LOST, `copy_found_on` dolu; 120,01 ve 120,00 para iadesi | 120,01 reddedilir; 120,00 kabul edilir; `refundable` 0; bakiye değişmez | Geçti |
| TC-273 | FR-16, FR-26, AC-16 (ADR-0041, KL-30) | G09 | servis | Senaryo | Bağı koparılmış (`loan_id` NULL) bedelin 80,00'ı ödenmemiş; yönetici "Nüsha bulundu" gerekçesiyle `cancel_fee_manual`; ardından aynı bedele para iadesi | Bakiye 80,00 azalır; CANCELLATION'ın `reason` alanı dolu; CANCELLATION denetim kaydında `amount_kurus` 8000, `member_no`, `target_entry_id`, `reason`, aktör ve zaman; para iadesi reddedilir | Geçti |
| TC-274 | FR-16 (ADR-0041) | G09 | servis | Karar tablosu | `cancel_fee_manual`: gerekçe "" ve "   "; ödüncüne bağlı bedel; ödenmemiş kısmı 0 olan bağsız bedel; bağsız FINE | "İptal için gerekçe zorunlu"; "Bu bedel ödüncüne bağlı; nüshayı Bulundu olarak işaretleyin"; "Bedelin ödenmemiş kısmı yok"; FINE reddedilir; hiçbirinde hareket yazılmaz | Geçti |
| TC-275 | FR-16, FR-22 (ADR-0041, KL-26) | G09 | view | Karar tablosu | Görevli POST `/borclar/<no>/iptal/`; döküm ekranı yönetici ve görevliyle; bedeller: iade edilebilir tutarlı, bağsız ve ödenmemiş, ikisi de değil | 403; yönetici para iadesi formunu yalnız ilk bedelde, iptal formunu yalnız ikincide görür; görevli iki formu da görmez | Geçti |
| TC-276 | FR-12, AC-12 (ADR-0040) | G10 | birim | Denklik sınıfı | `late_days(2026-11-16, 2026-11-20, {2026-11-18})`; `fine(3, 500, 15000)` | 3; 1500 | Geçti |
| TC-277 | FR-12 (ADR-0040) | G10 | birim | Sınır değer | Son tarih 11-16, iade 11-20; kapalı tarih kümesi {11-16}, {11-20}, {11-15, 11-21}; ayrıca `late_days(11-16, 11-17, {11-17})` | 4 (son tarih düşülmez); 3 (iade günü düşülür); 4 (aralık dışı); 0 | Geçti |
| TC-278 | FR-12 (ADR-0040, KL-29) | G11 | servis | Denklik sınıfı | Pazar haftalık kapalı; son tarih 2026-11-14 (cumartesi), iade 2026-11-17; ayrı testte 2026-11-15 (pazar) ayrıca kapalı tarih | İlkinde 3 gün, 15,00 TL FINE; ikincisinde 2 gün, 10,00 TL | Geçti |
| TC-279 | FR-11 (ADR-0046, KL-35) | G10 | birim | Denklik sınıfı | `classify_member_input`: "00000042", "05551112233", "5551112233", "0555 111 22 33", "(0555) 111-22-33", "1042", "12345678", "0000042", "012345678", "ayşe" | COPY_BARCODE; PHONE "05551112233"; PHONE "5551112233"; PHONE "05551112233"; PHONE "05551112233"; MEMBER_NO "1042"; MEMBER_NO; MEMBER_NO; MEMBER_NO; TEXT | Geçti |
| TC-280 | FR-08, FR-10 (KL-6) | G10 | birim | Karar tablosu | `checkout_blockers`: pasif, limit dolu, gecikmiş, eşik aşılmış, nüsha ON_LOAN; `renew_blockers`: uzatılmış, gecikmiş, borçlu | Beş engel enum sırasıyla; [ALREADY_RENEWED, LOAN_OVERDUE, HAS_DEBT] | Geçti |
| TC-281 | FR-11, AC-11 (ADR-0046) | G11 | view | Denklik sınıfı | 42 no'lu üye ve "00000042" barkodlu nüsha var; GET `/odunc/?uye=00000042` | Hiçbir üye açılmaz; "Bu bir nüsha barkodu. Üye kartını okutun." görünür; nüsha alanı ve onay düğmesi yok | Geçti |
| TC-282 | FR-11 (ADR-0046, KL-35) | G11 | view | Denklik sınıfı | GET `/odunc/?uye=0555 111 22 33` (tek eşleşme); GET `/odunc/?uye=ayşe` (iki eşleşme) | İkisinde de liste; her satır `?uye=<no>` bağlantısı; tek sonuçta da üye otomatik açılmaz | Geçti |
| TC-283 | FR-09, FR-12, AC-12 (ADR-0040) | G11 | view | Senaryo | Günlük ceza 5,00; son tarih 2026-11-16; 2026-11-18 kapalı tarih; 2026-11-20'de iade | 15,00 TL FINE; "İade alındı; 15,00 TL ceza yazıldı" | Geçti |
| TC-284 | FR-08, AC-08 (KL-6) | G11 | view | Karar tablosu | Pasif, limiti dolu ve eşiği aşmış üyeye POST `/odunc/` | 200; "Üye pasif; Ödünç limiti dolu; Borç eşiği aşıldı" bu sırayla görünür; ödünç yazılmaz | Geçti |
| TC-285 | FR-40, AC-33 | G11 | servis | Senaryo | Pasif üye `reactivate_member` ile aktifleştirilir; ardından `check_out` | Ödünç verilir | Geçti |
| TC-286 | FR-02, AC-02 (KL-22) | G11 | view | Senaryo | 20,00 TL borçlu, açık ödüncü yok üye; POST `/uyeler/<no>/pasif/` onaysız, sonra onay kutusuyla | İlkinde 200, "Üyenin 20,00 TL borcu var; onaylayarak pasifleştirin" ve onay kutusu; ikincisinde üye pasif | Geçti |
| TC-287 | FR-20 (ADR-0040, KL-29) | G11 | servis | Denklik sınıfı | Bugün 2026-11-20; son tarih 11-16; 11-18 kapalı tarih; `overdue_loans` | Satırda `late_days` 3, `accrued_fine` 1500 | Geçti |
| TC-288 | FR-10 (ADR-0040) | G11 | servis | Sınır değer | Son tarih 11-16; 11-17 kapalı tarih; bugün 11-17; `renew` | "Ödünç gecikmiş" ile reddedilir (uzatma kontrolü takvim gününe göre; `late_days` 0 olsa da) | Geçti |
| TC-289 | FR-15 (KL-7) | G12 | servis | Sınır değer | 10 gün gecikmiş ödünç; `mark_lost(fee_kurus=0)` | FINE 50,00 yazılır; FEE ve FEE denetim kaydı yazılmaz; COPY_LOST yazılır | Geçti |
| TC-290 | FR-13, FR-15 (KL-44, ADR-0017) | G12 | servis | Hata tahmini | 10 gün gecikmiş ödünç 120,00 bedelle kayıp işaretlenir; ardından 50,00 ödeme | FINE'ın `id`'si FEE'ninkinden küçük; ödeme FINE'ı kapatır, FEE'nin ödenmemiş kısmı 120,00 kalır | Geçti |
| TC-291 | FR-16 (ADR-0037) | G12 | servis | Durum geçişi (1-switch) | Nüsha: ödünç 1 LOST → bulundu → ödünç 2 → LOST → bulundu; ayrı testte ödünç 1 LOST → bulundu → raftan kayıp (`mark_shelf_copy`) → bulundu | İlkinde ikinci bulunduda yalnız ödünç 2'nin `copy_found_on`'u dolar ve yalnız onun bedeli iptal edilir; ikincisinde son bulunduda ödünç ve bedel değişmez | Geçti |
| TC-292 | FR-16, AC-16 (ADR-0037) | G12 | view | Senaryo | Bedeli tamamen ödenmiş (120,00) kayıp nüsha için görevli POST `/nushalar/<barkod>/bulundu/` | 303; "Ödenmiş 120,00 TL para iadesi için üyenin borç sayfasında" mesajı ve `/borclar/<no>/` bağlantısı | Geçti |
| TC-293 | FR-15, FR-39 | G12 | view | Denklik sınıfı | GET `/nushalar/99999998/`; ON_LOAN nüshanın ekranı yönetici ve görevliyle; ON_SHELF nüshanın ekranı yönetici ile | 404; ON_LOAN'da yönetici bedel alanlı kayıp ve hasarlı formlarını görür, görevli görmez; ON_SHELF formlarında bedel alanı yok | Geçti |
| TC-294 | FR-18 (ADR-0039) | G13 | servis | Hata tahmini | ORM ile aynı `(loan, kind, due_on)` için iki DUE_SOON SENT; farklı `due_on` ile iki SENT; aynı `due_on` ile iki MANUAL SENT; iki FAILED | İlki `IntegrityError`; diğerleri kabul | Geçti |
| TC-295 | FR-18 (KL-23) | G13 | komut | Senaryo | 11-14'te iki aday; biri için SMTP hata verir; 11-15'te SMTP çalışır | 11-14: "gönderilen=1, başarısız=1, atlanan=0", çıkış 1, `job_run` SUCCESS ve `detail` aynı metin; 11-15: yalnız başarısız olan yeniden denenir ve SENT olur | Geçti |
| TC-296 | FR-18 (KL-13) | G13 | servis | Denklik sınıfı | `library_name` "Merkez"; "Tutunamayanlar", son tarih 2026-11-16; DUE_SOON ve OVERDUE_1 e-postaları | Konular "Merkez: İade tarihi yaklaşıyor" ve "Merkez: İade tarihi geçti"; gövdelerde başlık ve "16.11.2026"; OVERDUE_1'de "5,00 TL" ve "150,00 TL"; alıcı yalnız üye; gönderen `LIBRARY_EMAIL_FROM` | Geçti |
| TC-297 | FR-19 | G13 | servis | Denklik sınıfı | `send_manual_reminders` ile beş ödünç: gecikmemiş; e-postasız; rızasız; SMTP hatalı; uygun | `not_overdue`, `no_email`, `no_consent`, `failed`, `sent`; yalnız son ikisinde `reminder_log` satırı | Geçti |
| TC-298 | FR-20, FR-19 (KL-29) | G13 | view | Denklik sınıfı | Geciken listesi: e-postasız, rızasız ve uygun üç ödünç; birinin aralığında kapalı tarih var | Her satırda seçim kutusu; "e-posta yok" ve "rıza yok" etiketleri; kapalı tarihli satırda gecikme günü ve ceza düşülmüş | Geçti |
| TC-299 | FR-37 (KL-24) | G14 | birim | Sınır değer (iki değerli) | `exports_to_delete`, run_on 2026-12-31; adlar: run_on − 56 ve − 57 tarihli `.libx`, `eski.libx` | Yalnız −57 silinecekler listesinde | Geçti |
| TC-300 | FR-37 (KL-24) | G14 | komut | Hata tahmini | Dışa aktarma klasöründe 60 günlük `.libx` var; `export_backup` parola dosyası olmadığı için başarısız | Çıkış 1; eski dosya silinmez | Geçti |
| TC-301 | FR-28 (KL-41) | G14 | komut | Hata tahmini | `restore_backup yok.sqlite3 --yes` | "Dosya bulunamadı: yok.sqlite3", çıkış 1; veritabanı değişmez | Geçti |
| TC-302 | FR-28 (KL-4) | G14 | servis | Durum geçişi | Alt süreç `hold_app_lock` ile kilidi tutar; ana süreç `try_lock`; alt süreç sonlandırılır; yeniden `try_lock` | Önce False, sonra True (Windows'ta ve Linux'ta ayrı ayrı koşulur, R-15) | Geçti |
| TC-303 | FR-37 (KL-14) | G14 | komut | Denklik sınıfı | 2026-11-01 ve 2026-11-02 tarihli günlük yedekler (farklı üye sayılı); `export_backup`; çıktı geri yüklenir | Geri yüklenen sayılar 2026-11-02 yedeğininki | Geçti |
| TC-304 | FR-37 | G14 | komut | Sınır değer | Parola dosyası "gizli\n"; ayrı testte boş dosya | İlkinde "gizli" ile şifrelenir (aynı parolayla çözülür); ikincisinde çıkış 1, `.libx` oluşmaz | Geçti |
| TC-305 | FR-25, AC-25 (ADR-0045, KL-34) | G15 | komut | Senaryo | Saklama 2 yıl; üye 2026-11-01'de pasifleştirilmiş, 20,00 TL borçlu; görev 2028-11-02'de; borç ödenir; görev 2028-11-03'te | 11-02: üye anonimleşmez, `deferred` 1; 11-03: anonimleşir, `deferred` 0 | Geçti |
| TC-306 | FR-25 (ADR-0045) | G15 | komut | Denklik sınıfı | TC-305'teki borçlu üyenin 2026-11-01'de iade edilmiş ödüncü; görev 2028-11-02 | Ödüncün üye bağı kopar, `archived_loan_count` +1; üye anonimleşmez | Geçti |
| TC-307 | FR-25 (küçük karar 4) | G15 | birim | Sınır değer | `add_years(2028-02-29, 2)`, `add_years(2024-02-29, 4)`; `is_expired(2028-02-29, 2, today)`, today = 2030-02-28 ve 2030-03-01 | 2030-02-28; 2028-02-29; False; True | Geçti |
| TC-308 | FR-25, FR-22 (KL-34) | G15 | view | Denklik sınıfı | İki borçlu bekleyen üye (pasifleşme 2026-11-01 ve 2026-10-01); yönetici ve görevli GET `/uyeler/saklama/` | Yönetici: 2026-10-01'li önce; sütunlarda üye no, ad, pasifleşme tarihi, süre sonu, bakiye ve "borç nedeniyle bekliyor"; görevli 403 | Geçti |
| TC-309 | FR-25 | G15 | view | Denklik sınıfı | Anonimleşmiş, 2 bağlı ödüncü ve `archived_loan_count` 3 olan üyenin ayrıntısı | "Anonimleştirilmiş üye" ve toplam ödünç 5 görünür | Geçti |
| TC-310 | FR-37, NFR-05 | G16 | birim | Sınır değer (iki değerli) | `jobs_due_for_catch_up`; EXPORT son SUCCESS 2026-10-26 (pazartesi); now 2026-11-02 02:59 ve 03:01; ayrı testte son SUCCESS 2026-11-02, now 2026-11-04 10:00 | 02:59'da EXPORT yok; 03:01'de var; 11-04'te yok | Geçti |
| TC-311 | NFR-05 | G16 | birim | Denklik sınıfı | Dört görevin de telafisi gerekiyor | Sıra [BACKUP, ANONYMIZE, EXPORT, REMINDERS] | Geçti |
| TC-312 | NFR-05 (KL-23) | G16 | birim | Durum geçişi | Bugünkü REMINDERS çalışması SUCCESS ama `detail` "başarısız=1" içeriyor; now 10:00 | REMINDERS telafi listesinde yok | Geçti |
| TC-313 | NFR-05 (KL-4, R-09) | G16 | servis | Hata tahmini | Kilit başka bir süreçte tutulurken `library_site.wsgi` yeni bir süreçte import edilir | `RuntimeError("Uygulama zaten çalışıyor: <kilit yolu>")`; zamanlayıcı başlamaz | Geçti |
| TC-314 | NFR-05 | G16 | servis | Hata tahmini | Zamanlayıcıda iki görev; ilki istisna fırlatır | İstisna loglanır; ikinci görev çalışır; zamanlayıcı çalışır durumda kalır | Geçti |
| TC-315 | FR-29 (ADR-0038) | G17 | komut | Karar tablosu | `--actor` yok; olmayan kullanıcı "yok"; pasif kullanıcı "eski"; dolu veritabanında geçerli aktör | Çıkış 2; "Personel bulunamadı ya da pasif: yok" ve çıkış 1; "Personel bulunamadı ya da pasif: eski" ve çıkış 1; "Veritabanı boş değil" ve çıkış 1; hiçbirinde veri yazılmaz | Geçti |
| TC-316 | FR-29 (ADR-0038, KL-16) | G17 | komut | Denklik sınıfı | TC-217'nin veritabanı | Bütün `created_by`, `closed_by`, `recorded_by` = "demo"; açık ödüncün nüshası ON_LOAN, kapalının ON_SHELF; üyelerin %50'si e-postalı ve rızalı; 5 üyenin borcu var; bütün e-postalar `@example.invalid` ile biter | Geçti |
| TC-317 | NFR-02 (KL-16) | G17 | komut (slow) | Denklik sınıfı | TC-220'nin veritabanı | Üyelerin %30'u e-postalı ve rızalı; kapalı ödünçlerin %10'unda eşit tutarlı FINE ve PAYMENT; bu üyelerin bakiyesi bu ödünçlerden dolayı 0 | Geçti |
| TC-318 | NFR-01 (ADR-0031, KL-17) | G18 | birim | Denklik sınıfı | `pick_operation(random.Random(42))` 10.000 kez; aday seçimi salt okunur bağlantıyla 5 iş parçacığına bölünür | Oranlar %40/20/20/10/10 ± 2 puan; iş parçacıklarının üye ve nüsha kümeleri ayrık; bağlantı URI'si `mode=ro` içerir | Geçti |
| TC-319 | FR-11, FR-03, FR-12 (ADR-0032, ADR-0038, ADR-0040, ADR-0047, KL-21, KL-27) | G19 | elle | Gözden geçirme | `docs/kullanim-kilavuzu.md` ve `README.md` okunur | Kılavuzda "üyeye adını sor" adımı, "geçmiş kapalı tarihleri silmeyin" ve geçmiş tarihli rıza notu var; README'de `migrate` → `createsuperuser` → `load_seed_data --profile demo --actor <ad>` sırası ve "Veri kaynakları" bölümü var | Planlandı |
| TC-320 | FR-28, NFR-04, AC-28 (ADR-0054) | G14 | komut | Senaryo | Mevcut veritabanı `-wal` ve `-shm` dosyalarıyla duruyor; `restore_backup <yedek>.sqlite3 --yes` | Çıkış 0; üç dosya `<db>.pre-restore-YYYYMMDD-HHMMSS`, `…-wal`, `…-shm` adıyla ve içerikleri değişmeden duruyor; yeni veritabanının sayıları yedektekiyle aynı; çıktıda koruma kopyasının yolu var | Geçti |
| TC-321 | FR-28 (ADR-0054) | G14 | komut | Hata tahmini | Mevcut veritabanı dosyası bozuk (SQLite olmayan baytlar); geçerli yedekle geri yükleme | Çıkış 0; bozuk dosya koruma kopyası olarak baytı baytına duruyor; sayılar yedektekiyle aynı | Geçti |
| TC-322 | FR-28 (ADR-0054, G14–G16 küçük karar 4) | G14 | komut | Hata tahmini | SQLite olmayan dosya; ayrı testte `django_migrations` tablosu olmayan SQLite dosyası geri yüklenir | Çıkış 1; veritabanı, `-wal` ve `-shm` değişmez; koruma kopyası oluşmaz; veritabanı klasöründe geçici dosya kalmaz | Geçti |
| TC-323 | FR-28, FR-37 (küçük karar 1) | G14 | komut | Denklik sınıfı | `backup_db --date 2026-13-40`; `export_backup --date 2026-02-30` | "Geçersiz tarih: …" ile `CommandError`, çıkış 1; `job_run` yazılmaz; dosya oluşmaz | Geçti |
| TC-324 | FR-37 (küçük karar 1) | G14 | komut | Denklik sınıfı | `export_backup --passphrase-file` olmadan; `LIBRARY_EXPORT_PASSPHRASE_FILE` bir parola dosyasını gösterir | Çıkış 0; `.libx` o dosyadaki parolayla çözülür | Geçti |
| TC-325 | FR-28, FR-37 (küçük karar 2) | G14 | komut | Denklik sınıfı | `.libx` içeriği `yedek.sqlite3` adıyla; SQLite yedeği `yedek.libx` adıyla geri yüklenir | İkisinde de çıkış 0 ve yedekteki sayılar (tür `LIBX` magic baytından anlaşılır) | Geçti |
| TC-326 | FR-28, FR-37 (küçük karar 2) | G14 | komut | Karar tablosu | `.libx` geri yükleme `--passphrase-file` olmadan: `LIBRARY_EXPORT_PASSPHRASE_FILE` doğru parola dosyasını gösterir; ayrı testte o dosya yok | İlkinde çıkış 0; ikincisinde çıkış 1 ve veritabanı değişmez | Geçti |
| TC-327 | FR-28 (küçük karar 3) | G14 | komut | Denklik sınıfı | `django_migrations` tablosunda bir satırı eksik olan yedek geri yüklenir | Çıkış 0; geri yüklenen `django_migrations` yedektekiyle aynı (migration çalışmaz); çıktıda "gerekirse `python manage.py migrate` çalıştırın" notu | Geçti |
| TC-328 | FR-28, FR-37 (küçük karar 4) | G14 | komut | Hata tahmini | Yedek ve (ayrı testte) dışa aktarma yazımı sırasında `PermissionError`; hedef klasörde aynı günün eski dosyası var | Çıkış 1; `job_run` FAILED; klasörde `.tmp` kalmaz; aynı günün eski dosyası değişmez | Geçti |
| TC-329 | FR-28, FR-37 (küçük karar 4) | G14 | komut | Senaryo | Aynı gün iki `backup_db` ve iki `export_backup`; iki koşu arasında bir üye eklenir | İkinci koşular aynı adlı dosyanın üzerine yazar; geri yüklenen sayılar ikinci durumunki; `.tmp` kalmaz | Geçti |
| TC-330 | FR-25, NFR-08 (ADR-0055) | G15 | komut | Denklik sınıfı | Bağı koparılacak ödüncün `error` dolu FAILED ve SENT `reminder_log` satırları; bağı kalan başka bir ödüncün `error` dolu FAILED satırı | Bağı kopan ödüncün satırlarında `error` NULL; `kind`, `status`, `due_on`, `sent_at` aynı; öteki ödüncün satırı değişmez | Geçti |
| TC-331 | FR-25, NFR-08 (küçük karar 8) | G15 | view | Denklik sınıfı | Anonim üye: üye no ile üye araması, ödünç ekranındaki üye paneli, borç dökümü, geciken listesi; ayrıca `Member.display_name` | Hepsinde "Anonimleştirilmiş üye"; `display_name` anonim üyede "Anonimleştirilmiş üye", diğerinde `full_name` | Geçti |
| TC-332 | FR-25 (küçük karar 1) | G15 | komut | Denklik sınıfı | `anonymize_expired --date 2028-02-30` | "Geçersiz tarih: 2028-02-30" ile `CommandError`, çıkış 1; `job_run` yazılmaz; veri değişmez | Geçti |
| TC-333 | FR-25 (küçük karar 9) | G15 | komut | Senaryo | TC-207'deki hatalı koşudan sonra hata giderilir ve görev aynı gün yeniden çalışır | İlk koşu: `job_run` FAILED, çıkış 1, ilk ödünç işlenmiş. İkinci koşu: kalan ödünç ve üye işlenir, ilk ödünç yeniden sayılmaz, `job_run` SUCCESS | Geçti |
| TC-334 | FR-25, FR-22 (küçük karar 7) | G15 | view | Denklik sınıfı | Yönetici ve görevli ana sayfayı açar | Yöneticinin menüsünde `/uyeler/saklama/` bağlantısı var; görevlininkinde yok | Geçti |
| TC-335 | NFR-05 (ADR-0053, küçük karar 5) | G16 | servis | Denklik sınıfı | `start_scheduler()` | Beş görev: dört cron ve `IntervalTrigger(hours=1)` telafisi; hepsinde `misfire_grace_time` 3600, `coalesce` True, `max_instances` 1; yürütücü tek işçili `ThreadPoolExecutor` | Geçti |
| TC-336 | NFR-03, NFR-05 (ADR-0053) | G16 | servis | Durum geçişi | Saatlik telafi 2026-11-04 (çarşamba) 03:10'da; bugün BACKUP FAILED, ANONYMIZE SUCCESS, EXPORT son SUCCESS 2026-11-02; ayrı testte BACKUP da SUCCESS | İlkinde yalnız BACKUP kuyruğa alınır ve log satırı yazılır; ikincisinde hiçbir görev kuyruğa alınmaz | Geçti |
| TC-337 | NFR-05 (küçük karar 5) | G16 | servis | Senaryo | Dört görevin telafisi gerekiyor; zamanlayıcı gerçekten çalışır (komutlar yamalı ve yavaş) | Komutlar BACKUP, ANONYMIZE, EXPORT, REMINDERS sırasıyla ve çakışmadan (aynı anda en fazla bir tane) çalışır | Geçti |
| TC-338 | NFR-05 (küçük karar 6, KL-23) | G16 | servis | Hata tahmini | Sarmalayıcı `send_reminders`'ı çalıştırır, bir hatırlatma FAILED olur; ayrı testte komut `RuntimeError` fırlatır | İkisi de `operations.scheduler` logger'ıyla ERROR olarak loglanır ve sarmalayıcıdan dışarı çıkmaz; ilkinde `job_run` SUCCESS | Geçti |
| TC-339 | NFR-05 (küçük karar 6) | G16 | birim | Denklik sınıfı | `base.py`'deki `LOGGING` | stderr'e yazan bir `StreamHandler`; `operations` ve `django` logger'ları INFO; biçim `%(asctime)s %(levelname)s %(name)s %(message)s` | Geçti |
| TC-340 | FR-29 (ADR-0033, ADR-0056) | G17 | birim | Senaryo | `fetch_books` sahte bir HTTP açıcıyla: ilk sayfa 2 kayıt, ikinci sayfa 1 kayıt, üçüncü sayfa boş; `--limit 2` ile ayrı koşu | Sorgu `language:tur isbn:978605*`; her istekte proje adını taşıyan `User-Agent`; iki istek arasında en az 1 sn bekleme (bekleme yamalı); boş sayfada durur; `--limit 2`'de ikinci sayfa istenmez; çıktı dosyası `_meta` ve kayıtlarla yazılır | Geçti |
| TC-341 | FR-29 (ADR-0056) | G17 | komut | Hata tahmini | Kitap dosyası yok; ayrı testte dosyada hiç kayıt yok; `load_seed_data --actor demo` | "Kitap dosyası bulunamadı: <yol>" ya da "Kitap dosyasında kayıt yok: <yol>" ve çıkış 1; hiçbir tabloya satır yazılmaz; ağ çağrısı yapılmaz | Geçti |
| TC-342 | FR-01, FR-29, AC-29, NFR-08 (ADR-0057) | G17 | komut | Denklik sınıfı | TC-217'nin veritabanı | Her üyenin telefonu `000 ddd dd dd` biçiminde; `phone_digits` "000" ile başlayan 10 rakam; telefonlar birbirinden farklı | Geçti |
| TC-343 | FR-29 (küçük karar 2, 3) | G17 | komut | Senaryo (metamorfik) | Bugün 2026-11-16 ve (ayrı koşuda) 2026-11-17; ikisinde de `--seed 42`, kapalı gün yok | 350 kapalı ödüncün `loaned_on` ve `closed_on` değerleri [bugün − 180, bugün − 1] aralığında; açık ödünçlerin `loaned_on` ≤ bugün; gecikmiş 10'unda `due_on` < bugün, diğerlerinde ≥ bugün; aynı nüshanın ödünçleri çakışmaz; ikinci koşuda bütün tarihler bir gün sonradır, diğer alanlar aynıdır | Geçti |
| TC-344 | FR-29, FR-17 (küçük karar 3) | G17 | komut | Denklik sınıfı | TC-217'nin veritabanı | Bakiyesi pozitif tam 5 üye var; her birinin borcu, `closed_on` > `due_on` olan bir iadenin ödenmemiş FINE'ıdır; diğer her FINE'ın aynı üyede aynı tutarlı bir PAYMENT'ı var | Geçti |
| TC-345 | FR-29, FR-13 (küçük karar 7) | G17 | komut | Değişmez kontrolü | TC-217'nin veritabanı | `audit_event` boş; her PAYMENT'ın Allocation toplamı tutarına eşit ve aynı üyenin FINE'larına gider; hiçbir FINE fazla dağıtılmamış (I4); her üyede `member_balance` = ödenmemiş FINE toplamı | Geçti |
| TC-346 | NFR-02, FR-25 (küçük karar 4) | G17 | komut (slow) | Sınır değer | TC-220'nin veritabanı; ardından `anonymize_expired` servisi aynı gün | Bütün ödünçlerin `loaned_on` ≥ bugün − 365; anonimleştirme 0 üye ve 0 ödünç işler | Geçti |
| TC-347 | FR-29, FR-07, FR-12 (küçük karar 5) | G17 | komut | Denklik sınıfı | Ayarlar: süre 21 gün, günlük ceza 2,00 TL, üst sınır 30,00 TL; pazar haftalık kapalı; bir kapalı tarih; `--profile demo` | Her ödünçte `due_on` = `due_date(loaned_on, 21, …)` ve kapalı güne düşmez; `daily_fine_kurus` 200, `fine_cap_kurus` 3000; her FINE = `fine(late_days(due_on, closed_on, kapalı tarihler), 200, 3000)`; barkod `f"{id:08d}"`; `search_key` = `normalize_tr`; `phone_digits` domain fonksiyonuyla aynı | Geçti |
| TC-348 | FR-29 (küçük karar 5) | G17 | komut | Hata tahmini | Ödünç yazımı sırasında istisna (yama) | "Tohum verisi yüklenemedi: <tür>: <metin>" ve çıkış 1; kitap, nüsha, üye, rıza, ödünç ve defter tabloları boş | Geçti |
| TC-349 | FR-29 (küçük karar 6, ADR-0033) | G17 | komut | Denklik sınıfı | Örnek dosyada 12 kayıt; `--profile demo` | 288 sentetik kitap: başlık 2–4 sözcük, her sözcük örnek dosyanın başlıklarından; yazar "<ad> <soyad>" ve ikisi de `seed/` listelerinden; `isbn13`, `publisher`, `source_ol_id` boş | Geçti |
| TC-350 | FR-29 (küçük karar 8) | G17 | komut | Denklik sınıfı | 300 kayıtlı dosya ve (ayrı koşuda) 12 kayıtlı dosya | İlk satır "kitap=300, nüsha=<n>, üye=200, açık ödünç=150 (gecikmiş 10), kapalı ödünç=350"; 300 kayıtta ikinci satır yok; 12 kayıtta ikinci satır sentetik tamamlamayı (12 kayıt, 288 sentetik kitap) bildirir | Geçti |
| TC-351 | FR-29, FR-03 (küçük karar 9) | G17 | komut | Denklik sınıfı | TC-217'nin veritabanı | E-postalı her üyede e-posta `uye<no>@example.invalid`, `has_email_consent` True ve tek bir `GIVEN` olayı; `effective_on` [bugün − 364, bugün] aralığında, `recorded_by` aktör; e-postasız üyede olay yok ve rıza False | Geçti |
| TC-352 | FR-29, AC-29 (küçük karar 1, KL-21, KL-27) | G17 | birim | Gözden geçirme (otomatik) | `README.md` | "Veri kaynakları" bölümünde Open Library ve CC0 atfı; "Demo verisi" bölümünde `migrate`, `createsuperuser` ve `load_seed_data --profile demo --actor <ad>` bu sırayla | Geçti |
| TC-353 | NFR-01 (ADR-0058) | G18 | birim | Karar tablosu | `--db` içinde bir üyenin e-postası `ali@ornek.com`; ayrı testte üyelerin e-postası boş ya da `@example.invalid` ile bitiyor | İlkinde stderr'de "Tohum verisi olmayan veritabanı", çıkış 1 ve hiçbir HTTP isteği yok; ikincisinde koruma geçer | Geçti |
| TC-354 | NFR-01 (küçük karar 10) | G18 | birim | Durum geçişi | Sahte istemciyle iş parçacığı: açık ödünç yokken seçilen iade ve uzatma; ödünç sonrası uzatma ve iade | Ödünçsüz iade ve uzatma istek atmadan yeniden seçilir ve raporda sayılmaz; uzatılan ödünç bir daha uzatılmaz ama iade edilebilir; iade edilen nüsha raf havuzuna döner | Geçti |
| TC-355 | NFR-01 (küçük karar 11) | G18 | birim | Denklik sınıfı | Yeni bir yorumlayıcıda `scripts.loadtest` import edilir; `pyproject.toml` okunur | `sys.modules`'ta `django` yok; `testpaths` `scripts`'i ve bütün app klasörlerini içerir | Geçti |
| TC-356 | NFR-01 (KL-17) | G18 | birim | Senaryo | Yerel sahte HTTP sunucusu: GET `/giris/` `csrftoken` çerezi verir; POST `/giris/` 302 ile `Secure` işaretli `sessionid` ve yeni `csrftoken` verir | Giriş POST'unda `X-CSRFToken` çerezdeki jetona eşit; sonraki isteklerde `sessionid` düz HTTP'de de gönderilir ve POST'larda yeni jeton kullanılır; 303 yönlendirmesi izlenmez | Geçti |
| TC-357 | FR-29 (ADR-0059) | G17 | birim | Denklik sınıfı | Özgün başlıklı eser ve eşleşen Türkçe baskısı; baskısız eser; `editions` alanı boş eser; önce Türkçe olmayan, sonra Türkçe baskılı eser; dili boş baskı; Türkçe harfi yalnız eser başlığında olan kayıt; istek alanları | Başlık, ISBN ve `ol_id` (`OL…M`) ilk Türkçe baskıdan, yazar ve yıl eserden gelir; Türkçe baskısı olmayan kayıt atılır; beş kural baskıya uygulanır; istek `editions.key`, `editions.title`, `editions.isbn`, `editions.language` alanlarını ister; `FILTER_VERSION` 2 | Geçti |
| TC-358 | FR-29 (ADR-0059) | G17 | birim | Durum geçişi | Sahte açıcı: sayfa 1'de 500, zaman aşımı, zaman aşımlı `URLError`, sonra kayıt; sayfa 2'de 503, sonra kayıt; ayrı koşularda dört kez 500, bir kez 404 ve `main` ile dört kez 502 | Aynı sayfa yeniden istenir; bekleme 2, 4, 8 sn (sayfa başına sıfırlanır), sayfalar arası 1 sn; dört 500'den sonra hata yükselir; 404 yeniden denenmez; `main` "Open Library'ye erişilemedi" ile çıkış 1 verir ve dosya yazmaz | Geçti |

## 7. Giriş ve çıkış ölçütleri

- **Giriş (görev başına):** Plan onaylı; görevin TC'leri bu tabloda; önceki görevlerin testleri geçiyor.
- **Görev çıkışı:** Görevin bütün TC'leri otomatik olarak geçiyor (elle olanlar hariç); görevin doğrulama komutu belirtilen çıktıyı veriyor; `python -m pytest -q` geçiyor; model değişikliği varsa `makemigrations --check --dry-run` "No changes detected" veriyor; NFR-13 hedefi tutuyor.
- **Faz 6 çıkışı:** Her Must FR'nin TC'leri geçiyor; her AC'nin kanıtı var; §4'teki kapsam hedefleri tutuyor; elle TC'ler (TC-223, TC-225…TC-234, TC-319) yapıldı ve sonuçları kaydedildi; açık Kritik ya da Yüksek hata yok. Should FR'lerde kalan hata ancak kullanıcı kararıyla kabul edilir.

## 8. Hata yönetimi

- **Kayıt yeri (KL-46):** Faz 5 ve 6'da bulunan hatalar bu bölümdeki tabloya `HT-01`'den başlayarak yazılır. Görev içinde TDD döngüsünde düzelen kırmızı testler hata sayılmaz.
- **Önem:** Kritik (veri kaybı, para hesabında yanlışlık, yetki açığı), Yüksek (bir Must FR çalışmıyor), Orta (Should FR ya da geçici çözümü olan Must FR), Düşük (metin, görünüm).
- **Akış:** Hata önce kırmızı bir testle yeniden üretilir, sonra düzeltilir; TC tabloda yoksa yeni TC numarasıyla eklenir.

| ID | Tarih | TC | Önem | Açıklama | Durum |
|---|---|---|---|---|---|
