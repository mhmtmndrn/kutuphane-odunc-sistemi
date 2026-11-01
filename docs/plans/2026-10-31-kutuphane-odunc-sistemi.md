# Görev planı: Kütüphane ödünç alma sistemi

- **Tarih:** 2026-10-31
- **İz:** Tam
- **Durum:** Faz 4 tamamlandı, onay kapısı geçildi. Kararlar alındı (ADR-0026…0048; küçük karar listesi onaylandı, 2026-10-31). Görevler, risk kaydı, test planı (319 TC), izlenebilirlik ve tutarlılık kontrolü yazıldı; inşa kontrolü ayıklandı (§8.1). Plan, test planı ve KL-1…KL-46 onaylandı (2026-10-31); faz 5 başladı: G01 tamam (2026-10-31); G02 kararları ADR-0049, ADR-0050 ve §11'de. Faz 5 tamamlandı (G01–G19, PR #1…#7, 2026-11-01). Faz 6 başladı (2026-11-01): ADR-0067, §12.

## 1. Süreç uyarlaması

- **İstek:** Küçük bir kütüphane için web tabanlı kitap ödünç alma sistemi: üyeler, kitaplar, ödünç verme ve iade, gecikme cezası.
- **Bağlam:** Gerçek kullanım (ürün modu). Kullanıcı yalnız kütüphane personeli; üyeler sisteme giriş yapmaz. Dağıtım: yerel sunucu, LAN (faz 1). Süre kısıtı yok. Dil, framework ve veritabanı seçilmedi; faz 3'te alternatiflerle sorulacak.
- **Artefaktlar:** `docs/srs.md`, `docs/architecture.md`, `docs/data-design.md`, `docs/test-plan.md`, `docs/risk-register.md`, bu görev planı, `docs/decisions/` altında ADR'ler.
- **Test yaklaşımı:** TDD.
- **Fırsat taraması:** 2026-10-31, ürün modu.
  - **Barkodla ödünç/iade masası:** kapsamda (FR numarası faz 1'de verilecek). Minimum sürüm: barkod okutmaya göre tasarlanmış ödünç/iade alanları (USB okuyucu klavye gibi çalışır), nüsha başına benzersiz kod, toplu etiket basmak için PDF. B planı: aynı alanlara elle kod girişi ya da arama. Not: nüsha düzeyinde takip gerektirir; veri tasarımında kullanıcıya sorulacak.
  - **Otomatik son tarih ve gecikme hatırlatması (e-posta):** kapsamda (FR numarası faz 1'de verilecek). Minimum sürüm: günde bir kez çalışan görev; son tarihe 2 gün kala ve gecikmenin 1. gününde şablonlu e-posta, gönderim kaydı. B planı: personelin tetiklediği "hatırlatma gönder" düğmesi ve uygulama içinde geciken ödünç listesi. Açık noktalar: e-posta servisi seçimi (faz 3'te ADR), KVKK açık rızası (faz 1), uygulama sürekli çalışmıyorsa zamanlanmış görevin atlanması.
  - **ISBN ile otomatik katalog doldurma:** fizibilite. Faz 2'de araştırılacak soru: Open Library, Google Books ve benzeri ücretsiz meta veri API'leri Türkçe kitapları ne oranda kapsıyor? Bunu 20–30 örnek ISBN ile ölç; lisans, rate limit ve kullanım şartlarını kontrol et. Kullanıcı bulgulardan sonra karar verecek. B planı: elle giriş.
  - **Gerek yok (yeniden önerilmeyecek):** `ml-recsys` (üye arayüzü yok, etkileşim verisi az), `ml-predict` (veri az, hatırlatma kuralla çözülüyor), `llm-feature`, `llm-rag`, `agent-*`, `ml-pretrained` (kapaktan OCR; ISBN sorgusu daha ucuz), `opt-*`, `sys-realtime`.

## 2. Dokunulan dokümanlar

| Doküman | Değişiklik |
|---|---|
| docs/srs.md | Faz 1'de oluşturuldu, onaylandı (2026-10-31); faz 2 ve faz 3 değişiklikleri onayla işlendi; faz 4 değişiklikleri kullanıcı kararlarıyla işlendi (ADR-0026…0047) |
| docs/architecture.md | Faz 3'te oluşturuldu (2026-10-31) |
| docs/data-design.md | Faz 3'te oluşturuldu (2026-10-31) |
| docs/decisions/0001…0025 | Faz 3'te yazıldı (2026-10-31) |
| docs/decisions/0026…0048 | Faz 4'te yazıldı (2026-10-31); 0048 bir süreç kararıdır |
| docs/decisions/0049, 0050 | Faz 5'te, G02'den önce yazıldı (2026-10-31): kilit cevabı ve kilit süresi |
| docs/decisions/0056…0058 | Faz 5'te, G17–G18 açılışında yazıldı (2026-11-01): Open Library çekimi, tohum telefonları, yük betiği koruması |
| docs/decisions/0059 | Faz 5'te, PR #6'nın yerel doğrulamasında yazıldı (2026-11-01): demo kitap kaydı eşleşen Türkçe baskıdan alınır; ADR-0033'ün durumu güncellendi |
| docs/decisions/0060…0066 | Faz 5'te, G19 açılışında yazıldı (2026-11-01): kurulum belgesinin yapısı, sabit IP, servis hesabı, araç sürümleri, sürüm arşivi ve güncelleme, Caddy erişim logu yok, dağıtım dosyalarının testleri |
| docs/decisions/0067 | Faz 6 açılışında yazıldı (2026-11-01): deneme projesi, tek Windows makinesi, `127.0.0.2`, kapsam dışı elle TC'ler, `v1.0.0-rc.1` etiketi |
| docs/architecture.md, docs/data-design.md | Faz 4 tutarlılık düzeltmeleri (§8) |
| docs/test-plan.md | Faz 4'te oluşturuldu (2026-10-31): 319 TC, test taslağından revize edildi; G14–G16 açılışında TC-320…TC-339, G17–G18 açılışında TC-340…TC-356, PR #6 yerel doğrulamasında TC-357…TC-358, G19 açılışında TC-359…TC-366 eklendi (2026-11-01) |
| docs/data-design.md | I6'ya ADR-0018 istisnası yazıldı (§8 T-02) |
| docs/risk-register.md | Faz 4'te oluşturuldu (2026-10-31); plan §6'daki riskler buraya taşındı |

## 3. Kararlar

Faz 0'da verilen süreç kararları: Tam iz, yukarıdaki artefakt seti, TDD. Faz 3 kararları aşağıda ve ADR-0001…0025'te.

Faz 1 kapsam kararları SRS'te kaynaklarıyla birlikte duruyor (tek üye tipi, yönetici ve görevli rolleri, rezervasyon yok, yerel sunucu, ayarlanabilir kurallar, KVKK). Stack ve servis seçimleri faz 3'te ADR olacak.

**Küçük kararlar (onaylandı 2026-10-31):**

1. Varsayılan ayarlar: günlük ceza 5,00 TL; ödünç başına ceza üst sınırı 150,00 TL; borç eşiği 50,00 TL (eşik dahil engeller); saklama süresi 2 yıl.
2. Gecikme günü = iade tarihi − son tarih (takvim günü); son tarihte iade 0 gün. *(Yerini aldı: ADR-0040. Aralıktaki tek tek kapalı tarihler düşülür.)*
3. Uzatmada yeni son tarih = mevcut son tarih + ödünç süresi, kapalı gün kaydırmasıyla.
4. Kayıp ve hasar işaretlemesini yalnız yönetici yapar.
5. Hasarlı nüsha: yönetici rafa döndürür (onarıldı) ya da kayıttan düşer (durum: Kayıttan düşmüş).
6. Açık ödüncü olan üye pasifleştirilemez; borcu olan üye uyarıyla pasifleştirilebilir.
7. Hatırlatma görevi her gün 09:00'da çalışır; ödünç ve hatırlatma tipi başına en fazla bir gönderim.
8. Üye no otomatik ve sıralı; nüsha barkodu Code 128, 8 haneli sıralı; etiket PDF'i A4, sayfa başına 24 etiket (3×8).
9. Parola en az 10 karakter; hesap kilidi 15 dakika.
10. Saat dilimi Europe/Istanbul; gün sınırı yerel gece yarısı.
11. Af kısmi olabilir (tutar ≤ borç); borçtan fazla ödeme kabul edilmez.

**Faz 2 kapsam kararları (2026-10-31):**

- ISBN kaynakları: ücretsiz global API'ler (Open Library, Google Books) ve Türk kaynakları (Milli Kütüphane, ISBN Türkiye vb.); ücretli servisler kapsam dışı.
- Örneklem: karma, tabakalı (klasik, güncel çok satan, çocuk, akademik, küçük yayınevi).
- FR-30 karar eşiği: başlık ve yazar isabeti ≥ %60 ise FR-30 tutulur.
- Demo veri seti lisansı: yalnız CC0, kamu malı ya da ODbL.

**Faz 2 küçük kararları (onaylandı 2026-10-31):**

1. Raporlar: `docs/research/2026-10-31-isbn-meta-veri-apileri.md`, `docs/research/2026-10-31-demo-kitap-veri-seti.md`.
2. Örneklem 25 ISBN (5 tabaka × 5); her ISBN bir yayınevi ya da kitapçı sayfasından doğrulanır ve ISBN-13 kontrol hanesi denetlenir; kaynak bağlantısı raporda.
3. Ölçüm: scratchpad'de standart kütüphaneli Python betiği, yalnız anahtarsız uçlar, saniyede en fazla 1 istek; depoya kod girmez; ISBN listesi ve ham sonuç tablosu rapora.
4. İsabet = başlık ve yazar doğru; yayınevi ve yıl doluluğu ile Türkçe karakter bozulması ayrıca raporlanır.
5. Türk kaynakları için programatik erişim yolu (API, SRU/Z39.50) ve şartlar incelenir; yoksa ölçüme girmez; kazıma önerilmez.
6. İki `researcher` subagent'ı paralel (API şartları; demo veri seti); kapsam ölçümünü ana oturum yapar.
7. Bulgu SRS'i değiştirirse önce kullanıcıya sorulur; faz sonunda STATUS ve plan güncellenir, `docs:` commit'i önerilir.

**Faz 2 sonuç kararları (kullanıcı, 2026-10-31):**

- Google Books kapsam dışı: ToS §5e kalıcı yerel kopyayı yasaklıyor.
- Türk kaynakları: KYGM Z39.50 iddiası beklenmeden açık soru olarak kaldı (SRS açık soru 8). E-posta gönderilecekse kullanıcı kendisi gönderir.
- LC SRU ve Wikidata ölçüme eklendi; kapsamı artırmadılar.
- Open Library lisans belirsizliği FR-29 için kabul edildi. Koşullar: yalnız bibliyografik alanlar (başlık, yazar, yayınevi, yıl, ISBN) alınır, kapak alınmaz, her kayıtta OL kimliği tutulur, atıf notu konur.
- FR-30 Could → Won't: Open Library isabeti %52, eşik %60 (n = 25, %95 aralığı [%33, %70]). SRS'te işaretlendi, ID silinmedi.
- AC-29 güncellendi: kitaplar açık veri setinden (Open Library) ya da sentetik olarak yüklenir; üyeler sentetiktir.
- Raporlar: [ISBN meta veri kaynakları](../research/2026-10-31-isbn-meta-veri-apileri.md), [demo kitap veri seti](../research/2026-10-31-demo-kitap-veri-seti.md).

**Faz 3 kararları (kullanıcı, 2026-10-31):** Her biri bir ADR olarak `docs/decisions/` altında.

| ADR | Karar |
|---|---|
| 0001 | Python + Django |
| 0002 | SQLite (WAL, IMMEDIATE işlemler) |
| 0003 | Sunucuda üretilen HTML ve az vanilla JS |
| 0004 | Kurum SMTP hesabı (SRS açık soru 3) |
| 0005 | Caddy ve yerel CA ile HTTPS (SRS açık soru 4) |
| 0006 | Haftalık şifreli USB rotasyonu (R-04) |
| 0007 | Uygulama içi APScheduler 3.x, idempotent komutlar |
| 0008 | ISBN-13 normalize, "978" düzeltme önerisi |
| 0009 | django-axes |
| 0010 | WinSW (Windows), systemd (Linux) |
| 0011 | cryptography (scrypt + AES-GCM) |
| 0012 | waitress, tek süreç |
| 0013 | Django 5.2 LTS, Python 3.11 |
| 0014 | reportlab |
| 0015 | Alan başına Django app, saf domain |
| 0016 | Tam sayı kuruş |
| 0017 | Ödeme FIFO dağıtımı |
| 0018 | Saklama sonrası bağ koparma ve arşiv sayacı (FR-25/AC-25 uzlaşması) |
| 0019 | Türkçe harf düşürme ve diakritik katlama |
| 0020 | Bakiye-nötr iade hareketi |
| 0021 | Kaleme yönelik af |
| 0022 | Rıza olay geçmişi |
| 0023 | Ödünç anındaki ceza oranı |
| 0024 | Üretimde Django admin paneli yok |
| 0025 | Üye kartı PDF'i |

SRS değişiklikleri kullanıcı onayıyla yapıldı:

- FR-04'e ISBN kuralı eklendi.
- FR-37 eklendi (haftalık şifreli dışa aktarma, Should) ve AC-30 yazıldı.
- FR-38 eklendi (üye kartı PDF'i, Should) ve AC-31 yazıldı.
- AC-25'e arşiv sayacı senaryosu eklendi.
- Açık soru 3 ve 4 kapatıldı.

Kapsam içi FR sayısı 31 (23 Must, 8 Should), Won't sayısı 7.

**Faz 3 küçük kararları (onaylandı 2026-10-31):**

1. Rol: özel `StaffUser(AbstractUser)` modelinde `role` alanı (Yönetici, Görevli). Yetki denetimi servis katmanında tek bir dekoratör/mixin ile yapılır.
2. Üye no otomatik artan tam sayıdır. Ödünç ekranında üye ve nüsha alanları ayrıdır.
3. Nüsha barkodu, nüsha kimliğinin 8 haneye sıfırla doldurulmuş halidir. Ayrı sayaç tablosu yoktur.
4. Saklama süresi yıl cinsinden tutulur. Koşul: tarih + süre < bugün.
5. Uzatmada ödüncün ceza oranı kopyası korunur.
6. Hatırlatma pencereleri: DUE_SOON için son tarih −2 ile son tarih arası, OVERDUE_1 için son tarih +1 ile +7 arası. Pencere dışı hatırlatma gönderilmez.
7. SMTP hatası FAILED olarak kaydedilir ve pencere içinde yeniden denenir. Tekrar engeli yalnız SENT kayıtları için geçerlidir.
8. `has_email_consent` alanı olay eklemesiyle aynı işlemde güncellenir. Üye anonimleştirilince rıza olayları silinir.
9. Haftalık kapalı günler ve tek tek kapalı tarihler ayrı tablolardadır.
10. Denetim kaydı ayrıntıları JSON'dur. Kayıtlar güncellenmez ve silinmez. Ayrıntılarda aynı anda hem üye hem ödünç bulunmaz.
11. Komut adları: `send_reminders`, `anonymize_expired`, `backup_db`, `export_backup`, `restore_backup`, `load_seed_data`.
12. Kod yerleşimi: `<app>/domain.py` saf kurallar, `<app>/services.py` veritabanı işlemleri.
13. Görev saatleri: yedek 02:00, anonimleştirme 02:30, hatırlatma 09:00, dışa aktarma pazartesi 03:00 (Europe/Istanbul).
14. Günlük yedek dosyası `library-YYYYMMDD.sqlite3` adıyla yazılır; 30 günden eskiler başarılı yedekten sonra silinir.
15. Dışa aktarma parolası, yalnız servis hesabının okuyabildiği bir dosyadan okunur; yolu ortam değişkeninde verilir.
16. Yapılandırma ortam değişkenleriyle verilir (WinSW `<env>`, systemd `EnvironmentFile`). python-dotenv eklenmez.

**Faz 3 varsayımlarının teyidi (2026-10-31):**

- (a) Onaylandı. `pytest`, `pytest-django`, `coverage` ve `argon2-cffi`, ADR-0001 kapsamında sayılır.
- (b) Onaylandı. Hatırlatmada önce e-posta gönderilir, sonra kayıt yazılır; bedeli nadir bir tekrar (architecture §10).
- (c) Onaylandı (faz 4 küçük karar 6).
- (d) Karara bağlandı: ADR-0028.

**Faz 4 kritik kararları (2026-10-31; faz 3'ten devreden açık noktaların hepsi kapandı):**

- [ADR-0026](../decisions/0026-shelf-copy-status-marking.md): Raftaki nüsha bedelsiz işaretlenir (FR-39, AC-32).
- [ADR-0027](../decisions/0027-refund-audit-term.md): Para iadesi FR-26'ya eklenir; "iade" yalnız kitap iadesidir.
- [ADR-0028](../decisions/0028-open-weekday-rule-shift-bound.md): En az bir açık hafta günü kuralı (FR-24) ve 366 günlük kaydırma sınırı.
- [ADR-0029](../decisions/0029-static-files-caddy.md): Statik dosyalar Caddy `file_server` ile sunulur.
- [ADR-0030](../decisions/0030-barcode-decode-test.md): Barkod testi pypdfium2 ve zxing-cpp ile yapılır (yalnız geliştirme bağımlılığı).
- [ADR-0031](../decisions/0031-load-test-stdlib-script.md): NFR-01 ölçümü stdlib yük betiğiyle yapılır.
- [ADR-0032](../decisions/0032-member-card-content-reprint.md): Kartta ad bulunmaz; kayıp kart aynı numarayla yeniden basılır.
- [ADR-0033](../decisions/0033-demo-books-one-time-fetch.md): Demo kitapları bir kez çekilir ve depoda JSON olarak tutulur; 300 kayıt, otomatik filtre (R-06).
- [ADR-0034](../decisions/0034-project-layout-flat.md): Düz kök klasör yapısı.
- [ADR-0035](../decisions/0035-library-name-setting.md): Kütüphane adı bir ayar alanıdır (FR-23).

**Faz 4 5. tur kararları (2026-10-31; ADR-0036 ve inşa kontrolü bulguları, §8.1):**

- [ADR-0036](../decisions/0036-label-card-selection-range-checkbox.md): Etiket ve kart için aralık girişi ve seçim kutuları (FR-06, FR-38).
- [ADR-0037](../decisions/0037-refund-precondition-found-lost-copy.md): Para iadesi yalnız bulunan kayıp nüshanın bedeline; `loan.copy_found_on`; bağsız bedelde iade yok (I5, bulgu 1).
- [ADR-0038](../decisions/0038-seed-data-actor-argument.md): Tohum veride zorunlu `--actor` (bulgu 2).
- [ADR-0039](../decisions/0039-reminder-per-due-date.md): `reminder_log.due_on`; tekrar engeli son tarih başına (bulgu 3).
- [ADR-0040](../decisions/0040-late-days-skip-closed-dates.md): Gecikme günü tek tek kapalı tarihleri saymaz; FR-12 değişti (bulgu 4).
- [ADR-0041](../decisions/0041-manual-cancellation-unlinked-fee.md): Bağı koparılmış bedelin yöneticice gerekçeli iptali (bulgu 5).
- [ADR-0042](../decisions/0042-member-reactivation.md): Pasif üyeyi personel yeniden aktifleştirir; FR-40 (bulgu 6).
- [ADR-0043](../decisions/0043-staff-password-change.md): Kendi parolasını değiştirme ve zorunlu ilk değişiklik; FR-41 (bulgu 7).
- [ADR-0044](../decisions/0044-backup-warning-home.md): Ana sayfada yedek uyarısı; FR-42 (bulgu 8).
- [ADR-0045](../decisions/0045-anonymization-deferred-for-debt.md): Borçlu üyenin anonimleştirilmesi ertelenir; hukuki teyit SRS açık soru 6 (bulgu 10).
- [ADR-0046](../decisions/0046-checkout-member-input-classification.md): Ödünç ekranında üye alanı biçime göre yorumlanır (bulgu 12).
- [ADR-0047](../decisions/0047-consent-event-ordering.md): Rıza olaylarının sıra kuralı (bulgu 13).
- [ADR-0048](../decisions/0048-cloud-sessions-implementation.md): Uygulama, özel GitHub reposundan bulut oturumlarıyla (süreç kararı).
- [ADR-0049](../decisions/0049-lockout-response-429.md): Kilitli hesaba giriş denemesi 429, giriş şablonu ve kilit mesajıyla cevaplanır (faz 5, G02).
- [ADR-0050](../decisions/0050-lockout-cooloff-not-reset.md): Kilitliyken yapılan denemeler kilit süresini uzatmaz (faz 5, G02).
- [ADR-0051](../decisions/0051-axes-w006-silenced.md): django-axes `axes.W006` uyarısı gerekçe yorumuyla susturulur; kilit yalnız kullanıcı adına göre kalır (faz 5, PR #1 incelemesi).
- [ADR-0052](../decisions/0052-smtp-timeout.md): Üretimde SMTP bağlantısına 10 saniyelik zaman aşımı (`EMAIL_TIMEOUT = 10`, `prod.py`); zaman aşımı FAILED kaydına düşer ve pencere içinde yeniden denenir (faz 5, G13 açılışı).
- [ADR-0053](../decisions/0053-hourly-catch-up.md): Kaçan görevler açılışa ek olarak saatlik bir telafi göreviyle de telafi edilir; cron ve telafi görevlerinde `misfire_grace_time=3600`, `coalesce=True` (ADR-0007'ye ek; faz 5, G14–G16 açılışı).
- [ADR-0054](../decisions/0054-restore-keeps-pre-restore-copy.md): Geri yükleme mevcut veritabanını ve `-wal`/`-shm` dosyalarını silmez, `<db>.pre-restore-YYYYMMDD-HHMMSS` adıyla koruma kopyası olarak bırakır (faz 5, G14–G16 açılışı).
- [ADR-0055](../decisions/0055-reminder-log-error-cleared-on-unlink.md): Ödüncün üye bağı koparılırken o ödüncün `reminder_log.error` alanları NULL yapılır (NFR-08; faz 5, G14–G16 açılışı).
- [ADR-0056](../decisions/0056-open-library-fetch-network-blocked.md): Bulut oturumunda Open Library'ye erişilemezse `seed/books_openlibrary.json` olmadan devam edilir; testler örnek dosyayla koşar, gerçek dosya yerel doğrulamada çekilip dala commit'lenir (ADR-0033'e ek; faz 5, G17–G18 açılışı).
- [ADR-0057](../decisions/0057-seed-phone-numbers.md): Tohum verideki telefonlar `000 ddd dd dd` biçiminde, hiçbir gerçek aboneye denk gelmeyen sahte numaralardır (TC-234; faz 5, G17–G18 açılışı).
- [ADR-0058](../decisions/0058-loadtest-seed-only-guard.md): `--db` içinde e-postası `@example.invalid` ile bitmeyen bir üye varsa yük betiği "Tohum verisi olmayan veritabanı" ile çıkış 1 verir ve hiç istek atmaz (faz 5, G17–G18 açılışı).
- [ADR-0059](../decisions/0059-demo-books-turkish-edition.md): Demo kitap kaydının başlığı, ISBN'i ve OL kimliği eserden değil, aramanın `editions` alanındaki ilk Türkçe baskıdan alınır; ADR-0033'ün beş kuralı o baskıya uygulanır, Türkçe baskısı olmayan kayıt atılır; filtre sürümü 2. HTTP 5xx ve zaman aşımında aynı sayfa en çok 3 kez daha, 2/4/8 sn beklenerek istenir (faz 5, PR #6 yerel doğrulaması).

- [ADR-0060](../decisions/0060-install-doc-common-body-two-platforms.md): `docs/kurulum.md` ortak bir gövde ve iki eşit ayrıntıda platform bölümünden (Windows, Linux) oluşur; ortak adımlar bir kez yazılır (faz 5, G19 açılışı).
- [ADR-0061](../decisions/0061-access-by-static-ip.md): Personel uygulamaya sunucunun DHCP rezervasyonuyla sabitlenmiş IP'siyle erişir; `LIBRARY_HOST`, `LIBRARY_BIND` ve `LIBRARY_ALLOWED_HOSTS` bu IP'dir, `tls internal` IP sertifikası üretir; personel bilgisayarlarına masaüstü kısayolu (faz 5, G19 açılışı).
- [ADR-0062](../decisions/0062-service-account.md): Servisler ayrı yerel hesapla çalışır (Windows `library-svc`, Linux `library`); veri, gizli değer ve Caddy veri klasörleri yalnız bu hesaba açılır (faz 5, G19 açılışı).
- [ADR-0063](../decisions/0063-tool-versions-winsw-caddy.md): WinSW 2.12.0; Caddy 2.11.7, indirme bağlantısı sürüme sabit, güncelleme elle (faz 5, G19 açılışı).
- [ADR-0064](../decisions/0064-release-zip-and-update-procedure.md): Kod sunucuya bir `vX.Y.Z` etiketinden `git archive` ile üretilen zip olarak gelir; belge ilk kurulum ve güncelleme yordamını verir (faz 5, G19 açılışı).
- [ADR-0065](../decisions/0065-caddy-no-access-log.md): Caddy erişim logu tutulmaz; Caddyfile'da `log` yönergesi yoktur (NFR-08; faz 5, G19 açılışı).
- [ADR-0066](../decisions/0066-deploy-files-consistency-tests.md): Dağıtım dosyaları ve kullanıcı belgeleri `tests/test_deploy_files.py`'deki tutarlılık testleriyle denetlenir; elle TC'ler de kalır (faz 5, G19 açılışı).

- [ADR-0067](../decisions/0067-phase6-trial-project-single-windows-machine.md): Faz 6 deneme projesi olarak bu Windows 11 makinesinde, yalnız Windows, `127.0.0.2` adresiyle yapılır; kurulumu kullanıcı belgeyi izleyerek yapar; kurulum `v1.0.0-rc.1` zip'inden; TC-226, TC-227, TC-228, TC-232, TC-233 kapsam dışı, TC-229 ve TC-230 kısmi (faz 6 açılışı).
- [ADR-0068](../decisions/0068-phase6-python-from-nuget-package.md): Faz 6 test ortamında servis Python'u resmi NuGet paketinden `C:\Program Files\Python311`'e açılır (faz 6, bulgu B1).
- [ADR-0069](../decisions/0069-closed-due-date-not-a-late-day.md): Ödünçten sonra kapatılan son tarih de gecikme günü sayılmaz; `late_days` aralığı `[due_on, on]` (faz 6 spec incelemesi, B11; ADR-0040'ı tamamlar).
- [ADR-0070](../decisions/0070-email-change-keeps-consent.md): E-posta adresi başka bir adresle değişince rıza korunur, olay yazılmaz (faz 6 spec incelemesi).

Sıradaki ADR numarası: 0071.

**Faz 4 küçük kararları (onaylandı 2026-10-31):**

1. Varsayılan ödünç süresi 14 gün, aynı anda ödünç limiti 3.
2. waitress `threads=8`.
3. Etiket: 70 × 37 mm, A4'te 3×8, üst ve alt boşluk 0,5 mm, yan boşluk 0. İçerik: kütüphane adı, 15 mm yüksekliğinde Code 128 (modül 0,33 mm), 8 haneli kod, başlığın ilk 30 karakteri. Ölçüler `LabelLayout` dataclass'ında parametredir.
4. Kart: ID-1 (85,6 × 54 mm), A4'te 2×5 = 10 kart, ince gri kesim çizgileri; içerik ADR-0032'deki gibi.
5. Paylaşılan PDF yardımcısı kökte, app olmayan `pdf/` paketinde: `pdf/sheets.py: render_sheet(items: list[SheetItem], layout: SheetLayout) -> bytes`.
6. architecture §6.4'teki ortam değişkenleri ve `LIBRARY_STATIC_ROOT`; `.libx` için scrypt n=2^17, r=8, p=1; çıkış kodları 0 başarı, 1 hata, 2 kullanım hatası.
7. ADR ayrıntıları olduğu gibi onaylandı:
   - 366 günlük sınır ve hata mesajları (ADR-0028).
   - `library_name` varchar(80), varsayılan "Kütüphane", "…" ile kısaltma (ADR-0035).
   - Yük senaryo karışımı %40/20/20/10/10, süre 120 sn (ADR-0031).
8. Denetim eylemleri: `PAYMENT`, `WAIVER`, `FEE`, `REFUND`, `COPY_LOST`, `COPY_DAMAGED`, `COPY_FOUND`, `COPY_REPAIRED`, `COPY_WITHDRAWN`, `SETTINGS_CHANGED`, `CLOSED_DAY_CHANGED`, `STAFF_CHANGED`. Raftaki nüsha geçişleri aynı kodları kullanır; ayrıntıda `{"from": "ON_SHELF"}` bulunur.
9. "Bugün"ün tek kaynağı `administration/clock.py: today() -> date` (`timezone.localdate()`). Servisler bunu çağırır, domain'e parametre olarak geçer; testlerde `monkeypatch` ile sabitlenir.
10. `requirements.txt` ve `requirements-dev.txt` dosyalarında `==` ile sabitleme. Sürümler faz 5'in ilk görevinde PyPI'deki son yamaya göre belirlenir; pip-tools kullanılmaz.
11. Test düzeni:
    - Her app'te `tests/test_domain.py`, `tests/test_services.py` ve `tests/test_views.py` dosyaları olur.
    - `pyproject.toml`'da `DJANGO_SETTINGS_MODULE=library_site.settings.test` tanımlanır ve `slow` işareti kullanılır.
    - Kapsam: `coverage run --branch -m pytest`, ardından `coverage report --include="*/domain.py" --fail-under=90`.
    - Test verisi `tests/support/factories.py` içindeki düz fonksiyonlarla kurulur; factory_boy kullanılmaz.
12. Tohum veri:
    - `--profile demo`: 300 kitap, kitap başına 1–3 nüsha, 200 üye, 150 açık ödünç (10'u gecikmiş).
    - `--profile load`: NFR-02 ölçeği.
    - `--seed 42` ile deterministik; adlar `seed/` altındaki sabit Türkçe ad ve soyad listelerinden üretilir.
13. Open Library atıf notu, README'nin "Veri kaynakları" bölümüne ve JSON dosyasının `_meta` alanına konur.
14. Log: `logging` stdout'a yazar, biçim `%(asctime)s %(levelname)s %(name)s %(message)s`. Görev sonuçları ayrıca `job_run` tablosuna yazılır.
15. URL'ler Türkçe kısa yollardır (`/odunc/`, `/iade/`, `/uyeler/`, `/kitaplar/`, `/nushalar/`, `/borclar/`, `/gecikenler/`, `/ayarlar/`, `/kapali-gunler/`, `/personel/`, `/denetim/`, `/giris/`, `/cikis/`). Tam liste görevlerde yer alır.
16. Faz 5'te her görev grubu için bir `feature/<ad>` dalı açılır. Commit her görevin sonunda önerilir ve yalnız kullanıcı onayıyla atılır; `main`'e birleştirme de kullanıcı onayıyla yapılır. *(Bulut istisnası, ADR-0048: bulut oturumu kendi dalına görev başına commit atıp push eder; onay `main`'e birleştirmede alınır.)*

Karar listesi dışında kalan iki ayrıntı ADR-0032'de yazılı: kartta "Üye No" etiketi bulunur ve kullanım kılavuzuna "adı sor" adımı eklenir.

**Faz 4 görev yazımı küçük karar listesi (KL; onaylandı 2026-10-31, onay kapısında):** Görevler yazılırken çıkan iç ayrıntılardır. Görevler bu maddelere atıf yapar.

1. **`job_run` modelinin yeri:** `administration/models.py` (`JobRun`) ve `administration/jobs.py` (`run_job`, `last_success`). Gerekçe: ana sayfadaki dışa aktarma uyarısı ve bütün komutlar zaten `administration`'a bağımlı; yeni ok gerekmez. *Alternatif:* `operations` (ama `administration → operations` döngü oluşturur).
2. **`normalize_tr`'nin yeri:** `catalog/domain.py`'de kalır; architecture §3'e `members → catalog` (yalnız `catalog.domain`) oku eklenir. *Alternatif:* app olmayan bir `text/` paketi.
3. **Para yardımcıları:** `administration/money.py`.
   - `parse_tl` şu girdileri kabul eder: "15", "15,5", "15,50", "1.250,00", "1250". Negatif değeri, ikiden fazla ondalık haneyi ve boş girdiyi `ValueError` ile reddeder.
   - Binlik ayırıcı nokta yalnız üç haneli gruplarda kabul edilir; "15.00", "1.25" ve "1,250.00" `ValueError` verir.
   - `format_tl(1250_00) → "1.250,00 TL"`.
   - Şablon filtresi: `{{ x|tl }}`.
4. **Uygulama kilidi:** `wsgi.py` açılışta `LIBRARY_DB_PATH + ".app.lock"` dosyası üzerinde işletim sistemi kilidi tutar (Windows'ta `msvcrt.locking`, Linux'ta `fcntl.flock`). `restore_backup` kilidi bloklamadan alamazsa reddeder. Kilit süreç ölünce kendiliğinden kalkar. *Alternatif:* PID dosyası (çökmeden sonra bayat kalır).
5. **Zamanlayıcının başladığı yer:** `library_site/wsgi.py`, `get_wsgi_application()` çağrısından sonra. Uygulama servisinin komutu `waitress-serve --listen=127.0.0.1:8000 --threads=8 library_site.wsgi:application` olur. *Alternatif:* `AppConfig.ready()` (yönetim komutlarında da çalışır, ek koruma ister).
6. **Engel gösterimi:** Bütün geçerli engeller birlikte ve `Blocker` sırasıyla listelenir. SRS'te metni olmayan mesajlar: "Üye bulunamadı", "Nüsha bulunamadı", uzatmada "Ödünç gecikmiş", iadede "Bu nüshanın açık ödüncü yok".
7. **Sıfır bedel:** Kayıp ya da hasarda bedel ≥ 0,00 TL olabilir. 0 girilirse FEE yazılmaz, birikmiş ceza yine yazılır. *Alternatif:* bedel > 0 zorunlu.
8. **Son yönetici koruması:** Son aktif yönetici pasifleştirilemez ya da görevliye çevrilemez; mesaj "En az bir aktif yönetici kalmalı" olur. Yönetici kendi hesabını pasifleştiremez; mesaj "Kendi hesabınızı pasifleştiremezsiniz" olur.
9. **Parola doğrulayıcıları:** Django'nun dört varsayılan doğrulayıcısı kullanılır; `MinimumLengthValidator` için `min_length=10`.
10. **Arama kuralları:**
    - Üye: Sorgudan boşluk, `-`, `(` ve `)` atılır (KL-35 ile aynı karakterler). Geriye yalnız rakam kalırsa sonuç, üye no tam eşleşmesi ile `phone_digits LIKE %q%` sonuçlarının birleşimidir. Diğer sorgular özgün metinle `search_key LIKE %normalize_tr(q)%` ile aranır.
    - Kitap: Sorgu geçerli bir ISBN ise `isbn13` tam eşleşmesi, 8 haneli ise barkod tam eşleşmesi aranır. Her durumda `search_key` içerir araması da yapılır ve sonuçlar birleştirilir.
    - İki aramada da en fazla 50 sonuç döner.
11. **Sayfalama ve sıra:** Denetim kaydı 50 satır/sayfa ve en yeni önce. Arama sonuçları en fazla 50. Geciken listesi sayfalanmaz ve son tarihe göre en eskiden başlar.
12. **Rıza tarihi:** Varsayılan bugündür; gelecek tarih reddedilir.
13. **Hatırlatma metinleri** (Django şablonu; `{{ library_name }}`, `{{ title }}`, `{{ due_on|date:"d.m.Y" }}`, `{{ daily_fine|tl }}`, `{{ fine_cap|tl }}`):
    - DUE_SOON konu: "{{ library_name }}: İade tarihi yaklaşıyor". Gövde: "Merhaba,\n\n\"{{ title }}\" kitabının son iade tarihi {{ due_on }}. Bu tarihe kadar iade ederseniz gecikme cezası oluşmaz.\n\nBu e-postayı hatırlatma almaya onay verdiğiniz için alıyorsunuz. Onayınızı kütüphane masasında geri alabilirsiniz.\n\n{{ library_name }}"
    - OVERDUE_1 ve MANUAL konu: "{{ library_name }}: İade tarihi geçti". Gövde: "Merhaba,\n\n\"{{ title }}\" kitabının son iade tarihi {{ due_on }} idi. Geciken her gün için {{ daily_fine }} ceza işler (ödünç başına en fazla {{ fine_cap }}). Kitabı en kısa sürede iade etmenizi rica ederiz.\n\n(Onay cümlesi ve imza DUE_SOON ile aynı.)"
14. **Yedek saklama ve dışa aktarma yaşı:**
    - Adı `library-YYYYMMDD.sqlite3` olan ve tarihi `run_on − 30 gün`den eski yedekler silinir.
    - Dışa aktarma en yeni günlük yedeği kullanır; yedek yoksa çıkış 1.
    - Yaş, son SUCCESS EXPORT kaydının `run_on` değerinden hesaplanır. `bugün − run_on > 7` ise "Bina dışı yedek 7 günden eski" uyarısı gösterilir. Hiç dışa aktarma yoksa "Bina dışı yedek henüz alınmadı" gösterilir.
15. **Denetim hedefleri:**
    - Para eylemleri (`PAYMENT`, `WAIVER`, `FEE`, `REFUND`): hedef `ledger_entry` ve yeni hareketin kimliği. `details` alanı `{"amount_kurus", "member_no", "target_entry_id"?, "reason"?}` içerir.
    - Nüsha eylemleri: hedef `copy`. `details` alanı `{"from", "note", "fee_kurus"?}` içerir.
    - `SETTINGS_CHANGED`: hedef `library_settings`, kimlik 1.
    - `CLOSED_DAY_CHANGED`: tarih için hedef `closed_date` ve tarihin kimliği; haftalık günler için hedef `weekly_closed_day` ve kimlik 0. `details` alanı `{"op": "add"|"remove"|"set", ...}` içerir.
    - `STAFF_CHANGED`: hedef `staff_user` ve hesabın kimliği.
16. **Tohum profilleri:**
    - **demo** (küçük karar 12): Üyelerin %50'si e-postalı ve rızalıdır. Açık ödünçlerin 10'u gecikmiştir, 5 üyenin borcu vardır.
    - **load:**
      - 15.000 kitap, 20.000 nüsha, 5.000 üye; üyelerin %30'u e-postalı ve rızalıdır.
      - 100.000 ödünç; bunların 3.000'i açık ve açıkların 300'ü gecikmiştir.
      - Kapalı ödünçlerin %10'u gecikmeli iade edilmiştir: her biri için bir FINE ve aynı tutarda bir PAYMENT yazılır.
17. **Yük betiği adayları:** `scripts/loadtest.py`'ye `--db PATH` argümanı eklenir (ADR-0031'deki imzaya ek).
    - Betik başlangıçta veritabanını salt okunur açar (`file:…?mode=ro`). Engeli olmayan üyeleri ve Rafta nüshaları seçip iş parçacıklarına ayrık olarak böler.
    - Ödünç, uzatma ve iade işlemleri kendi açtığı ödünçler üzerinde zincir halinde yapılır. Aramalar, tohum verideki başlık sözcüklerinden seçilir.
    - CSRF jetonu `csrftoken` çerezinden `X-CSRFToken` başlığıyla gönderilir.
18. **Bağımlılık sabitleme:** Doğrudan ve geçişli bütün bağımlılıklar sabitlenir. Liste, temiz bir sanal ortamda kurulumdan sonra alınan `pip freeze` çıktısıdır. Windows'ta zoneinfo için `tzdata` de dahildir.
19. **Nüsha ekleme sınırı:** Tek istekte 1–50 nüsha.
20. **Kök testler:** `tests/test_authorization.py` (NFR-07), `tests/test_prod_settings.py`; yardımcılar `tests/support/` altında.
21. **Kullanıcı belgeleri** (Türkçe):
    - `README.md`: kısa tanıtım ve "Veri kaynakları" bölümü.
    - `docs/kurulum.md`: kurulum, geri yükleme ve USB rotasyonu.
    - `docs/kullanim-kilavuzu.md`: masa işleri.
22. **Import yönü:** `views` modülleri yapraktır ve her servisi çağırabilir. Pasifleştirme kuralı `circulation.services.deactivate_member` içindedir (G06, G11). *Alternatif:* üye ayrıntısını parçalara bölüp her app'in kendi parçasını sunması (daha karmaşık).
23. **Kısmi e-posta hatası** (§8.1-9): `send_reminders` en az bir FAILED olsa da `job_run` kaydını SUCCESS yazar. `detail` alanı "gönderilen=…, başarısız=…, atlanan=…" metnini taşır ve komutun çıkış kodu 1 olur. Telafi bu çalışmayı başarılı sayar; FAILED kayıtlar pencere içinde ertesi çalışmada yeniden denenir (faz 3 küçük karar 7). *Alternatif:* FAILED yazmak (telafi aynı gün yeniden dener, başarılı alıcılar tekrar engeline takılır).
24. **Dışa aktarma saklama** (§8.1-11): Başarılı dışa aktarmadan sonra, adı `library-export-YYYYMMDD.libx` olan ve tarihi `run_on − 56 gün`den eski dosyalar silinir (son 8 hafta). Desene uymayan dosyalara dokunulmaz. Domain: `exports_to_delete(names, run_on, keep_days=56)`.
25. **Etiket ve kart seçimi** (ADR-0036):
    - Aralık: Etikette iki uç 8 haneli barkod, kartta pozitif tam sayı üye no olur. Başlangıç bitişten büyükse "Başlangıç bitişten büyük olamaz". Aralık genişliği en fazla 240'tır ("En fazla 240 öğe seçilebilir").
    - Hariç tutma: Aralıktaki var olmayan barkodlar ve Kayıttan düşmüş nüshalar atlanır. Kartta pasif ve anonimleştirilmiş üyeler atlanır. Geriye öğe kalmazsa "Aralıkta basılacak nüsha yok" ya da "Aralıkta basılacak üye yok".
    - Seçim kutuları: Kitap ayrıntısında Kayıttan düşmüş olmayan nüshalarda, üye arama sonuçlarında aktif ve anonimleştirilmemiş üyelerde bulunur. `copy_ids` ya da `member_nos` adıyla POST edilir; sunucu aynı hariç tutma kurallarını yeniden uygular.
    - Aralık ve liste birlikte gelirse "Aralık ya da seçim kutuları kullanın, ikisini birden değil" hatası verilir.
    - Sıra barkoda ya da üye no'ya göre artandır.
    - Servisler: `catalog.services.copies_for_labels(copy_ids: list[int] | None, start: str | None, end: str | None) -> list[int]` ve `members.services.members_for_cards(member_nos: list[int] | None, start: int | None, end: int | None) -> list[int]`.
26. **Para iadesi ayrıntısı** (ADR-0037): `refundable(fee)` = o bedele yapılmış PAYMENT dağıtımlarının toplamı − REFUND toplamı. Ön koşul sağlanmazsa sonuç 0'dır. Döküm ekranında para iadesi formu yalnız `refundable > 0` olan bedellerde görünür.
27. **Tohum veri aktörü** (ADR-0038): `--actor` her iki profilde zorunludur. Kurulum ve README'deki demo sırası: `migrate` → `createsuperuser` → `load_seed_data --profile demo --actor <ad>`.
28. **Hatırlatma son tarihi** (ADR-0039): `reminder_log.due_on` MANUAL kayıtlarda da doldurulur. Elle hatırlatmada tekrar engeli yoktur (değişmedi).
29. **Gecikme günü arayüzü** (ADR-0040): `late_days(due_on: date, on: date, closed_dates: AbstractSet[date]) -> int`. Kapalı tarihler `administration.services.closed_dates() -> frozenset[date]` ile bir kez okunur. Haftalık kapalı güne denk gelen tek tarih de düşülür. Çağıranlar: `check_in`, `mark_lost`, `mark_damaged`, `overdue_loans`. Kullanım kılavuzuna "geçmiş kapalı tarihleri silmeyin" notu eklenir.
30. **Elle iptal** (ADR-0041): Yol `/borclar/<no>/iptal/` (POST, yönetici), form alanları `fee_id` ve `reason`. Denetim eylemi `CANCELLATION`; hedef yeni `ledger_entry`; `details` alanı `{"amount_kurus", "member_no", "target_entry_id", "reason"}` içerir. `AuditAction` 14 değerden oluşur.
31. **Aktifleştirme** (ADR-0042): Yol `/uyeler/<no>/aktif/` (POST, personel). Denetim eylemi `MEMBER_REACTIVATED`; hedef `member`; `details` alanı `{"member_no"}` içerir.
32. **Parola değiştirme** (ADR-0043):
    - Yol `/parola/` (GET, POST). View doğrulamayı Django `PasswordChangeForm` ile yapar; kaydetmeyi `accounts.services.change_own_password(user, new_password: str) -> None` yapar. Servis bayrağı False yapar ve `STAFF_CHANGED` (`password_changed`) yazar.
    - Şablon `templates/registration/password_change.html`. Başarıda "Parolanız değiştirildi" mesajı gösterilir ve `/` adresine yönlendirilir.
    - `ForcePasswordChangeMiddleware`, `MIDDLEWARE` listesinde `AuthenticationMiddleware`'den sonra yer alır. Muaf yollar `/parola/`, `/cikis/` ve `STATIC_URL` önekidir.
33. **Yedek uyarısı** (ADR-0044): `administration.jobs.last_finished(job) -> JobRun | None` ve `last_success_at(job) -> datetime | None`. Ana sayfadaki uyarı bileşeni iki uyarıyı alt alta gösterir: önce yedek, sonra dışa aktarma.
34. **Ertelenen anonimleştirme** (ADR-0045):
    - `AnonymizeCounts(members, loans, deferred)`.
    - `operations.services.deferred_members(today) -> list[DeferredRow(member_no, full_name, deactivated_on, expires_on, balance_kurus)]`.
    - Yol `/uyeler/saklama/` (GET, yönetici; view `members/views.py`, KL-22). Liste pasifleştirme tarihine göre en eskiden başlar, sayfalanmaz. Durum sütununda "borç nedeniyle bekliyor" yazar.
    - architecture §3'e `operations → billing` oku eklenir (bakiye için).
    - Hukuki teyit: SRS açık soru 6. Teyit gelene kadar uygulama bu kuralla çalışır.
35. **Üye alanı yorumlama** (ADR-0046):
    - Temizlenen karakterler: boşluk, `-`, `(`, `)`.
    - `MemberInput(kind: Literal["COPY_BARCODE", "PHONE", "MEMBER_NO", "TEXT"], value: str)`.
    - Telefon araması `phone_digits LIKE %value%` (KL-10) ile en fazla 50 sonuç döndürür. Tek sonuç olsa da liste gösterilir; üye otomatik açılmaz.
36. **Rıza** (ADR-0047): Mesajlar ADR'dedir. Rıza olayları için ayrı denetim kaydı yazılmaz, çünkü olayların kendisi izdir.
37. **Yeni FR öncelikleri:** FR-40 Should, FR-41 Must, FR-42 Should. Kapsam içi FR sayısı 35 olur (24 Must, 11 Should); Won't sayısı 7.
38. **Bulut oturumu görev şablonu** (ADR-0048): Her oturumun açılış istemi şunları içerir: dal adı, plan görev bölümünün yolu, TC listesi, doğrulama komutu ve "kritik karar çıkarsa dur ve soruyu raporla" kuralı. Oturum başında `python --version` (3.11) kontrol edilir (R-15). Commit kuralı ADR-0048'dedir (kullanıcı kararı): görev başına commit ve kendi dalına push. **Faz 5 başında verilen kullanıcı kararları (2026-10-31):** Oturumları kullanıcı kendisi açar (`claude --cloud` ya da claude.ai/code); Claude açılış istemini hazırlar. *(İlk karar, oturumları Claude'un Agent aracının remote moduyla başlatmasıydı. Bu mod bulutta değil yerelde çalıştığı için kullanıcı kararıyla değişti; §11.)* Her görev grubu için bir oturum açılır ve o oturum grubun görevlerini sırayla yapar. Oturum, grubun sonunda `main`'e PR açar. Birleştirme kullanıcı onayıyla yapılır. Repo `mhmtmndrn/kutuphane-odunc-sistemi` (özel); uzak tarafa yalnız `main` gönderildi.
39. **Görev sırası** (§8 T-01): `circulation/models.py` (`Loan`) ve `circulation/migrations/0001_initial.py` G10'da oluşturulur. Migration, kısmi benzersiz indeksi, data-design §4'teki indeksleri ve `copy_found_on` sütununu CHECK kısıtıyla içerir (ADR-0037). Uygulama sırası G10 → G09 → G11 olur; G11 servisleri, view'ları ve şablonları ekler. Gerekçe: G09'daki `LedgerEntry.loan` yabancı anahtarı ve billing migration'ı circulation migration'ına bağımlıdır. *Alternatif:* G09'u G11'den sonraya almak; G11 `post_charge` ve `member_balance` kullandığı için bu mümkün değil.
40. **ISBN-10'da küçük "x":** `parse_isbn` son hanedeki "x"i "X" olarak kabul eder (TC-253).
41. **Geri yüklenecek dosya yoksa:** `restore_backup` "Dosya bulunamadı: <yol>" mesajıyla çıkış 1 verir. Çıkış 2 yalnız argparse kullanım hatalarıdır (TC-301).
42. **Barkod taşması:** `add_copies`, atanacak id 99.999.999'u aşarsa "Barkod aralığı doldu" mesajıyla `RuleViolation` fırlatır ve işlem geri alınır (TC-263). *Alternatif:* yalnız belgelemek (tasarım ölçeği 20.000 nüsha).
43. **Zorunlu ortam değişkenleri:** `prod` ayarında architecture §6.4'teki değişkenlerin hepsi `env()` ile zorunlu okunur. Tek istisna `LIBRARY_SCHEDULER_ENABLED`'dır (varsayılan "0"). `DJANGO_SETTINGS_MODULE`'u Django okur (TC-02, TC-236).
44. **Kayıp ve hasarda yazım sırası:** `mark_lost` ve `mark_damaged` önce FINE'ı, sonra FEE'yi yazar. Böylece FIFO (ADR-0017) sonraki ödemeyi önce cezaya düşer (TC-290).
45. **Pasifleştirilen personelin oturumu:** Açık oturum sonraki istekte kapanır ve `/giris/` adresine yönlendirir. Ek kod gerekmez; Django `ModelBackend.get_user` pasif kullanıcıyı döndürmez. Davranış TC-237 ile sabitlenir.
46. **Hata kaydı:** Faz 5 ve 6'da bulunan hatalar `docs/test-plan.md` §8 tablosuna `HT-NN` numarasıyla yazılır. Önem ölçeği Kritik, Yüksek, Orta, Düşük. *Alternatif:* özel GitHub reposunun Issues bölümü (ADR-0048).

**Bu oturumda genişletilen KL maddeleri (2026-10-31, test planı yazımı):** KL-3 (binlik ayırıcı), KL-8 (kendini pasifleştirme mesajı) ve KL-10 (telefon aramasında temizlenen karakterler). Üçü de henüz onaylanmamış maddelerdi.

## 4. Görevler

### 4.0 Bütün görevler için ortak kurallar

- **TDD:** Her görevde önce §5'teki TC'lerin testi yazılır ve kırmızı görülür, sonra kod yazılır. Test dosyaları küçük karar 11'e göre düzenlenir: `<app>/tests/test_domain.py`, `test_services.py`, `test_views.py`. Uygulamalar arası testler kökteki `tests/` klasöründedir (KL-20).
- **Katmanlar (ADR-0015):** `domain.py` saf fonksiyonlardan oluşur; ORM, HTTP ya da saat çağrısı içermez. `services.py` her genel fonksiyonu tek bir `transaction.atomic()` içinde çalıştırır; ilk satırı yetki denetimi (`require_role`), son adımı denetim kaydıdır. `views.py` yalnız formları ve servisleri çağırır. "Bugün" değeri yalnız `administration.clock.today()` ile alınır (küçük karar 9).
- **Import yönü (KL-22):** `domain`, `services` ve `models` modülleri architecture §3'teki okları izler. `views` modülleri yapraktır: herhangi bir app'in servisini import edebilir, ama hiçbir modül bir `views` modülünü import etmez. Bu yüzden üye ayrıntısı gibi birden çok app'e dokunan ekranlar, döngü oluşturmadan `circulation` ve `billing` servislerini çağırabilir.
- **Hatalar:** Servisler kural ihlalinde `administration.errors.RuleViolation(message: str)` fırlatır. View bu hatayı yakalar ve formu 200 ile aynı ekranda mesajla yeniden gösterir. Yetki hatası `django.core.exceptions.PermissionDenied` ile 403 döner. Geçersiz durum geçişi `circulation.domain.InvalidTransition`, `RuleViolation`'ın alt sınıfıdır.
- **Para:** Tutarlar her katmanda `int` kuruştur. Formlar `administration.money.parse_tl`, şablonlar `format_tl` filtresini kullanır (ADR-0016, KL-3).
- **Şablonlar:** Arayüz yalnız Türkçedir (`<html lang="tr">`, `LANGUAGE_CODE = "tr"`); tarihler `16.11.2026` biçiminde gösterilir. Her app'in şablonları `templates/<app>/`, ortak iskelet kökteki `templates/base.html`'dir. Durum değiştiren her form POST'tur ve `{% csrf_token %}` taşır.
- **Dallar ve commit (küçük karar 16):** Görev grupları ve dalları: `feature/foundation` (G01–G04), `feature/catalog-members` (G05–G08), `feature/circulation` (G10, G09, G11, G12 sırasıyla; KL-39), `feature/notifications` (G13), `feature/operations` (G14–G16), `feature/seed-load` (G17–G18), `feature/deploy` (G19). Her görevin sonunda `feat:`/`test:` commit'i önerilir ve yalnız kullanıcı onayıyla atılır. Grup bitince `main`'e birleştirme de onayla yapılır.
- **Ortak doğrulama:** Her görevin kendi komutundan sonra `python -m pytest -q` komutu çalıştırılır ve önceki görevlerin testleri de geçmelidir. Model değişikliği olan görevlerde `python manage.py makemigrations --check --dry-run` "No changes detected" çıktısını vermelidir.

### 4.1 URL listesi (küçük karar 15)

"Yönetici" işaretli her view `require_role(Role.ADMIN)` ile korunur. G04'teki NFR-07 testi bu işareti URL çözücüden okur.

| Yol | Yöntem | Rol | App | İşlev |
|---|---|---|---|---|
| `/` | GET | Personel | administration | Ana sayfa; yöneticiye son dışa aktarma tarihi ve yaş uyarısı (FR-37) ve yedek uyarısı (FR-42) |
| `/giris/`, `/cikis/` | GET, POST / POST | Herkes / Personel | accounts | Giriş, çıkış (FR-27) |
| `/parola/` | GET, POST | Personel | accounts | Kendi parolasını değiştir (FR-41, ADR-0043) |
| `/personel/` | GET | Yönetici | accounts | Personel listesi |
| `/personel/yeni/` | GET, POST | Yönetici | accounts | Hesap oluştur (FR-21) |
| `/personel/<int:pk>/` | GET, POST | Yönetici | accounts | Rol değiştir |
| `/personel/<int:pk>/pasif/` | POST | Yönetici | accounts | Pasifleştir |
| `/personel/<int:pk>/parola/` | POST | Yönetici | accounts | Parola sıfırla |
| `/personel/<int:pk>/kilit-ac/` | POST | Yönetici | accounts | Kilidi kaldır (ADR-0009) |
| `/ayarlar/` | GET, POST | Yönetici | administration | Ayarlar (FR-23) |
| `/kapali-gunler/` | GET, POST | Yönetici | administration | Haftalık kapalı günler ve tarih listesi (FR-24) |
| `/kapali-gunler/tarih/` | POST | Yönetici | administration | Kapalı tarih ekle |
| `/kapali-gunler/tarih/<int:pk>/sil/` | POST | Yönetici | administration | Kapalı tarih sil |
| `/denetim/` | GET | Yönetici | administration | Denetim kaydı, 50 satır/sayfa (FR-26) |
| `/uyeler/` | GET | Personel | members | Arama (`?q=`) (FR-01) |
| `/uyeler/yeni/` | GET, POST | Personel | members | Üye oluştur |
| `/uyeler/<int:member_no>/` | GET | Personel | members | Üye ayrıntısı: bilgiler, rıza tarihleri, açık ödünçler, bakiye |
| `/uyeler/<int:member_no>/duzenle/` | GET, POST | Personel | members | Üye güncelle |
| `/uyeler/<int:member_no>/pasif/` | POST | Personel | members (view), circulation (servis) | Pasifleştir (FR-02; G11) |
| `/uyeler/<int:member_no>/aktif/` | POST | Personel | members | Aktifleştir (FR-40, ADR-0042) |
| `/uyeler/<int:member_no>/riza/` | POST | Personel | members | Rıza ver ya da geri al (FR-03) |
| `/uyeler/kart/` | GET, POST | Personel | members | Aralık formu (GET) ve üye kartı PDF'i (POST) (FR-38, ADR-0036) |
| `/uyeler/saklama/` | GET | Yönetici | members (view), operations (servis) | Borç nedeniyle bekleyen anonimleştirmeler (FR-25, ADR-0045) |
| `/kitaplar/` | GET | Personel | catalog | Arama (`?q=`) (FR-04) |
| `/kitaplar/yeni/` | GET, POST | Personel | catalog | Kitap oluştur |
| `/kitaplar/<int:pk>/` | GET | Personel | catalog | Kitap ve nüshaları |
| `/kitaplar/<int:pk>/duzenle/` | GET, POST | Personel | catalog | Kitap güncelle |
| `/kitaplar/<int:pk>/nusha/` | POST | Personel | catalog | Nüsha ekle (1–50) (FR-05) |
| `/nushalar/etiket/` | GET, POST | Personel | catalog | Aralık formu (GET) ve etiket PDF'i (POST) (FR-06, ADR-0036) |
| `/nushalar/<str:barcode>/` | GET | Personel | circulation | Nüsha durumu, ödünç geçmişi ve rolüne göre işlemler |
| `/nushalar/<str:barcode>/kayip/` | POST | Yönetici | circulation | Kayıp (FR-15, FR-39) |
| `/nushalar/<str:barcode>/hasarli/` | POST | Yönetici | circulation | Hasarlı (FR-15, FR-39) |
| `/nushalar/<str:barcode>/bulundu/` | POST | Personel | circulation | Bulundu (FR-16) |
| `/nushalar/<str:barcode>/onarildi/` | POST | Yönetici | circulation | Onarıldı (FR-16) |
| `/nushalar/<str:barcode>/kayittan-dus/` | POST | Yönetici | circulation | Kayıttan düş (FR-16, FR-39) |
| `/odunc/` | GET, POST | Personel | circulation | Ödünç ekranı (`?uye=&nusha=`) (FR-07, FR-08, FR-11) |
| `/odunc/<int:loan_id>/uzat/` | POST | Personel | circulation | Uzat (FR-10) |
| `/iade/` | GET, POST | Personel | circulation | İade ekranı (FR-09, FR-11) |
| `/borclar/<int:member_no>/` | GET | Personel | billing | Bakiye ve döküm (FR-17) |
| `/borclar/<int:member_no>/odeme/` | POST | Personel | billing | Ödeme (FR-13) |
| `/borclar/<int:member_no>/af/` | POST | Yönetici | billing | Af (FR-14) |
| `/borclar/<int:member_no>/para-iadesi/` | POST | Yönetici | billing | Para iadesi (FR-16, ADR-0020, ADR-0037) |
| `/borclar/<int:member_no>/iptal/` | POST | Yönetici | billing | Bağı koparılmış bedelin elle iptali (FR-16, ADR-0041) |
| `/gecikenler/` | GET | Personel | notifications | Geciken listesi (FR-20) |
| `/gecikenler/hatirlat/` | POST | Personel | notifications | Elle hatırlatma (FR-19) |
| `/admin/` | – | – | – | Yalnız `dev` ayarında; üretimde 404 (ADR-0024) |

### Görev G01: Proje iskeleti ve ayarlar

- **Gereksinimler:** NFR-09 (dil ve saat dilimi), ADR-0013, ADR-0024, ADR-0029, ADR-0034, architecture §6.4.
- **Dosyalar:** oluştur `manage.py`, `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, `.gitignore` (değiştir: `*.sqlite3`, `staticfiles/`), `library_site/__init__.py`, `library_site/settings/{__init__,base,dev,test,prod}.py`, `library_site/urls.py`, `library_site/wsgi.py`, `templates/base.html`, `static/css/app.css`, `tests/__init__.py`, `tests/test_prod_settings.py`.
- **Arayüzler:** sunar `library_site.settings.base.env(name: str, default: str | None = None) -> str`. Değişken tanımsızsa ve `default` verilmemişse `ImproperlyConfigured("Eksik ortam değişkeni: <ad>")` fırlatır. Zorunlu değişkenler KL-43'tedir.
- **Davranış:**
  - Sürümler ilk adımda PyPI'den alınır (küçük karar 10, KL-18). Üretim bağımlılıkları: Django 5.2.x, waitress, APScheduler 3.x, django-axes, argon2-cffi, cryptography, reportlab ve Windows için tzdata. Geliştirme bağımlılıkları: `-r requirements.txt`, pytest, pytest-django, coverage, pypdfium2, zxing-cpp.
  - `base.py`: `TIME_ZONE = "Europe/Istanbul"`, `USE_TZ = True`, `LANGUAGE_CODE = "tr"`, `AUTH_USER_MODEL = "accounts.StaffUser"`, `PASSWORD_HASHERS` listesinde ilk sırada `Argon2PasswordHasher`. SQLite `OPTIONS` değerleri `{"transaction_mode": "IMMEDIATE", "init_command": "PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL; PRAGMA foreign_keys=ON; PRAGMA busy_timeout=5000;"}` olur (data-design §5). `NAME`, `env("LIBRARY_DB_PATH")` değeridir.
  - `dev.py`: `DEBUG = True`, `django.contrib.admin` açık, konsol e-posta backend'i, varsayılan değerlerle `env`.
  - `test.py`: bellek e-posta backend'i, hızlı parola hasher'ı (`MD5PasswordHasher`; yalnız testte). Argon2 testi (NFR-06) `base` listesini okur.
  - `prod.py`: `DEBUG = False`, admin yok, `STATIC_ROOT = env("LIBRARY_STATIC_ROOT")`, SMTP ayarları `LIBRARY_EMAIL_*` değerlerinden okunur (587, STARTTLS). `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")`, `SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = True`. `CSRF_TRUSTED_ORIGINS`, `LIBRARY_ALLOWED_HOSTS` listesinden `https://` önekiyle türetilir. HTTPS yönlendirmesini Caddy yapar; bu yüzden `security.W008` ve `security.W004` gerekçe yorumuyla `SILENCED_SYSTEM_CHECKS` listesine eklenir.
  - `pyproject.toml`: `[tool.pytest.ini_options]` altında `DJANGO_SETTINGS_MODULE = "library_site.settings.test"`, `markers = ["slow: PDF ve barkod çözme testleri"]`. `[tool.coverage.run]` altında `branch = true`, `omit = ["*/migrations/*", "*/tests/*"]`.
- **Testler:** TC-01…TC-03, TC-224, TC-235…TC-236 (6 TC; `docs/test-plan.md` §6)
- **Doğrulama:** `python -m pytest tests/test_prod_settings.py -q` → hepsi geçer. `python manage.py check --deploy --settings=library_site.settings.prod` (gerekli ortam değişkenleri geçici değerlerle verilir) → "System check identified no issues (2 silenced)."
- [x] Tamamlandı
  - Kanıt (2026-10-31, yerel Windows 11, Python 3.11.9): `python -m pytest tests/test_prod_settings.py -q` → 19 passed; `python manage.py check --deploy --settings=library_site.settings.prod` (geçici ortam değişkenleriyle) → "System check identified no issues (2 silenced)."; `python -m pytest -q` → 19 passed; TC-224: `coverage report --include="*/domain.py" --fail-under=90` → "No data to report." (henüz `domain.py` yok; G03'ten itibaren ölçülür).
  - G02'de axes.W006 susturuldu; güncel sonuç (3 silenced), bkz. ADR-0051.

### Görev G02: Personel modeli, giriş, oturum, kilit ve rol denetimi

- **Gereksinimler:** FR-27, FR-22, NFR-06; AC-27; ADR-0009, ADR-0049, ADR-0050; küçük kararlar 1 ve 9 (faz 1 ve faz 3); G02 küçük kararları (a)–(e) (§11).
- **Dosyalar:** oluştur `accounts/{__init__,apps,models,permissions,views,urls,forms}.py`, `accounts/migrations/0001_initial.py`, `templates/registration/login.html`, `accounts/tests/{test_domain,test_services,test_views}.py`; değiştir `library_site/settings/base.py`, `library_site/urls.py`.
- **Arayüzler:**
  - sunar `accounts.models.Role(TextChoices)`: `ADMIN = "ADMIN", "Yönetici"`, `CLERK = "CLERK", "Görevli"`.
  - sunar `accounts.models.StaffUser(AbstractUser)`: `role` alanı CharField(10) ve CHECK kısıtı; `must_change_password` BooleanField(default=False) (ADR-0043; davranışı G04'te). `objects.create_superuser`, `role=ADMIN` atar; böylece ilk yönetici `createsuperuser` ile oluşturulur.
  - sunar `accounts.permissions.require_role(role: Role) -> Callable`. Hem servis fonksiyonunu hem view'ı sarar.
    - Servis için ilk argüman `actor: StaffUser` olur. Rol `ADMIN` istenmişse ve `actor.role != ADMIN` ise `PermissionDenied` fırlatılır. `CLERK` istenmişse aktif her personel geçer.
    - View için denetim, URL argümanları ve nesne aramasından önce yapılır; bu yüzden yetkisiz istek 404 değil 403 alır.
    - Sarılan nesneye `required_role` özniteliği yazılır.
  - sunar `accounts.permissions.staff_view(view)`. `login_required` ile `require_role(Role.CLERK)` birleşimidir.
- **Davranış:**
  - `SESSION_COOKIE_AGE = 1800`, `SESSION_SAVE_EVERY_REQUEST = True`.
  - axes ayarları: `AXES_FAILURE_LIMIT = 5`, `AXES_COOLOFF_TIME = timedelta(minutes=15)`, `AXES_LOCKOUT_PARAMETERS = ["username"]`, `AXES_RESET_ON_SUCCESS = True`, `AXES_RESET_COOL_OFF_ON_FAILURE_DURING_LOCKOUT = False` (ADR-0050). `AUTHENTICATION_BACKENDS` listesi `["axes.backends.AxesStandaloneBackend", "django.contrib.auth.backends.ModelBackend"]` olur, `AxesMiddleware` eklenir. Kilitli hesap giriş ekranında "Hesap geçici olarak kilitlendi. 15 dakika sonra yeniden deneyin." mesajını görür. Cevap HTTP 429'dur; `AXES_LOCKOUT_CALLABLE` giriş şablonunu formla birlikte çizer (ADR-0049).
  - Parola doğrulayıcıları KL-9'a göre ayarlanır.
  - Giriş için Django `LoginView` kullanılır, şablon Türkçedir. Çıkış yalnız POST ile yapılır.
- **Testler:** TC-04…TC-12 (9 TC; `docs/test-plan.md` §6)
- **Doğrulama:** `python -m pytest accounts -q` → hepsi geçer.
- [x] Tamamlandı
  - Kanıt (2026-10-31, bulut oturumu, Linux, Python 3.11): `python -m pytest accounts -q` → 35 passed; `python -m pytest -q` → 54 passed; `coverage report --include="accounts/permissions.py"` → %100 (dal); `makemigrations --check --dry-run` → "No changes detected"; `check --deploy --settings=library_site.settings.prod` → "System check identified no issues (3 silenced)." (axes.W006 eklendi, §11). TC-12'nin `create_staff` ve `reset_password` kısmı G04'te.

### Görev G03: Yönetim çekirdeği: saat, para, ayarlar, kapalı günler, denetim kaydı, görev kaydı, ana sayfa

- **Gereksinimler:** FR-23, FR-24, FR-26 (altyapı), FR-37 (uyarı), FR-42, NFR-12; AC-22, AC-23, AC-24, AC-30 (2. senaryo), AC-35; ADR-0028, ADR-0035, ADR-0040 (`closed_dates`), ADR-0044; küçük kararlar 8, 9 ve 14 (faz 4); KL-1, KL-3, KL-14, KL-15, KL-29, KL-30, KL-31, KL-33.
- **Dosyalar:** oluştur `administration/{__init__,apps,models,domain,services,views,urls,forms,clock,money,errors,audit,jobs}.py`, `administration/templatetags/money.py`, `administration/migrations/0001_initial.py` (tek satırlık ayarı varsayılanlarla oluşturan `RunPython` dahil), `administration/templates/administration/{home,settings,closed_days,audit_list}.html`, `administration/tests/*`.
- **Arayüzler:**
  - `clock.today() -> date`; `timezone.localdate()` sonucunu döndürür.
  - `money.parse_tl(text: str) -> int`, `money.format_tl(kurus: int) -> str` (KL-3).
  - `errors.RuleViolation(Exception)`, `.message: str`.
  - `domain.validate_weekly_closed(days: set[int]) -> None`. `len(days) == 7` ise "En az bir gün açık kalmalı" mesajıyla `RuleViolation` fırlatır; 0–6 dışındaki değer `ValueError` verir.
  - `domain.export_age_warning(last_export_on: date | None, today: date) -> str | None` (KL-14).
  - `domain.backup_warning(last_success_at: datetime | None, last_finished_failed: bool, now: datetime) -> str | None` (ADR-0044).
  - `models.LibrarySettings`, `WeeklyClosedDay`, `ClosedDate`, `AuditEvent`, `JobRun` (data-design §2.1, §2.6; `JobRun` KL-1).
  - `services.get_settings() -> LibrarySettings`.
  - `services.update_settings(actor, **changes) -> LibrarySettings` (yönetici). Değişen her alan için `{"<alan>": {"old": x, "new": y}}` bilgisiyle tek bir `SETTINGS_CHANGED` kaydı yazar. Değişiklik yoksa kayıt yazmaz.
  - `services.set_weekly_closed(actor, days: set[int]) -> None` (yönetici).
  - `services.add_closed_date(actor, on: date, note: str = "") -> ClosedDate` (yönetici).
  - `services.remove_closed_date(actor, pk: int) -> None` (yönetici).
  - `services.closed_day_predicate() -> Callable[[date], bool]`. Haftalık günleri ve tarihleri bir kez okur; dönen fonksiyon O(1) küme kontrolü yapar.
  - `services.closed_dates() -> frozenset[date]`: yalnız `closed_date` tarihleri (ADR-0040, KL-29).
  - `audit.record_audit(actor: StaffUser | None, action: AuditAction, target_type: str, target_id: int, details: dict) -> AuditEvent`. `details` içinde aynı anda hem `member` hem `loan` anahtarı bulunursa `ValueError` fırlatır (küçük karar 10).
  - `audit.AuditAction(TextChoices)`: faz 4 küçük kararı 8'deki 12 değer ile `CANCELLATION` ve `MEMBER_REACTIVATED` (KL-30, KL-31); toplam 14 değer.
  - `jobs.Job(TextChoices)`: `BACKUP`, `ANONYMIZE`, `REMINDERS`, `EXPORT`.
  - `jobs.run_job(job: Job, run_on: date, fn: Callable[[date], str]) -> JobRun`. Önce `RUNNING` satırı yazılır, sonra `fn(run_on)` çağrılır. Dönüş değeri `detail` olur ve durum `SUCCESS` yapılır. İstisna olursa `FAILED` ve hata metni yazılır, istisna yeniden fırlatılır.
  - `jobs.last_success(job: Job) -> date | None`.
  - `jobs.last_finished(job: Job) -> JobRun | None` ve `jobs.last_success_at(job: Job) -> datetime | None` (KL-33).
- **Davranış:**
  - Ayar formu tutarları TL olarak alır. Ödünç süresi 1–365, limit 1–20, saklama 1–10 yıl aralığındadır. Kütüphane adı 1–80 karakter olmalıdır.
  - AC-23'ün ikinci koşulu (mevcut ödünçler değişmez) G11'de test edilir.
  - Ana sayfa bütün personele modül bağlantılarını gösterir. Yöneticiye ek olarak son dışa aktarma tarihini ve varsa uyarıları gösterir: önce yedek uyarısı (FR-42), sonra dışa aktarma uyarısı (KL-33).
- **Testler:** TC-13…TC-26, TC-238…TC-247 (24 TC; `docs/test-plan.md` §6)
- **Doğrulama:** `python -m pytest administration -q` → hepsi geçer.
- [x] Tamamlandı
  - Kanıt (2026-10-31, bulut oturumu, Linux, Python 3.11): `python -m pytest administration -q` → 118 passed; `python -m pytest -q` → 172 passed; `coverage report --include="*/domain.py" --fail-under=90` → %100 (dal); `makemigrations --check --dry-run` → "No changes detected".

### Görev G04: Personel yönetimi ve yetki testi (NFR-07)

- **Gereksinimler:** FR-21, FR-22, FR-26 (personel değişikliği), FR-41, NFR-07; AC-21, AC-22, AC-34; ADR-0009, ADR-0043; KL-8, KL-32.
- **Dosyalar:** oluştur `accounts/services.py`, `accounts/middleware.py`, `accounts/templates/accounts/{staff_list,staff_form}.html`, `templates/registration/password_change.html`, `tests/test_authorization.py`; değiştir `accounts/views.py`, `accounts/urls.py`, `library_site/settings/base.py` (`MIDDLEWARE`).
- **Arayüzler:** Aşağıdaki servislerin hepsi yönetici ister ve `STAFF_CHANGED` kaydı yazar. `details["change"]` değeri sırasıyla `created`, `role`, `deactivated`, `password_reset`, `unlocked` olur; parola hiçbir zaman yazılmaz. `create_staff` ve `reset_password` `must_change_password = True` yazar (ADR-0043).
  - `accounts.services.create_staff(actor, username: str, full_name: str, role: Role, password: str) -> StaffUser`
  - `set_role(actor, user, role) -> None`
  - `deactivate_staff(actor, user) -> None`
  - `reset_password(actor, user, new_password: str) -> None`
  - `unlock_staff(actor, user) -> None`; `axes.utils.reset(username=…)` çağırır.
  - `change_own_password(user, new_password: str) -> None` (bütün personel; aktör kullanıcının kendisi). Bayrağı False yapar, `STAFF_CHANGED` kaydını `change = "password_changed"` ile yazar (KL-32).
  - `accounts.middleware.ForcePasswordChangeMiddleware` (KL-32).
- **Davranış:**
  - KL-8: Son aktif yönetici pasifleştirilemez ya da görevliye çevrilemez; hata mesajı "En az bir aktif yönetici kalmalı" olur. Yönetici kendi hesabını pasifleştiremez ("Kendi hesabınızı pasifleştiremezsiniz").
  - KL-45: Pasifleştirilen personelin açık oturumu sonraki istekte kapanır; ek kod yazılmaz, TC-237 davranışı sabitler.
  - `tests/test_authorization.py` iki şeyi doğrular:
    - URL çözücüdeki bütün desenler gezilir ve `required_role == ADMIN` olan her view'a görevli oturumuyla GET ve POST istekleri gönderilir. Desen argümanları `1` ya da `"00000001"` ile doldurulur. Her istek için 403 beklenir.
    - §4.1'deki 19 yönetici yolunun hepsi testteki sabit listededir. `Role.ADMIN` ile korunan yollar, bu listenin bugün var olan yollarla kesişimine eşit olmalıdır. Böylece yanlışlıkla işaretsiz kalan bir yönetici view'ı da yakalanır.
  - Bu test sonraki görevlerin URL'lerini de kapsar: bir görev §4.1'deki yönetici yolunu eklediği anda yol kontrol edilir ve ADMIN koruması yoksa test düşer; listeye bir şey eklemek gerekmez. Görevliye açık kalması gereken `/parola/`, `/nushalar/<barcode>/bulundu/` ve `/uyeler/<no>/aktif/` de var oldukları anda görevli rolüyle kontrol edilir.
- **Testler:** TC-27…TC-33, TC-237, TC-248…TC-252 (13 TC; `docs/test-plan.md` §6)
- **Doğrulama:** `python -m pytest accounts tests/test_authorization.py -q` → hepsi geçer.
- [x] Tamamlandı
  - Kanıt (2026-10-31, bulut oturumu, Linux, Python 3.11): `python -m pytest accounts tests/test_authorization.py -q` → 79 passed; `python -m pytest -q` → 216 passed; `coverage report --include="accounts/permissions.py,accounts/middleware.py" --fail-under=100` → %100 (dal); `coverage report --include="*/domain.py" --fail-under=90` → %100; `makemigrations --check --dry-run` → "No changes detected"; `check --deploy` → "no issues (3 silenced)".

### Görev G05: Katalog domain'i: Türkçe normalizasyon ve ISBN

- **Gereksinimler:** FR-04 (ISBN kuralı), NFR-10, NFR-13; AC-04 (2. senaryo); ADR-0008, ADR-0019; KL-2.
- **Dosyalar:** oluştur `catalog/{__init__,apps,domain}.py`, `catalog/tests/test_domain.py`.
- **Arayüzler:** sunar
  - `normalize_tr(text: str) -> str`: ADR-0019'daki dört adımı uygular. O(L).
  - `IsbnOk(isbn13: str)`, `IsbnSuggest(suggestion: str)`, `IsbnInvalid(reason: str)`: frozen dataclass'lar.
  - `parse_isbn(raw: str) -> IsbnOk | IsbnSuggest | IsbnInvalid`: ADR-0008'deki kurala uyar; ISBN-10'un son hanesinde küçük "x" kabul edilir (KL-40). `reason` değerleri "ISBN 10 ya da 13 haneli olmalı" ve "ISBN kontrol hanesi hatalı" olur.
  - `isbn10_to_13(isbn10: str) -> str`
- **Testler:** TC-34…TC-43, TC-253 (11 TC; `docs/test-plan.md` §6)
- **Doğrulama:** `python -m pytest catalog/tests/test_domain.py -q` → hepsi geçer.
- [x] Tamamlandı
  - Kanıt (2026-10-31, bulut oturumu, Linux, Python 3.11.18): `python -m pytest catalog/tests/test_domain.py -q` → 48 passed; `python -m pytest -q` → 267 passed; `coverage report --include="*/domain.py" --fail-under=90` → %100 (dal; `catalog/domain.py` %100); `makemigrations --check --dry-run` → "No changes detected".

### Görev G06: Üyeler

- **Gereksinimler:** FR-01, FR-03, FR-40, NFR-08 (veri minimizasyonu), NFR-10; AC-01, AC-03 (bütün senaryolar; 1. senaryonun hatırlatma koşulu G13'te), AC-33; ADR-0022, ADR-0042, ADR-0047; küçük karar 6 (faz 1), küçük kararlar 2 ve 8 (faz 3); KL-10, KL-12, KL-31, KL-36.
- **Dosyalar:** oluştur `members/{__init__,apps,models,domain,services,views,urls,forms}.py`, migration, `members/templates/members/{search,form,detail}.html`, `members/tests/*`, `tests/support/factories.py` (ilk fonksiyonlar: `make_staff`, `make_member`).
- **Arayüzler:**
  - domain `phone_digits(phone: str) -> str`.
  - domain `classify_member_query(q: str) -> MemberQuery`. Yalnız rakamdan oluşan sorgu `digits` alır, diğerleri `normalize_tr` ile `text` alır (KL-10).
  - Servisler:
    - `create_member(actor, full_name: str, phone: str, email: str | None) -> Member`. `member_no` değeri `max + 1` olur ve IMMEDIATE işlem içinde atanır.
    - `update_member(actor, member, **fields) -> Member`. E-posta NULL yapılırken geçerli rıza durumu GIVEN ise aynı işlemde WITHDRAWN olayı yazar (ADR-0047).
    - `search_members(q: str, limit: int = 50) -> list[Member]`
    - `set_inactive(actor, member) -> None`. İç servistir; yalnız `circulation.services.deactivate_member` çağırır (G11). `is_active=False` ve `deactivated_on=today()` yazar.
    - `set_consent(actor, member, given: bool, on: date) -> ConsentEvent`. ADR-0047'deki sıra kuralını uygular: gelecek tarih ve geçerli durumu tekrarlayan olay reddedilir, `has_email_consent` geçerli durumdan yeniden hesaplanır.
    - `reactivate_member(actor, member) -> None` (personel; ADR-0042, KL-31).
    - `member_by_no(member_no: int) -> Member`; bulunamazsa `RuleViolation("Üye bulunamadı")`.
    - `consent_dates(member) -> tuple[date | None, date | None]`: son verme ve son geri alma tarihi.
- **Davranış:**
  - Pasifleştirme yolu (`/uyeler/<no>/pasif/`) ve kuralları G11'dedir, çünkü bu kurallar ödünç ve borç verisine bakar.
  - Üye ayrıntısı bu görevde bilgileri ve rıza tarihlerini gösterir; pasif ve anonimleştirilmemiş üyede "Aktifleştir" düğmesi bulunur (`/uyeler/<no>/aktif/`). Açık ödünçler, bakiye ve uzatma düğmeleri G11'de eklenir.
  - Rıza, e-posta adresi yoksa verilemez ("Rıza için e-posta adresi gerekli"). Gelecek bir tarih reddedilir (KL-12).
  - Üye modelinde FR-01 dışında kişisel alan yoktur (NFR-08).
- **Testler:** TC-44…TC-52, TC-57…TC-59, TC-254…TC-261 (20 TC; `docs/test-plan.md` §6)
- **Doğrulama:** `python -m pytest members -q` → hepsi geçer.
- [x] Tamamlandı
  - Kanıt (2026-10-31, bulut oturumu, Linux, Python 3.11.18): `python -m pytest members -q` → 112 passed; `python -m pytest -q` → 379 passed (TC-31…TC-33 dahil; `uyeler/<int:member_no>/aktif/` görevli rolüyle korunuyor); `coverage report --include="*/domain.py" --fail-under=90` → %100 (dal; `members/domain.py` %100); `members/services.py` %100 (dal); `makemigrations --check --dry-run` → "No changes detected".

### Görev G07: Kitaplar ve nüshalar

- **Gereksinimler:** FR-04, FR-05, NFR-10; AC-04, AC-05; ADR-0008; küçük karar 3 (faz 3); KL-10, KL-19.
- **Dosyalar:** oluştur `catalog/{models,services,views,urls,forms}.py`, migration, `catalog/templates/catalog/{search,form,detail}.html`, `catalog/tests/{test_services,test_views}.py`; değiştir `tests/support/factories.py` (`make_book`, `make_copy`).
- **Arayüzler:**
  - `create_book(actor, title, author, isbn13: str | None, publisher, year) -> Book`
  - `update_book(actor, book, **fields) -> Book`
  - `add_copies(actor, book, n: int) -> list[Copy]`. Geçerli aralık 1–50. Barkod, kayıttan hemen sonra aynı işlemde `f"{id:08d}"` olarak atanır. id 99.999.999'u aşarsa "Barkod aralığı doldu" (KL-42).
  - `find_copy(barcode: str) -> Copy`; bulunamazsa `RuleViolation("Nüsha bulunamadı")`.
  - `search_books(q: str, limit: int = 50) -> list[Book]` (KL-10)
- **Davranış:**
  - Kitap formu ISBN'i `parse_isbn` ile doğrular. `IsbnSuggest` sonucunda form kaydetmez. "Kontrol hanesi hatalı. Bunu mu demek istediniz: 9786053609322" mesajı ve `name="isbn_accept" value="<öneri>"` adlı ikinci bir gönder düğmesi gösterilir. Bu düğmeyle gelen değer yeniden `parse_isbn` ile doğrulanır, `IsbnOk` ise kaydedilir.
  - `Book.save()` ve `Copy` durum değişiklikleri `search_key` ve `status_changed_at` alanlarını günceller.
  - Kitap ayrıntısında nüshalar barkod ve durumuyla listelenir.
- **Testler:** TC-60…TC-68, TC-262…TC-264 (12 TC; `docs/test-plan.md` §6)
- **Doğrulama:** `python -m pytest catalog -q` → hepsi geçer.
- [x] Tamamlandı
  - Kanıt (2026-10-31, bulut oturumu, Linux, Python 3.11.18): `python -m pytest catalog -q` → 117 passed; `python -m pytest -q` → 448 passed (TC-31…TC-33 dahil); `coverage report --include="*/domain.py" --fail-under=90` → %100 (dal); `catalog/services.py` %100 (dal); `makemigrations --check --dry-run` → "No changes detected".

### Görev G08: PDF sayfa yardımcısı, nüsha etiketi ve üye kartı

- **Gereksinimler:** FR-06, FR-38, NFR-08; AC-06, AC-31; ADR-0014, ADR-0025, ADR-0030, ADR-0032, ADR-0035, ADR-0036; küçük kararlar 3, 4 ve 5 (faz 4); KL-25.
- **Dosyalar:** oluştur `pdf/__init__.py`, `pdf/sheets.py`, `pdf/tests/test_sheets.py`, `tests/support/barcode.py`; oluştur `catalog/templates/catalog/label_range.html`, `members/templates/members/card_range.html`; değiştir `catalog/services.py`, `catalog/views.py`, `catalog/urls.py`, `catalog/templates/catalog/detail.html` (seçim kutuları), `members/services.py`, `members/views.py`, `members/urls.py`, `members/templates/members/search.html` (seçim kutuları).
- **Arayüzler:**
  - `pdf.sheets.SheetLayout`, frozen dataclass. Alanlar mm cinsindendir: `page_w=210, page_h=297, cols, rows, item_w, item_h, margin_top, margin_left, gap_x=0, gap_y=0, cut_lines: bool`. Hazır değerler:
    - `LABEL_LAYOUT = SheetLayout(cols=3, rows=8, item_w=70, item_h=37, margin_top=0.5, margin_left=0, cut_lines=False)`
    - `CARD_LAYOUT = SheetLayout(cols=2, rows=5, item_w=85.6, item_h=54, margin_top=13.5, margin_left=19.4, cut_lines=True)`
  - `pdf.sheets.SheetItem`, frozen dataclass: `header: str`, `barcode_value: str`, `caption: str`, `footer: str`.
  - `pdf.sheets.render_sheet(items: list[SheetItem], layout: SheetLayout) -> bytes`. Öğeler satır satır, soldan sağa yerleşir; sayfa dolunca yeni sayfaya geçilir. Code 128 barkod 15 mm yüksekliğinde çizilir, modül genişliği 0,33 mm'dir. `header` 80 karakteri ya da öğe genişliğini aşarsa "…" ile kısaltılır (ADR-0035).
  - `catalog.services.label_pdf(copy_ids: list[int]) -> bytes`. Her etiket için `header=library_name`, `barcode_value=barcode`, `caption=barcode`, `footer=title[:30]`.
  - `members.services.member_card_pdf(member_nos: list[int]) -> bytes`. Her kart için `header=library_name`, `barcode_value=str(member_no)`, `caption=f"Üye No: {member_no}"`, `footer=""`. Ad basılmaz (ADR-0032).
  - `tests.support.barcode.decode_pdf_barcodes(pdf: bytes, dpi: int = 300) -> list[str]` (ADR-0030).
  - `catalog.services.copies_for_labels(...)` ve `members.services.members_for_cards(...)` (KL-25).
- **Davranış:**
  - Seçim ADR-0036 ve KL-25'e göre yapılır: GET ile aralık formu, POST ile aralık ya da seçim kutuları; kitap ayrıntısında ve üye arama sonuçlarında seçim kutuları.
  - Boş seçim "En az bir nüsha seçin" ya da "En az bir üye seçin" hatası verir. Bir istekte en fazla 240 öğe seçilebilir (10 sayfa etiket).
  - Yanıt `application/pdf` türündedir ve `Content-Disposition: inline; filename="etiketler.pdf"` ya da `"uye-kartlari.pdf"` taşır.
  - Kart yerleşiminin kenar boşlukları kartları A4'te ortalar: (210 − 2 × 85,6) / 2 = 19,4 mm ve (297 − 5 × 54) / 2 = 13,5 mm.
- **Testler:** TC-69…TC-75, TC-265…TC-269 (12 TC; `docs/test-plan.md` §6)
- **Doğrulama:** `python -m pytest pdf catalog members -q` → hepsi geçer (`slow` testleri dahil).
- [x] Tamamlandı
  - Kanıt (2026-10-31, bulut oturumu, Linux, Python 3.11.18): `python -m pytest pdf catalog members -q` → 296 passed (`slow` dahil; `python -m pytest -q -m slow` → 4 passed: TC-70 iki test, TC-71, TC-74; barkodlar pypdfium2 5.14.0 ve zxing-cpp 3.1.1 ile bu ortamda çözüldü); `python -m pytest -q` → 515 passed; `coverage report --include="pdf/*"` → %100 (satır ve dal); `*/domain.py` %100 (dal); `catalog/services.py` ve `members/services.py` %100 (dal); `accounts/permissions.py`, `accounts/middleware.py` %100; `makemigrations --check --dry-run` → "No changes detected".

### Görev G09: Borç defteri

- **Gereksinimler:** FR-13, FR-14, FR-16 (iptal, elle iptal ve para iadesi), FR-17, FR-26 (ödeme, af, para iadesi, elle iptal), NFR-12, NFR-13; AC-13, AC-14, AC-16 (defter kısmı), AC-17, AC-26; data-design I1–I6; ADR-0016, ADR-0017, ADR-0020, ADR-0021, ADR-0027, ADR-0037, ADR-0041; KL-26, KL-30.
- **Dosyalar:** oluştur `billing/{__init__,apps,models,domain,services,views,urls,forms}.py`, migration, `billing/templates/billing/statement.html`, `billing/tests/*`; değiştir `tests/support/factories.py` (`make_charge`).
- **Arayüzler:**
  - domain:
    - `OpenCharge(id: int, unpaid: int)`
    - `allocate_fifo(open_charges: list[OpenCharge], amount: int) -> list[tuple[int, int]]`. `amount <= 0` ise ya da `amount > Σ unpaid` ise `ValueError` fırlatır. Girdi sırasını korur. O(k).
    - `balance(entries: Iterable[tuple[str, int]]) -> int`
  - Servisler:
    - `post_charge(actor, member, loan, kind: Literal["FINE", "FEE"], amount: int) -> LedgerEntry`. İç servistir; çağıran işlemin içinde çalışır. FEE için `FEE` denetim kaydı da yazar.
    - `record_payment(actor, member, amount: int) -> LedgerEntry`. Borçtan fazla ödeme "Ödeme tutarı borcu aşamaz" mesajıyla reddedilir.
    - `waive(actor, charge: LedgerEntry, amount: int, reason: str) -> LedgerEntry` (yönetici). Boş gerekçe "Af için gerekçe zorunlu", ödenmemiş kısmı aşan tutar "Af tutarı kalemin ödenmemiş kısmını aşamaz" mesajıyla reddedilir.
    - `cancel_unpaid(actor, fee: LedgerEntry) -> LedgerEntry | None`. Ödenmemiş kısım 0 ise `None` döner.
    - `refund(actor, fee: LedgerEntry, amount: int) -> LedgerEntry` (yönetici). I5 (ADR-0037) uygulanır: ön koşul ihlali "Para iadesi yalnız bulunan kayıp nüshanın bedeli için yapılabilir", tutar ihlali "Para iadesi, ödenmiş ve henüz iade edilmemiş tutarı aşamaz" mesajıyla reddedilir.
    - `cancel_fee_manual(actor, fee: LedgerEntry, reason: str) -> LedgerEntry` (yönetici; ADR-0041, KL-30).
    - `member_balance(member) -> int` (S3)
    - `open_charges(member) -> list[OpenCharge]` (S4)
    - `statement(member) -> list[StatementRow]`
    - `refundable(fee) -> int` (KL-26)
- **Davranış:**
  - Döküm ekranı tarih, tür, tutar, personel ve gerekçeyi gösterir.
  - Yöneticiye ek olarak üç form görünür: ödenmemiş kalem seçilerek yapılan af, iade edilebilir tutarı olan bedel için para iadesi ve bağı koparılmış, ödenmemiş kısmı olan bedel için elle iptal.
  - Türler Türkçe gösterilir: Ceza, Bedel, Ödeme, Af, İptal, Para iadesi.
- **Testler:** TC-76…TC-103, TC-270…TC-275 (34 TC; `docs/test-plan.md` §6)
- **Doğrulama:** `python -m pytest billing -q` → hepsi geçer. `coverage run --branch -m pytest billing && coverage report --include="billing/domain.py" --fail-under=90` → çıkış 0.
- [x] Tamamlandı
  - Kanıt (2026-11-01, bulut oturumu, Linux, Python 3.11.18): `python -m pytest billing -q` → 69 passed (TC-103 dosya tabanlı SQLite ve iki iş parçacığıyla); `coverage run --branch -m pytest billing` → 69 passed; `coverage report --include="billing/domain.py" --fail-under=90` → %100 (dal), çıkış 0; `billing/services.py` %100 (dal), `billing` toplam %99; `python -m pytest -q` → 658 passed (TC-31 ve TC-32 yeni üç yönetici yolunu da denetliyor); `makemigrations --check --dry-run` → "No changes detected".

### Görev G10: Ödünç domain'i

- **Gereksinimler:** FR-07, FR-08, FR-10, FR-11 (üye alanı), FR-12, FR-24 (kaydırma), NFR-13; AC-07, AC-08, AC-10, AC-11 (2. senaryo), AC-12, AC-24 (1. senaryo); ADR-0023, ADR-0028, ADR-0037 (`copy_found_on`), ADR-0040, ADR-0046; data-design §2.4; küçük karar 3 (faz 1); KL-6, KL-29, KL-35, KL-39.
- **Dosyalar:** oluştur `circulation/{__init__,apps,domain,models}.py`, `circulation/migrations/0001_initial.py` (`Loan`; kısmi benzersiz indeks `UniqueConstraint(fields=["copy"], condition=Q(closed_on__isnull=True))`, data-design §4'teki indeksler, `copy_found_on` ve CHECK kısıtı; ADR-0037, KL-39), `circulation/tests/test_domain.py`.
- **Arayüzler:** sunar
  - `NoOpenDayError(RuleViolation)`: mesajı ADR-0028'deki metindir.
  - `due_date(start: date, period_days: int, is_closed: Callable[[date], bool]) -> date`. Aday tarih `start + period_days` olur. `i = 0…366` için `aday + i` kontrol edilir ve ilk açık gün döner; hiçbiri açık değilse `NoOpenDayError` fırlatılır. En kötü durum O(366).
  - `late_days(due_on: date, on: date, closed_dates: AbstractSet[date]) -> int`: `max(0, (on − due_on).days − |{d ∈ closed_dates : due_on ≤ d ≤ on}|)` (ADR-0040; alt sınır ADR-0069, faz 6). O(c).
  - `MemberInput` ve `classify_member_input(raw: str) -> MemberInput` (ADR-0046, KL-35).
  - `fine(late_days: int, daily_kurus: int, cap_kurus: int) -> int`: `min(late_days × daily_kurus, cap_kurus)`.
  - `Blocker(Enum)`, değeri SRS mesajıdır: `MEMBER_INACTIVE="Üye pasif"`, `LIMIT_REACHED="Ödünç limiti dolu"`, `HAS_OVERDUE="Gecikmiş ödünç var"`, `DEBT_THRESHOLD="Borç eşiği aşıldı"`, `COPY_NOT_ON_SHELF="Nüsha rafta değil"`, `ALREADY_RENEWED="Uzatma hakkı kullanıldı"`, `LOAN_OVERDUE="Ödünç gecikmiş"`, `HAS_DEBT="Ödenmemiş borç var"`.
  - `CheckoutState(member_active: bool, open_loans: int, max_open_loans: int, has_overdue: bool, balance_kurus: int, debt_threshold_kurus: int, copy_status: str)`
  - `checkout_blockers(s: CheckoutState) -> list[Blocker]`. Bütün geçerli engeller enum sırasıyla döner (KL-6). Eşik dahildir: `balance ≥ threshold` engeller.
  - `RenewState(renewed: bool, due_on: date, today: date, balance_kurus: int)`
  - `renew_blockers(s: RenewState) -> list[Blocker]`. `due_on < today` ise ödünç gecikmiş sayılır.
  - `renewed_due_date(current_due: date, period_days: int, is_closed) -> date`: `due_date(current_due, period_days, is_closed)` sonucunu döndürür.
  - `COPY_TRANSITIONS: dict[tuple[str, str], Literal["ADMIN", "CLERK"]]`: architecture §5.1'deki geçişler ve gereken rol.
  - `check_transition(from_status: str, to_status: str) -> Literal["ADMIN", "CLERK"]`. Tabloda olmayan geçişte `InvalidTransition("Bu durum değişikliği yapılamaz: <eski> → <yeni>")` fırlatır.
- **Testler:** TC-104…TC-123, TC-276…TC-277, TC-279…TC-280 (24 TC; `docs/test-plan.md` §6)
- **Doğrulama:** `coverage run --branch -m pytest circulation/tests/test_domain.py && coverage report --include="circulation/domain.py" --fail-under=90` → çıkış 0. `python manage.py makemigrations --check --dry-run` → "No changes detected".
- [x] Tamamlandı
  - Kanıt (2026-11-01, bulut oturumu, Linux, Python 3.11.18): `coverage run --branch -m pytest circulation/tests/test_domain.py` → 67 passed; `coverage report --include="circulation/domain.py" --fail-under=90` → %100 (dal), çıkış 0; `python -m pytest circulation -q` → 73 passed (6'sı `Loan` kısıt testi); `python -m pytest -q` → 588 passed; `makemigrations --check --dry-run` → "No changes detected".

### Görev G11: Ödünç verme, iade ve uzatma

- **Gereksinimler:** FR-02, FR-07, FR-08, FR-09, FR-10, FR-11, FR-12, FR-23 (AC-23'ün 2. koşulu), NFR-11; AC-02, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12, AC-23; ADR-0003, ADR-0023, ADR-0040, ADR-0046; data-design §5 (eşzamanlılık); KL-6, KL-22, KL-29, KL-35. `Loan` modeli G10'da (KL-39).
- **Dosyalar:** oluştur `circulation/{services,views,urls,forms}.py`, `circulation/templates/circulation/{checkout,checkin}.html`, `static/js/scan.js`, `circulation/tests/*`; değiştir `tests/support/factories.py` (`make_loan`).
- **Arayüzler:**
  - `member_status(member_no: int, today: date) -> MemberStatus`: üye, açık ödünçler, bakiye, engeller.
  - `preview_checkout(member_no: int, barcode: str, today: date) -> CheckoutPreview`: nüsha, son tarih, engeller.
  - `check_out(actor, member_no: int, barcode: str) -> Loan`. İşlem içinde engelleri yeniden değerlendirir; varsa `RuleViolation` mesajında engeller "; " ile birleştirilir. Ayarlardaki ceza oranları kopyalanır.
  - `check_in(actor, barcode: str) -> CheckInResult(loan, fine_kurus)`. Ceza `late_days(due_on, today, closed_dates())` ile hesaplanır (KL-29).
  - `renew(actor, loan_id: int) -> Loan`. `renewed_on = today`, `due_on = renewed_due_date(...)`.
  - `open_loans(member) -> list[Loan]`
  - `deactivate_member(actor, member, confirm_debt: bool) -> None` (personel):
    - Açık ödüncü olan üye için `RuleViolation("Açık ödüncü olan üye pasifleştirilemez")` fırlatır.
    - Borcu olan üye `confirm_debt=False` ile gelirse `RuleViolation("Üyenin <tutar> borcu var; onaylayarak pasifleştirin")` fırlatır. Form onay kutusuyla yeniden gösterilir.
    - Bu kontrollerden geçerse `members.services.set_inactive` çağrılır.
  - `overdue_loans(today: date) -> list[OverdueRow(loan, member_no, full_name, phone, title, due_on, late_days, accrued_fine)]` (S5)
- **Davranış:**
  - **Ödünç ekranı (`/odunc/`):**
    - Üye alanı açılışta odaktadır (`autofocus`). Okutma Enter ile GET `?uye=` gönderir.
    - Üye bilgisi, adı ve engeller gösterilir. Adın gösterilmesi ADR-0032'deki "adı sor" adımı içindir. Açık ödünçler "Uzat" düğmeleriyle listelenir. Ardından odak nüsha alanına geçer.
    - Nüsha okutulunca GET `?uye=&nusha=` gönderilir. Önizlemede başlık ve son tarih görünür, odak "Onayla" düğmesindedir. Enter, POST'u gönderir.
    - Başarılı POST 303 ile `/odunc/` adresine döner. Flash mesajı "Son tarih 16.11.2026" biçimindedir ve odak üye alanındadır.
    - Engel varsa onay düğmesi görünmez.
    - Üye alanı `classify_member_input` ile yorumlanır (ADR-0046, KL-35). Nüsha barkodunda üye açılmaz ve "Bu bir nüsha barkodu. Üye kartını okutun." uyarısı gösterilir. Telefonda ve ad aramasında sonuçlar listelenir; her satır `?uye=<no>` bağlantısıdır. Üye no doğrudan açılır.
    - Nüsha alanına 8 haneli olmayan bir değer girilirse kitap arama sonuçlarındaki Rafta nüshalar `?uye=&nusha=` bağlantısıyla gösterilir (FR-11, elle seçim).
  - **İade ekranı (`/iade/`):**
    - Barkod alanı odaktadır. Enter doğrudan POST gönderir; onay adımı yoktur.
    - Sonuç mesajı "İade alındı" ya da "İade alındı; 15,00 TL ceza yazıldı" olur. Odak yeniden barkod alanına döner.
    - 8 haneli olmayan girişte kitap arama sonuçlarındaki Ödünçte nüshalar "İade al" düğmeleriyle gösterilir.
  - `scan.js` yalnız odak yönetimi yapar: `data-next-focus` özniteliğiyle odak geçişi ve sayfa yüklenince `autofocus`. Formlar JS olmadan da çalışır.
  - Uzatma, üye ayrıntısında ve ödünç ekranındaki açık ödünç listesinde bulunur.
  - Üye ayrıntısına (`members/views.py`) açık ödünçler, bakiye, `/borclar/<no>/` bağlantısı ve pasifleştirme formu eklenir. Pasifleştirme formu `circulation.services.deactivate_member` çağırır (KL-22).
- **Testler:** TC-53…TC-56, TC-124…TC-149, TC-278, TC-281…TC-288 (39 TC; `docs/test-plan.md` §6)
- **Doğrulama:** `python -m pytest circulation -q` → hepsi geçer. `coverage run --branch -m pytest circulation && coverage report --include="circulation/domain.py" --fail-under=90` → çıkış 0.
- [x] Tamamlandı
  - Kanıt (2026-11-01, bulut oturumu, Linux, Python 3.11.18): `python -m pytest circulation -q` → 140 passed (TC-145…TC-148 dosya tabanlı SQLite ve iki iş parçacığıyla); `coverage run --branch -m pytest circulation` → 140 passed; `coverage report --include="circulation/domain.py" --fail-under=90` → %100 (dal), çıkış 0; tam koşuda `circulation/services.py` %99 (dal; tek eksik `IntegrityError` dalı, IMMEDIATE işlemler yüzünden ulaşılamaz), `members/views.py` %99; `python -m pytest -q` → 733 passed; `makemigrations --check --dry-run` → "No changes detected". Pasifleştirme korumasının testleri (kullanıcı kararı 2026-11-01): `test_tc53_guard_anonymized_member_is_refused`, `test_tc53_guard_inactive_member_keeps_its_deactivation_date` (servis), `test_tc53_deactivation_form_only_for_active_members`, `test_tc53_guard_view_refuses_inactive_and_anonymized` (view).

### Görev G12: Nüsha durum işlemleri

- **Gereksinimler:** FR-15, FR-16, FR-26 (kayıp, hasar, bulundu, onarıldı, kayıttan düşme), FR-39; AC-15, AC-16, AC-32; ADR-0020, ADR-0026, ADR-0037, ADR-0040; küçük kararlar 4 ve 5 (faz 1), küçük karar 8 (faz 4); KL-7, KL-29.
- **Dosyalar:** değiştir `circulation/services.py`, `circulation/views.py`, `circulation/urls.py`; oluştur `circulation/templates/circulation/copy_detail.html`.
- **Arayüzler:** Her servis `check_transition` ile geçişi ve rolü doğrular. Denetim kaydında hedef `copy`'dir ve `details` içinde `{"from": <eski durum>, "note": <not>}` bulunur.
  - `mark_lost(actor, barcode, fee_kurus: int, note: str = "") -> Loan` ve `mark_damaged(actor, barcode, fee_kurus: int, note: str = "") -> Loan` (yönetici; nüsha Ödünçte olmalı):
    - Ödünç kapatılır; `close_reason` LOST ya da DAMAGED olur.
    - `fine(late_days(due_on, today, closed_dates()), …)` sonucu 0'dan büyükse FINE yazılır (ADR-0040).
    - `fee_kurus > 0` ise FEE yazılır (KL-7). FINE her zaman FEE'den önce yazılır (KL-44).
    - Nüsha durumu güncellenir ve `COPY_LOST` ya da `COPY_DAMAGED` kaydı yazılır.
  - `mark_shelf_copy(actor, barcode, new_status: Literal["LOST", "DAMAGED", "WITHDRAWN"], note: str = "") -> Copy` (yönetici; nüsha Rafta olmalı). Ödünç ve borç kaydı oluşmaz.
  - `mark_found(actor, barcode) -> FoundResult(copy, cancelled_kurus, refundable_kurus)` (personel; Kayıp → Rafta):
    - Hedef, nüshanın en son ödüncüdür (en büyük `id`). Bu ödüncün `close_reason` değeri LOST ve `copy_found_on` değeri NULL ise `copy_found_on = today` yazılır ve bağlı FEE için `cancel_unpaid` çağrılır (ADR-0037).
    - Koşul sağlanmazsa (raftan kaybolmuş nüsha) iki adım da atlanır. Ödüncün bağı koparılmışsa bedel bulunamaz; yönetici elle iptal yapar (ADR-0041).
    - `COPY_FOUND` kaydı yazılır.
  - `repair(actor, barcode, note="") -> Copy` (yönetici; Hasarlı → Rafta; `COPY_REPAIRED`).
  - `withdraw(actor, barcode, note="") -> Copy` (yönetici; Hasarlı ya da Kayıp → Kayıttan düşmüş; `COPY_WITHDRAWN`). Kayıp nüsha için olan geçiş FR-39'dan gelir.
- **Davranış:**
  - Nüsha ekranı yalnız geçerli işlemleri gösterir. Yönetici işlemleri görevliye görünmez, sunucu da 403 döndürür.
  - Kayıp ve hasar formunda bedel alanı yalnız nüsha Ödünçteyse gösterilir.
  - Bulundu sonucunda iade edilebilir tutar varsa "Ödenmiş <tutar> para iadesi için üyenin borç sayfasında" mesajı ve bağlantısı gösterilir.
  - Bütün yollarda nüsha `barcode` ile bulunur. Bulunamazsa 404 döner.
- **Testler:** TC-150…TC-170, TC-289…TC-293 (26 TC; `docs/test-plan.md` §6)
- **Doğrulama:** `python -m pytest circulation billing -q` → hepsi geçer.
- [x] Tamamlandı
  - Kanıt (2026-11-01, bulut oturumu, Linux, Python 3.11.18): `python -m pytest circulation billing -q` → 260 passed; `python -m pytest -q` → 784 passed; `makemigrations --check --dry-run` → "No changes detected"; tam koşuda dal kapsamı `*/domain.py` %100, `billing/services.py` %100, `circulation/services.py` %98, `members/services.py` %100, `accounts/permissions.py` ve `accounts/middleware.py` %100; `circulation` + `billing` + `members` toplam %99. Ödünç, iade, nüsha, döküm ve üye ekranları geliştirme sunucusunda Playwright ile açılıp göz kontrolünden geçti (odak "Onayla" düğmesinde; nüsha ekranında yalnız geçerli işlemler).

### Görev G13: Geciken listesi ve hatırlatmalar

- **Gereksinimler:** FR-18, FR-19, FR-20, FR-03 (AC-03'ün 2. koşulu), NFR-05 (pencereler); AC-03, AC-18, AC-19, AC-20; ADR-0004, ADR-0007, ADR-0039; küçük kararlar 6 ve 7 (faz 3); KL-1, KL-11, KL-13, KL-23, KL-28.
- **Dosyalar:** oluştur `notifications/{__init__,apps,models,domain,services,views,urls}.py`, migration (`reminder_log.due_on` ve data-design §2.6'daki `(loan_id, kind, due_on)` kısmi benzersiz indeksi dahil, ADR-0039), `notifications/templates/notifications/overdue.html`, `notifications/templates/notifications/email/{due_soon,overdue}_{subject,body}.txt`, `notifications/management/commands/send_reminders.py`, `notifications/tests/*`; değiştir `library_site/settings/prod.py` (`EMAIL_TIMEOUT = 10`, ADR-0052).
- **Arayüzler:**
  - domain `ReminderKind(TextChoices)`: `DUE_SOON`, `OVERDUE_1`, `MANUAL`.
  - domain `due_reminder_kind(due_on: date, today: date) -> ReminderKind | None`. `today ∈ [due−2, due]` ise DUE_SOON, `today ∈ [due+1, due+7]` ise OVERDUE_1 döner.
  - `send_due_reminders(today: date) -> ReminderCounts(sent, failed, skipped)`:
    - S6 adayları okunur (tekrar engeli `due_on = loan.due_on` ile, ADR-0039). Her aday için e-posta gönderilir, ardından `reminder_log` deneme anındaki `due_on` ile ayrı bir işlemde yazılır.
    - Benzersiz kısıt ihlali gönderilmiş sayılır ve `skipped` sayısına eklenir.
    - SMTP istisnası FAILED olarak kaydedilir.
  - `send_manual_reminders(actor, loan_ids: list[int]) -> list[ManualResult(loan_id, outcome)]`. `outcome` değerleri: `sent`, `no_consent` ("rıza yok"), `no_email` ("e-posta yok"), `failed` ("gönderilemedi"), `not_overdue`.
  - Komut `send_reminders [--date YYYY-MM-DD]`, `administration.jobs.run_job(Job.REMINDERS, …)` içinde çalışır. Sayımları yazar. En az bir FAILED varsa çıkış kodu 1'dir; `job_run` yine SUCCESS olur ve `detail` sayımları taşır (KL-23).
- **Davranış:**
  - Geciken listesi `overdue_loans(today)` sonucunu son tarihe göre, en eskiden başlayarak sayfalamadan gösterir. Her satırda seçim kutusu bulunur. Rızası ya da e-postası olmayan satırda "rıza yok" ya da "e-posta yok" etiketi görünür.
  - E-posta metinleri KL-13'tedir. Alıcı yalnız üyedir, gönderen `LIBRARY_EMAIL_FROM`'dur.
- **Testler:** TC-171…TC-185, TC-294…TC-298 (20 TC; `docs/test-plan.md` §6)
- **Doğrulama:** `python -m pytest notifications -q` → hepsi geçer. `python manage.py send_reminders --date 2026-11-14` (dev, konsol backend'i) → "gönderilen=…, başarısız=0, atlanan=…" ve çıkış 0.
- [x] Tamamlandı
  - Kanıt (2026-11-01, bulut oturumu, Linux, Python 3.11.18): `python -m pytest notifications -q` → 67 passed; `python -m pytest -q` → 852 passed (`slow` dahil; önceki 784); `python -m pytest -m slow -q` → 4 passed; `makemigrations --check --dry-run` → "No changes detected"; tam koşuda dal kapsamı `*/domain.py` %100 (`notifications/domain.py` %100), `accounts/permissions.py` ve `accounts/middleware.py` %100, `notifications/services.py` %98 (hedef yok, yalnız rapor), `notifications` toplam %99, proje toplamı %99. Dev ayarlarıyla `send_reminders --date 2026-11-14` → "gönderilen=2, başarısız=0, atlanan=0", çıkış 0; aynı tarihte ikinci koşu "gönderilen=0, başarısız=0, atlanan=0", çıkış 0. `/gecikenler/` geliştirme sunucusunda Playwright ile açılıp göz kontrolünden geçti (seçim kutuları, "rıza yok"/"e-posta yok" etiketleri, boş seçim hatası, elle hatırlatma sonrası mesajlar). Commit `158d43d`.

### Görev G14: Yedek, şifreli dışa aktarma ve geri yükleme

- **Gereksinimler:** FR-28, FR-37, NFR-03, NFR-04; AC-28, AC-30; ADR-0002, ADR-0006, ADR-0011; küçük kararlar 13, 14 ve 15 (faz 3), küçük karar 6 (faz 4); KL-4, KL-14, KL-24.
- **Dosyalar:** oluştur `operations/{__init__,apps,domain,libx,backup,applock}.py`, `operations/management/commands/{backup_db,export_backup,restore_backup}.py`, `operations/tests/*`; değiştir `library_site/settings/base.py` (`INSTALLED_APPS`'e `operations`).
- **Arayüzler:**
  - domain:
    - `backup_name(on: date) -> str`
    - `backups_to_delete(names: list[str], run_on: date, keep_days: int = 30) -> list[str]`. Adı desene uymayan dosyalara dokunulmaz.
    - `latest_backup(names: list[str]) -> str | None`
    - `exports_to_delete(names: list[str], run_on: date, keep_days: int = 56) -> list[str]` (KL-24). Adı desene uymayan dosyalara dokunulmaz.
  - `libx.encrypt(plaintext: bytes, passphrase: str, n=2**17, r=8, p=1) -> bytes` ve `libx.decrypt(blob: bytes, passphrase: str) -> bytes`. Biçim architecture §6.3'tedir. Hatalı parola ya da bozuk dosya `LibxError("Parola hatalı ya da dosya bozuk")`, bilinmeyen sürüm `LibxError("Desteklenmeyen dosya sürümü")` verir.
  - `backup.backup_db(run_on: date) -> Path`. `sqlite3.Connection.backup` önce geçici bir dosyaya yazılır, sonra `os.replace` ile yerine konur. Ardından eski yedekler silinir.
  - `backup.export_backup(run_on: date, passphrase_file: Path) -> Path`. Başarılı yazımdan sonra eski dışa aktarmaları siler (KL-24).
  - `backup.restore(path: Path, passphrase_file: Path | None) -> RestoreCounts(members, copies, loans)`. Sonuç ayrıca koruma kopyasının yolunu taşır (`RestoreResult(counts, pre_restore: Path | None)`, ADR-0054).
  - `applock.hold_app_lock(db_path: Path) -> IO` ve `applock.try_lock(db_path: Path) -> bool` (KL-4). Kilit alınamazsa `hold_app_lock`, `RuntimeError`'ın alt sınıfı `AppLockError("Uygulama zaten çalışıyor: <kilit yolu>")` fırlatır (G16'daki `wsgi.py` mesajı).
  - Komutlar (G14–G16 küçük karar 1): `backup_db [--date YYYY-MM-DD]`, `export_backup [--date …] [--passphrase-file PATH]` (verilmezse `LIBRARY_EXPORT_PASSPHRASE_FILE`), `restore_backup PATH [--passphrase-file PATH] --yes`. Tarih geçersizse `job_run` yazılmadan `CommandError("Geçersiz tarih: …")`.
- **Davranış:**
  - Parola dosyasının içeriğinin sonundaki satır sonu atılır. Boş parola hatadır.
  - Yedek ve dışa aktarma önce hedef klasörde bir `.tmp` dosyasına yazılır, ardından `os.replace` ile yerine konur. Hata olursa `.tmp` silinir. Aynı gün ikinci koşu dosyanın üzerine yazar (küçük karar 4).
  - `restore_backup PATH [--passphrase-file PATH] --yes` şu adımları izler:
    1. `--yes` yoksa çıkış 2. PATH yoksa "Dosya bulunamadı: <yol>" ile çıkış 1 (KL-41).
    2. Uygulama kilidi alınamıyorsa "Uygulama çalışıyor; önce servisi durdurun" mesajıyla çıkış 1.
    3. Dosya türü uzantıdan değil `LIBX` magic baytından anlaşılır. `.libx` dosyası `--passphrase-file`, o yoksa `LIBRARY_EXPORT_PASSPHRASE_FILE` ile çözülür; ikisi de yoksa çıkış 1 (küçük karar 2). Çözülen ya da kopyalanan içerik veritabanıyla aynı klasörde geçici bir dosyaya yazılır (küçük karar 4).
    4. Geçici dosyada `PRAGMA integrity_check = ok` ve `django_migrations` tablosunun varlığı doğrulanır.
    5. Mevcut veritabanı dosyası ve varsa `-wal`/`-shm` dosyaları silinmez; `<db>.pre-restore-YYYYMMDD-HHMMSS` (ve `…-wal`, `…-shm`) olarak yeniden adlandırılır. Mevcut dosya bozuk olsa da bu adım çalışır. Ardından geçici dosya `os.replace` ile yerine konur ([ADR-0054](../decisions/0054-restore-keeps-pre-restore-copy.md)).
    6. Sayımlar ve koruma kopyasının yolu yazılır. Geri yükleme migration çalıştırmaz; çıktı "gerekirse `python manage.py migrate` çalıştırın" notunu da yazar (küçük karar 3).
  - `backup_db` ve `export_backup`, `run_job` içinde çalışır (`BACKUP`, `EXPORT`).
- **Testler:** TC-186…TC-200, TC-299…TC-304, TC-320…TC-329 (31 TC; `docs/test-plan.md` §6)
- **Doğrulama:** `python -m pytest operations -q` → hepsi geçer. Elle: dev veritabanında `python manage.py backup_db`, ardından `export_backup` ve `restore_backup <libx> --yes` → çıkış 0 ve yazılan sayımlar yedekten önceki sayımlarla aynı.
- [x] Tamamlandı
  - Kanıt (2026-11-01, bulut oturumu, Linux, Python 3.11.18): `python -m pytest operations -q` → 68 passed; `python -m pytest -q` → 920 passed (`slow` dahil; önceki 852); `python -m pytest -m slow -q` → 4 passed; `makemigrations --check --dry-run` → "No changes detected"; tam koşuda dal kapsamı `*/domain.py` %100 (`operations/domain.py` %100; `--fail-under=90` çıkış 0), `accounts/permissions.py` ve `accounts/middleware.py` %100 (`--fail-under=100` çıkış 0), `operations` toplam %99 (`backup.py` %99: kapsanmayan tek dal `integrity_check`'in "ok" dışı sonucu; `libx.py`, `applock.py`, `domain.py`, `cli.py` ve komutlar %100), proje toplamı %99. Dev veritabanında (5 üye, 7 nüsha, 3 ödünç) `backup_db` → "Yedek alındı: …/var/backups/library-20261101.sqlite3", `export_backup` → "Dışa aktarıldı: …/var/exports/library-export-20261101.libx (kaynak: library-20261101.sqlite3)", `restore_backup var/exports/library-export-20261101.libx --yes` → "Geri yüklendi: üye=5, nüsha=7, ödünç=3", "Önceki veritabanı korundu: …/var/library.sqlite3.pre-restore-20261101-142040"; üçü de çıkış 0, geri yükleme sonrası ORM sayımları 5/7/3. Kilit testleri (TC-199, TC-302) bulutta yalnız Linux'ta (`fcntl`) koştu; Windows (`msvcrt`) koşusu yerel doğrulamada.

### Görev G15: Saklama süresi ve anonimleştirme

- **Gereksinimler:** FR-25, NFR-08; AC-25; ADR-0018, ADR-0045; küçük kararlar 4 ve 8 (faz 3); KL-34.
- **Dosyalar:** değiştir `operations/domain.py`, `operations/services.py`, `members/views.py`, `members/urls.py`; oluştur `operations/management/commands/anonymize_expired.py`, `members/templates/members/retention_pending.html`, testler. Açılış kararlarıyla eklenenler: `members/models.py` (`Member.display_name`), anonim üyenin adını gösteren şablon ve servisler (`members/templates/members/{search,detail}.html`, `billing/templates/billing/statement.html`, `circulation/templates/circulation/checkout.html`, `circulation/services.py` `overdue_loans` ve üye ayrıntısındaki toplam için `loan_total`, `members/views.py` `_detail_page`, `notifications/services.py` elle hatırlatma sonucu), `templates/base.html` (yöneticiye "Saklama" bağlantısı), `tests/test_authorization.py`.
- **Arayüzler:**
  - domain `add_years(d: date, years: int) -> date`: 29 Şubat, 28 Şubat'a düşer.
  - domain `is_expired(start: date, years: int, today: date) -> bool`: `add_years(start, years) < today` (küçük karar 4).
  - `anonymize_expired(today: date) -> AnonymizeCounts(members, loans, deferred)`. Her kayıt kendi işleminde işlenir:
    - **Borçlu üye:** `billing.services.member_balance(member) > 0` ise üye atlanır ve `deferred` artar (ADR-0045).
    - **Üye:** `full_name`, `phone`, `phone_digits` ve `email` alanları NULL, `search_key` boş, `has_email_consent` False olur. `consent_event` satırları silinir ve `anonymized_at` doldurulur.
    - **Ödünç:** `member` NULL olur ve `member_unlinked_at` doldurulur. Üyenin `archived_loan_count` sayacı 1 artar. Bağlı `ledger_entry.loan` alanları NULL olur. Aynı işlemde o ödüncün `reminder_log` satırlarının `error` alanı NULL olur; tür, durum ve tarihler kalır ([ADR-0055](../decisions/0055-reminder-log-error-cleared-on-unlink.md)).
  - Komut `anonymize_expired [--date …]`, `run_job(Job.ANONYMIZE, …)` içinde çalışır. Tarih geçersizse `job_run` yazılmadan `CommandError("Geçersiz tarih: …")` (G14–G16 küçük karar 1).
  - `deferred_members(today) -> list[DeferredRow]` ve `/uyeler/saklama/` listesi (KL-34).
  - `Member.display_name`: anonim üyede "Anonimleştirilmiş üye", diğerlerinde `full_name` (küçük karar 8).
- **Davranış:**
  - Anonim üye her yerde "Anonimleştirilmiş üye" olarak görünür: listeler, ödünç ekranı, borç dökümü ve geciken listesi; ad tek kaynaktan, `Member.display_name`'den gelir (küçük karar 8). Toplam ödünç sayısı, bağlı ödünçlerle `archived_loan_count` toplamıdır ve üye ayrıntısında gösterilir.
  - `anonymize_expired` ilk istisnada durur. Önceki kayıtlar işlenmiş kalır, `job_run` FAILED olur, çıkış 1 olur (TC-207). Sonraki koşu kaldığı yerden devam eder (küçük karar 9).
  - Menüde yalnız yöneticinin gördüğü bir `/uyeler/saklama/` bağlantısı bulunur (küçük karar 7).
- **Testler:** TC-201…TC-207, TC-305…TC-309, TC-330…TC-334 (17 TC; `docs/test-plan.md` §6)
- **Doğrulama:** `python -m pytest operations -q` → hepsi geçer.
- [x] Tamamlandı
  - Kanıt (2026-11-01, bulut oturumu, Linux, Python 3.11.18): `python -m pytest operations -q` → 85 passed; `python -m pytest members/tests/test_retention_views.py -q` → 7 passed; `python -m pytest -q` → 944 passed (`slow` dahil; G14 sonrası 920); `python -m pytest -m slow -q` → 4 passed; `makemigrations --check --dry-run` → "No changes detected"; tam koşuda dal kapsamı `*/domain.py` %100 (`--fail-under=90` çıkış 0), `accounts/permissions.py` ve `accounts/middleware.py` %100 (`--fail-under=100` çıkış 0), `operations` toplam %99 (`operations/services.py` %95: kapsanmayan iki satır eşzamanlı koşuya karşı koruma dalları; `backup.py` %99), proje toplamı %99. Dev veritabanında `anonymize_expired` → "anonimleştirilen üye=1, bağı koparılan ödünç=2, ertelenen üye=2", çıkış 0. `/uyeler/saklama/` (iki borçlu üye, en eski pasifleşme önce, bakiye ve "borç nedeniyle bekliyor"), anonim üyenin ayrıntısı ("Anonimleştirilmiş üye · Pasif", "Toplam ödünç: 2") ve üye aramasındaki anonim satır geliştirme sunucusunda Playwright ile açılıp göz kontrolünden geçti; menüde yöneticiye "Saklama" bağlantısı görünüyor.

### Görev G16: Zamanlayıcı ve telafi

- **Gereksinimler:** FR-18 (09:00), FR-25, FR-28, FR-37 (haftalık), NFR-03, NFR-05; ADR-0007, ADR-0012; küçük kararlar 13 ve 14 (faz 3), küçük karar 14 (faz 4); KL-5.
- **Dosyalar:** oluştur `operations/scheduler.py`, `operations/tests/test_scheduler.py`; değiştir `library_site/wsgi.py`, `operations/domain.py` (`jobs_due_for_catch_up`), `library_site/settings/base.py` (`LOGGING`, küçük karar 6).
- **Arayüzler:**
  - `SCHEDULE: list[ScheduledJob(job: Job, command: str, cron: dict)]`: BACKUP 02:00, ANONYMIZE 02:30, REMINDERS 09:00, EXPORT pazartesi 03:00 (Europe/Istanbul).
  - `jobs_due_for_catch_up(now: datetime, last_success: dict[Job, date | None]) -> list[Job]` (domain'de, saf):
    - Günlük görev için koşul: bugünün planlanan saati geçmiş ve `last_success < bugün`.
    - Haftalık görev için koşul: en son pazartesi 03:00 geçmiş ve `last_success` o pazartesiden eski.
    - Sıra: BACKUP, ANONYMIZE, EXPORT, REMINDERS.
  - `start_scheduler() -> BackgroundScheduler`. Görevler `call_command(command)` ile çalışır; telafi görevleri tek seferlik `date` tetikleyicisiyle hemen kuyruğa alınır.
  - `catch_up(scheduler, now) -> list[Job]`: son başarılı çalışmaları okur, `jobs_due_for_catch_up` sonucunu sırayla kuyruğa alır ve döndürür. Açılışta bir kez ve `IntervalTrigger(hours=1)` göreviyle saatte bir çalışır ([ADR-0053](../decisions/0053-hourly-catch-up.md)).
  - `run_command(command: str) -> None`: her `call_command` çağrısını sarar; `CommandError` ve diğer istisnalar `logging.getLogger("operations.scheduler")` ile loglanır, dışarı çıkmaz (küçük karar 6).
- **Davranış:**
  - `wsgi.py` önce `hold_app_lock` çağırır (her zaman). Kilit alınamazsa `RuntimeError("Uygulama zaten çalışıyor: <kilit yolu>")` fırlatır ve süreç başlamaz (R-09). Ardından `LIBRARY_SCHEDULER_ENABLED == "1"` ise `start_scheduler()` çalışır (KL-5).
  - Testlerde ve yönetim komutlarında zamanlayıcı başlamaz, çünkü bunlar `wsgi.py`'yi yüklemez.
  - Görev istisnası loglanır ve zamanlayıcıyı durdurmaz. `send_reminders`'ın FAILED varken verdiği `CommandError` da bu yolla yakalanır; `job_run` zaten SUCCESS'tir (KL-23).
  - Zamanlayıcı tek işçili yürütücüyle çalışır (`ThreadPoolExecutor(max_workers=1)`, `max_instances=1`); telafi sırası korunur ve EXPORT taze yedeği görür (küçük karar 5). Cron ve telafi görevlerinde `misfire_grace_time=3600` ve `coalesce=True` (ADR-0053).
  - `base.py`'deki `LOGGING` stderr'e yazar; `operations` ve `django` logger'ları INFO seviyesindedir (küçük karar 6).
- **Testler:** TC-208…TC-213, TC-310…TC-314, TC-335…TC-339 (16 TC; `docs/test-plan.md` §6)
- **Doğrulama:** `python -m pytest operations/tests/test_scheduler.py -q` → hepsi geçer. Elle: `LIBRARY_SCHEDULER_ENABLED=1` ile `waitress-serve` başlatılır → logda beş tetikleyicinin (dört görev ve saatlik telafi) sonraki çalışma zamanları ve gerekiyorsa telafi satırları görünür.
- [x] Tamamlandı
  - Kanıt (2026-11-01, bulut oturumu, Linux, Python 3.11.18): `python -m pytest operations/tests/test_scheduler.py -q` → 21 passed (TC-310…TC-312 domain testleri `test_domain.py`'de); `python -m pytest operations -q` → 113 passed; `python -m pytest -q` → 972 passed (`slow` dahil; G15 sonrası 944); `python -m pytest -m slow -q` → 4 passed; `makemigrations --check --dry-run` → "No changes detected"; tam koşuda dal kapsamı `*/domain.py` %100 (`--fail-under=90` çıkış 0), `accounts/permissions.py` ve `accounts/middleware.py` %100 (`--fail-under=100` çıkış 0), `operations` toplam %99 (`scheduler.py` %100, `domain.py` %100, `services.py` %95, `backup.py` %99), proje toplamı %99. Elle: dev ayarlarıyla `LIBRARY_SCHEDULER_ENABLED=1 waitress-serve --listen=127.0.0.1:8001 --threads=8 library_site.wsgi:application` → logda beş satır "Zamanlanmış görev catch-up: sonraki çalışma 2026-11-01 15:40:36…+03:00", "backup … 2026-11-02 02:00:00+03:00", "anonymize … 02:30", "export … 03:00", "reminders … 09:00"; ardından "Telafi: BACKUP kuyruğa alındı (backup_db)", "Telafi: EXPORT …", "Telafi: REMINDERS …" ve üç görev bu sırayla "tamamlandı" (G14'teki geri yükleme, kendi `job_run` satırlarını içermeyen yedeği geri koyduğu için BACKUP ve EXPORT da vadesi gelmiş sayıldı). Aynı gün ikinci açılışta telafi satırı yok. Uygulama çalışırken ikinci bir `waitress-serve` → `AppLockError: Uygulama zaten çalışıyor: …/var/library.sqlite3.app.lock`, `restore_backup` → "Uygulama çalışıyor; önce servisi durdurun", çıkış 1. Kilit testleri (TC-302, TC-313) bulutta yalnız Linux'ta (`fcntl`) koştu; Windows (`msvcrt`) koşusu yerel doğrulamada.

### Görev G17: Tohum veri

- **Gereksinimler:** FR-29, NFR-02 (yük verisi); AC-29; ADR-0031, ADR-0033, ADR-0038, ADR-0056, ADR-0057, ADR-0059; küçük kararlar 12 ve 13 (faz 4); KL-16, KL-27; G17–G18 küçük kararları 1–9 (§11).
- **Dosyalar:** oluştur `scripts/__init__.py`, `scripts/fetch_demo_books.py`, `scripts/tests/{__init__,test_fetch_demo_books}.py`, `seed/books_openlibrary.json` (betik bir kez çalıştırılır, çıktısı depoya girer; ağ engelliyse yerel doğrulamada, ADR-0056), `seed/first_names.txt`, `seed/last_names.txt`, `operations/seed.py`, `operations/management/commands/load_seed_data.py`, `operations/tests/test_seed.py` ve örnek kitap dosyası `operations/tests/data/books_sample.json`; oluştur `README.md` ("Veri kaynakları" ve "Demo verisi" bölümleri; küçük karar 1).
- **Arayüzler:**
  - `scripts/fetch_demo_books.py --out seed/books_openlibrary.json --limit 300`
  - `filter_records(raw: Iterable[dict]) -> list[dict]`: ADR-0033'teki beş filtre aynı sırayla, her eserin eşleşen ilk Türkçe baskısına uygulanır (ADR-0059). Ağ çağrısı içermediği için birim testiyle doğrulanır.
  - `operations.seed.load(profile: Literal["demo", "load"], seed: int, actor: StaffUser) -> SeedCounts`
  - Komut `load_seed_data --profile demo|load --actor <kullanıcı adı> [--seed 42]`. Varsayılan `demo` ve 42'dir. `--actor` eksikse çıkış 2; kullanıcı yoksa ya da pasifse "Personel bulunamadı ya da pasif: <ad>" ile çıkış 1 (ADR-0038). Üye ya da kitap tablosu boş değilse "Veritabanı boş değil" mesajıyla çıkış 1.
- **Davranış:**
  - Demo ve yük profillerinin ayrıntısı KL-16'dadır. **Demo** ayrıca son 180 güne yayılmış 350 kapalı ödünç içerir (150 açık ödünce ek). 5 borçlu üyenin borcu gecikmeli iadeden doğan ödenmemiş FINE'dır; diğer gecikmeli iadeler FINE ve aynı tutarda PAYMENT alır (küçük karar 3). **Yük** profilinde 100.000 ödünç son 365 güne yayılır; 2 yıllık saklama görevi yük verisine dokunmaz (küçük karar 4).
  - Tarihler komutun çalıştığı günden (`administration.clock.today()`, yani `timezone.localdate()`) geriye doğru üretilir. Aynı gün ve aynı `--seed` aynı veriyi verir (küçük karar 2).
  - Son tarih (kapalı gün kaydırması dahil, `due_date`), ceza (`late_days`, `fine`), barkod (`f"{id:08d}"`), `search_key` (`normalize_tr`) ve `phone_digits` mevcut domain fonksiyonlarıyla hesaplanır; süre, ceza oranı ve üst sınır `LibrarySettings`'ten okunur. Yazım `bulk_create` ile tek bir `transaction.atomic()` içinde yapılır; hata olursa hiçbir satır kalmaz (küçük karar 5).
  - Tohum veri ORM ile doğrudan yazılır ve tutarlı durum üretir: açık ödüncün nüshası Ödünçtedir, kapalı ödüncün nüshası Raftadır. Aynı nüshanın ödünçleri zamanda çakışmaz.
  - `seed/books_openlibrary.json`'daki ilk 300 kayıt (yük profilinde de en çok 300) Open Library kitabı olarak yazılır (`source_ol_id` dolu). Eksik kısım sentetik kitaplarla tamamlanır: başlık, dosyadaki başlıklardan alınan 2–4 sözcüktür; yazar ad ve soyad listelerinden gelir; ISBN, yayınevi ve `source_ol_id` boştur (küçük karar 6).
  - Tohum veri audit kaydı yazmaz. PAYMENT'ların Allocation satırları FIFO (`allocate_fifo`) ile yazılır; bakiyeler defterle tutarlıdır (küçük karar 7).
  - Çıktı kitap, nüsha, üye, açık ödünç (gecikmiş) ve kapalı ödünç sayılarını verir. Sentetik tamamlama olduysa bunu ayrı bir satırda yazar (küçük karar 8).
  - Rızalı üye için `ConsentEvent(GIVEN)` yazılır; `effective_on` son 365 günden rastgele bir gündür. Sentetik üye e-postaları `uye<no>@example.invalid` biçimindedir; gerçek bir alıcıya ulaşmaz (küçük karar 9).
  - Telefonlar `000 ddd dd dd` biçiminde, "000" önekli sahte numaralardır; hiçbir gerçek aboneye denk gelmez ([ADR-0057](../decisions/0057-seed-phone-numbers.md)).
  - Personel hesabı oluşturulmaz. Bütün `created_by`, `closed_by` ve `recorded_by` alanları `--actor` personelidir (ADR-0038).
  - `load_seed_data` ağa çıkmaz. Open Library'ye bulut oturumundan erişilemezse JSON dosyası yerel doğrulamada çekilip dala commit'lenir ([ADR-0056](../decisions/0056-open-library-fetch-network-blocked.md)).
- **Testler:** TC-214…TC-220, TC-315…TC-317, TC-340…TC-352, TC-357…TC-358 (25 TC; `docs/test-plan.md` §6). Yük profilini yükleyen TC-220, TC-317 ve TC-346 `slow` olarak işaretlenir.
- **Doğrulama:** `python -m pytest operations -q -k seed` ve `python -m pytest scripts -q` → hepsi geçer. `python scripts/fetch_demo_books.py --out seed/books_openlibrary.json --limit 300` denenir (ADR-0056). Boş dev veritabanında (bulutta migrate edilmiş geçici bir veritabanı, `LIBRARY_DB_PATH`) `createsuperuser` sonrası `python manage.py load_seed_data --profile demo --actor <ad>` → "kitap=300, nüsha=…, üye=200, açık ödünç=150 (gecikmiş 10), kapalı ödünç=350" ve çıkış 0. İkinci çalıştırmada çıkış 1.
- [x] Tamamlandı
  - Kanıt (2026-11-01, bulut oturumu, Linux, Python 3.11.18): `python -m pytest operations -q -k seed` → 25 passed; `python -m pytest scripts -q` → 8 passed (G17'nin `test_fetch_demo_books.py`'si); `python -m pytest operations -q` → 138 passed; `python -m pytest -q` → 1005 passed (`slow` dahil; önceki 972); `makemigrations --check --dry-run` → "No changes detected"; dal kapsamı `*/domain.py` %100 (`--fail-under=90` çıkış 0), `operations/seed.py` ve `load_seed_data.py` %100. ADR-0056 denemesi: `python scripts/fetch_demo_books.py --out seed/books_openlibrary.json --limit 300` → "Open Library'ye erişilemedi: Tunnel connection failed: 403 Forbidden", çıkış 1 (bulut ağ politikası); `seed/books_openlibrary.json` dala girmedi, yerel doğrulamada çekilecek. Elle: scratchpad'de migrate edilmiş geçici veritabanı (`LIBRARY_DB_PATH`), dev ayarları, örnek dosyanın geçici kopyası `seed/books_openlibrary.json` olarak (commit'lenmedi); `createsuperuser --username demo` sonrası `load_seed_data --profile demo --actor demo` → "kitap=300, nüsha=606, üye=200, açık ödünç=150 (gecikmiş 10), kapalı ödünç=350" ve "Open Library dosyasında 12 kayıt var; 288 sentetik kitap eklendi", çıkış 0, 0,7 sn; ikinci çalıştırma "Veritabanı boş değil", çıkış 1; `--actor yok` "Personel bulunamadı ya da pasif: yok", çıkış 1; `--actor` olmadan argparse çıkış 2. Ayrı veritabanında `--profile load` → "kitap=15000, nüsha=20000, üye=5000, açık ödünç=3000 (gecikmiş 300), kapalı ödünç=97000", 14 sn, ~21 MB; ardından `anonymize_expired` → "anonimleştirilen üye=0, bağı koparılan ödünç=0, ertelenen üye=0". Demo verisiyle üye araması, kitap araması, geciken listesi ve borçlu üyenin dökümü dev ayarlarıyla test istemcisinde 200 döndü ve göz kontrolünden geçti. Commit `ef50b96`.
  - Kanıt, yerel doğrulama (2026-11-01, Windows 11, Python 3.11): Filtre sürümü 1 ile çekilen dosyanın 300 kaydının 43'ü yabancı baskıydı (ISBN Türk öneki taşımıyor, başlıklar "Den skrattande polisen", "Smaragdgrün" gibi). Kullanıcı kararıyla [ADR-0059](../decisions/0059-demo-books-turkish-edition.md) yazıldı: kayıt eşleşen Türkçe baskıdan alınıyor ve 5xx ile zaman aşımında yeniden deneniyor (TC-357, TC-358; TDD, önce kırmızı). `python scripts/fetch_demo_books.py --out seed/books_openlibrary.json --limit 300` → "300 kayıt yazıldı", çıkış 0, 2 dk 18 sn. `_meta.filter_version` 2. 300 ISBN'in hepsi 978605 önekli, tekrar yok, 300 `ol_id` `OL…M`, yabancı harfli başlık yok (ör. "Atomik Alışkanlıklar", "Küçük Prens", "Açlık Oyunları"). Geçici veritabanında `load_seed_data --profile demo --actor demo` → "kitap=300, nüsha=592, üye=200, açık ödünç=150 (gecikmiş 10), kapalı ödünç=350", sentetik satır yok, çıkış 0; ikinci koşu "Veritabanı boş değil", çıkış 1. `python -m pytest -q` → 1022 passed; `-m slow` → 7 passed; `makemigrations --check --dry-run` → "No changes detected"; kapsam `*/domain.py` %100, `accounts` izinleri %100, `operations` %99 (eşikler çıkış 0), `fetch_demo_books.py` %98, proje %97.

### Görev G18: Yük testi betiği

- **Gereksinimler:** NFR-01, NFR-02; ADR-0031, ADR-0058; KL-17; G17–G18 küçük kararları 10–12 (§11).
- **Dosyalar:** oluştur `scripts/loadtest.py`, `scripts/tests/test_loadtest.py` (yüzdelik hesabı, karışım seçimi, aday seçimi, koruma ve iş parçacığı akışı için birim testleri); değiştir `pyproject.toml` (`testpaths`'e `scripts`; küçük karar 11).
- **Arayüzler:**
  - `scripts/loadtest.py --base-url URL --user U --password-file F --db PATH --workers 5 --duration 120 [--seed 42]`
  - `percentile(values: list[float], p: float) -> float`: en yakın sıra yöntemi.
  - `pick_operation(rng) -> str`: ağırlıklar %40/20/20/10/10.
- **Davranış:**
  - KL-17'ye göre çalışır.
  - **Koruma** ([ADR-0058](../decisions/0058-loadtest-seed-only-guard.md)): `--db` içinde e-postası `@example.invalid` ile bitmeyen bir üye varsa betik "Tohum verisi olmayan veritabanı" mesajıyla çıkış 1 verir ve hiç istek atmaz. E-postası boş üyeler korumayı tetiklemez.
  - Kendi açık ödüncü yokken iade ya da uzatma seçilirse işlem yeniden seçilir ve sayılmaz. Uzatılan ödünç uzatma havuzundan çıkar; iade edilebilir kalır (küçük karar 10).
  - `scripts/` bir pakettir ve `pyproject.toml` `testpaths`'e eklenir. Betik Django'yu import etmez (küçük karar 11).
  - Rapor işlem türü başına `istek, p50, p95, hata` sütunlarını içerir.
  - Bütün türlerde p95 < 500 ms ve hata = 0 ise çıkış 0, değilse 1.
- **Testler:** TC-221…TC-223, TC-318, TC-353…TC-356 (8 TC; `docs/test-plan.md` §6)
- **Doğrulama:** `python -m pytest scripts -q` → hepsi geçer. Elle duman testi (küçük karar 12): demo verisiyle `waitress` + `scripts/loadtest.py --duration 10`; p95 bağlayıcı değildir, yalnız not edilir. Ölçümün kendisi faz 6'da yapılır (TC-223).
- [x] Tamamlandı
  - Kanıt (2026-11-01, bulut oturumu, Linux, Python 3.11.18): `python -m pytest scripts -q` → 21 passed; `python -m pytest -q` → 1018 passed (`slow` dahil; G17 sonrası 1005); `python -m pytest -m slow -q` → 7 passed; `makemigrations --check --dry-run` → "No changes detected"; `scripts/loadtest.py` kapsamı %76 (kapsanmayan kısım `main()`'in iş parçacığı ve giriş akışı; elle duman testinde koştu), `scripts/fetch_demo_books.py` %97. Elle duman testi (küçük karar 12): G17'nin demo veritabanında dev ayarlarıyla `waitress-serve --listen=127.0.0.1:8011 --threads=8 library_site.wsgi:application`, ardından `python scripts/loadtest.py --base-url http://127.0.0.1:8011 --user demo --password-file <dosya> --db <demo db> --workers 5 --duration 10` → kitap arama 334 istek (p50 39,4 ms, p95 207,3 ms), ödünç 170 (32,3 / 148,9), iade 139 (29,0 / 228,8), uzatma 61 (31,0 / 133,4), üye arama 74 (24,6 / 388,0), hata 0, "Sonuç: geçti", çıkış 0 (p95 bağlayıcı değil; bulut kapsayıcısı, Caddy yok). Sonrasında veritabanında 670 ödünç (500 + 170), 181 açık, 61 uzatılmış; defter ve denetim kaydı değişmedi; nüsha durumları açık ödünçlerle tutarlı; waitress logunda hata yok. Bir üyesinin e-postası `ali@ornek.com` yapılmış kopyada betik "Tohum verisi olmayan veritabanı" ile çıkış 1 verdi. Commit `ac74da7`.

### Görev G19: Dağıtım dosyaları ve kullanıcı belgeleri

- **Gereksinimler:** FR-28 (geri yükleme adımı belgesi), NFR-04, NFR-05 (yeniden başlatma), NFR-06, NFR-08 (LAN, erişim logu yok), ADR-0005, ADR-0006, ADR-0010, ADR-0012, ADR-0029, ADR-0032 ("adı sor" adımı), ADR-0038 (demo sırası), ADR-0040 (kapalı tarih notu), ADR-0047 (rıza notu), ADR-0054 (koruma kopyası KVKK notu), ADR-0060…ADR-0066; KL-21, KL-27, KL-29; G19 küçük kararları 1–12 (§11).
- **Dosyalar:** oluştur `deploy/Caddyfile`, `deploy/winsw/library-app.xml`, `deploy/winsw/library-caddy.xml`, `deploy/systemd/library-app.service`, `deploy/systemd/library-caddy.service`, `deploy/library.env.example`, `docs/kurulum.md`, `docs/kullanim-kilavuzu.md`, `tests/test_deploy_files.py` (ADR-0066); değiştir `README.md` (küçük karar 11).
- **Davranış:**
  - **Caddyfile:**
    - Site adresi `{$LIBRARY_HOST}` ve `tls internal` ile tanımlanır. `LIBRARY_HOST` sunucunun sabit IP adresidir; `tls internal` IP sertifikası üretir ([ADR-0061](../decisions/0061-access-by-static-ip.md)).
    - `handle_path /static/*` bloğu `root * {$LIBRARY_STATIC_ROOT}` ve `file_server` kullanır.
    - Diğer yollar `reverse_proxy 127.0.0.1:8000` ile waitress'e gider.
    - `bind`, LAN arayüzünün adresidir (`{$LIBRARY_BIND}`).
    - `log` yönergesi yoktur; erişim logu tutulmaz ([ADR-0065](../decisions/0065-caddy-no-access-log.md)).
  - **Servisler:**
    - Uygulama servisinin komutu KL-5'tedir: `waitress-serve --listen=127.0.0.1:8000 --threads=8 library_site.wsgi:application`, `LIBRARY_SCHEDULER_ENABLED=1`. Ortam değişkenleri architecture §6.4'tedir; Caddy servisi `LIBRARY_HOST`, `LIBRARY_BIND` ve `LIBRARY_STATIC_ROOT`'u okur.
    - İki servis de ayrı bir yerel hesapla çalışır: Windows'ta `library-svc` (WinSW `<serviceaccount>`), Linux'ta `library` ([ADR-0062](../decisions/0062-service-account.md)). Veri klasörü, gizli değer dosyaları ve Caddy veri klasörü yalnız bu hesaba ve yöneticilere açılır.
    - Windows'ta WinSW 2.12.0: `onfailure restart` 10 sn, 3 deneme, `resetfailure` 1 gün; log `roll-by-size` 10 MB × 8 dosya; Caddy servisi `<depend>library-app</depend>`. Linux'ta systemd: `Restart=on-failure`, `RestartSec=5`, `NoNewPrivileges=yes`, `PrivateTmp=yes`, `ProtectSystem=strict`, `ReadWritePaths=` yalnız veri, yedek ve dışa aktarma klasörleri (Caddy'de kendi veri klasörü); Caddy unit'i `After=` ve `Wants=` ile uygulamaya bağlı ve `AmbientCapabilities=CAP_NET_BIND_SERVICE`; log journald (küçük kararlar 2–5).
    - Caddy sürümü 2.11.7'dir; indirme bağlantısı bu sürüme sabitlenir ([ADR-0063](../decisions/0063-tool-versions-winsw-caddy.md)).
  - **`deploy/library.env.example`:** §6.4 değişkenleri ile `LIBRARY_HOST` ve `LIBRARY_BIND`; her değişkenin üstünde bir Türkçe açıklama satırı, gizli değerler boş. WinSW `<env>` değerlerinde kuruma özgü ve gizli değerler `__DOLDUR__`'dur (küçük karar 8).
  - **`docs/kurulum.md`** ortak bir gövde ve eşit ayrıntıda Windows ve Linux bölümlerinden oluşur ([ADR-0060](../decisions/0060-install-doc-common-body-two-platforms.md)). architecture §8'deki 7 adımı içerir. Ayrıca şunları içerir:
    - Sürüm arşivinin üretilmesi (`git archive`), ilk kurulum ve güncelleme yordamı: servisi durdur → `backup_db` → zip'i aç → `pip install -r requirements.txt` → `migrate` → `collectstatic` → servisi başlat → kontrol ([ADR-0064](../decisions/0064-release-zip-and-update-procedure.md)).
    - Migration öncesinde elle `backup_db` çalıştırılması.
    - Yedekten geri yükleme yordamı: servisi durdur, `restore_backup`, servisi başlat ve sayımları kontrol et. AC-28'de bu yordamın süresi ölçülür.
    - Geri yüklemenin bıraktığı koruma kopyası (`<db>.pre-restore-…`, ADR-0054) saklama kuralı dışında kalan bir kişisel veri kopyasıdır; geri yükleme kontrol edildikten sonra elle silinmelidir (KVKK notu).
    - Sabit IP (DHCP rezervasyonu) ve masaüstü kısayolu, servis hesabı ve klasör izinleri, güvenlik duvarı (Windows'ta 80/443 Private profil ve `LocalSubnet`, Linux'ta LAN alt ağıyla sınırlı `ufw`; yönlendiricide dışarı port açılmaz).
    - USB rotasyonu, parolanın çevrimdışı saklanması, CA kök sertifikasının yüklenmesi (`certutil -addstore -f Root root.crt`, Firefox notu, kök sertifikanın Caddy veri klasöründeki yeri), NTP ayarı, SQLite dosyasının yerel diskte tutulması ve yedek ve dışa aktarma klasörlerinin elle açılması.
  - **`docs/kullanim-kilavuzu.md`**, yalnız metin olarak masa işlerini adım adım anlatır: giriş, ödünç ("üyeye adını sor" adımı), iade, uzatma, üye kaydı ve rıza, ödeme, kayıp ve hasar, etiket ve kart basımı. Yönetici bölümü kapalı günleri, ayarları, yedek ve dışa aktarma uyarılarını anlatır. Ayrıca şu notları içerir: geçmiş kapalı tarihler silinmez (ADR-0040); geçmiş tarihli rıza olayı geçerli durumu değiştirmez (ADR-0047).
  - **`README.md`:** "Veri kaynakları" ve "Demo verisi" korunur (TC-352); "Geliştirme ortamı", "Testler" ve "Belgeler" (kurulum ve kılavuz bağlantıları) eklenir; girişteki "G19'da eklenecek" cümlesi kaldırılır.
- **Testler:** Elle: TC-225…TC-234, TC-319 (11 TC, faz 6). Otomatik ([ADR-0066](../decisions/0066-deploy-files-consistency-tests.md)): TC-359…TC-366 (`tests/test_deploy_files.py`).
- **Doğrulama:** `python -m pytest tests/test_deploy_files.py -q` ve `python -m pytest -q` → hepsi geçer. Bulutta Caddy ikilisi indirilebilirse `caddy validate` ve `caddy adapt` çalıştırılır; indirilemezse not edilir. Yerel Windows doğrulamasında taşınabilir Caddy ikilisiyle `caddy validate` ve geçici portlarda waitress + Caddy ile `/static/css/app.css` → 200, `/admin/` → 404 kontrol edilir; servis kaydı yapılmaz. Faz 6'da test ortamına kurulum yapılır ve şunlar kontrol edilir:
  - `curl -k https://<host>/static/css/app.css` → 200.
  - `/admin/` → 404.
  - LAN dışından erişim olmamalı.
  - AC-28 geri yükleme süresi < 1 saat olmalı.
  - Kanıt (2026-11-01, bulut oturumu, Linux, Python 3.11.18): TDD: `tests/test_deploy_files.py` önce yazıldı; dosyalar yokken 19 failed, 1 passed (TC-359 mevcut ayarlarla zaten tutarlı olduğu için geçti; koruma testidir). Ardından `python -m pytest tests/test_deploy_files.py -q` → 20 passed; `python -m pytest -q` → 1042 passed (önceki 1022); `python -m pytest -m slow -q` → 7 passed; `makemigrations --check --dry-run` → "No changes detected"; dal kapsamı `*/domain.py` %100 (`--fail-under=90` çıkış 0), `accounts/permissions.py` ve `accounts/middleware.py` %100 (`--fail-under=100` çıkış 0), `billing/services.py` ve `circulation/services.py` %99 (`--fail-under=85` çıkış 0), `operations` %99 (`--fail-under=80` çıkış 0), proje %97. Caddy 2.11.7 Linux ikilisi GitHub sürüm sayfasından indirildi (SHA-512 `checksums.txt` ile aynı): `caddy validate --config deploy/Caddyfile --adapter caddyfile` → "Valid configuration"; `caddy fmt` farksız; `caddy adapt` → tek sunucu, `listen` yalnız `<LIBRARY_BIND>:443`, `tls` politikası `internal`. Canlı deneme (scratchpad, prod ayarları, geçici veritabanı, `LIBRARY_HOST`=`LIBRARY_BIND`=`127.0.0.2`): `waitress-serve --listen=127.0.0.1:8000 --threads=8 library_site.wsgi:application` ve `caddy run` ile `https://127.0.0.2/static/css/app.css` → 200, `/admin/` → 404, `/giris/` → 200, `http://127.0.0.2/giris/` → 308 HTTPS'e; dinlenen adresler `127.0.0.2:80`, `127.0.0.2:443`, `127.0.0.1:8000` ve Caddy yönetim ucu `127.0.0.1:2019`; sertifikanın SAN'ı `IP Address:127.0.0.2`, Caddy'nin ürettiği `root.crt` ile `curl --cacert` doğrulaması 200; `/uyeler/?q=…` isteğinden sonra Caddy logunda istek satırı yok (ADR-0065). `systemd-analyze verify` iki unit için yalnız sunucuda bulunmayan ikilileri (`/opt/library/venv/bin/waitress-serve`, `/usr/local/bin/caddy`) bildirdi, sözdizimi hatası yok. `library.env.example` `set -a; . …` ile kabukta yüklendi (16 değişken). WinSW 2.12.0 indirme bağlantısı 200 döndü; XML'ler ayrıştırıldı, WinSW Windows'ta çalıştırılmadı (yerel doğrulamada da servis kaydı yapılmaz, faz 6). Elle TC'ler (TC-225…TC-234, TC-319) faz 6'dadır.
  - Kanıt (2026-11-01, yerel Windows 11, Python 3.11.9): `coverage run --branch -m pytest -q` → 1042 passed; `-m slow` → 7 passed; `makemigrations --check --dry-run` → "No changes detected"; dört kapsam eşiği çıkış 0 (`*/domain.py` %100, izinler %100, servisler %99, `operations` %99), proje %97. Caddy 2.11.7 Windows arşivinin SHA-512'si `checksums.txt` ve ADR-0063'teki değerle aynı; `caddy validate` → "Valid configuration"; repodaki (LF) Caddyfile `caddy fmt` ile farksız (çalışma kopyası `core.autocrlf` yüzünden CRLF, `validate` onunla da geçer). Prod ayarları, geçici veritabanı, `LIBRARY_HOST`=`LIBRARY_BIND`=`127.0.0.2`, waitress + Caddy: `/static/css/app.css` → 200, `/admin/` → 404, `/giris/` → 200, `http://…/giris/` → 308; sertifika SAN `IP Address 127.0.0.2`, `root.crt` ile doğrulandı; dinlenen adresler `127.0.0.2:80`, `127.0.0.2:443`, `127.0.0.1:8000`, `127.0.0.1:2019`; `/uyeler/?q=…` isteği Caddy loguna düşmedi. Not: Git for Windows `curl`'ü (Schannel) yerel CA'da iptal kontrolü yapamadığı için `--cacert` ile 000 döner; `--ssl-no-revoke` ya da `-k` gerekir (kurulum belgesindeki kontrol `-k` kullanıyor). Servis kaydı yapılmadı.
- [x] Tamamlandı

## 5. Testler

Test planı: [docs/test-plan.md](../test-plan.md). 366 TC (TC-01…TC-366; TC-320…TC-339 G14–G16, TC-340…TC-356 G17–G18 açılış kararlarıyla, TC-357…TC-358 ADR-0059 ile, TC-359…TC-366 G19 açılış kararlarıyla 2026-11-01'de eklendi); seviyeler, teknikler, kapsam hedefleri, ortam ve giriş-çıkış ölçütleri orada. Her görevin TC listesi görevin **Testler** satırındadır. Elle TC'ler (TC-223, TC-225…TC-234, TC-319) faz 6'da yapılır.

## 6. Riskler

Riskler [docs/risk-register.md](../risk-register.md) dosyasına taşındı (2026-10-31). R-01 ve R-06 kapandı, R-07…R-14 eklendi. En önemli açık riskler: R-04 (bina olayı), R-10 (saat dilimi verisi), R-13 (çalışan uygulamaya geri yükleme), R-02 ve R-11 (e-posta). R-15 ve R-16 bulut oturumu kararıyla eklendi (ADR-0048).

## 7. İzlenebilirlik

Kapsam içindeki 35 FR ve 13 NFR'nin her biri bir tasarım öğesine, göreve ve teste bağlı. Test sütunu `docs/test-plan.md` §6'nın "Gereksinim" sütunundan üretildi (AC'ler FR'lerine eşlendi). Her görev en az bir gereksinime hizmet ediyor; TC-02, TC-236 ve TC-359…TC-362 architecture §6.4'e bağlı.

| Gereksinim | Tasarım öğesi | Görev | Test |
|---|---|---|---|
| FR-01 | `members`: `create_member`, `update_member`, `search_members`; `member` tablosu | G06, G17 | TC-35, TC-44…TC-52, TC-261, TC-342 |
| FR-02 | `circulation.services.deactivate_member`, `members.services.set_inactive`, `Blocker.MEMBER_INACTIVE` | G06, G10, G11 | TC-53…TC-56, TC-115, TC-126, TC-286 |
| FR-03 | `consent_event`, `set_consent`, `update_member` (ADR-0022, ADR-0047); S6 rıza koşulu; `docs/kullanim-kilavuzu.md` rıza notu | G06, G13, G17, G19 | TC-57…TC-59, TC-177, TC-254…TC-258, TC-319, TC-351, TC-365 |
| FR-04 | `catalog.domain`: `parse_isbn`, `normalize_tr`; `create_book`, `search_books`; `book` tablosu | G05, G07 | TC-35, TC-37…TC-43, TC-60…TC-63, TC-66…TC-68, TC-253, TC-264 |
| FR-05 | `copy` tablosu, `add_copies`, `COPY_TRANSITIONS`, `check_transition` | G07, G10, G12 | TC-64…TC-65, TC-71, TC-163…TC-169, TC-262…TC-263 |
| FR-06 | `pdf.sheets.render_sheet`, `LABEL_LAYOUT`, `label_pdf`, `copies_for_labels` (ADR-0036) | G08 | TC-69…TC-72, TC-228, TC-265…TC-267, TC-269 |
| FR-07 | `circulation.domain.due_date`, `closed_day_predicate`, `check_out` | G03, G10, G11, G17 | TC-104…TC-105, TC-107…TC-109, TC-124, TC-133, TC-140, TC-347 |
| FR-08 | `checkout_blockers`, `check_out`, `loan` kısmi benzersiz indeksi | G10, G11 | TC-114, TC-116…TC-119, TC-124…TC-127, TC-145…TC-146, TC-149, TC-280, TC-284 |
| FR-09 | `check_in`, iade ekranı | G11 | TC-111, TC-134…TC-135, TC-138, TC-147, TC-283 |
| FR-10 | `renew_blockers`, `renewed_due_date`, `renew` | G10, G11 | TC-120…TC-123, TC-139…TC-144, TC-148, TC-280, TC-288 |
| FR-11 | Ödünç ve iade ekranları, `scan.js`, `classify_member_input` (ADR-0046); kılavuzdaki "üyeye adını sor" adımı (ADR-0032) | G10, G11, G19 | TC-128…TC-130, TC-227, TC-279, TC-281…TC-282, TC-319, TC-365 |
| FR-12 | `late_days` (ADR-0040), `fine`, `loan` oran kopyası (ADR-0023); kılavuzdaki kapalı tarih notu | G10, G11, G12, G17, G19 | TC-13, TC-110…TC-113, TC-132, TC-134, TC-136…TC-137, TC-152, TC-246, TC-276…TC-278, TC-283, TC-319, TC-347, TC-365 |
| FR-13 | `allocate_fifo`, `record_payment`, `allocation` tablosu (ADR-0017) | G09, G17 | TC-78…TC-85, TC-100, TC-103, TC-290, TC-345 |
| FR-14 | `waive` (ADR-0021) | G09 | TC-86…TC-90 |
| FR-15 | `mark_lost`, `mark_damaged`, `post_charge` | G12 | TC-150…TC-152, TC-162, TC-289…TC-290, TC-293 |
| FR-16 | `mark_found`, `repair`, `withdraw`, `cancel_unpaid`, `refund`, `cancel_fee_manual`, `loan.copy_found_on` (ADR-0037, ADR-0041) | G09, G12 | TC-92…TC-97, TC-153…TC-158, TC-162, TC-168…TC-169, TC-270…TC-275, TC-291…TC-292 |
| FR-17 | `balance`, `member_balance` (S3), `statement`, döküm ekranı | G09, G17 | TC-76…TC-77, TC-98…TC-99, TC-101, TC-344 |
| FR-18 | `due_reminder_kind`, `send_due_reminders`, `reminder_log` (ADR-0039), `send_reminders` | G13, G16 | TC-173…TC-176, TC-178, TC-180…TC-182, TC-185, TC-208, TC-232, TC-294…TC-296 |
| FR-19 | `send_manual_reminders`, `/gecikenler/hatirlat/` | G13 | TC-183…TC-184, TC-297…TC-298 |
| FR-20 | `overdue_loans` (S5), `/gecikenler/` | G11, G13 | TC-171…TC-172, TC-287, TC-298 |
| FR-21 | `accounts.services`: `create_staff`, `set_role`, `deactivate_staff`, `reset_password`, `unlock_staff` | G02, G04 | TC-12, TC-27…TC-29, TC-237, TC-252 |
| FR-22 | `require_role`, `staff_view`, `tests/test_authorization.py` | G02, G03, G04, G15 | TC-01, TC-11, TC-21, TC-31, TC-275, TC-308, TC-334 |
| FR-23 | `LibrarySettings`, `update_settings`, ayar ekranı | G03, G08, G11 | TC-18…TC-20, TC-73, TC-131 |
| FR-24 | `WeeklyClosedDay`, `ClosedDate`, `validate_weekly_closed` (ADR-0028) | G03, G10 | TC-22…TC-24, TC-106, TC-246 |
| FR-25 | `anonymize_expired`, `add_years`, `deferred_members`, `Member.display_name` (ADR-0018, ADR-0045, ADR-0055) | G15, G16, G17 | TC-201…TC-208, TC-305…TC-309, TC-330…TC-334, TC-346 |
| FR-26 | `audit.record_audit`, `AuditEvent`, `/denetim/` | G03, G04, G06, G09, G12 | TC-18, TC-22, TC-26…TC-27, TC-91, TC-93, TC-157…TC-158, TC-170, TC-247, TC-259, TC-273 |
| FR-27 | Django `LoginView`, django-axes, oturum ayarları (ADR-0009) | G02 | TC-04…TC-10, TC-12, TC-30, TC-237 |
| FR-28 | `backup_db`, `restore_backup` (koruma kopyası, ADR-0054), `applock`; `docs/kurulum.md` (güncelleme ve geri yükleme yordamı, ADR-0064) | G14, G16, G19 | TC-186…TC-191, TC-199…TC-200, TC-208, TC-225, TC-301…TC-302, TC-320…TC-323, TC-325…TC-329, TC-366 |
| FR-29 | `fetch_demo_books`, `filter_records`, `operations.seed`, `load_seed_data`, `README.md` (ADR-0033, ADR-0038, ADR-0056, ADR-0057, ADR-0059) | G17, G19 | TC-214…TC-219, TC-234, TC-315…TC-316, TC-340…TC-345, TC-347…TC-352, TC-357…TC-358, TC-365 |
| FR-37 | `libx`, `export_backup`, `export_age_warning` (ADR-0006, ADR-0011) | G03, G14, G16 | TC-25, TC-192…TC-198, TC-208, TC-226, TC-244…TC-245, TC-299…TC-300, TC-303…TC-304, TC-310, TC-323…TC-326, TC-328…TC-329 |
| FR-38 | `CARD_LAYOUT`, `member_card_pdf`, `members_for_cards` (ADR-0032, ADR-0036) | G08 | TC-69, TC-74…TC-75, TC-228, TC-266, TC-268…TC-269 |
| FR-39 | `mark_shelf_copy`, `withdraw` (ADR-0026) | G12 | TC-159…TC-161, TC-293 |
| FR-40 | `reactivate_member` (ADR-0042) | G06, G11 | TC-259…TC-260, TC-285 |
| FR-41 | `change_own_password`, `ForcePasswordChangeMiddleware`, `must_change_password` (ADR-0043) | G02, G04 | TC-248…TC-251 |
| FR-42 | `backup_warning`, `jobs.last_finished`, `last_success_at` (ADR-0044) | G03 | TC-241…TC-243, TC-245 |
| NFR-01 | data-design §4 indeksleri, `scripts/loadtest.py` (ADR-0031, ADR-0058) | G18 | TC-221…TC-223, TC-318, TC-353…TC-356 |
| NFR-02 | `load_seed_data --profile load` | G17, G18 | TC-220, TC-223, TC-317, TC-346 |
| NFR-03 | BACKUP 02:00, `backup_db`, telafi (saatlik, ADR-0053) | G14, G16, G19 | TC-190, TC-233, TC-336 |
| NFR-04 | `restore_backup` (ADR-0054), `docs/kurulum.md` (ADR-0060, ADR-0064) | G14, G19 | TC-225, TC-320, TC-366 |
| NFR-05 | `jobs_due_for_catch_up`, `catch_up` (saatlik, ADR-0053), `run_command`, tek işçili zamanlayıcı, `run_job`, `reminder_log` tekrar engeli; servislerin yeniden başlatılması (WinSW `onfailure`, systemd `Restart=on-failure`) | G03, G13, G16, G19 | TC-178…TC-179, TC-209…TC-213, TC-233, TC-310…TC-314, TC-335…TC-339, TC-361, TC-362, TC-364 |
| NFR-06 | `Argon2PasswordHasher`, Caddy `tls internal` (ADR-0005, ADR-0061) | G01, G19 | TC-03, TC-230, TC-363 |
| NFR-07 | `require_role`, `tests/test_authorization.py` | G04 | TC-11, TC-31…TC-33 |
| NFR-08 | `member` alanları, anonimleştirme, `reminder_log.error` temizliği (ADR-0055), `Member.display_name`, Caddy LAN bağlaması, Caddy erişim logu yok (ADR-0065), servis hesabı (ADR-0062) | G06, G15, G17, G19 | TC-52, TC-206, TC-229…TC-230, TC-330…TC-331, TC-342, TC-359…TC-364 |
| NFR-09 | `LANGUAGE_CODE = "tr"`, `TIME_ZONE`, `templates/base.html` | G01, G19 | TC-231, TC-235 |
| NFR-10 | `normalize_tr`, `search_key` (ADR-0019) | G05, G06, G07 | TC-34, TC-36, TC-47, TC-67 |
| NFR-11 | Ödünç ekranı odak akışı, `scan.js` | G11, G19 | TC-128, TC-227 |
| NFR-12 | `administration.money`, tam sayı kuruş (ADR-0016) | G03, G09 | TC-14…TC-17, TC-102, TC-238…TC-240 |
| NFR-13 | `*/domain.py`, `coverage report --fail-under=90` | G01 (her görev), G09, G10 | TC-224 |

## 8. Tutarlılık kontrolü

Geçişler: kapsam, belirsizlik, eksik belirtim, çelişki, terim kayması, sıralama. "KL onayıyla" işaretli düzeltmeler plana yazıldı ve onay kapısındaki KL onayıyla kesinleşir.

| ID | Geçiş | Önem | Bulgu | Düzeltme | Durum |
|---|---|---|---|---|---|
| T-01 | Sıralama | Yüksek | G09'daki `LedgerEntry.loan`, G11'de oluşturulan `circulation.Loan`'a yabancı anahtar veriyordu; billing migration'ı henüz olmayan bir migration'a bağımlıydı | `Loan` modeli ve migration'ı G10'a alındı; sıra G10 → G09 → G11 (KL-39) | Düzeltildi (KL onayıyla) |
| T-02 | Çelişki | Orta | data-design I6 "hareketler güncellenmez" diyor; ADR-0018 ve G15 saklama sonunda `ledger_entry.loan_id`'yi NULL yapıyor | I6'ya ADR-0018 istisnası yazıldı; TC-101 ve TC-202 buna göre | Düzeltildi |
| T-03 | Terim | Düşük | architecture §3 bileşen tablosu `deactivate_member`'ı members'ta gösteriyordu | KL-22'ye göre circulation'a taşındı | Düzeltildi (önceki oturum) |
| T-04 | Kapsam | Düşük | G06 "AC-03 (1., 3. ve 4. senaryo)" diyordu; AC-03'te üç senaryo var | "AC-03 (bütün senaryolar; 1. senaryonun hatırlatma koşulu G13'te)" | Düzeltildi |
| T-05 | Sıralama | Düşük | Taslakta pasifleştirme TC'leri (TC-53…TC-56) G06'daydı; kural G11'de (KL-22) | TC'ler G11'e taşındı ve `deactivate_member` mesajlarıyla yeniden yazıldı | Düzeltildi |
| T-06 | Çelişki | Orta | TC-48 tireli telefonla aramayı bekliyordu; KL-10 yalnız rakamlı sorguyu telefon sayıyordu. Ödünç ekranı (KL-35) bu karakterleri temizliyor, üye araması temizlemiyordu | KL-10 genişletildi: boşluk, `-`, `(`, `)` atılarak sınıflandırılır (TC-261) | Düzeltildi (KL onayıyla) |
| T-07 | Eksik belirtim | Düşük | KL-3 "15.00" gibi binlik ayırıcı karışıklığını tanımlamıyordu | KL-3: nokta yalnız üç haneli gruplarda (TC-240) | Düzeltildi (KL onayıyla) |
| T-08 | Eksik belirtim | Düşük | KL-8 kendini pasifleştirme reddinin mesajını vermiyordu | "Kendi hesabınızı pasifleştiremezsiniz" (TC-252) | Düzeltildi (KL onayıyla) |
| T-09 | Eksik belirtim | Düşük | `mark_lost` FINE ve FEE'nin yazım sırasını belirtmiyordu; FIFO sonucu buna bağlı | KL-44 (TC-290) | Düzeltildi (KL onayıyla) |
| T-10 | Eksik belirtim | Düşük | architecture §6.4 hangi değişkenlerin zorunlu olduğunu söylemiyordu | KL-43 (TC-02, TC-236) | Düzeltildi (KL onayıyla) |
| T-11 | Eksik belirtim | Düşük | ISBN-10'da küçük "x" tanımsızdı | KL-40 (TC-253) | Düzeltildi (KL onayıyla) |
| T-12 | Eksik belirtim | Düşük | `restore_backup`'a verilen dosya yoksa çıkış kodu tanımsızdı | KL-41 (TC-301) | Düzeltildi (KL onayıyla) |
| T-13 | Eksik belirtim | Düşük | 99.999.999'dan büyük nüsha id'si için davranış tanımsızdı | KL-42 (TC-263) | Düzeltildi (KL onayıyla) |
| T-14 | Eksik belirtim | Düşük | Pasifleştirilen personelin açık oturumuna ne olacağı yazılı değildi | KL-45 (TC-237) | Düzeltildi (KL onayıyla) |
| T-15 | Kapsam | Orta | R-10'un önlemi olan Europe/Istanbul `localdate` testi G01'de yoktu (TC-13 G03'te `clock.today()`'i test ediyor) | TC-235 G01'e eklendi | Düzeltildi |
| T-16 | Kapsam | Düşük | Test planı yokken §4'teki 19 görevde test listesi boştu | `docs/test-plan.md` yazıldı; görevlere TC listeleri işlendi; 48 gereksinimin ve 35 AC'nin hepsinin TC'si var (§7) | Düzeltildi |
| T-17 | Eksik belirtim | Orta | architecture `due_date` için üst sınır vermiyordu | O(366) sınırı yazıldı (ADR-0028) | Düzeltildi (önceki oturum) |
| T-18 | Çelişki | Orta | architecture'daki domain imzaları ADR-0028 ile uyuşmuyordu | İmzalar ADR-0028'e uyduruldu | Düzeltildi (önceki oturum) |
| T-19 | Eksik belirtim | Orta | `mark_shelf_copy`, `deactivate_member` ve `check_transition` architecture'da yoktu | Eklendi | Düzeltildi (önceki oturum) |
| T-20 | Sıralama | Orta | `notifications → administration` bağımlılığı çizilmemişti | Ok çizildi | Düzeltildi (önceki oturum) |
| T-21 | Eksik belirtim | Düşük | accounts ↔ administration modül düzeyi ilişkisi ve `pdf/` paketi açıklanmamıştı | Açıklama ve not eklendi | Düzeltildi (önceki oturum) |
| T-22 | Çelişki | Orta | architecture §6.2 `load_seed_data [--books N] [--members N]` diyordu; plan `--profile` kullanıyordu | §6.2 `--profile demo\|load --actor` olarak düzeltildi (ADR-0038) | Düzeltildi (önceki oturum) |
| T-23 | Belirsizlik | Düşük | architecture §10'da açık sorular kalmıştı | Kapatıldı | Düzeltildi (önceki oturum) |
| T-24 | Terim | Düşük | data-design denetim eylem listesi eksikti; para için "iade" terimi kullanılıyordu | Liste tamamlandı; "para iadesi" terimi her yere yazıldı (ADR-0027) | Düzeltildi (önceki oturum) |

### 8.2 Test tasarımı taslağının açık soruları (2026-10-31)

Taslaktaki 27 sorunun her biri bir karara bağlandı; ilgili TC'ler buna göre yazıldı.

| Soru | Konu | Karar | TC |
|---|---|---|---|
| 1 | Yedek saklamada −30. gün; desene uymayan dosyalar | KL-14: `run_on − 30`'dan eskiler silinir, −30 kalır; desene uymayana dokunulmaz | TC-187 |
| 2 | I5 ile tamamen ödenmiş bedel | ADR-0037 | TC-155, TC-272 |
| 3 | I6 ile anonimleştirme | T-02 | TC-101, TC-202 |
| 4 | Haftalık EXPORT telafisi | G16 haftalık koşulu | TC-310 |
| 5 | Kısmi SMTP hatasında `job_run` | KL-23 | TC-180, TC-295, TC-312 |
| 6 | `load_seed_data` arayüzü; dolu veritabanı | ADR-0038, G17 ("Veritabanı boş değil", çıkış 1) | TC-217, TC-315 |
| 7 | 366 gün sınırının kapsamı | G10: `aday + 0…366` kontrol edilir | TC-109 |
| 8 | Birden çok ödünç engeli | KL-6 | TC-280, TC-284 |
| 9 | Gecikmiş ödünç uzatma mesajı | KL-6: "Ödünç gecikmiş" | TC-122, TC-143 |
| 10 | Kayıp/hasarda denetim kayıtları | KL-15 ve G09 `post_charge`: FEE kaydı ve `fee_kurus` taşıyan COPY_* kaydı | TC-150, TC-151 |
| 11 | FINE ile FEE'nin sırası | KL-44 | TC-290 |
| 12 | Sıfır bedel | KL-7 | TC-289 |
| 13 | Dışa aktarma yaşının kaynağı | KL-14 | TC-25, TC-244 |
| 14 | 29 Şubat ve saklama | G15 `add_years` | TC-307 |
| 15 | Uzatılan ödüncün hatırlatması | ADR-0039 | TC-182, TC-294 |
| 16 | TL giriş ve gösterim biçimleri | KL-3 | TC-238…TC-240 |
| 17 | Anonim üyenin `search_key`'i | G15: boş metin | TC-201, TC-206 |
| 18 | Rıza tarihi ve e-posta | ADR-0047, KL-12, G06 | TC-254…TC-258 |
| 19 | Son yönetici; pasif personelin oturumu | KL-8, KL-45 | TC-237, TC-252 |
| 20 | Zorunlu ortam değişkenleri | KL-43 | TC-02, TC-236 |
| 21 | Boş seçimle PDF | G08 ("En az bir nüsha seçin") | TC-267, TC-268 |
| 22 | Kart barkodunun değeri | G08: doldurmasız `str(member_no)`; ADR-0046 ile çakışmaz | TC-74, TC-279 |
| 23 | ISBN ile arama | KL-10: geçerli ISBN `parse_isbn` ile normalize edilir | TC-264 |
| 24 | ISBN-10'da küçük "x" | KL-40 | TC-253 |
| 25 | `restore_backup` kilidi; olmayan dosya | KL-4, KL-41 | TC-199, TC-301, TC-302 |
| 26 | Barkod taşması | KL-42 | TC-263 |
| 27 | p95 yöntemi | G18: en yakın sıra | TC-222 |

### 8.1 İnşa kontrolü bulguları (2026-10-31; ayıklandı)

Taze bir general-purpose subagent planı okudu ve şu 13 soruyu önem sırasıyla bildirdi. Bunların test işaretleri ve ADR-0036 dışında kaldığı belirtildi. Önerilen ayıklama parantez içinde; kesin karar sonraki oturumda verilir.

1. **Tamamı ödenmiş kayıp bedeli, nüsha bulununca iade edilebilir mi?** I5 (data-design §2.5), REFUND için önce CANCELLATION almış olmayı şart koşuyor. Bedel tamamen ödenmişse `cancel_unpaid` hiçbir şey yazmıyor, bu yüzden para iadesi engelleniyor. Oysa G12 personeli para iadesine yönlendiriyor. Ön koşul yeniden tanımlanmalı: "kalemin ödüncü LOST ile kapandı ve nüsha bulundu". (Kullanıcı; I5'teki çelişki Yüksek.)
2. **Tohum veride kayıtların sahibi hangi personel?** G17 personel hesabı oluşturmuyor. Ama `loan.created_by`, `ledger_entry.created_by` ve `consent_event.recorded_by` alanları NOT NULL. Seçenekler: `--actor` argümanı, pasif bir tohum kullanıcısı ya da nullable alan. (Kullanıcı.)
3. **Uzatılan ödünç, yeni son tarihi için yeniden DUE_SOON alsın mı?** Mevcut benzersiz kısıt yüzünden almıyor. Almasını sağlamak `reminder_log`'a `due_on` alanı eklemek demek. (Kullanıcı; veri modeli.)
4. **Açık bir ödüncün son tarihine kapalı tarih eklenirse ne olur?** Seçenekler: son tarih kaydırılır, gecikme günü sayımı kapalı günleri atlar ya da ceza aynen işler. (Kullanıcı.)
5. **Saklama nedeniyle bağı koparılmış kayıp ödüncün bedeli, nüsha bulununca nasıl iptal edilir?** Elle iptal ekranı ya da af. Af yolunda sonradan para iadesi I5'e göre imkânsız olur. (Kullanıcı.)
6. **Pasif üyeyi yeniden aktifleştirmek kapsamda mı?** (Kullanıcı; kapsam.)
7. **Personel kendi parolasını değiştirebilir mi? Yöneticinin sıfırladığı parola ilk girişte değiştirilmek zorunda mı?** (Kullanıcı; kapsam ve şema.)
8. **Başarısız ya da eskimiş günlük yedek, dışa aktarma gibi ana sayfada uyarı versin mi?** (Kullanıcı; görünür davranış.)
9. **E-postaların bir kısmı başarısız olursa `job_run` SUCCESS mı yazılır, FAILED mı?** Bu, telafi davranışını ve çıkış kodunu belirler. (KL: önerim SUCCESS, detail alanında failed sayısı, çıkış kodu 1; pencere içinde ertesi çalışma yeniden dener.)
10. **Saklama süresi dolduğunda borcu olan üye de anonimleştirilir mi?** (Kullanıcı; KVKK, SRS açık soru 6 ile bağlantılı.)
11. **Dışa aktarma klasöründe kaç `.libx` dosyası tutulur?** (KL: önerim son 8 hafta.)
12. **Ödünç ekranında üye alanına girilen rakam nasıl yorumlanır?** Nüsha barkodu (8 hane, baştaki sıfırlarla) üye alanına okutulursa 42 numaralı üye açılır; telefon numarası girilirse "Üye bulunamadı" çıkar. (Kullanıcı; masa davranışı, FR-11.)
13. **Rıza olaylarının sıra kuralı ne?** Son olay `effective_on` mı, `recorded_at` mı? Geriye tarihli ve tekrarlayan olaylar kabul edilir mi? E-posta silinince rıza geri alınmış sayılır mı? (Kısmen KL, kısmen kullanıcı; KVKK izi.)

**Ayıklama (2026-10-31):** 1 → ADR-0037; 2 → ADR-0038; 3 → ADR-0039; 4 → ADR-0040; 5 → ADR-0041; 6 → ADR-0042; 7 → ADR-0043; 8 → ADR-0044; 9 → KL-23; 10 → ADR-0045; 11 → KL-24; 12 → ADR-0046; 13 → ADR-0047.

Alt başlık olarak bildirilip uygulayıcıya bırakılanlar: `/nushalar/etiket/` URL sırası, id oluşmadan önceki geçici barkod, uzatmada süre olarak mevcut ayarın kullanılması, personelin `full_name` eşlemesi, geri yüklemede parola dosyası yedeği.

## 9. Önerilen commit noktaları

- Kök commit (`main`): `chore: set up project docs skeleton`. Onaylandı 2026-10-31; AGENTS.md'deki dal kuralına tek istisna.
- `feature/requirements`: `docs: add approved SRS and phase 1 plan updates`.
- `feature/requirements`: `docs: add phase 2 research reports` (onaylandı ve commit'lendi 2026-10-31).
- `feature/requirements`: `docs: add phase 3 ADRs, architecture and data design` (onaylandı ve commit'lendi 2026-10-31). SRS, plan ve STATUS'taki faz 2 ve faz 3 değişiklikleri de bu commit'te.
- `feature/requirements`: `docs: add phase 4 decisions and SRS updates` (onaylandı ve commit'lendi 2026-10-31, `8c06c2b`).
- `feature/requirements`: `docs: add phase 4 plan, test plan and risk register` (onaylandı 2026-10-31). Ardından `feature/requirements` → `main` birleştirmesi `--no-ff` merge commit'iyle yapılır (onaylandı 2026-10-31).
- Faz 5: Her görevin sonunda bir commit; görev grupları ve dallar §4.0'da.

## 10. Onay

- **2026-10-31, kullanıcı:** Plan (19 görev, sıra G10 → G09 → G11), `docs/test-plan.md` (319 TC), izlenebilirlik (§7), tutarlılık bulguları (§8) ve KL-1…KL-46 onaylandı. Uygulama seçeneği: temiz oturumda uygula. Test tasarımı taslağı kullanıcı kararıyla silindi.
- KL onayıyla architecture §3'e işlenenler: `job_run` `administration`'da (KL-1), `members → catalog` oku (KL-2), "view'lar yapraktır" kuralı (KL-22). `operations → billing` oku (KL-34) önceden çizilmişti.
- Sıradaki: faz 4 dokümanlarının commit'i (§9), özel GitHub reposu ve push (ADR-0048); her biri ayrıca onayla.

## 11. Sapmalar

- **2026-10-31, commit bölümü:** Faz 2 commit'i yalnız iki araştırma raporunu içeriyor; mesajındaki "and SRS updates" kısmı çıkarıldı. Sebebi, SRS, plan ve STATUS'taki faz 2 ve faz 3 değişikliklerinin aynı satırlarda iç içe olması. Bunları ayırmak, hiç var olmamış bir ara sürümü geçmişe yazmak demekti. Bu yüzden üç dosya faz 3 commit'ine alındı.
- **2026-10-31, G01 — `AUTH_USER_MODEL` G02'de:** G01 `base.py`'de `AUTH_USER_MODEL = "accounts.StaffUser"` istiyor, ama `accounts` app'i G02'de oluşuyor; kurulu olmayan modele işaret eden ayarla Django açılmıyor. Ayar G02'de, modelle aynı commit'te eklenir. G01'deki TC-03 `get_user_model()` ile yazıldı; G02'den sonra `StaffUser` üzerinde de geçmelidir. Son durum plandakiyle aynı olur.
- **2026-10-31, G01 — ortam değişkenlerinin yeri:** `base.py`, bütün ortamların ihtiyaç duyduğu değişkenleri `env()` ile okur: `LIBRARY_SECRET_KEY`, `LIBRARY_DB_PATH`, `LIBRARY_BACKUP_DIR`, `LIBRARY_EXPORT_DIR`, `LIBRARY_EXPORT_PASSPHRASE_FILE`, `LIBRARY_SCHEDULER_ENABLED` (varsayılan "0"). `prod.py` geri kalanları okur (`LIBRARY_ALLOWED_HOSTS`, `LIBRARY_STATIC_ROOT`, `LIBRARY_EMAIL_*`). `dev.py` ve `test.py`, `base`'i import etmeden önce bu değişkenlere `os.environ.setdefault` ile varsayılan verir ("varsayılan değerlerle env"); geliştirme verisi depoda yok sayılan `var/` klasörüne yazılır. `LIBRARY_ALLOWED_HOSTS` virgülle ayrılmış listedir. `LIBRARY_EMAIL_PORT` tam sayı değilse "Geçersiz ortam değişkeni: …" ile `ImproperlyConfigured` verilir.
- **2026-10-31, G01 — `.gitignore`:** Plandaki `*.sqlite3` ve `staticfiles/` satırlarına ek olarak `*.sqlite3-wal`, `*.sqlite3-shm` (WAL dosyaları), `var/`, `__pycache__/`, `.pytest_cache/` ve `.coverage` eklendi; derleme ve test artıkları depoya girmesin diye.
- **2026-10-31, G01 — varsayılan ayar modülleri:** `manage.py` varsayılan olarak `library_site.settings.dev`, `wsgi.py` ise `library_site.settings.prod` kullanır (waitress yalnız üretimde çalışır); ikisi de `DJANGO_SETTINGS_MODULE` verilmişse ona uyar.
- **2026-10-31, G01 — çalışma ortamı:** G01 bulutta değil, kullanıcının yerel Windows 11 makinesinde Python 3.11.9 sanal ortamıyla uygulandı. Windows'a özgü TC-235 (tzdata) doğrudan Windows'ta koştu. pytest'in varsayılan geçici klasörüne erişim kum havuzunda engellendiği için testler `PYTEST_DEBUG_TEMPROOT` yalnız kabukta ayarlanarak koşturuldu; depoya bir şey eklenmedi.
- **2026-10-31, faz 5 — bulut oturumu açma yolu (KL-38):** Agent aracının `isolation: "remote"` modu bulut oturumu açmadı; yerel bir worktree'de (`.claude/worktrees/agent-a4c3b8e184eb5859a`) çalıştı ve kullanıcının 5 saatlik plan kullanımından harcadı. G01 bu yüzden yerelde yapıldı. Kullanıcı kararı: bulut oturumlarını kullanıcı kendisi açar (`claude --cloud` ya da claude.ai/code), Claude açılış istemini hazırlar. KL-38 buna göre düzeltildi. G02–G04 bulut oturumunda yapılacak.
- **2026-10-31, G02 — uygulamadan önce verilen kararlar:** Yerel agent'ın G02 hazırlığında bulduğu açık noktalar kullanıcıya soruldu (bulut oturumu soru soramaz).
  - Kritik: ADR-0049 (kilitli hesaba 429, giriş şablonu ve mesaj) ve ADR-0050 (`AXES_RESET_COOL_OFF_ON_FAILURE_DURING_LOCKOUT = False`).
  - Küçük kararlar (onaylandı 2026-10-31):
    - (a) `/odunc/` G11'e kadar yok. TC-04, 05, 09, 10, 237 ve 248, yalnız testte kullanılan `tests/support/urls.py` ile `@pytest.mark.urls` kullanır; ürün koduna yer tutucu girmez.
    - (b) TC-12, G02'de `validate_password` ile 9 ve 10 karakterle test edilir; `create_staff` ve `reset_password` iddiaları G04'te eklenir.
    - (c) Personelin `full_name` değeri şema değişikliği olmadan `first_name` alanında tutulur (§8.1'de uygulayıcıya bırakılan ayrıntı).
    - (d) Yönetici view'ları yalnız `require_role(Role.ADMIN)` ile sarılır; böylece en dıştaki sarmalayıcıdaki `required_role` doğru kalır. Oturumsuz kullanıcı `redirect_to_login`'e gider (architecture §6.1).
    - (e) Testlerde saat, `axes.attempts.now`, `axes.handlers.proxy.now` ve `django.utils.timezone.now` patch'lenerek sabitlenir. TC-08'in 14:59 ve 15:01 sınırları ayrı testlerde yazılır.
- **2026-10-31, G02 — uygulama ayrıntıları (bulut oturumu):**
  - `accounts/tests/test_domain.py` yazılmadı: `accounts`'ta saf kural (`domain.py`) yok. Testler `test_services.py` ve `test_views.py`'de.
  - Test yardımcıları: `tests/support/clock.py` (`FrozenClock`, G02 (e)'deki üç `now`'ı patch'ler), `tests/support/factories.py` (`make_staff`), `tests/support/urls.py` (G02 (a)). django-axes istek nesnesi olmadan `authenticate` çağrısını reddettiği için testlerde `client.login` yerine `client.force_login` kullanılır.
  - `staff_view` tek sarmalayıcıdır: `require_role(Role.CLERK)`. `require_role` oturumsuz isteği zaten `redirect_to_login`'e gönderdiği için `login_required` ile aynı sonucu verir ve `required_role` en dıştaki nesnede kalır.
  - `StaffUser.role` varsayılanı `CLERK`'tir (en az yetki); `createsuperuser` `ADMIN` atar. Tablo adları data-design'daki gibidir (`db_table = "staff_user"`).
  - django-axes `axes.W006` uyarısı ("AXES_LOCKOUT_PARAMETERS 'ip_address' içermiyor") gerekçe yorumuyla `base.py`'de `SILENCED_SYSTEM_CHECKS` listesine alındı; `prod.py` bu listeyi genişletir. Gerekçe ADR-0009'daki kullanıcı adına göre kilit: Caddy arkasında bütün istekler 127.0.0.1'den gelir, IP'ye göre kilit bütün personeli birden kilitler. G01'deki `check --deploy` çıktısı bu yüzden "(3 silenced)" oldu. Karar [ADR-0051](../decisions/0051-axes-w006-silenced.md) ile kayda geçti (kullanıcı onayı 2026-10-31).
  - Kilitli hesabın 5. hatalı denemesi de 429 alır (axes kilidi bu denemede koyar); TC-07 6. denemeyi doğrular.
- **2026-10-31, G03 — uygulama ayrıntıları (bulut oturumu):**
  - Plandaki arayüzlere ek servisler: `weekly_closed() -> set[int]`, `closed_date_list() -> list[ClosedDate]` (kapalı günler ekranı), `audit_events(actor)` (yönetici; denetim listesi) ve `admin_home(actor) -> AdminHome(last_export_on, warnings)` (yönetici; ana sayfa paneli). Böylece view'lar ORM'e ve `jobs` modülüne doğrudan dokunmaz.
  - Ayar aralıkları `domain.validate_settings(values)` içindedir; servis bunu çağırır, form aynı sınırları alan düzeyinde de uygular. Bilinmeyen ayar adı `TypeError` verir (programlama hatası). Mesajlar SRS'te yoktu, uygulayıcı seçti: "Ödünç süresi 1 ile 365 gün arasında olmalı", "Ödünç limiti 1 ile 20 arasında olmalı", "Saklama süresi 1 ile 10 yıl arasında olmalı", "Günlük ceza negatif olamaz", "Ceza üst sınırı negatif olamaz", "Borç eşiği 0,00 TL'den büyük olmalı", "Kütüphane adı 1 ile 80 karakter arasında olmalı"; kapalı tarihte "Bu tarih zaten kapalı" ve "Kapalı tarih bulunamadı".
  - `AuditAction` ve `Job` seçenekleri döngüsel import olmasın diye `administration/models.py`'de tanımlıdır; `audit.AuditAction` ve `jobs.Job` aynı sınıflardır.
  - `record_audit`'in üye ve ödünç denetimi (küçük karar 10) `member`/`member_no`/`member_id` ile `loan`/`loan_id` anahtarlarına bakar; KL-15'teki ayrıntılar `member_no` kullanır.
  - Denetim kaydı modeli güncellemeyi ve silmeyi reddeder (`save` ve `delete` `ValueError`). Ayar değişmezse ve haftalık kapalı günler aynıysa kayıt yazılmaz.
  - Ana sayfadaki modül bağlantıları yalnız var olan ekranları gösterir; her görev kendi ekranının bağlantısını ekler. Denetim listesinde sayfa parametresi `?sayfa=`dır.
  - Ayar ve kapalı gün işlemleri başarıda 302 ile aynı ekrana döner ve mesaj gösterir.
- **2026-10-31, G04 — uygulama ayrıntıları (bulut oturumu):**
  - Plandaki arayüzlere ek servisler: `staff_list(actor)` ve `get_staff(actor, pk)` (yönetici; view ORM'e dokunmasın diye). Bilinmeyen `pk` yetki denetiminden sonra 404 verir.
  - `create_staff` ad soyadı, kullanıcı adı biçimini (Django `username_validator`) ve benzersizliği denetler. Mesajlar uygulayıcı seçimidir: "Ad soyad boş olamaz", "Kullanıcı adı yalnız harf, rakam ve @ . + - _ karakterlerinden oluşabilir", "Bu kullanıcı adı zaten kullanılıyor". Parola hataları Django doğrulayıcılarının Türkçe mesajlarıyla `RuleViolation` olur. `change_own_password` de doğrulayıcıları yeniden çalıştırır.
  - Rol aynıysa `set_role`, hesap zaten pasifse `deactivate_staff` hiçbir şey yazmaz. Personeli yeniden aktifleştirme §4.1'de olmadığı için yapılmadı.
  - Hesap oluşturma formu parolayı iki kez ister; yöneticinin parola sıfırlama formu tek alandır. `staff_form.html` hem oluşturma hem ayrıntı ekranıdır.
  - `accounts` URL'leri `accounts` ad alanındadır (`accounts:login` vb.); `LOGIN_URL` yine `/giris/`.
  - TC-32 URL adları yerine URL desenlerini (`personel/<int:pk>/pasif/` gibi) sabit kümeyle karşılaştırır; §4.1 ile birebir eşlenir. Küme §4.1'deki 19 yolun hepsidir; test ADMIN korumalı yolları kümenin var olan yollarla kesişimiyle karşılaştırır, böylece sonraki görevlerin yönetici yolları eklendikleri anda denetlenir (inceleme D3, kullanıcı kararı 2026-10-31). Ek test: `giris/` ve `cikis/` dışındaki her yolda `required_role` bulunmalı.
- **2026-10-31, G02–G04 — uygulayıcının seçtiği kullanıcıya görünen metinler (inceleme D2):** SRS'te, KL'de ya da ADR'de olmayan bütün metinler aşağıdadır. Kullanıcı 2026-10-31'de PR #1 incelemesinde hepsini onayladı; metin değiştirilmedi. SRS/KL/ADR'den gelen metinler (kilit mesajı, "En az bir gün açık kalmalı", "En az bir aktif yönetici kalmalı", "Kendi hesabınızı pasifleştiremezsiniz", "Parolanız değiştirildi", yedek ve dışa aktarma uyarıları, "Yönetici"/"Görevli") ve Django'nun kendi Türkçe metinleri (giriş ve parola değiştirme formu hataları, parola doğrulayıcı mesajları) listede yoktur.
  - "Personel girişi": `templates/registration/login.html`, sayfa başlığı.
  - "Giriş yap": `templates/registration/login.html`, düğme.
  - "Kullanıcı adı": `accounts/forms.py` `LoginForm` ve `StaffCreateForm` alan etiketi; `accounts/staff_list.html` sütun başlığı.
  - "Parola": `accounts/forms.py` `LoginForm` ve `StaffCreateForm` alan etiketi; `templates/base.html` üst menü bağlantısı.
  - "Ana sayfa": `templates/base.html` üst menü bağlantısı; `administration/home.html` sayfa başlığı.
  - "Personel": `templates/base.html` üst menü bağlantısı; `administration/home.html` modül bağlantısı; `accounts/staff_list.html` sayfa başlığı; `administration/audit_list.html` sütun başlığı.
  - "Çıkış": `templates/base.html`, çıkış düğmesi.
  - "Kütüphane": bütün şablonlarda `<title>` sonu (`… · Kütüphane`); ayarlardaki `library_name` varsayılanı ADR-0035'tendir.
  - "Parola değiştir": `templates/registration/password_change.html`, sayfa başlığı.
  - "Devam etmeden önce yöneticinin verdiği parolayı değiştirmeniz gerekiyor.": `templates/registration/password_change.html`, bayrak True iken uyarı.
  - "Parola en az 10 karakter olmalı.": `templates/registration/password_change.html`, not.
  - "Değiştir": `templates/registration/password_change.html`, düğme.
  - "Personel bulunamadı": `accounts/views.py` `_get_staff`, 404 nedeni (yalnız `DEBUG` açıkken görünür).
  - "Personel hesabı oluşturuldu": `accounts/views.py` `staff_create`, başarı mesajı.
  - "Rol kaydedildi": `accounts/views.py` `staff_detail`, başarı mesajı.
  - "Hesap pasifleştirildi": `accounts/views.py` `staff_deactivate`, başarı mesajı.
  - "Parola sıfırlandı; ilk girişte değiştirilecek": `accounts/views.py` `staff_reset_password`, başarı mesajı.
  - "Hesap kilidi kaldırıldı": `accounts/views.py` `staff_unlock`, başarı mesajı.
  - "Ad soyad": `accounts/forms.py` `StaffCreateForm` alan etiketi; `accounts/staff_list.html` sütun başlığı.
  - "Rol": `accounts/forms.py` `StaffCreateForm` ve `StaffRoleForm` alan etiketi; `accounts/staff_list.html` sütun başlığı; `accounts/staff_form.html` bölüm başlığı.
  - "Parola (tekrar)": `accounts/forms.py` `StaffCreateForm` alan etiketi.
  - "Parolalar aynı değil": `accounts/forms.py` `StaffCreateForm.clean`, `password2` alan hatası.
  - "Yeni parola": `accounts/forms.py` `PasswordResetByAdminForm` alan etiketi.
  - "Ad soyad boş olamaz": `accounts/services.py` `create_staff`, `RuleViolation`.
  - "Kullanıcı adı yalnız harf, rakam ve @ . + - _ karakterlerinden oluşabilir": `accounts/services.py` `create_staff`, `RuleViolation`.
  - "Bu kullanıcı adı zaten kullanılıyor": `accounts/services.py` `create_staff`, `RuleViolation`.
  - "Yeni personel hesabı": `accounts/staff_list.html` bağlantı; `accounts/staff_form.html` sayfa başlığı.
  - "Durum": `accounts/staff_list.html`, sütun başlığı.
  - "Aktif": `accounts/staff_list.html` ve `accounts/staff_form.html`, hesap durumu.
  - "Pasif": `accounts/staff_list.html` ve `accounts/staff_form.html`, hesap durumu.
  - "Yeni personel": `accounts/staff_form.html`, oluşturma ekranının `<title>`'ı.
  - "Personel listesi": `accounts/staff_form.html`, geri bağlantısı.
  - "Personel ilk girişte parolasını değiştirmek zorundadır.": `accounts/staff_form.html`, oluşturma formu notu.
  - "Oluştur": `accounts/staff_form.html`, oluşturma düğmesi.
  - "Rolü kaydet": `accounts/staff_form.html`, düğme.
  - "Parola sıfırla": `accounts/staff_form.html`, bölüm başlığı.
  - "Parolayı sıfırla": `accounts/staff_form.html`, düğme.
  - "Hesap": `accounts/staff_form.html`, bölüm başlığı.
  - "Kilidi kaldır": `accounts/staff_form.html`, düğme.
  - "Pasifleştir": `accounts/staff_form.html`, düğme.
  - "Ayarlar kaydedildi": `administration/views.py` `settings_view`, başarı mesajı.
  - "Haftalık kapalı günler kaydedildi": `administration/views.py` `closed_days`, başarı mesajı.
  - "Kapalı tarih eklendi": `administration/views.py` `closed_date_add`, başarı mesajı.
  - "Kapalı tarih silindi": `administration/views.py` `closed_date_remove`, başarı mesajı.
  - "Geçerli bir tutar girin (ör. 5,00)": `administration/forms.py` `TLField`, alan hatası.
  - "Pazartesi": `administration/forms.py` `WEEKDAYS`, haftalık kapalı gün seçeneği.
  - "Salı": `administration/forms.py` `WEEKDAYS`, haftalık kapalı gün seçeneği.
  - "Çarşamba": `administration/forms.py` `WEEKDAYS`, haftalık kapalı gün seçeneği.
  - "Perşembe": `administration/forms.py` `WEEKDAYS`, haftalık kapalı gün seçeneği.
  - "Cuma": `administration/forms.py` `WEEKDAYS`, haftalık kapalı gün seçeneği.
  - "Cumartesi": `administration/forms.py` `WEEKDAYS`, haftalık kapalı gün seçeneği.
  - "Pazar": `administration/forms.py` `WEEKDAYS`, haftalık kapalı gün seçeneği.
  - "Ödünç süresi (gün)": `administration/forms.py` `SettingsForm` alan etiketi.
  - "Aynı anda ödünç limiti": `administration/forms.py` `SettingsForm` alan etiketi.
  - "Günlük ceza (TL)": `administration/forms.py` `SettingsForm` alan etiketi.
  - "Ödünç başına ceza üst sınırı (TL)": `administration/forms.py` `SettingsForm` alan etiketi.
  - "Borç eşiği (TL)": `administration/forms.py` `SettingsForm` alan etiketi.
  - "Saklama süresi (yıl)": `administration/forms.py` `SettingsForm` alan etiketi.
  - "Kütüphane adı": `administration/forms.py` `SettingsForm` alan etiketi.
  - "Haftalık kapalı günler": `administration/forms.py` `WeeklyClosedForm` alan etiketi; `administration/closed_days.html` bölüm başlığı.
  - "Tarih": `administration/forms.py` `ClosedDateForm` alan etiketi; `administration/closed_days.html` sütun başlığı.
  - "Not": `administration/forms.py` `ClosedDateForm` alan etiketi; `administration/closed_days.html` sütun başlığı.
  - "Ödünç süresi 1 ile 365 gün arasında olmalı": `administration/domain.py` `SETTING_BOUNDS`, `RuleViolation`.
  - "Ödünç limiti 1 ile 20 arasında olmalı": `administration/domain.py` `SETTING_BOUNDS`, `RuleViolation`.
  - "Günlük ceza negatif olamaz": `administration/domain.py` `SETTING_BOUNDS`, `RuleViolation`.
  - "Ceza üst sınırı negatif olamaz": `administration/domain.py` `SETTING_BOUNDS`, `RuleViolation`.
  - "Borç eşiği 0,00 TL'den büyük olmalı": `administration/domain.py` `SETTING_BOUNDS`, `RuleViolation`.
  - "Saklama süresi 1 ile 10 yıl arasında olmalı": `administration/domain.py` `SETTING_BOUNDS`, `RuleViolation`.
  - "Kütüphane adı 1 ile 80 karakter arasında olmalı": `administration/domain.py` `LIBRARY_NAME_MESSAGE`, `RuleViolation`.
  - "Bu tarih zaten kapalı": `administration/services.py` `add_closed_date`, `RuleViolation`.
  - "Kapalı tarih bulunamadı": `administration/services.py` `remove_closed_date`, `RuleViolation`.
  - "Son dışa aktarma:": `administration/home.html`, yönetici paneli.
  - "yok": `administration/home.html`, hiç dışa aktarma yoksa tarih yerine.
  - "Modüller": `administration/home.html`, bölüm başlığı.
  - "Ayarlar": `administration/home.html` modül bağlantısı; `administration/settings.html` sayfa başlığı.
  - "Kapalı günler": `administration/home.html` modül bağlantısı; `administration/closed_days.html` sayfa başlığı.
  - "Denetim kaydı": `administration/home.html` modül bağlantısı; `administration/audit_list.html` sayfa başlığı.
  - "Kaydet": `administration/settings.html` ve `administration/closed_days.html`, düğme.
  - "Değişiklikler yalnız sonraki ödünçlere uygulanır; mevcut ödünçlerin son tarihi ve ceza oranı değişmez.": `administration/settings.html`, not.
  - "Kapalı tarihler": `administration/closed_days.html`, bölüm başlığı.
  - "Ekle": `administration/closed_days.html`, düğme.
  - "Sil": `administration/closed_days.html`, düğme.
  - "Kapalı tarih yok.": `administration/closed_days.html`, boş liste.
  - "Zaman": `administration/audit_list.html`, sütun başlığı.
  - "İşlem": `administration/audit_list.html`, sütun başlığı.
  - "Hedef": `administration/audit_list.html`, sütun başlığı.
  - "Ayrıntılar": `administration/audit_list.html`, sütun başlığı.
  - "Sistem": `administration/audit_list.html`, aktörsüz (zamanlanmış görev) kayıt.
  - "Kayıt yok.": `administration/audit_list.html`, boş liste.
  - "Önceki": `administration/audit_list.html`, sayfalama.
  - "Sonraki": `administration/audit_list.html`, sayfalama.
  - "Sayfa N / M": `administration/audit_list.html`, sayfalama.
  - "Ödeme": `administration/models.py` `AuditAction` etiketi; denetim listesinde işlem adı.
  - "Af": `administration/models.py` `AuditAction` etiketi.
  - "Bedel": `administration/models.py` `AuditAction` etiketi.
  - "Para iadesi": `administration/models.py` `AuditAction` etiketi.
  - "Nüsha kayıp": `administration/models.py` `AuditAction` etiketi.
  - "Nüsha hasarlı": `administration/models.py` `AuditAction` etiketi.
  - "Nüsha bulundu": `administration/models.py` `AuditAction` etiketi.
  - "Nüsha onarıldı": `administration/models.py` `AuditAction` etiketi.
  - "Nüsha kayıttan düşüldü": `administration/models.py` `AuditAction` etiketi.
  - "Ayar değişikliği": `administration/models.py` `AuditAction` etiketi.
  - "Kapalı gün değişikliği": `administration/models.py` `AuditAction` etiketi.
  - "Personel değişikliği": `administration/models.py` `AuditAction` etiketi.
  - "Bedel iptali": `administration/models.py` `AuditAction` etiketi.
  - "Üye yeniden aktifleştirildi": `administration/models.py` `AuditAction` etiketi.
- **2026-10-31, inceleme küçük kararı 2 — `tl` filtresi `None` ile `TypeError` verir:** Değişiklik yapılmadı. Bütün tutar alanları `NOT NULL`'dır (data-design), bu yüzden şablona `None` gelmesi bir hatadır ve sessizce "0,00 TL" yazmak yerine görünür biçimde patlamalıdır (kullanıcı onayı 2026-10-31).
- **2026-10-31, inceleme küçük kararı 4 — kilitli kullanıcı adı ve boş parola:** Kilitli kullanıcı adıyla boş parolalı giriş POST'u 429 değil, 200 ve "zorunlu alan" hatası alır; böyle kalır. Boş parolayla kimlik doğrulama hiç denenmez ve cevap kilit durumunu açığa vurmaz; ADR-0049 bu durumu kapsamaz (kullanıcı onayı 2026-10-31).
- **2026-10-31, inceleme D4 — kural ihlalinde aynı ekran 200 ile:** `staff_deactivate` (`accounts/views.py`) ve `closed_date_remove` (`administration/views.py`) `RuleViolation`'da artık 302 ile yönlendirmez; personel ayrıntısı ve kapalı günler ekranını 200 ile, mesajı hata mesajı olarak göstererek yeniden çizer. Gerekçe plan §4.0'daki kural; bu iki view'da form olmadığı için mesaj form hatası yerine sayfanın mesaj alanında görünür ve sonraki istekte tekrar çıkmaz (kullanıcı kararı 2026-10-31).
- **2026-10-31, inceleme küçük kararı 3 — yalnız boşluktan oluşan kütüphane adı:** `validate_settings` doğrudan çağrıldığında boşluklu adı kabul ediyordu (form alanı boşlukları zaten kırpıyordu). Artık boş adla aynı mesajla ("Kütüphane adı 1 ile 80 karakter arasında olmalı") reddeder; ad kaydedilirken kırpılmaz, yalnız boş sayılır (kullanıcı onayı 2026-10-31).
- **2026-10-31, inceleme gözlemi — `deactivate_staff` son yönetici denetimi:** `accounts/services.py`'deki `user.role == Role.ADMIN and not _other_active_admins(user)` dalına bugünkü kurallarla ulaşılamaz: aktör her zaman aktif bir yöneticidir (`require_role(Role.ADMIN)`) ve kendini pasifleştirme bu denetimden önce reddedilir; bu yüzden hedef dışında en az bir aktif yönetici hep vardır. Dal, "en az bir aktif yönetici" değişmezini aktör kuralından bağımsız koruyan bir savunma olarak kalır; `accounts/services.py`'nin dal kapsamının %96 olmasının bir nedeni budur (kullanıcı kararı 2026-10-31).
- **2026-11-01, kullanıcı kararı — grup başına bir bulut oturumu:** Her görev grubu kendi bulut oturumunda yapılır; grup bitince oturum PR açar ve durur. Sonraki grup yeni bir oturumda ve yeni bir açılış istemiyle başlar (KL-38'deki "grup başına bir oturum" kuralının açık hali).
- **2026-11-01, kullanıcı kararı — bulut oturumunda kritik soru:** Bulut oturumunda kritik bir açık nokta çıkarsa oturum durup raporlamak yerine soruyu oturumun içinde kullanıcıya sorar ve cevabı bekler; cevap ADR ya da §11 maddesi olarak kaydedilir (ADR-0048'deki "soru soramaz" varsayımının yerine).
- **2026-11-01, kullanıcı kararı — planın vermediği kullanıcıya görünen metinler:** Plan, SRS, KL ya da ADR'nin vermediği etiket, başlık, düğme ve mesaj metinlerini uygulayıcı mevcut şablonların üslubuyla seçer, §11'de metin ve dosyasıyla listeler; metinler G02–G04'teki D2 gibi PR'da onaylanır. Uygulayıcı bu metinler için durmaz.
- **2026-11-01, kullanıcı kararı — pasif ya da anonimleştirilmiş üye pasifleştirilemez:** `circulation.services.deactivate_member`, açık ödünç ve borç denetimlerinden önce anonimleştirilmiş üyeyi "Anonimleştirilmiş üye pasifleştirilemez", zaten pasif üyeyi "Üye zaten pasif" mesajıyla `RuleViolation` ile reddeder. Böylece saklama süresinin başlangıcı olan `deactivated_on` (ADR-0045) hiçbir zaman üzerine yazılmaz. Üye ayrıntısında pasifleştirme formu yalnız aktif ve anonimleştirilmemiş üyede görünür. Kural `members.services.reactivate_member`'ın ("Üye zaten aktif", "Anonimleştirilmiş üye aktifleştirilemez") aynası; G11'de testleriyle uygulanır.
- **2026-10-31, G05 — uygulama ayrıntıları (bulut oturumu):**
  - `catalog` app'i G05'te `INSTALLED_APPS`'e eklendi (`library_site/settings/base.py`). G05'in dosya listesinde `base.py` yok, ama `catalog/apps.py` bu görevde oluşuyor; model G07'de gelir ve app'in o zaman ayrıca eklenmesi gerekmez.
  - `normalize_tr`'nin 4. adımı (`" ".join(text.split())`) boşlukları teke indirirken baştaki ve sondaki boşluğu da atar. Gerekçe: " ayşe" gibi bir arama terimi `search_key LIKE %…%` ile baştaki boşluk yüzünden eşleşmeyi kaçırmasın.
  - `parse_isbn` tireleri ve bütün boşluk karakterlerini (sekme dahil) atar, sonra büyük harfe çevirir (KL-40'taki küçük "x" böyle kabul edilir). Yalnız ASCII rakamlar kabul edilir; Python'un `isdigit()`'inin kabul ettiği başka rakamlar (ör. Arapça-Hint rakamları) reddedilir.
  - `IsbnInvalid.reason` seçimi: biçim hataları (10 ya da 13 karakter değil, ISBN-10'un son hanesi dışında harf, ISBN-13'te "X", boş giriş) "ISBN 10 ya da 13 haneli olmalı"; kontrol hanesi tutmayan 10 ya da 13 haneli giriş "ISBN kontrol hanesi hatalı" verir (TC-40…TC-43). Son hanesi "X" olan ve kontrol hanesi tutmayan ISBN-10'a öneri verilmez, çünkü "978" + "…X" bir ISBN-13 değildir.
  - `isbn10_to_13` ISBN-10 kontrol hanesini doğrulamaz (ilk dokuz haneyi alır ve ISBN-13 kontrol hanesini yeniden hesaplar); biçimi bozuk girişte `ValueError` fırlatır. Doğrulama `parse_isbn`'in işidir.
- **2026-10-31, G06 — kullanıcı kararı: anonimleştirilmiş üye güncellenemez:** Plan anonimleştirilmiş üyenin düzenlenip düzenlenemeyeceğini söylemiyordu; düzenlemeye izin vermek, KVKK saklama süresinin sildiği kişisel veriyi geri yazmayı mümkün kılardı. Oturumda kullanıcıya soruldu, önerilen seçenek seçildi: `update_member` "Anonimleştirilmiş üye güncellenemez" mesajıyla `RuleViolation` fırlatır; düzenleme ekranı 200 ile mesajı gösterir; anonim üyenin ayrıntısında "Düzenle" bağlantısı ve rıza formu yoktur (ADR-0042'deki "Anonimleştirilmiş üye aktifleştirilemez" ile aynı yön).
- **2026-10-31, G06 — uygulama ayrıntıları (bulut oturumu):**
  - G06'nın dosya listesi dışında değişenler: `library_site/settings/base.py` (`members` app'i), `library_site/urls.py` (`members.urls`), `templates/base.html` (üst menüde "Üyeler") ve `administration/home.html` (modül bağlantısı; G03 §11'deki "her görev kendi ekranının bağlantısını ekler" kuralı).
  - `search_key` ve `phone_digits`, `Member.save()` içinde tek noktada yazılır (ADR-0019'daki "model katmanında tek noktada"); servisler ve `make_member` bunları hesaplamaz. `update_fields` verilse de iki türetilmiş alan kayda eklenir. Anonim üyede `search_key` boş metin, `phone_digits` NULL olur.
  - Üye alanı kuralları `members/domain.py: validate_member_fields(full_name, phone)` içindedir: ad soyad ve telefon zorunlu, ad soyad en fazla 200, telefon en fazla 30 karakter (data-design §2.2) ve telefonda 1–20 rakam (`phone_digits` varchar(20)). Değerler kırpılarak kaydedilir. E-posta Django `validate_email` ile denetlenir ve en fazla 254 karakterdir; boş e-posta NULL olur. Telefon biçimi ayrıca denetlenmez.
  - `MemberQuery` frozen dataclass'tır: `digits` ve `text` alanları (biri dolu) ve `is_empty`. Temizlendikten sonra boş kalan sorgu boş sonuç verir; arama ekranı `q` boşken yalnız formu gösterir. Rakam sorgusunda üye no tam eşleşmesi önce, sonra üye no sırasıyla telefon eşleşmeleri gelir; 18 haneden uzun rakam dizisi yalnız telefonda aranır (SQLite tam sayı sınırı). Metin sorgusu `search_key`'e, sonra üye no'ya göre sıralanır. Django `contains` LIKE joker karakterlerini kaçırır (TC-50).
  - `set_consent` denetim sırası: gelecek tarih, e-posta yokluğu (yalnız rıza verirken), geçerli durumu tekrarlama. Rızayı geri almak e-posta istemez. E-posta silinmeyip değiştirilirse rıza durumu değişmez (ADR-0047 yalnız silmeyi kapsar).
  - Üye oluşturma, güncelleme ve rıza denetim kaydı yazmaz: faz 4 küçük karar 8'deki eylem listesinde üye oluşturma ve güncelleme yok, rıza olayları KL-36'ya göre kendi izidir. Yalnız `reactivate_member` `MEMBER_REACTIVATED` yazar.
  - Okuma servisleri (`search_members`, `member_by_no`, `consent_dates`) aktör almaz ve `require_role` taşımaz (plan imzaları; G03'teki `get_settings` gibi); koruma view'dadır. Bilinmeyen üye no ayrıntı, düzenleme, aktifleştirme ve rıza yollarında 404 verir ("Üye bulunamadı"; G04'teki personel ayrıntısıyla aynı).
  - `consent_dates` her eylem için en büyük `effective_on` değerini döndürür.
  - Rıza formu tek formdur: gizli `given` alanı ("1" ver, "0" geri al) geçerli duruma uyan düğmeyle gelir; tarih varsayılanı bugündür (`clock.today()`), `YYYY-AA-GG` ve `GG.AA.YYYY` biçimleri kabul edilir. E-postası ve rızası olmayan üyede form yerine "Rıza için e-posta adresi gerekli." notu görünür. Rıza ve aktifleştirme hataları ayrıntı ekranını 200 ile yeniden gösterir (§4.0, G04 D4).
  - `tests/support/factories.py: make_member(full_name, phone, email, *, member_no, is_active, deactivated_on, anonymized)` üyeyi ORM ile doğrudan kurar (aktör ve denetim yok); pasif üyede `deactivated_on` verilmezse 2026-10-01 olur.
  - TC-52 (model alan listesi) veritabanı istemediği için `members/tests/test_domain.py`'dedir.
- **2026-10-31, G07 — uygulama ayrıntıları (bulut oturumu):**
  - G07'nin dosya listesi dışında değişenler: `library_site/urls.py` (`catalog.urls`), `templates/base.html` (üst menüde "Kitaplar") ve `administration/home.html` (modül bağlantısı).
  - `Book.save()` `search_key`'i (`normalize_tr(title + " " + author)`), `Copy.save()` `status_changed_at`'i yazar: eklemede ve durum her değiştiğinde (`update_fields` verilse de alan kayda eklenir). Alanın veritabanı varsayılanı yoktur; zaman `save()` içinde `timezone.now()` ile alınır, böylece testlerdeki `FrozenClock` geçerli olur.
  - Geçici barkod (§8.1'de uygulayıcıya bırakılan ayrıntı): `add_copies` her nüshayı `"PENDING-"` barkoduyla ekler, id'yi alır ve aynı işlemde `f"{id:08d}"` yazar. Bir sonraki ekleme bundan sonra yapıldığı için benzersiz sütunda aynı anda tek geçici değer olur; değer hiçbir zaman commit edilmez. id'ler Django'nun SQLite'taki `AUTOINCREMENT` sütunundan gelir, silinen id yeniden kullanılmaz. KL-42 denetimi her eklemeden sonra yapılır; 99.999.999'u aşan ilk id bütün grubu geri alır. TC-65 ve TC-263 sırayı `sqlite_sequence` tablosuyla ayarlar.
  - `create_book` ve `update_book` ISBN'i ham haliyle alır ve `parse_isbn` ile normalize eder; boş ISBN NULL olur. `IsbnSuggest` sonucunu servis de reddeder (mesaj formdakiyle aynı öneri metnidir); öneriyi kabul etmek formun işidir. Alan kuralları ve mesajları servistedir: başlık ve yazar zorunlu, başlık ve yazar en fazla 300, yayınevi en fazla 200 karakter (data-design §2.3), yıl 1–9999. Değerler kırpılır; boş yayınevi NULL olur.
  - Plandaki arayüzlere ek servisler: `get_book(pk) -> Book | None`, `book_copies(book)` (barkod sırasıyla), `shelf_counts(books)` (tek sorguda kitap başına raftaki ve toplam nüsha), `is_barcode(q)` ve `suggestion_message(suggestion)`. Bilinmeyen kitap 404 verir ("Kitap bulunamadı").
  - `search_books` sıralaması: ISBN ya da barkod tam eşleşmeleri önce, sonra `search_key` ve id. Boş sorgu boş sonuç verir. Arama ekranı her kitapta "Rafta / Toplam" sayısını gösterir; 8 haneli sorgu bir nüshaya denk gelirse listenin üstünde "Nüsha 00000042: Tutunamayanlar · Rafta" satırı çıkar (TC-66, AC-04).
  - `BookForm`: ham ISBN alanı en fazla 40 karakterdir. `isbn_accept` düğmesinin metni "Öneriyi kabul et ve kaydet"tir. `isbn_accept` ile gelen değer yalnız bir öneri üretiyorsa (elle değiştirilmiş istek) "ISBN kontrol hanesi hatalı" ile reddedilir.
  - Nüsha ekleme formunun alanı `count`'tur. 1–50 aralığını servis denetler ve mesaj alan hatası olarak görünür; tarayıcıya `min`/`max` ipucu verilir. Kural ihlalinde kitap ayrıntısı 200 ile yeniden gösterilir.
  - Kitap ve nüsha işlemleri denetim kaydı yazmaz (faz 4 küçük karar 8'deki listede yoklar).
  - `tests/support/factories.py`: `make_book(title, author, *, isbn13, publisher, year)` ISBN'i olduğu gibi yazar; `make_copy(book, *, pk, status)` barkodu `f"{id:08d}"` yapar.
- **2026-10-31, G08 — uygulama ayrıntıları (bulut oturumu):**
  - **Yazı tipi:** PDF'lerdeki metin, reportlab paketinin içinde gelen Vera TrueType yazı tipiyle (`Vera.ttf`, Bitstream Vera lisansı gömmeye izin verir) yazılır ve PDF'e alt küme olarak gömülür. PDF'in temel yazı tipleri (Helvetica, WinAnsi kodlaması) ş, ğ, ı ve İ harflerini içermiyor; "İstanbul Şehir Kütüphanesi" kare kutularla basılıyordu. Yeni bağımlılık ya da dosya eklenmedi; yazı tipi reportlab'ın kendi yazı tipi yolundan bulunur (Windows'ta da).
  - **Öğe yerleşimi:** Üstte başlık (8 pt), ortada 15 mm Code 128 barkod (modül 0,33 mm, reportlab'ın varsayılan 10 modüllük sessiz bölgeleriyle), altında açıklama (9 pt) ve varsa alt metin (7 pt) bulunur. Blok öğenin içinde yatay ve dikey ortalanır; metinler için yanlarda 2 mm boşluk kalır. Her metin satırı öğe genişliğine sığmazsa "…" ile kısaltılır, başlık ayrıca 80 karakterle sınırlıdır (ADR-0035; yazı boyutu küçültülmez). Etikette alt metin `title[:30]`'dur ve genişliğe sığdığı sürece kısaltılmaz (TC-72). Kart kesim çizgileri her kartın çevresinde 0,25 pt açık gri dikdörtgendir.
  - `SheetLayout` `kw_only` frozen dataclass'tır (varsayılanlı `page_w`, `page_h` zorunlu alanlardan önce geldiği için); `__post_init__` öğelerin sayfaya sığmadığı yerleşimi `ValueError` ile reddeder ve `per_page` özelliği vardır. Plandaki arayüze ek olarak `item_position(index, layout)` ve `fit_text(text, size, max_width, max_chars)` dışa açıktır. `render_sheet([])` `ValueError` verir. Çıktı `invariant=True` ile üretilir; aynı girdi aynı baytları verir.
  - `tests/support/barcode.py`: `decode_pdf_barcodes`'a ek olarak `read_pdf_barcodes` (sayfa, değer, biçim), `pdf_page_count` ve `pdf_text` (pypdfium2 ile metin çıkarma; TC-72, TC-73, TC-74). Aynı satırdaki barkodlar, merkezleri arasındaki dikey fark 7,5 mm'den azsa bir satır sayılır.
  - Barkod çözen testler (TC-70, TC-71, TC-74) ADR-0030'a göre `slow` işaretlidir; TC-70'in seviyesi test planında "birim" olsa da çözme yapar. Bu oturumda dört `slow` testin hepsi Linux'ta koştu.
  - **Seçim kuralları (KL-25):** İki uçtan biri dolu ise aralık kullanılmış sayılır. Etikette uçlardan biri boş ya da 8 haneli barkod değilse "Başlangıç ve bitiş 8 haneli barkod olmalı", kartta pozitif tam sayı değilse "Başlangıç ve bitiş pozitif üye no olmalı" verilir. Seçim kutusu listesinde 240 sınırı tekrarsız öğe sayısına uygulanır. Hariç tutmadan sonra listede öğe kalmazsa "En az bir nüsha seçin" ya da "En az bir üye seçin" verilir (aralıktaki "Aralıkta basılacak … yok" mesajının liste karşılığı). Aralıkta yalnız Kayıttan düşmüş nüshalar atlanır; Kayıp, Hasarlı ve Ödünçteki nüshaların etiketi basılabilir. Barkod aralığı, sıfırla doldurulmuş 8 haneli barkodların metin karşılaştırmasıyla seçilir.
  - `label_pdf` ve `member_card_pdf` kütüphane adını `administration.services.get_settings()` ile okur; listede olmayan id atlanır.
  - `/nushalar/etiket/` ve `/uyeler/kart/` kural ihlalinde aralık formunu 200 ile ve mesajla gösterir; istek kitap ayrıntısındaki ya da üye aramasındaki seçim kutularından gelse de hata bu ekranda görünür. Seçim formu boş POST'ta da bağlanır (boş istek "En az bir … seçin" alır). Ortak `IntListField` (`administration/forms.py`) seçim kutusu değerlerini tam sayıya çevirir; geçersiz değer "Geçersiz seçim" verir.
  - **URL sırası (§8.1'de uygulayıcıya bırakılan ayrıntı):** `nushalar/etiket/` `catalog.urls` içindedir; `library_site/urls.py`'de `catalog.urls`, G12'de eklenecek circulation yollarından önce gelmelidir, yoksa `nushalar/<str:barcode>/` "etiket"i barkod sanar. `catalog/urls.py`'de bu not yorum olarak duruyor.
  - "Etiket bas" düğmesi yalnız basılabilir nüsha varsa, "Kart bas" düğmesi yalnız seçilebilir üye varsa görünür. Kitap arama ekranında "Nüsha etiketleri", üye arama ekranında "Üye kartları" bağlantısı aralık formuna gider.
  - G08'in dosya listesi dışında değişenler: `administration/forms.py` (`IntListField`), `catalog/forms.py`, `members/forms.py`, `catalog/templates/catalog/search.html` ve `members/templates/members/search.html` (bağlantılar), `catalog/tests/*` ve `members/tests/*` (TC-71…TC-75, TC-265…TC-269), `pdf/tests/__init__.py`.
- **2026-11-01, G10 — uygulama ayrıntıları (bulut oturumu):**
  - `circulation` app'i G10'da `INSTALLED_APPS`'e eklendi (`library_site/settings/base.py`; G05'teki `catalog` gibi, dosya listesinde yok ama model bu görevde oluşuyor).
  - `InvalidTransition` mesajında durumlar Türkçe etiketleriyle yazılır ("Bu durum değişikliği yapılamaz: Kayıp → Hasarlı"); kodlar (`LOST`) personele anlamsızdır. Etiketler domain ORM modülü import etmesin diye `circulation.domain.STATUS_LABELS`'ta tutulur; bir test bunları `catalog.models.CopyStatus` etiketleriyle eşit tutar.
  - `NoOpenDayError` mesajı ADR-0028'deki metindir ve `NO_OPEN_DAY_MESSAGE` sabitidir; `RuleViolation`'ın alt sınıfı olduğu için view'lar onu ayrıca yakalamaz.
  - `classify_member_input`: temizlikten sonra boş kalan girdi `TEXT` ve boş değerdir (ekran boş girdiyi aramaz). `TEXT` değeri özgün metnin kırpılmış halidir; normalizasyonu `search_members` yapar. Yalnız ASCII rakamlar rakam sayılır (`members.domain` ile aynı).
  - `late_days`, takvim farkı 0 ya da negatifse kapalı tarihleri saymadan 0 döner; sonuç formülle aynıdır.
  - `Loan` modeli: `db_table = "loan"`; data-design §2.4'teki CHECK'ler (`due_on > loaned_on`, `close_reason` değerleri, `closed_on` ile `close_reason`'ın birlikte dolu ya da boş olması, `copy_found_on` için `closed_on IS NOT NULL AND close_reason = 'LOST' AND copy_found_on >= closed_on`) ve §4'teki indeksler (`loan_one_open_per_copy` kısmi benzersiz, `loan(member_id, closed_on)`, kısmi `loan(due_on) WHERE closed_on IS NULL`, `loan(closed_on)`) migration'dadır. `copy_found_on` CHECK'ine `closed_on IS NOT NULL` eklendi: SQL'de `close_reason` NULL iken karşılaştırma bilinmez sonuç verir ve CHECK geçerdi; açık ödünçte `copy_found_on` böylece reddedilir. `CloseReason` etiketleri: "İade edildi", "Kayıp", "Hasarlı".
  - Model kısıt testleri `circulation/tests/test_services.py`'nin başındadır (KL-11'deki üç dosya düzeni; `test_domain.py` veritabanına dokunmaz).
- **2026-11-01, G09 — kullanıcı kararı: denetim listesinde tutarlar TL olarak:** TC-91 af kaydının `/denetim/`'de "5,00 TL" olarak görünmesini bekliyordu; G03'ün denetim listesi ayrıntıları ham JSON olarak (`"amount_kurus": 500`) gösteriyordu. Oturumda soruldu, önerilen seçenek seçildi: `administration/templatetags/audit.py` `details_text` filtresi `amount_kurus` ve `fee_kurus` anahtarlarının değerini `format_tl` ile ("5,00 TL") gösterir; saklanan JSON ve öteki anahtarlar (ayar değişikliklerindeki eski ve yeni değerler dahil) değişmez. G03 ekranında küçük bir gösterim değişikliğidir; ADR gerekmedi.
- **2026-11-01, G09 — uygulama ayrıntıları (bulut oturumu):**
  - `billing` app'i `INSTALLED_APPS`'e, `billing.urls` `library_site/urls.py`'ye (`catalog.urls`'ten sonra) eklendi.
  - `LedgerEntry` ve `Allocation` yalnız eklenir (I6): model `save` güncellemeyi, `delete` silmeyi `ValueError` ile reddeder (G03'teki `AuditEvent` gibi). ADR-0018'deki tek istisna (G15, `loan_id` NULL) queryset `update` ile yapılır. `created_at` `save()` içinde `timezone.now()` ile yazılır (`FrozenClock` geçerli olsun diye; G07'deki `Copy.status_changed_at` gibi). CHECK kısıtları: tür listesi, `amount_kurus > 0`, WAIVER/CANCELLATION/REFUND'da `target_entry` dolu, WAIVER'da `reason` dolu ve boş değil (data-design §2.5). `allocation` için `amount_kurus > 0` ve `UNIQUE(credit_entry, charge_entry)`. data-design §4'teki `ledger_entry(member_id)`, `(target_entry_id)`, `(loan_id)` ve `allocation(charge_entry_id)` indeksleri Django'nun yabancı anahtar indeksleridir. `EntryKind` etiketleri plandaki Türkçe adlardır.
  - `post_charge` ve `cancel_unpaid` iç servislerdir ve `require_role(Role.CLERK)` taşır (çağıranlar: görevlinin iadesi, yöneticinin kayıp/hasar işaretlemesi, görevlinin "bulundu" işareti). `post_charge` FINE ya da FEE dışındaki türü ve pozitif olmayan tutarı, `cancel_unpaid` FEE dışındaki kalemi programlama hatası sayıp `ValueError` ile reddeder. `cancel_unpaid` kendi denetim kaydını yazmaz: otomatik iptal `mark_found`'un `COPY_FOUND` kaydıyla izlenir; `CANCELLATION` eylemi yalnız elle iptalindir (ADR-0041, KL-30).
  - Denetim sırası: `waive` gerekçe → tür → tutar > 0 → ödenmemiş kısım; `cancel_fee_manual` tür → gerekçe → ödünç bağı → ödenmemiş kısım; `refund` ön koşul (I5) → tutar > 0 → iade edilebilir tutar. Gerekçe kırpılarak kaydedilir.
  - Plandaki arayüzlere ek: `get_entry(member, entry_id)` (formdaki gizli kimlik başka üyenin kalemine ulaşamasın diye; yoksa "Kalem bulunamadı") ve `StatementRow` alanları (`entry_id`, `created_at`, `kind`, `kind_label`, `amount_kurus`, `staff_name`, `reason`, `target_entry_id`, `unpaid_kurus`, `refundable_kurus`, `manually_cancellable`). `staff_name` personelin ad soyadıdır (`first_name`, G02 (c)); boşsa kullanıcı adı. Döküm `created_at, id` sırasıyla en eskiden başlar.
  - Döküm ekranı: ödeme formu yalnız bakiye > 0 iken görünür (herkese); af formu yalnız yöneticiye ve ödenmemiş kalem varken, açılır listede ödenmemiş kalemlerle; para iadesi ve elle iptal formları bedel satırı başına birer küçük formdur (KL-26, ADR-0041). Seçilen kimliği servis denetler. Başarı 302 ile döküme döner ve mesaj gösterir; kural ihlali dökümü 200 ile yeniden çizer (ödeme ve af formunda form hatası olarak, satır formlarında sayfa mesajı olarak; G04 D4).
  - **Test yardımcıları:** `make_charge(member, kind, amount_kurus, *, loan, created_by, created_at)` (yalnız FINE ve FEE). `make_loan` G11 yerine G09'da eklendi, çünkü TC-92…TC-96 ödüncü LOST ile kapanmış bedel istiyor; nüsha durumunu ödüncün durumuna uydurur (açık → ON_LOAN, LOST/DAMAGED kapanış → LOST/DAMAGED). Factory'lerin varsayılan personeli `kayit.test` kullanıcı adıyla oluşturulur; testlerin kendi `ali`/`ayse.y` hesaplarıyla çakışmaz.
  - **Eşzamanlılık testleri:** `tests/support/concurrency.py`: `file_db` fixture'ı `default` bağlantısını bir test boyunca migrate edilmiş geçici bir dosya veritabanına (üretimdeki WAL, IMMEDIATE, `busy_timeout` ayarlarıyla) yönlendirir, sonra bellekteki test veritabanını geri koyar; `run_parallel` çağrıları `threading.Barrier` ile aynı anda, kendi bağlantılarıyla çalıştırır (test planı §5). Bellekteki paylaşımlı önbellekli veritabanında SQLite tablo kilitleri beklemeden hata verdiği için IMMEDIATE işlemler orada sınanamaz.
- **2026-11-01, G11 — uygulama ayrıntıları (bulut oturumu):**
  - `MemberStatus(member, open_loans, balance_kurus, blockers)`: `blockers` üyenin kendi engelleridir (nüsha engeli dışındaki hepsi; durum `copy_status="ON_SHELF"` ile hesaplanır). `CheckoutPreview(copy, due_on, blockers)`; son tarih bulunamazsa önizleme de `NoOpenDayError` verir. `open_loans` son tarihe, sonra id'ye göre sıralıdır.
  - Plandaki arayüzlere ek servisler: `copies_matching(q, status)` (`search_books` sonuçlarının verilen durumdaki nüshaları; ödünçte Rafta, iadede Ödünçte; FR-11 elle seçim) ve `get_loan(loan_id)` (uzatma view'ı için).
  - `check_out` engelleri işlem içinde veritabanından yeniden okur (S2, S3). Kısmi benzersiz indeksin `IntegrityError`'ı "Nüsha rafta değil" olarak `RuleViolation`'a çevrilir (data-design §5'teki ikinci güvence); IMMEDIATE işlemlerde bu dala ulaşılmaz, TC-145 ikinci isteğin engelden döndüğünü gösterir.
  - `renew` mesajları (plan vermiyordu): bilinmeyen ödünç "Ödünç bulunamadı", kapanmış ödünç "Ödünç kapanmış" (TC-144). Uzatma engelleri de "; " ile birleştirilir.
  - Ödünç, iade, uzatma ve pasifleştirme denetim kaydı yazmaz (faz 4 küçük karar 8'deki listede yoklar); gecikme cezası `billing.post_charge` ile ödünce ve üyeye bağlı FINE olarak yazılır.
  - **Ödünç ekranı:** Tek bir GET formu `uye` ve (üye açıksa) `nusha` alanlarını taşır; "Getir" düğmesi JS'siz kullanım içindir. Üye açık değilken `uye`, açıkken `nusha`, önizlemede "Onayla" düğmesi `autofocus` alır; üye açıkken `uye` alanında `data-next-focus="id_nusha"` vardır. Onay formu POST'tur ve `uye`, `nusha` gizli alanlarını taşır; üyenin ya da nüshanın engeli varsa görünmez. 18 haneden uzun ya da rakam olmayan üye no "Üye bulunamadı" verir (SQLite tam sayı sınırı; G06 ile aynı). Anonimleştirilmiş üye "Anonimleştirilmiş üye" adıyla ve "Üye pasif" engeliyle açılır. Başarılı POST 303 döner (`HttpResponseRedirect`, durum 303).
  - **Uzatma yolu:** POST `/odunc/<id>/uzat/` gizli `next` alanını taşır (üye ayrıntısı ya da ödünç ekranı); güvenli yerel adres değilse ödünç ekranına (`/odunc/?uye=<no>`) döner. Kural ihlalinde ödünç ekranı o üyeyle 200 ve mesajla gösterilir: view'lar başka bir app'in view modülünü import edemez (KL-22) ve ödünç ekranı da açık ödünçleri "Uzat" düğmeleriyle listeler. Açık ödünç listesi `circulation/templates/circulation/_loans.html` parçasıdır; ödünç ekranı ve üye ayrıntısı bunu kullanır. Uzatılmış ödünçte düğme yerine "Uzatıldı (GG.AA.YYYY)" yazar.
  - **İade ekranı:** Form POST'tur; boş POST boş formu gösterir. 8 haneli olmayan girişte `copies_matching(q, ON_LOAN)` sonuçları satır başına bir "İade al" POST formuyla listelenir; sonuç yoksa "Nüsha bulunamadı".
  - **`scan.js`:** Sayfa yüklenince (ve tarayıcı önbellekten geri dönünce) `autofocus` öğesine odaklanır ve metnini seçer; `data-next-focus` alanında Enter, hedef aynı formda ve boşsa formu göndermek yerine odağı hedefe taşır. Formlar JS'siz çalışır.
  - **Üye ayrıntısı:** "Ödünç ve borç" bölümü bakiyeyi, `/borclar/<no>/` bağlantısını ve açık ödünç listesini gösterir. Pasifleştirme formu yalnız aktif ve anonimleştirilmemiş üyede görünür (kullanıcı kararı 2026-11-01). Onay kutusu (`confirm_debt`) plandaki gibi yalnız borç nedeniyle yapılan retten sonra, formla birlikte yeniden gösterilir; bütün retler ayrıntıyı 200 ve mesajla yeniden çizer (G04 D4).
  - G11'in dosya listesi dışında değişenler: `members/views.py`, `members/urls.py` ve `members/templates/members/detail.html` (plan Davranış'ta), `library_site/urls.py` (`circulation.urls`, `catalog.urls`'ten sonra), `templates/base.html` ve `administration/home.html` ("Ödünç" ve "İade" bağlantıları; G03 §11 kuralı), `tests/support/urls.py`.
  - `tests/support/urls.py`'deki G02 yer tutucusu (`/odunc/`) kaldırıldı: gerçek ödünç ekranı yolu artık karşılıyor; modül ürünün URL listesini aynen verir, G02 testleri `@pytest.mark.urls` işaretleriyle değişmeden geçer.
  - `make_loan` G09'da eklendi (yukarıda).
- **2026-11-01, G12 — uygulama ayrıntıları (bulut oturumu):**
  - Her servis önce kendi ele aldığı kaynak durumu denetler (kayıp/hasar: Ödünçte; `mark_shelf_copy`: Rafta; `mark_found`: Kayıp; `repair`: Hasarlı; `withdraw`: Hasarlı ya da Kayıp), sonra `check_transition` ile geçişi ve rolü doğrular. Kaynak durum servise uymuyorsa da aynı `InvalidTransition` mesajı verilir; bunun için `circulation.domain.transition_error(eski, yeni)` eklendi (TC-164: Ödünçteki nüshada `mark_shelf_copy`, tabloda geçerli bir geçiş olsa da reddedilir). `check_transition`'ın döndürdüğü rol yönetici ise ve aktör yönetici değilse `PermissionDenied` verilir; yönetici servisleri ayrıca `require_role(Role.ADMIN)` taşır.
  - Kayıp ve hasarda negatif bedel "Bedel negatif olamaz" ile reddedilir. Ödünçteki nüsha için bedel alanı formda zorunludur: boş bırakılırsa "Bedel girin (bedel yoksa 0)" verilir (0 bilerek girilir; KL-7). COPY_LOST ve COPY_DAMAGED ayrıntısı ödünçteki nüshada `fee_kurus`'u (0 dahil) taşır; raftaki nüshada taşımaz (KL-15'teki "?"). `mark_found`'un ayrıntısında `note` boştur (servisin not parametresi yok).
  - `mark_found` bedeli `billing.services.loan_fee(loan)` ile bulur (plandaki arayüze ek; ödüncün ilk FEE kalemi). Otomatik iptal yalnız `COPY_FOUND` ile izlenir (G09 maddesi).
  - Plandaki arayüzlere ek: `copy_loans(copy)` (nüsha ekranındaki ödünç geçmişi; ödünç tarihine göre en yeniden başlar).
  - **Nüsha ekranı:** Durum ve role göre gösterilen işlemler: Rafta → yönetici Kayıp, Hasarlı, Kayıttan düş; Ödünçte → yönetici bedel alanlı Kayıp ve Hasarlı; Kayıp → herkes Bulundu, yönetici Kayıttan düş; Hasarlı → yönetici Onarıldı ve Kayıttan düş; Kayıttan düşmüş → işlem yok. `/kayip/` ve `/hasarli/` nüsha Ödünçteyse `mark_lost`/`mark_damaged`, değilse `mark_shelf_copy`'yi; `/kayittan-dus/` Raftaysa `mark_shelf_copy(WITHDRAWN)`, değilse `withdraw`'u çağırır. Başarı 303 ile nüsha ekranına döner ve mesaj gösterir; kural ihlali ekranı 200 ve mesajla yeniden çizer; bilinmeyen barkod GET ve POST'ta 404 verir. Ekranda açık ödünç (üye bağlantısı, son tarih) ve ödünç geçmişi (kapanış nedeni ve varsa bulunma tarihi) bulunur.
  - Bulundu mesajı: iptal edilen tutar varsa "Nüsha bulundu olarak işaretlendi; <tutar> ödenmemiş bedel iptal edildi"; iade edilebilir tutar varsa ikinci mesaj "Ödenmiş <tutar> para iadesi için üyenin borç sayfasında: Borç dökümü" ve `/borclar/<no>/` bağlantısı (plandaki metne bağlantı metni eklendi; mesaj `format_html` ile güvenli HTML'dir). Üye, nüshanın en son ödüncünden okunur.
  - G12'nin dosya listesi dışında değişenler: `circulation/forms.py` (`CopyMarkForm`, `NoteForm`), `billing/services.py` (`loan_fee`), `catalog/templates/catalog/detail.html` (her barkod nüsha ekranına bağlantı; G12 ekranına katalogdan ulaşılsın diye).
  - `library_site/urls.py`'de `catalog.urls` `circulation.urls`'ten önce durur; `/nushalar/etiket/` hâlâ etiket ekranına gider (test: `test_label_route_still_wins_over_the_barcode_route`).
- **2026-10-31, G05–G08 uygulayıcının seçtiği kullanıcıya görünen metinler:** Plan, SRS, KL ya da ADR'nin vermediği ve uygulayıcının seçtiği kullanıcıya görünen metinler (2026-11-01 kullanıcı kararı; PR'da onaylanır). Kullanıcı 2026-11-01'de PR #2 incelemesinde hepsini onayladı; metin değiştirilmedi. G02–G04 listesinde zaten onaylı olup aynen yeniden kullanılanlar "(G02–G04'te onaylı)" ile işaretlidir.
  - G06:
    - "Üyeler": `templates/base.html` üst menü bağlantısı; `administration/home.html` modül bağlantısı; `members/search.html` sayfa başlığı; `members/form.html` ve `members/detail.html` geri bağlantısı.
    - "Yeni üye": `members/search.html` bağlantı; `members/form.html` sayfa başlığı.
    - "Üye no, ad soyad ya da telefon": `members/search.html`, arama alanı etiketi.
    - "Ara": `members/search.html`, düğme.
    - "Üye no": `members/search.html`, sütun başlığı.
    - "Ad soyad" (G02–G04'te onaylı): `members/forms.py` `MemberForm` alan etiketi; `members/search.html` sütun başlığı; `members/detail.html` satır başlığı.
    - "Telefon": `members/forms.py` `MemberForm` alan etiketi; `members/search.html` sütun başlığı; `members/detail.html` satır başlığı.
    - "E-posta": `members/forms.py` `MemberForm` alan etiketi; `members/detail.html` satır başlığı.
    - "Durum", "Aktif", "Pasif" (G02–G04'te onaylı): `members/search.html` ve `members/detail.html`; pasif üyede "Pasif (GG.AA.YYYY)" pasifleştirme tarihiyle.
    - "Anonimleştirilmiş üye": `members/search.html` ad yerine; `members/detail.html` ("Anonimleştirilmiş üye · Pasif").
    - "Sonuç yok.": `members/search.html`, boş sonuç.
    - "Üye N": `members/detail.html` sayfa başlığı; `members/form.html` düzenleme ekranının `<title>`'ı ve geri bağlantısı.
    - "Üyeyi düzenle": `members/form.html`, düzenleme ekranı başlığı.
    - "Kaydet" (G02–G04'te onaylı): `members/form.html`, düğme.
    - "Düzenle": `members/detail.html`, bağlantı.
    - "—": `members/detail.html`, e-posta ya da rıza tarihi yoksa.
    - "E-posta rızası": `members/detail.html`, bölüm başlığı.
    - "Rıza: var" / "Rıza: yok": `members/detail.html`, geçerli durum.
    - "Son verme:" ve "Son geri alma:": `members/detail.html`, rıza tarihleri.
    - "Tarih" (G02–G04'te onaylı): `members/forms.py` `ConsentForm` alan etiketi.
    - "Rıza ver" ve "Rızayı geri al": `members/detail.html` düğmeleri; `members/forms.py` `ConsentForm.given` seçenekleri.
    - "Rıza verildi" ve "Rıza geri alındı": `members/models.py` `ConsentAction` etiketleri.
    - "Üye kaydedildi": `members/views.py` `member_create`, başarı mesajı.
    - "Üye bilgileri kaydedildi": `members/views.py` `member_edit`, başarı mesajı.
    - "Üye aktifleştirildi": `members/views.py` `member_reactivate`, başarı mesajı.
    - "Rıza kaydedildi" ve "Rıza geri alındı": `members/views.py` `member_consent`, başarı mesajları.
    - "Ad soyad boş olamaz" (G02–G04'te onaylı): `members/domain.py` `validate_member_fields`, `RuleViolation`.
    - "Ad soyad en fazla 200 karakter olabilir": `members/domain.py` `validate_member_fields`, `RuleViolation`.
    - "Telefon boş olamaz": `members/domain.py` `validate_member_fields`, `RuleViolation`.
    - "Telefon en fazla 30 karakter olabilir": `members/domain.py` `validate_member_fields`, `RuleViolation`.
    - "Telefon 1 ile 20 rakam içermeli": `members/domain.py` `validate_member_fields`, `RuleViolation`.
    - "Geçerli bir e-posta adresi girin": `members/services.py` `_clean_email`, `RuleViolation`.
    - "Anonimleştirilmiş üye güncellenemez": `members/services.py` `update_member`, `RuleViolation` (davranış oturumda kullanıcı kararıyla; metin onay bekliyor).
  - G07:
    - "Kitaplar": `templates/base.html` üst menü bağlantısı; `administration/home.html` modül bağlantısı; `catalog/search.html` sayfa başlığı; `catalog/form.html` ve `catalog/detail.html` geri bağlantısı.
    - "Yeni kitap": `catalog/search.html` bağlantı; `catalog/form.html` sayfa başlığı.
    - "Başlık, yazar, ISBN ya da barkod": `catalog/search.html`, arama alanı etiketi.
    - "Ara", "Sonuç yok.", "Düzenle", "—" (G06'daki gibi): `catalog/search.html` ve `catalog/detail.html`.
    - "Başlık": `catalog/forms.py` `BookForm` alan etiketi; `catalog/search.html` sütun başlığı.
    - "Yazar", "ISBN", "Yıl": `catalog/forms.py` `BookForm` alan etiketleri; `catalog/search.html` sütun başlıkları; `catalog/detail.html` satır başlıkları.
    - "Yayınevi": `catalog/forms.py` `BookForm` alan etiketi; `catalog/detail.html` satır başlığı.
    - "Rafta / Toplam": `catalog/search.html`, sütun başlığı.
    - "Nüsha NNNNNNNN: <başlık> · <durum>": `catalog/search.html`, barkod eşleşmesi satırı.
    - "Kitabı düzenle": `catalog/form.html`, düzenleme ekranı başlığı (`<title>` kitabın başlığıdır).
    - "Kaydet" (G02–G04'te onaylı): `catalog/form.html`, düğme.
    - "Öneriyi kabul et ve kaydet": `catalog/form.html`, `isbn_accept` düğmesi.
    - "Nüshalar": `catalog/detail.html`, bölüm başlığı.
    - "Barkod", "Durum": `catalog/detail.html`, nüsha tablosu sütun başlıkları.
    - "Nüsha yok.": `catalog/detail.html`, boş nüsha listesi.
    - "Nüsha ekle": `catalog/detail.html`, bölüm başlığı.
    - "Nüsha sayısı": `catalog/forms.py` `AddCopiesForm` alan etiketi.
    - "Ekle" (G02–G04'te onaylı): `catalog/detail.html`, düğme.
    - "Kitap kaydedildi": `catalog/views.py` `book_create`, başarı mesajı.
    - "Kitap bilgileri kaydedildi": `catalog/views.py` `book_edit`, başarı mesajı.
    - "N nüsha eklendi": `catalog/views.py` `book_add_copies`, başarı mesajı.
    - "Kitap bulunamadı": `catalog/views.py` `_get_book`, 404 nedeni (yalnız `DEBUG` açıkken görünür).
    - "Başlık boş olamaz", "Yazar boş olamaz": `catalog/services.py` `_clean_book`, `RuleViolation` (TC-61).
    - "Başlık en fazla 300 karakter olabilir", "Yazar en fazla 300 karakter olabilir", "Yayınevi en fazla 200 karakter olabilir": `catalog/services.py` `_clean_book`, `RuleViolation`.
    - "Yıl 1 ile 9999 arasında olmalı": `catalog/services.py` `_clean_book`, `RuleViolation`.
    - "Nüsha sayısı 1 ile 50 arasında olmalı": `catalog/services.py` `add_copies`, `RuleViolation` (TC-262).
  - G08:
    - "Nüsha etiketleri": `catalog/search.html` bağlantı; `catalog/label_range.html` sayfa başlığı.
    - "Üye kartları": `members/search.html` bağlantı; `members/card_range.html` sayfa başlığı.
    - "Başlangıç barkodu" ve "Bitiş barkodu": `catalog/forms.py` `LabelSelectionForm` alan etiketleri.
    - "Başlangıç üye no" ve "Bitiş üye no": `members/forms.py` `CardSelectionForm` alan etiketleri.
    - "Aralıkta kayıttan düşmüş nüshalar atlanır; bir seferde en fazla 240 etiket (10 sayfa) basılır.": `catalog/label_range.html`, not.
    - "Aralıkta pasif ve anonimleştirilmiş üyeler atlanır; bir seferde en fazla 240 kart basılır.": `members/card_range.html`, not.
    - "Başlangıç ve bitiş 8 haneli barkod olmalı": `catalog/services.py` `copies_for_labels`, `RuleViolation`.
    - "Başlangıç ve bitiş pozitif üye no olmalı": `members/services.py` `members_for_cards`, `RuleViolation`.
    - "Geçersiz seçim": `administration/forms.py` `IntListField`, alan hatası.
    - "Etiket bas" ve "Kart bas" ADR-0036'dan gelir; aralık formlarının düğmesinde de aynı metin kullanıldı.
- **2026-11-01, G09–G12 uygulayıcının seçtiği kullanıcıya görünen metinler:** Plan, SRS, KL ya da ADR'nin vermediği ve uygulayıcının seçtiği kullanıcıya görünen metinler (2026-11-01 kullanıcı kararı; PR'da onaylanır). Kullanıcı 2026-11-01'de PR #3 incelemesinde hepsini onayladı; metin değiştirilmedi. Önceki listelerde onaylı olup aynen kullanılanlar "(onaylı)" ile işaretlidir.
  - G09:
    - "Borç dökümü": `billing/statement.html`, sayfa başlığı ve `<title>` ("Borç dökümü · Üye N · Kütüphane").
    - "Üye N" (onaylı): `billing/statement.html`, üye ayrıntısına geri bağlantı.
    - "Güncel borç: <tutar>": `billing/statement.html`, bakiye satırı.
    - "Tarih", "Personel" (onaylı), "Tür", "Tutar", "Ödenmemiş", "Gerekçe": `billing/statement.html`, döküm tablosu sütun başlıkları; "—" (onaylı) boş hücrede.
    - "Hareket yok.": `billing/statement.html`, boş döküm.
    - "Ödeme al": `billing/statement.html`, bölüm başlığı. "Ödemeyi kaydet": düğme.
    - "Tutar (TL)": `billing/forms.py` `PaymentForm`, `WaiverForm`, `RefundForm` alan etiketi; `billing/statement.html` para iadesi satırı.
    - "Af" (onaylı, `AuditAction` etiketi): `billing/statement.html`, bölüm başlığı. "Kalem" ve "Gerekçe": `billing/forms.py` `WaiverForm` alan etiketleri. "Affet": düğme.
    - "<Tür> · GG.AA.YYYY · <tutar> (ödenmemiş <tutar>)": `billing/views.py` `_charge_choices`, af formundaki kalem seçeneği.
    - "Para iadesi" (onaylı, `AuditAction` etiketi): `billing/statement.html`, bölüm başlığı. "Bedel (GG.AA.YYYY, <tutar>): iade edilebilir <tutar>": satır metni. "Para iadesi yap": düğme.
    - "Bedel iptali" (onaylı, `AuditAction` etiketi): `billing/statement.html`, bölüm başlığı. "Ödüncüyle bağı koparılmış bedeller; ödenmemiş kısmın tamamı iptal edilir.": not. "Bedel (GG.AA.YYYY, <tutar>): ödenmemiş <tutar>": satır metni. "Gerekçe": `CancelForm` alan etiketi. "İptal et": düğme.
    - "Ödeme alındı: <tutar>", "Af kaydedildi: <tutar>", "Para iadesi kaydedildi: <tutar>", "Bedel iptal edildi: <tutar>": `billing/views.py`, başarı mesajları.
    - "Ödeme tutarı 0,00 TL'den büyük olmalı": `billing/services.py` `record_payment`, `RuleViolation`.
    - "Af tutarı 0,00 TL'den büyük olmalı" ve "Yalnız ceza ve bedel kalemleri affedilebilir": `billing/services.py` `waive`, `RuleViolation`.
    - "Para iadesi tutarı 0,00 TL'den büyük olmalı": `billing/services.py` `refund`, `RuleViolation`.
    - "Yalnız bedel kalemleri iptal edilebilir": `billing/services.py` `cancel_fee_manual`, `RuleViolation`.
    - "Kalem bulunamadı": `billing/services.py` `get_entry`, `RuleViolation`.
    - "Üye bulunamadı" (onaylı): `billing/views.py`, bilinmeyen üye no'da 404 nedeni.
    - "5,00 TL" biçimi: `administration/templatetags/audit.py` `details_text`, denetim listesinde `amount_kurus` ve `fee_kurus` değerleri (kullanıcı kararı, yukarıda).
  - G11:
    - "Ödünç": `templates/base.html` üst menü bağlantısı; `administration/home.html` modül bağlantısı; `circulation/checkout.html` sayfa başlığı.
    - "İade": `templates/base.html` üst menü bağlantısı; `administration/home.html` modül bağlantısı; `circulation/checkin.html` sayfa başlığı.
    - "Üye kartı, üye no, telefon ya da ad": `circulation/checkout.html`, üye alanı etiketi.
    - "Nüsha barkodu ya da kitap": `circulation/checkout.html` ve `circulation/checkin.html`, nüsha alanı etiketi.
    - "Getir": `circulation/checkout.html`, GET formunun düğmesi.
    - "Üyeler" (onaylı): `circulation/checkout.html`, üye arama sonuçları başlığı; satır "Üye N · <ad soyad> · <telefon>" ve pasifse " · Pasif"; anonimde "Anonimleştirilmiş üye" (onaylı).
    - "Üye N" (onaylı) ve "<ad soyad> · Borç: <tutar>": `circulation/checkout.html`, üye paneli.
    - "Açık ödünçler": `circulation/checkout.html` ve `members/detail.html`, bölüm başlığı.
    - "Barkod", "Başlık" (onaylı), "Son tarih": `circulation/_loans.html`, sütun başlıkları.
    - "Uzatıldı (GG.AA.YYYY)": `circulation/_loans.html`, uzatılmış ödünç.
    - "Açık ödünç yok.": `circulation/_loans.html`, boş liste.
    - "Raftaki nüshalar": `circulation/checkout.html`, nüsha arama sonuçları başlığı; satır "<barkod> · <başlık> · <yazar>".
    - "Nüsha NNNNNNNN · <durum>": `circulation/checkout.html`, önizleme.
    - "Ödünçteki nüshalar": `circulation/checkin.html`, arama sonuçları başlığı; "Yazar" (onaylı) sütun başlığı.
    - "Uzatıldı; yeni son tarih GG.AA.YYYY": `circulation/views.py` `renew`, başarı mesajı.
    - "Ödünç bulunamadı": `circulation/services.py` `renew`, `RuleViolation`; `circulation/views.py` `renew`, 404 nedeni.
    - "Ödünç kapanmış": `circulation/services.py` `renew`, `RuleViolation`.
    - "Ödünç ve borç": `members/detail.html`, bölüm başlığı. "Borç: <tutar>": bakiye satırı. "Borç dökümü": `/borclar/<no>/` bağlantısı.
    - "Borç olduğunu biliyorum; üyeyi yine de pasifleştir": `members/detail.html`, `confirm_debt` onay kutusu etiketi.
    - "Pasifleştir" (onaylı): `members/detail.html`, düğme.
    - "Üye pasifleştirildi": `members/views.py` `member_deactivate`, başarı mesajı.
    - "Anonimleştirilmiş üye pasifleştirilemez" ve "Üye zaten pasif": `circulation/services.py` `deactivate_member`, `RuleViolation` (davranış ve metin 2026-11-01 kullanıcı kararıyla verildi; listede bilgi için).
    - Planın verdiği metinler listede yoktur: "Uzat", "Onayla", "İade al", "Son tarih 16.11.2026", "İade alındı", "İade alındı; 15,00 TL ceza yazıldı", "Bu bir nüsha barkodu. Üye kartını okutun.", KL-6 mesajları.
  - G12:
    - "Nüsha NNNNNNNN": `circulation/copy_detail.html`, sayfa başlığı ve `<title>`; kitap başlığı geri bağlantısı.
    - "Başlık", "Yazar", "Durum" (onaylı): `circulation/copy_detail.html`, satır başlıkları.
    - "Ödünç": `circulation/copy_detail.html`, açık ödünç satırı ("Üye N · Son tarih GG.AA.YYYY") ve ödünç geçmişi sütun başlığı.
    - "İşlemler": `circulation/copy_detail.html`, bölüm başlığı.
    - "Bedel (TL)" ve "Not" (onaylı): `circulation/forms.py` ve `circulation/copy_detail.html`, alan etiketleri.
    - "Kayıp", "Hasarlı", "Bulundu", "Onarıldı", "Kayıttan düş": `circulation/copy_detail.html`, düğmeler (durum adları `CopyStatus` etiketleriyle aynı).
    - "Ödünç geçmişi": `circulation/copy_detail.html`, bölüm başlığı; sütunlar "Ödünç", "Üye", "Son tarih", "Kapanış", "Sonuç"; açık ödünçte "Açık", bulunan kayıpta " · bulundu GG.AA.YYYY"; boş listede "Ödünç yok.".
    - "İade edildi", "Kayıp", "Hasarlı": `circulation/models.py` `CloseReason` etiketleri (G10).
    - "Nüsha kayıp olarak işaretlendi", "Nüsha hasarlı olarak işaretlendi", "Nüsha onarıldı olarak işaretlendi", "Nüsha kayıttan düşüldü", "Nüsha bulundu olarak işaretlendi" ve "; <tutar> ödenmemiş bedel iptal edildi": `circulation/views.py`, başarı mesajları.
    - "Ödenmiş <tutar> para iadesi için üyenin borç sayfasında" planın metnidir; ardındaki ": Borç dökümü" bağlantı metni uygulayıcı seçimidir (`circulation/views.py` `copy_found`).
    - "Bedel girin (bedel yoksa 0)": `circulation/views.py` `_mark`, ödünçteki nüshada boş bedel.
    - "Bedel negatif olamaz": `circulation/services.py` `_mark_loaned_copy`, `RuleViolation`.
    - "Bu durum değişikliği yapılamaz: <eski> → <yeni>" plandandır; durumlar Türkçe etiketleriyle yazılır (G10 maddesi).
- **2026-11-01, G13 — açılıştan önce verilen kararlar (kullanıcı onayı 2026-11-01):**
  - **Kritik:** [ADR-0052](../decisions/0052-smtp-timeout.md). `library_site/settings/prod.py`'ye `EMAIL_TIMEOUT = 10` (saniye) eklenir. Django'nun varsayılanı `None`'dır; SMTP yanıt vermezse elle hatırlatma bir waitress iş parçacığını, `send_reminders` zamanlayıcı iş parçacığını (KL-5) süresiz kilitler. Zaman aşımı `OSError` olarak FAILED kaydına düşer ve pencere içinde yeniden denenir (faz 3 küçük karar 7). Reddedilenler: 30 saniye, `LIBRARY_EMAIL_TIMEOUT` ortam değişkeni, varsayılanı korumak. G13'ün "Dosyalar" satırına `prod.py` eklendi; bir ayar testi değeri sabitler.
  - **Küçük kararlar:**
    1. Elle hatırlatma POST'u PRG ile `/gecikenler/`e döner (G11'deki `messages` geleneği). Seçilen her ödünç için bir mesaj gösterilir: "<üye no> <ad>, <kitap>: gönderildi | rıza yok | e-posta yok | gönderilemedi | gecikmemiş". `sent` başarı mesajıdır, diğerleri uyarıdır.
    2. Boş seçimde liste 200 ile yeniden gösterilir ve "Hatırlatma göndermek için en az bir ödünç seçin" hata mesajı çıkar (uygulayıcı seçimi; G13 metin listesinde).
    3. `send_manual_reminders`, `send_due_reminders` ile aynı akışı izler: yetki denetimi, e-posta, ardından `reminder_log` kendi işleminde yazılır. SMTP sırasında açık `transaction.atomic()` olmaz. Bu, §4.0'daki "her genel servis tek bir `transaction.atomic()`" kuralının bilinçli istisnasıdır (data-design §5, architecture §10).
    4. E-postadaki `daily_fine` ve `fine_cap` ödüncün kopyalarından gelir (`Loan.daily_fine_kurus`, `fine_cap_kurus`; ADR-0023), güncel ayardan değil. `library_name` ayarlardan gelir.
    5. Yalnız `smtplib.SMTPException` ve `OSError` FAILED olarak yakalanır; `error` = `f"{type(exc).__name__}: {exc}"[:500]`. Diğer istisnalar yükselir.
    6. Base menüsüne ve ana sayfaya "Gecikenler" bağlantısı eklenir (G11'deki "Ödünç" ve "İade" gibi).
    7. `send_reminders --date` geçersizse `CommandError("Geçersiz tarih: …")` verilir.
  - Elle hatırlatma denetim kaydı yazmaz; kaydı `reminder_log.triggered_by` tutar. `AuditAction` 14 değerde kalır (KL-30).
- **2026-11-01, G13 — uygulama ayrıntıları (bulut oturumu):**
  - `notifications` app'i `INSTALLED_APPS`'e (`library_site/settings/base.py`), `notifications.urls` `library_site/urls.py`'ye (`billing.urls`'ten sonra) eklendi; ikisi de dosya listesinde yoktu (G09'daki `billing` gibi).
  - **Plandaki arayüzlere ek:**
    - `notifications.services.overdue_list(today) -> list[OverdueEntry(row, block)]`: `circulation.services.overdue_loans` satırlarına "rıza yok"/"e-posta yok" işaretini (`block`: `no_email`, `no_consent` ya da None) ekler; view ORM'e dokunmasın diye.
    - `ManualResult` alanlarına `member_no`, `full_name` ve `title` eklendi (G13 küçük karar 1'deki mesaj için).
    - Domain: `due_ranges(today)` (S6'daki iki `due_on` aralığı), `contact_block(has_email, has_consent)` (önce e-posta, sonra rıza), `OUTCOME_LABELS`, `counts_text(counts)` (KL-23 metni), `error_text(exc)` (küçük karar 5). `ReminderCounts` domain'dedir.
  - **Model:** `ReminderLog`, `db_table = "reminder_log"`. CHECK'ler `kind` ve `status` değerleri içindir; kısmi benzersiz indeks `reminder_log_one_sent_per_due` (`loan`, `kind`, `due_on`; `status = 'SENT' AND kind <> 'MANUAL'`). `loan` ve `triggered_by` `PROTECT`'tir. `sent_at`, `save()` içinde `timezone.now()` ile yazılır (G07'deki `Copy.status_changed_at` gibi). `ReminderKind` plandaki gibi `notifications/domain.py`'de bir `TextChoices`'tur; model onu import eder.
  - **Otomatik adaylar (S6):** Açık ödünç, `due_on` pencerede, üye aktif, rızalı ve e-postası dolu (NULL ve boş metin dışlanır), o tür ve ödüncün güncel `due_on`'u için SENT kaydı yok. Her aday için önce e-posta, sonra kayıt kendi `transaction.atomic()`'inde yazılır; `IntegrityError` `skipped` sayılır. FAILED kayıtlar tekrar engeline girmez (küçük karar 7).
  - **Elle hatırlatma:** Kimlikler sırası korunarak tekilleştirilir. Bilinmeyen bir kimlik varsa hiçbir e-posta gönderilmeden `RuleViolation("Ödünç bulunamadı")` fırlatılır (G11'deki onaylı mesaj); view sayısal olmayan değeri de aynı mesajla reddeder ve listeyi 200 ile gösterir. Denetim sırası: kapanmış ya da `due_on >= bugün` → `not_overdue` (listeyle aynı ölçüt: kapalı günler yüzünden 0 gecikme günlü bir ödünç de listede olduğu için gecikmiş sayılır), sonra e-posta, sonra rıza. Üyesi olmayan ödünç `no_email` sayılır; açık ödüncün bağı kopmadığı için bu dala ulaşılmaz (`notifications/services.py`'nin kapsanmayan tek satırı).
  - **Komut:** Sayımlar stdout'a yazılır; en az bir FAILED varsa ardından `CommandError("<n> hatırlatma gönderilemedi", returncode=1)` verilir (çıkış kodu 1, KL-23). `--date` `strptime("%Y-%m-%d")` ile katı okunur; geçersizse `job_run` satırı yazılmadan `CommandError("Geçersiz tarih: …")` (çıkış 1).
  - **E-posta şablonları:** Düz metindir ve `{% autoescape off %}` kullanır; başlıktaki `&` ve tırnaklar HTML'e çevrilmez (test sabitler). Konu tek satıra indirilir. Gövde imzadan sonra bir satır sonuyla biter. Gönderen `DEFAULT_FROM_EMAIL`'dir; üretimde `LIBRARY_EMAIL_FROM`, dev ve testte Django varsayılanı.
  - **Ekran:** Başarılı POST 303 ile `/gecikenler/`e döner (G11 geleneği). Üye no üye ayrıntısına bağlantıdır; telefon yoksa "—". Hatırlatma uyarıları için `static/css/app.css`'e `.message-warning` (uyarı rengi), etiketler için `.tag`, sayı sütunları için `.num` eklendi.
  - **Testler:** Komut testleri KL-11'deki üç dosyaya ek olarak `notifications/tests/test_commands.py`'dedir (komut düzeyi TC'ler: TC-180, TC-185, TC-295). TC-181'deki eşzamanlı çalışma, `services._send` sırasında aynı SENT kaydını yazan bir yama ile canlandırılır. Küçük karar 3, `django_db(transaction=True)` ile SMTP sırasında `connection.in_atomic_block`'un False olduğunu doğrulayan bir testle sabitlenir. ADR-0052'nin değeri `tests/test_prod_settings.py`'de ayrı süreçte sabitlenir. `tests/test_authorization.py`'deki `CLERK_ROUTES_NOT_ADMIN` kümesine `gecikenler/` ve `gecikenler/hatirlat/` eklendi.
  - G13'ün dosya listesi dışında değişenler: `library_site/settings/base.py`, `library_site/urls.py`, `templates/base.html` ve `administration/templates/administration/home.html` ("Gecikenler" bağlantıları; küçük karar 6), `static/css/app.css`, `tests/test_authorization.py`, `tests/test_prod_settings.py`.
- **2026-11-01, G13 uygulayıcının seçtiği kullanıcıya görünen metinler:** Plan, SRS, KL, ADR ya da açılış kararlarının vermediği metinler (2026-11-01 kullanıcı kararı; PR'da onaylanır). Kullanıcı 2026-11-01'de PR #4 incelemesinde hepsini onayladı; metin değiştirilmedi. Planın, KL-13'ün ve kullanıcı kararlarının verdiği metinler (e-posta konu ve gövdeleri, "rıza yok", "e-posta yok", "gönderildi", "gönderilemedi", "gecikmemiş", mesaj biçimi "<üye no> <ad>, <kitap>: …", "Geçersiz tarih: …", "gönderilen=…, başarısız=…, atlanan=…") listede yoktur. Önceki listelerde onaylı olup aynen kullanılanlar "(onaylı)" ile işaretlidir.
  - "Gecikenler": `templates/base.html` üst menü bağlantısı; `administration/home.html` modül bağlantısı; `notifications/overdue.html` sayfa başlığı ve `<title>` ("Gecikenler · Kütüphane").
  - "Seç", "Üye", "Telefon", "Kitap", "Son tarih", "Gecikme (gün)", "Birikmiş ceza", "Hatırlatma": `notifications/overdue.html`, tablo sütun başlıkları.
  - "Seç: <kitap>": `notifications/overdue.html`, seçim kutusunun `aria-label`'ı.
  - "—" (onaylı): `notifications/overdue.html`, telefonu ya da üyesi olmayan satır.
  - "Hatırlatma gönder": `notifications/overdue.html`, düğme (TC-183'teki adla).
  - "Geciken ödünç yok.": `notifications/overdue.html`, boş liste.
  - "Hatırlatma göndermek için en az bir ödünç seçin": `notifications/views.py` `EMPTY_SELECTION`, boş seçim hatası (küçük karar 2).
  - "Ödünç bulunamadı" (onaylı, G11): `notifications/services.py` `send_manual_reminders` ve `notifications/views.py` `_loan_ids`, bilinmeyen ya da sayısal olmayan kimlik.
  - "<n> hatırlatma gönderilemedi": `notifications/management/commands/send_reminders.py`, en az bir FAILED varsa `CommandError` (stderr'de "CommandError: …").
  - "Son tarihi yaklaşan ve geciken ödünçler için hatırlatma e-postalarını gönderir." ve "YYYY-MM-DD; varsayılan bugün": `send_reminders.py`, `--help` metinleri.
  - Arayüzde şimdilik görünmeyen etiketler: `ReminderKind` "Son tarih yaklaşıyor", "Gecikme", "Elle" (`notifications/domain.py`); `ReminderStatus` "Gönderildi", "Gönderilemedi" (`notifications/models.py`); app adı "Bildirimler" (`notifications/apps.py`).
- **2026-11-01, G14–G16 — açılıştan önce verilen kararlar (kullanıcı onayı 2026-11-01):**
  - **Kritik:**
    - [ADR-0053](../decisions/0053-hourly-catch-up.md), saatlik telafi (ADR-0007'ye ek): `jobs_due_for_catch_up` açılışa ek olarak bir `IntervalTrigger(hours=1)` göreviyle saatte bir de çalışır ve vadesi gelen görevleri aynı sırayla kuyruğa alır. Uygulama açıkken kaçan tetiklemeler (ör. sunucu 02:00'de uykudaydı) ve FAILED görevler en geç bir saat içinde telafi edilir; sürekli başarısız olan görevin saatte bir yeniden denenmesi kabul edildi. Cron ve telafi görevlerine `misfire_grace_time=3600` ve `coalesce=True` verilir. Cron ile telafinin çakışması komutlar idempotent olduğu için zararsızdır. Reddedilenler: yalnız geniş misfire toleransı; yalnız açılışta telafi (plandaki).
    - [ADR-0054](../decisions/0054-restore-keeps-pre-restore-copy.md), geri yükleme öncesi koruma kopyası: `restore_backup` mevcut veritabanını ve varsa `-wal`/`-shm` dosyalarını silmez, `<db>.pre-restore-YYYYMMDD-HHMMSS` (ve `…-wal`, `…-shm`) olarak yeniden adlandırır, sonra yeni dosyayı `os.replace` ile yerine koyar; mevcut dosya bozuk olsa da çalışır. Kopyanın yolu çıktıya yazılır, kopya otomatik silinmez. KVKK notu G19'da kurulum belgesine yazılır (G19 bölümüne satır eklendi). Plan G14 davranışındaki 5. adım değişti. Reddedilen: kopya bırakmamak.
    - [ADR-0055](../decisions/0055-reminder-log-error-cleared-on-unlink.md), hatırlatma kaydının hata metni temizlenir: G15'te bir ödüncün üye bağı koparılırken (ADR-0018) aynı işlemde o ödünce ait `reminder_log` satırlarının `error` alanı NULL yapılır; tür, durum ve tarihler kalır. Sebep: G13'ün sakladığı SMTP hata metni alıcının e-posta adresini içerebilir (NFR-08). Bu, architecture §3'e `operations → notifications` okunu ekler. Reddedilenler: G13'ün `error_text`'inde adres ayıklamak; olduğu gibi bırakmak.
  - **Küçük kararlar (onaylı):**
    1. Komutlar: `backup_db [--date YYYY-MM-DD]`, `export_backup [--date …] [--passphrase-file PATH]` (verilmezse `LIBRARY_EXPORT_PASSPHRASE_FILE`), `anonymize_expired [--date …]`. Tarih geçersizse `job_run` yazılmadan `CommandError("Geçersiz tarih: …")` verilir (G13 geleneği).
    2. `restore_backup` dosya türünü uzantıdan değil `LIBX` magic baytından anlar. `.libx` dosyası `--passphrase-file` olmadan verilirse `LIBRARY_EXPORT_PASSPHRASE_FILE` kullanılır; ikisi de yoksa çıkış 1.
    3. Geri yükleme migration çalıştırmaz. Başarı çıktısı "gerekirse `python manage.py migrate` çalıştırın" notunu da yazar.
    4. Yedek ve dışa aktarma önce hedef klasörde bir `.tmp` dosyasına yazılır, ardından `os.replace` ile yerine konur. Hata olursa `.tmp` silinir. Aynı gün ikinci koşu dosyanın üzerine yazar. Geri yüklemenin geçici dosyası veritabanıyla aynı klasördedir.
    5. Zamanlayıcı tek işçili yürütücüyle çalışır (`ThreadPoolExecutor(max_workers=1)`, `max_instances=1`). Telafi sırası BACKUP → ANONYMIZE → EXPORT → REMINDERS böylece gerçekten korunur ve EXPORT taze yedeği görür.
    6. Zamanlayıcı her `call_command` çağrısını sarar. `CommandError` ve diğer istisnalar `logging.getLogger("operations.scheduler")` ile loglanır ve zamanlayıcıyı durdurmaz. `send_reminders`'ın FAILED varken verdiği `CommandError` da bu yolla yakalanır; `job_run` zaten SUCCESS'tir. `base.py`'ye stderr'e yazan küçük bir `LOGGING` ayarı eklenir; logger'lar `operations` ve `django`, seviye INFO. *Not:* Faz 4 küçük karar 14 log için stdout diyordu; bu onaylı kararla log stderr'e yazılır (biçim aynı: `%(asctime)s %(levelname)s %(name)s %(message)s`).
    7. `/uyeler/saklama/` için menüye yalnız yöneticinin gördüğü bir bağlantı eklenir. `tests/test_authorization.py` kümeleri güncellenir.
    8. Anonim üyenin adı her yerde "Anonimleştirilmiş üye" olarak görünür: listeler, ödünç geçmişi, defter, gecikenler. Bunu `Member.display_name` adlı tek bir özellik sağlar.
    9. `anonymize_expired` ilk istisnada durur. Önceki kayıtlar işlenmiş kalır, `job_run` FAILED olur, çıkış 1 olur (TC-207). Görev idempotent olduğu için sonraki koşu kaldığı yerden devam eder.
  - **Plana işlenenler:** G14, G15 ve G16 bölümlerinin "Dosyalar", "Arayüzler", "Davranış" ve "Testler" satırları; G19'a KVKK notu; §3'te ADR-0053…0055 (sıradaki numara 0056); §7'de yeni TC'ler. Yeni davranışların testleri `docs/test-plan.md`'de TC-320…TC-339 (G14: TC-320…TC-329, G15: TC-330…TC-334, G16: TC-335…TC-339).
  - Kilit testleri (TC-302, TC-313) bulutta yalnız Linux'ta (`fcntl`) koşar; Windows (`msvcrt`) koşusu yerel doğrulamada yapılır (R-15).
- **2026-11-01, G14–G16 — uygulama ayrıntıları (bulut oturumu):**
  - **G14:**
    - `operations` app'i `INSTALLED_APPS`'e eklendi (`library_site/settings/base.py`; G14 dosya listesine açılışta işlendi). App modeli yoktur, migration yoktur.
    - **Plana ek arayüzler:** domain `export_name(on)`, `passphrase_from_text(text)` (bir satır sonu atılır; boşsa `ValueError`); `backup.OperationError` (mesajı kullanıcıya olduğu gibi gösterilen beklenen hata), `BackupResult(path, deleted)`, `ExportResult(path, source, deleted)`, `RestoreResult(counts, pre_restore)`, `read_passphrase(path)`, `db_path()`, `KDF_PARAMS`; `libx.is_libx(data)`; `applock.AppLockError`, `lock_path(db_path)`, `release_app_lock(handle)`; `operations/cli.py` (`run_on_option`, `command_error`; G15'teki `anonymize_expired` de kullanır).
    - **Yedeğin kaynağı:** Yedek, Django bağlantısını değil veritabanı dosyasına açılan ayrı bir SQLite bağlantısını (`mode=rw`) kullanır. SQLite'ın yedek API'si, işlem içindeki bir kaynak bağlantıda sonsuza dek bekler; ayrı bir okuyucu ise yalnız commit edilmiş veriyi görür (TC-190). `mode=rw` sayesinde eksik veritabanı boş bir dosya yaratmaz. Yedek dosyası `journal_mode=DELETE`'e çevrilir; yanında `-wal` bulunmayan tek dosyadır.
    - **Klasörler:** Yedek ve dışa aktarma klasörü yoksa oluşturulmaz; "Yedek klasörü bulunamadı: <yol>" ya da "Dışa aktarma klasörü bulunamadı: <yol>" ile çıkış 1 (takılı olmayan bir diskin yerine sistem diskine yazılmasın diye). Eski dosyalar yalnız başarılı yazımdan sonra silinir.
    - **Dışa aktarma:** Önce parola dosyası, sonra en yeni yedek denetlenir. Parola dosyası `utf-8-sig` ile okunur; Windows Not Defteri'nin BOM'u parolaya girmez. `.tmp` yazımı `fsync` ile diske indirilir.
    - **`.libx` okuma:** `libx.decrypt`, başlıktaki n, r ve p değerlerini scrypt'ten önce sınırlar: n ikinin kuvveti ve ≤ 2^20, r ≤ 32, p ≤ 16, bellek ≤ 1 GiB. Değiştirilmiş bir başlık bellek tüketmeden "Parola hatalı ya da dosya bozuk" verir. Magic yanlışsa ya da dosya kısaysa aynı mesaj; sürüm baytı 1 değilse "Desteklenmeyen dosya sürümü".
    - **Geri yükleme:** Uygulama kilidi yalnız denetlenip bırakılmaz, geri yükleme bitene kadar tutulur; böylece geri yükleme sürerken uygulama başlatılamaz. `LIBX` ile başlamayan dosyalar ("LIBY" dahil) SQLite olarak denenir ve "Geçerli bir veritabanı yedeği değil: <yol>" ile reddedilir (TC-196). Geçici dosya `mkstemp` ile veritabanı klasöründe açılır (`<db>.restore-*.tmp`). Sayımlar doğrulama sırasında geçici dosyadan okunur. Ardından Django bağlantıları kapatılır, koruma kopyası alınır ve `os.replace` yapılır. Aynı saniyede alınan ikinci koruma kopyasının adı `…-HHMMSS-2` olur. Kilit dosyası (`<db>.app.lock`) silinmez.
    - **Kullanım hataları:** `--yes` argparse'ta `required=True`'dur. PATH ya da `--yes` eksikse komut satırında çıkış 2 olur. TC-200 bu yüzden alt süreçte `manage.py` ile doğrulanır; `call_command` kullanım hatasını `CommandError` olarak verir.
    - **Hata mesajları:** Beklenen hatalar (`OperationError`, `LibxError`) kendi mesajlarıyla gösterilir. Diğerleri "Yedek alınamadı: <tür>: <metin>", "Dışa aktarma yapılamadı: …" ya da "Geri yükleme yapılamadı: …" ile `CommandError` olur (çıkış 1). `run_job` FAILED satırının `detail` alanına `<tür>: <metin>` yazar.
    - **Testler:** `operations/tests/{test_domain,test_libx,test_applock,test_commands}.py`; yardımcılar `conftest.py` (`ops` fixture'ı: `file_db`, boşluklu ve Türkçe karakterli klasörler, hızlı KDF) ve `support.py` (kilidi alt süreçte tutan `lock_held_elsewhere`, alt süreçte `manage`). Komut testlerinde scrypt maliyeti `backup.KDF_PARAMS` ile n=2^10'a indirilir; TC-192 gerçek değerlerle koşar. TC-190 servis düzeyinde (`backup.backup_db`) koşar, çünkü komut bir `job_run` satırı yazacağı için açık yazma işlemini bekler. TC-199 ve TC-302 kilidi ayrı bir süreçte tutar.
    - G14'ün dosya listesi dışında değişen dosya yok (`base.py` açılışta listeye eklendi).
  - **G15:**
    - **Plana ek arayüzler:** domain `AnonymizeCounts` (domain'dedir, `operations.services` yeniden dışa verir) ve `anonymize_counts_text(counts)`; `operations.services._clear_reminder_errors(loan_id)` (ADR-0055 adımı; TC-207'de hata bu adıma enjekte edilir); `members.models.ANONYMIZED_NAME` ve `Member.display_name`; `circulation.services.loan_total(member)` (üye ayrıntısındaki toplam ödünç; view ORM'e dokunmasın diye).
    - **İşlem sırası:** Önce ödünçler (`closed_on`, `id` sırasıyla), sonra üyeler (`deactivated_on`, `member_no` sırasıyla); her kayıt kendi `transaction.atomic()`'inde. Aday sorgusu `add_years(today, -years)` tarih sınırıyla daraltılır; son karar `is_expired` ile verilir (29 Şubat).
    - **Ödüncün başlangıç tarihi** `closed_on`'dur: iade, kayıp ya da hasarla kapanma tarihi. Planın "iadesinin üzerinden" ifadesi bütün kapanma nedenlerine uygulandı; açık ödünç işlenmez.
    - **Bağ koparma:** Bütün adımlar queryset `update` ile yapılır: `member` NULL ve `member_unlinked_at`; `archived_loan_count = F() + 1`; `ledger_entry.loan` NULL (defter yalnız eklenir, I6); `reminder_log.error` NULL (ADR-0055).
    - **Üye:** Borç denetimi (`member_balance`) aynı işlemdedir. `save()` `search_key`'i "" ve `phone_digits`'i NULL yazar; rıza olayları silinir.
    - **Eşzamanlılık korumaları:** Bağı zaten kopmuş ödünç ve zaten anonim üye sayılmaz; bu iki dal eşzamanlı bir koşu olmadan oluşmaz (`operations/services.py`'nin kapsanmayan iki satırı).
    - **`deferred_members(today)`** aktör almaz (KL-34 imzası); yetki view'da `require_role(Role.ADMIN)` iledir. Satırdaki ad `full_name`'dir (bekleyen üye tanımı gereği anonim değildir).
    - **`display_name`:** `members/search.html`, `members/detail.html`, `billing/statement.html`, `circulation/checkout.html` (iki yer; listede telefon yalnız anonim olmayan üyede), `circulation.services.overdue_loans` (`OverdueRow.full_name`) ve `notifications.services` elle hatırlatma sonucu (`ManualResult.full_name`). Nüsha ayrıntısındaki ödünç geçmişi hiçbir üyenin adını göstermez, yalnız üye no'yu gösterir. Bu yüzden orada değişiklik yapılmadı; ad eklemek ekrandaki kişisel veriyi artırırdı (NFR-08).
    - **Toplam ödünç:** "Toplam ödünç: <n>" anonim olsun olmasın her üyenin ayrıntısında görünür.
    - **Menü:** `templates/base.html`'de yöneticiye "Personel"den önce "Saklama" bağlantısı. Ana sayfanın modül listesi değişmedi.
    - **Yetki testi:** G15 ile plan §4.1'deki 19 yönetici yolunun hepsi var oldu. `tests/test_authorization.py`'de TC-32 artık "bugün var olanlarla kesişim" yerine yönetici kümesinin beklenen listeye tam eşitliğini ve iki listedeki bütün yolların varlığını ister; açıklama ve yorumlar buna göre değişti.
    - **Testler:** `operations/tests/test_anonymize.py` (komut ve servis), `members/tests/test_retention_views.py` (view).
    - G15'in dosya listesi dışında değişen dosya yok (açılışta listeye eklenenler dışında).
  - **G16:**
    - **Plana ek arayüzler:** `scheduler.build_scheduler()` (tek işçili yürütücü), `run_catch_up(scheduler, now=None)` (saatlik görevin fonksiyonu; hatayı loglar), `start_scheduler(now=None)` (`now` yalnız testler için), `COMMANDS`, `JOB_OPTIONS`, `TIME_ZONE` ve sürecin zamanlayıcısını tutan `_scheduler`; domain `PLANNED` (görev başına hafta günü ve saat) ve `CATCH_UP_ORDER`. Domain `Job`'u import etmez, görev adlarını metin olarak karşılaştırır (`Job` bir `str` enum'udur) ve kendisine verilen anahtarları döndürür; böylece `administration.models`'e bağlanmaz. Bir test `SCHEDULE`'ın cron alanlarını `PLANNED` ile karşılaştırır.
    - **Görev kimlikleri:** `backup`, `anonymize`, `reminders`, `export`, `catch-up`; telafi işleri `catch-up-<sıra>-<görev>`. APScheduler aynı anda vadesi gelen işleri kimlik sırasıyla çalıştırdığı için sıra numarası kimliktedir. `replace_existing=True` sayesinde bekleyen bir telafi işi ikinci kez kuyruğa girmez. Telafi işinin tetikleyicisi gerçek "şimdi"dir (`DateTrigger()`); `now` yalnız vade kararında kullanılır.
    - **Açılış:** `start_scheduler` zamanlayıcıyı başlatır, beş görevin sonraki çalışma zamanını loglar ve telafiyi aynı iş parçacığında bir kez çalıştırır. Telafi hatası (ör. migrate edilmemiş veritabanı) "Telafi denetimi başarısız oldu" ile loglanır; uygulama yine açılır.
    - **`run_command`:** Komutun stdout'unu yakalar ve "Görev <komut> tamamlandı: <çıktı>" olarak loglar (satırlar " / " ile birleşir). `CommandError` ERROR olarak "Görev <komut> başarısız: <mesaj>", diğer istisnalar `logger.exception` ile "Görev <komut> beklenmeyen bir hatayla durdu" olarak loglanır. İşçi iş parçacığının bağlantısı için önce ve sonra `close_old_connections()` çağrılır.
    - **Günlük kural:** "Planlanan saat geçmiş" koşulu tam dakikayı da kapsar (`>=`). Planlanan saatten önce, önceki günün kaçan çalışması telafi edilmez; o gün cron'u çalıştırır (plandaki kural).
    - **`LOGGING`:** `operations` ve `django` logger'ları `propagate: False`'tur. waitress `logging.basicConfig()` ile kök logger'a kendi handler'ını ekler; elle doğrulamada her satır iki kez yazılınca bu ayar eklendi ve TC-339 sabitler. Testler pytest'in `caplog` handler'ını `operations` logger'ına doğrudan ekler. APScheduler'ın kendi logları yapılandırılmadı (kararın kapsamı iki logger).
    - **`wsgi.py`:** Kilit `get_wsgi_application()`'dan sonra (veritabanı yolu ayarlardan gelir), zamanlayıcıdan önce alınır ve süreç boyunca tutulur. *Not:* `runserver` de `WSGI_APPLICATION` üzerinden `wsgi.py`'yi yükler; geliştirme sunucusu da kilidi tutar ve açıkken `restore_backup` reddedilir. Zamanlayıcı yalnız `LIBRARY_SCHEDULER_ENABLED=1` ile başlar (dev varsayılanı "0"). Planın "yönetim komutları `wsgi.py`'yi yüklemez" ifadesinin tek istisnası budur.
    - **Testler:** `operations/tests/test_scheduler.py`. TC-209 ve TC-313 `library_site.wsgi`'yi test ayarlarıyla ve geçici `LIBRARY_DB_PATH` ile alt süreçte import eder; TC-313'te kilidi başka bir alt süreç tutar. Gerçek zamanlayıcı başlatan testler (TC-208, TC-335, TC-337, TC-314) zamanlayıcı modülündeki `call_command`'ı yamalar; işçi iş parçacığı veritabanına dokunmaz.
    - G16'nın dosya listesi dışında değişen dosya yok (`base.py` ve `operations/domain.py` açılışta listeye eklendi).
- **2026-11-01, G14–G16 uygulayıcının seçtiği kullanıcıya görünen metinler:** Plan, SRS, KL, ADR ya da açılış kararlarının vermediği metinler (2026-11-01 kullanıcı kararı; PR'da onaya sunulur). Kullanıcı 2026-11-01'de PR #5 incelemesinde hepsini onayladı; metin değiştirilmedi. Planın, KL'lerin, ADR'lerin ve açılış kararlarının verdiği metinler ("Dosya bulunamadı: <yol>", "Uygulama çalışıyor; önce servisi durdurun", "Parola hatalı ya da dosya bozuk", "Desteklenmeyen dosya sürümü", "Geçersiz tarih: …", "Uygulama zaten çalışıyor: <kilit yolu>", "Anonimleştirilmiş üye", "borç nedeniyle bekliyor") listede yoktur. Önceki listelerde onaylı olup aynen kullanılanlar "(onaylı)" ile işaretlidir.
  - **G14, komut çıktıları:**
    - "Yedek alındı: <yol>" ve "Silinen eski yedek: <n>": `backup_db` çıktısı. `job_run` detayı: "library-YYYYMMDD.sqlite3, silinen=<n>".
    - "Dışa aktarıldı: <yol> (kaynak: <yedek adı>)" ve "Silinen eski dışa aktarma: <n>": `export_backup` çıktısı. `job_run` detayı: "<dosya adı> (kaynak <yedek adı>), silinen=<n>".
    - "Geri yüklendi: üye=<n>, nüsha=<n>, ödünç=<n>", "Önceki veritabanı korundu: <yol>" (ADR-0054) ve "Gerekirse python manage.py migrate çalıştırın." (küçük karar 3'ün notu): `restore_backup` çıktısı.
  - **G14, hata mesajları** (`CommandError`, çıkış 1): "Yedek klasörü bulunamadı: <yol>", "Dışa aktarma klasörü bulunamadı: <yol>", "Günlük yedek bulunamadı: <yedek klasörü>" (KL-14'ün "yedek yoksa çıkış 1" durumu), "Parola dosyası bulunamadı: <yol>", "Parola dosyası boş: <yol>", "Geçerli bir veritabanı yedeği değil: <yol>" (plan G14 4. adım), "Yedek alınamadı: <tür>: <metin>", "Dışa aktarma yapılamadı: <tür>: <metin>", "Geri yükleme yapılamadı: <tür>: <metin>".
  - **G14, `--help` metinleri:** `backup_db` "Veritabanının günlük yedeğini alır ve 30 günden eski yedekleri siler."; `export_backup` "Son günlük yedeği parolayla şifreleyip bina dışı yedek dosyası (.libx) üretir." ve `--passphrase-file` "Parola dosyası; varsayılan LIBRARY_EXPORT_PASSPHRASE_FILE"; `restore_backup` "Veritabanını bir günlük yedekten (.sqlite3) ya da şifreli dışa aktarmadan (.libx) geri yükler. Uygulama durdurulmuş olmalıdır.", PATH "Geri yüklenecek yedek ya da dışa aktarma dosyası", `--passphrase-file` "Şifreli dosyanın parola dosyası; varsayılan LIBRARY_EXPORT_PASSPHRASE_FILE", `--yes` "Veritabanının değiştirileceğini onaylar"; `--date` "YYYY-MM-DD; varsayılan bugün" (onaylı, G13).
  - **G14, arayüzde görünmeyen:** app adı "Yedek ve görevler" (`operations/apps.py`).
  - **G15, ekranlar:**
    - "Saklama": `templates/base.html`, yöneticinin menü bağlantısı (küçük karar 7).
    - "Bekleyen anonimleştirmeler": `members/retention_pending.html` sayfa başlığı ve `<title>` ("Bekleyen anonimleştirmeler · Kütüphane").
    - "Saklama süresi dolduğu hâlde borcu olduğu için anonimleştirilmeyen pasif üyeler. Borç kapanınca sonraki görev çalışmasında anonimleştirilirler.": aynı sayfa, açıklama.
    - "Üye no", "Ad soyad", "Pasifleşme", "Süre sonu", "Bakiye", "Durum": aynı sayfa, sütun başlıkları.
    - "Borç nedeniyle bekleyen üye yok.": aynı sayfa, boş liste.
    - "Toplam ödünç: <n>": `members/detail.html`.
  - **G15, komut:** "anonimleştirilen üye=<n>, bağı koparılan ödünç=<n>, ertelenen üye=<n>" (`anonymize_expired` çıktısı ve `job_run` detayı); "Anonimleştirme yapılamadı: <tür>: <metin>" (hata, çıkış 1); `--help` "Saklama süresi dolan ödünçlerin üye bağını koparır ve süresi dolan pasif üyeleri anonimleştirir; borçlu üyeler ertelenir."
  - **G16, log satırları** (`operations.scheduler`, stderr): "Zamanlanmış görev <kimlik>: sonraki çalışma <zaman>", "Telafi: <GÖREV> kuyruğa alındı (<komut>)", "Telafi denetimi başarısız oldu", "Görev <komut> tamamlandı: <çıktı>", "Görev <komut> başarısız: <mesaj>", "Görev <komut> beklenmeyen bir hatayla durdu". Arayüzde görünmeyen APScheduler görev adları: "Saatlik telafi", "Telafi: <GÖREV>".
- **2026-11-01, G17–G18 — açılıştan önce verilen kararlar (kullanıcı onayı 2026-11-01):**
  - **Kritik:**
    - [ADR-0056](../decisions/0056-open-library-fetch-network-blocked.md), Open Library çekimi (ADR-0033'e ek): Oturum `scripts/fetch_demo_books.py`'yi çalıştırmayı dener. Ağ engelliyse `seed/books_openlibrary.json` olmadan devam edilir; testler küçük bir örnek dosyayla koşar ve ADR-0033'teki sentetik tamamlama çalışır. Gerçek JSON yerel doğrulamada çekilip dala commit'lenir; bu adım STATUS'a yazılır. Reddedilenler: G17'yi beklemeye almak; dosyayı başka kaynaktan üretmek.
    - [ADR-0057](../decisions/0057-seed-phone-numbers.md), tohum telefonları: Telefonlar "000" önekli sahte numaralardır (ör. `000 123 45 67`) ve hiçbir gerçek aboneye denk gelmez. Kaynak TC-234. Reddedilenler: gerçek biçimli rastgele cep numarası; telefonsuz üye.
    - [ADR-0058](../decisions/0058-loadtest-seed-only-guard.md), yük betiği koruması: `--db` içinde e-postası `@example.invalid` ile bitmeyen bir üye varsa betik "Tohum verisi olmayan veritabanı" mesajıyla çıkış 1 verir ve hiç istek atmaz. Sınırı: e-postasız gerçek veriyi yakalayamaz. Reddedilenler: veritabanında tohum işareti (migration gerekir); yalnız belge.
  - **Küçük kararlar (onaylı):**
    1. README.md yok. G17 onu yalnız "Veri kaynakları" (Open Library CC0 atfı) ve "Demo verisi" (`migrate` → `createsuperuser` → `load_seed_data --profile demo --actor <ad>`) bölümleriyle oluşturur; G19 genişletir.
    2. Tarihler komutun çalıştığı günden (`timezone.localdate()`) geriye doğru üretilir. Aynı gün ve aynı `--seed` aynı veriyi verir; TC-218'de zaman sabitlenir.
    3. Demo profili: 150 açık ödünce ek olarak son 180 güne yayılmış 350 kapalı ödünç. 5 borçlu üyenin borcu gecikmeli iadeden doğan ödenmemiş FINE'dır; diğer gecikmeli iadeler FINE + PAYMENT alır.
    4. Yük profili: 100.000 ödünç son 365 güne yayılır; 2 yıllık saklama görevi yük verisine dokunmaz.
    5. Son tarih (kapalı gün kaydırması dahil), ceza, barkod, `search_key` ve `phone_digits` mevcut domain fonksiyonlarıyla hesaplanır; ayarlar `LibrarySettings`'ten okunur. Yazım `bulk_create` ile, tek `transaction.atomic` içinde yapılır.
    6. Sentetik kitabın başlığı, Open Library başlıklarındaki sözcüklerden 2–4 sözcüktür; yazarı ad ve soyad listelerinden gelir. ISBN, yayınevi ve `source_ol_id` boştur.
    7. Tohum veri audit kaydı yazmaz. PAYMENT'ların Allocation satırları yazılır, bakiyeler tutarlı olur.
    8. Çıktı kitap, nüsha, üye, açık ödünç (gecikmiş) ve kapalı ödünç sayılarını verir. Sentetik tamamlama olduysa bunu ayrı bir satırda yazar.
    9. Rızalı üye için `ConsentEvent(GRANT)` yazılır (modeldeki adı `ConsentAction.GIVEN`); `effective_on` son 365 günden rastgele bir gündür. E-posta `uye<no>@example.invalid` biçimindedir.
    10. G18: Kendi açık ödüncü yokken iade ya da uzatma seçilirse işlem yeniden seçilir ve sayılmaz. Uzatılan ödünç uzatma havuzundan çıkar.
    11. G18: `scripts/` bir paket olur ve `pyproject.toml` `testpaths`'e eklenir. Betik Django'yu import etmez.
    12. G18 elle duman testi: demo verisiyle `waitress` + `loadtest.py --duration 10`. p95 bağlayıcı değildir, yalnız not edilir.
  - **Plana işlenenler:** G17 ve G18 bölümlerinin "Gereksinimler", "Dosyalar", "Davranış", "Testler" ve "Doğrulama" satırları; §2'de ADR-0056…0058; §3'te ADR-0056…0058 (sıradaki numara 0059); §5'te TC sayısı; §7'de yeni TC'ler. Yeni davranışların testleri `docs/test-plan.md`'de TC-340…TC-356 (G17: TC-340…TC-352, G18: TC-353…TC-356). TC-220, TC-317 ve TC-346 `slow` işaretlidir.
  - **Açılışta sabitlenen uygulama seçimleri** (kararların doğrudan sonucu; onaya sunulan metinler grubun sonunda bu bölüme eklenir):
    - G17'nin testleri ağsızdır; `filter_records` ve çekim döngüsü (TC-214…TC-216, TC-340) `scripts/tests/`'te, komut ve servis testleri `operations/tests/test_seed.py`'dedir. `scripts/` paketi bu yüzden G17'de açılır; `testpaths` ayarı küçük karar 11'e göre G18'de eklenir.
    - Kitap dosyası yoksa `load_seed_data` tamamen sentetik veri üretmez, hata verir (ADR-0056; TC-341). Bulutta elle doğrulama, örnek dosyanın geçici bir kopyasıyla yapılır.
    - Demo profilinde gecikmeli iade oranı yük profilindekiyle aynıdır (kapalı ödünçlerin %10'u, 35 ödünç); 5'i borçlu üyelerin ödenmemiş cezasıdır (küçük karar 3).
- **2026-11-01, G17–G18 — uygulama ayrıntıları (bulut oturumu):**
  - **G17:**
    - **Plana ek arayüzler:** `operations.seed`: `Profile` ve `PROFILES` (demo, load), `SeedCounts(books, copies, members, open_loans, overdue_loans, closed_loans, ol_records, synthetic_books)`, `SeedError` (mesajı olduğu gibi gösterilen beklenen hata), `counts_lines(counts)`, `seed_phone(n)`, `seed_email(member_no)`, `title_words(titles)`, `read_books(path)`, `BOOKS_FILE` ve ad listelerinin yolları, `_bulk(model, rows)` (tek yazım yolu; TC-348 hatayı buraya enjekte eder). `scripts/fetch_demo_books.py`: `fetch_books(limit, *, urlopen, sleep)`, `write_output(path, records, fetched_on)`, `main(argv)`, `FILTER_VERSION = 1`. `catalog.domain.copy_barcode(copy_id)` yeni: barkodun tek kaynağıdır, `catalog.services.add_copies` de bunu kullanır (küçük karar 5 "mevcut domain fonksiyonu" dediği için barkod biçimi domain'e alındı).
    - **Kimlikler:** Tablolar boş olduğu için kitap, nüsha, üye, rıza, ödünç, defter ve dağıtım satırlarının `id`'leri 1'den açıkça verilir; `member_no` = `id`, barkod = `copy_barcode(id)`. SQLite `AUTOINCREMENT` sayacı en büyük kimliğe ilerler; sonra eklenen nüshaların barkodu çakışmaz.
    - **Zaman damgaları** tarihlerden türetilir, `timezone.now()` çağrılmaz (küçük karar 2, TC-218): `Copy.status_changed_at` açık ödünçte `loaned_on` 10:00, kapalı ödüncü olan nüshada son `closed_on` 12:00, hiç ödünç almamış nüshada pencerenin başı 09:00; FINE `closed_on` 12:00, PAYMENT 12:05; `ConsentEvent.recorded_at` `effective_on` 10:00 (Europe/Istanbul).
    - **Açık ödünçler:** Rastgele nüshalara; üyeler karıştırılmış listeden sırayla atanır (demo 150, yük 3.000 farklı üye; limit 3 aşılmaz). Gecikmiş ödünçte `loaned_on` = bugün − süre − (1…20 gün); kapalı gün kaydırması `due_on`'u bugüne taşırsa `loaned_on` bir gün geri alınır. Gecikmemiş ödünçte `loaned_on` = bugün − (0…süre − 1).
    - **Kapalı ödünçler:** Nüshalara karıştırılmış sırayla dağılır (yükte nüsha başına en çok 5). Her nüshanın penceresi (bugün − 180 ya da 365 gün … açık ödüncünden ya da bugünden bir gün önce) eşit dilimlere bölünür ve her ödünç kendi diliminde kalır; aynı nüshanın ödünçleri çakışmaz (TC-343). Zamanında iade 1…süre gün sonra, gecikmeli iade son tarihten 1–20 gün sonradır. Hepsi `RETURNED`'dır; kayıp, hasar, uzatma ve pasif üye üretilmez.
    - **Gecikme ve borç:** Gecikmeli iade oranı iki profilde de kapalı ödünçlerin %10'udur (demo 35, yük 9.700; açılışta sabitlendi). Demo'nun 5 borçlusu, gecikmeli iadesi olan üyelerden rastgele seçilir; her birinin **en son** gecikmeli iadesinin cezası ödenmemiş kalır. Önceki cezalar aynı gün kendi ödemeleriyle FIFO'ya göre kapanır, böylece borçlunun tek açık kalemi o ceza olur (TC-344). PAYMENT'ın `loan` alanı boştur (`record_payment` gibi).
    - **Kitaplar:** Open Library kayıtlarında yayınevi boştur (ADR-0033 yayınevi almaz). Sentetik başlığın sözcükleri dosyadaki bütün başlıkların harf dizileridir (rakam ve noktalama atılır, ilk görülme sırası, tekrarsız). Sentetik kitabın yılı 1950 ile bu yıl arasında rastgeledir (küçük karar 6 yılı boş saymadığı için). Çekim betiğinde birden çok yazar ", " ile birleşir; kaydın ISBN'i, belgedeki ISBN'lerden 13 haneli ve geçerli olan ilkidir; `ol_id` eser anahtarıdır (`OL…W`).
    - **Ad listeleri:** `seed/first_names.txt` 83, `seed/last_names.txt` 79 tek sözcüklü Türkçe ad ve soyad.
    - **Denetim sırası:** Komut önce aktörü, sonra işlemin içinde veritabanının boşluğunu, sonra kitap dosyasını denetler. Dosya yoksa "Kitap dosyası bulunamadı", kaydı yoksa "Kitap dosyasında kayıt yok" ile çıkış 1 (TC-341). Komut `job_run` yazmaz.
    - **Süre:** Yük profili bulutta 14 sn'de yüklenir (100.000 ödünç, 9.700 FINE, 9.700 PAYMENT, 9.700 dağıtım; ~21 MB). Demo 0,7 sn.
    - **Testler:** `operations/tests/test_seed.py` (25). TC-218 ve TC-343 iki yüklemeyi aynı test veritabanında işlemi geri alarak yapar (her yükleme boş veritabanında başlar). TC-220, TC-317 ve TC-346 modül kapsamlı tek bir yükleme fikstürünü paylaşır; fikstür sayıları toplar ve işlemi geri alır. TC-315'in kullanım hatası (çıkış 2) alt süreçte `manage.py` ile. `scripts/tests/test_fetch_demo_books.py` (8; TC-214…TC-216, TC-340) ağsızdır: HTTP açıcı ve bekleme yamalıdır. Örnek dosya `operations/tests/data/books_sample.json` (12 kayıt, `_meta.source` "Test örneği").
    - **Dosya listesi dışında değişenler:** `catalog/domain.py` ve `catalog/services.py` (`copy_barcode`).
  - **G18:**
    - **Plana ek arayüzler:** `OPERATIONS` (işlem adları), `OpStats(durations_ms, errors)`, `passes(stats)`, `report_lines(stats)`, `ro_uri(path)`, `connect_ro(path)`, `check_seed_only(con)` ve `NotSeedData`, `WorkerPlan(members, copies, book_words, member_words)`, `load_candidates(con, workers, rng) -> (plans, max_open_loans)`, `Client(base_url)` (`request`, `login`), `Worker(client, plan, rng, lookup_loan, max_open_loans)` (`next_operation`, `step`, `run`), `main(argv)`.
    - **Adaylar:** Üye aktif, anonim değil, açık ödüncü yok ve bakiyesi 0'dır (uzatma borçta reddedildiği için "engelsiz"den sıkı). Nüsha Raftadır. İkisi de `--seed` ile karıştırılıp `i::workers` ile ayrık bölünür (TC-318). Ödünç limiti `library_settings`'ten okunur.
    - **Arama sözcükleri:** Kitap aramasında başlık sözcükleri (en az 3 harf); üye aramasında üyelerin soyadları. KL-17'nin "başlık sözcükleri" kuralı üye aramasında sonuç vermeyeceği için üye aramasına soyad seçildi.
    - **Zincir:** Ödünçten sonra ödüncün kimliği iş parçacığının kendi salt okunur bağlantısıyla aranır (süreye girmez). Uygun üye ya da rafta nüsha kalmadıysa ödünç de, iade ve uzatma gibi (küçük karar 10), istek atılmadan yeniden seçilir. İade edilen nüsha raf havuzuna, üyenin kotası geri döner.
    - **Başarı ölçütü:** Ödünç, iade ve uzatma 303, aramalar 200 beklenir. Kural ihlali aynı ekranda 200 döndüğü için hata sayılır; ağ hatası da hata sayılır. Süre her istekte ölçülür (hatalılar dahil). İstek yapılmamış bir tür sonucu "kaldı" yapar (kanıt eksik).
    - **HTTP:** Yönlendirmeler izlenmez. `Secure` işaretli çerezler düz HTTP'de de gönderilir; betik üretimde (`SESSION_COOKIE_SECURE = True`) Caddy'siz waitress'e bağlandığı için bu gerekir (ADR-0031). Her iş parçacığı sırayla oturum açar; başarısız girişte çıkış 1. Parola dosyası `utf-8-sig` ile okunur, sondaki satır sonu atılır. Faz 6'da `LIBRARY_ALLOWED_HOSTS` waitress adresini (ör. `127.0.0.1`) içermelidir.
    - **`testpaths`:** Bütün app klasörleri, `scripts` ve `tests`. Yeni bir app eklenirse listeye de eklenmelidir; TC-355 bunu denetler.
    - **Testler:** `scripts/tests/test_loadtest.py` (13). TC-318 aday seçimini `file_db` ve fabrika fonksiyonlarıyla kurulmuş gerçek şemada sınar; TC-356 stdlib `http.server` ile yerel sahte sunucu kullanır.
    - **Dosya listesi dışında değişenler:** Yok (`pyproject.toml`'daki `slow` işaretinin açıklaması "yük profili tohumu"nu da kapsayacak biçimde güncellendi).
- **2026-11-01, G17–G18 uygulayıcının seçtiği kullanıcıya görünen metinler** (PR'da onaya sunulur). Planın, ADR'lerin ve açılış kararlarının verdiği metinler ("Personel bulunamadı ya da pasif: <ad>", "Veritabanı boş değil", "Tohum verisi olmayan veritabanı", "kitap=…, nüsha=…, üye=…, açık ödünç=… (gecikmiş …)") listede yoktur.
  - **G17, `load_seed_data`:**
    - Çıktının ilk satırının sonuna eklenen ", kapalı ödünç=<n>" (küçük karar 8).
    - "Open Library dosyasında <n> kayıt var; <m> sentetik kitap eklendi": sentetik tamamlama satırı.
    - Hatalar (çıkış 1): "Kitap dosyası bulunamadı: <yol>", "Kitap dosyasında kayıt yok: <yol>", "Tohum verisi yüklenemedi: <tür>: <metin>".
    - `--help`: komut "Boş veritabanına demo ya da yük testi verisi yükler; kayıtların sahibi --actor personelidir."; `--profile` "demo ya da load; varsayılan demo"; `--actor` "Kayıtların sahibi olacak aktif personelin kullanıcı adı"; `--seed` "Rastgele üretecin tohumu; varsayılan 42".
  - **G17, `scripts/fetch_demo_books.py`:** açıklama "Demo kitaplarını Open Library'den bir kez çeker ve JSON dosyasına yazar."; `--out` "Yazılacak JSON dosyası"; `--limit` "En çok kayıt sayısı; varsayılan 300"; "<n> kayıt yazıldı: <yol>"; "Open Library'ye erişilemedi: <neden>" (çıkış 1); "pozitif bir tam sayı olmalı: <değer>" (çıkış 2). `_meta.source` "Open Library (https://openlibrary.org), arama API'si"; `_meta.license` "Open Library kataloğu verisi CC0 (kamu malı) olarak sunulur; yalnız bibliyografik alanlar (başlık, yazar, yıl, ISBN) ve OL kimliği alındı, kapak alınmadı."; `User-Agent` "kutuphane-odunc-sistemi/1.0 (one-time demo data fetch; <repo adresi>)".
  - **G17, `README.md`:** Başlık "Kütüphane ödünç sistemi", tanıtım cümlesi, "Veri kaynakları" bölümünün iki maddesi (Open Library CC0 atfı ve teşekkür; sentetik ad, "000" telefon ve `@example.invalid` notu) ve "Demo verisi" bölümünün metni (üç komut ve `<ad>` açıklaması).
  - **G17, veri:** `seed/first_names.txt` ve `seed/last_names.txt` listeleri.
  - **G18, `scripts/loadtest.py`:** işlem adları "kitap arama", "ödünç", "iade", "uzatma", "üye arama"; rapor başlığı "işlem, istek, p50 (ms), p95 (ms), hata"; istek yapılmamış türde "-"; son satır "Sonuç: geçti" ya da "Sonuç: kaldı". Hatalar (çıkış 1): "Parola dosyası okunamadı: <yol>", "Veritabanı okunamadı: <yol>: <hata>", "Sunucuya bağlanılamadı: <adres>: <hata>", "Giriş başarısız: <kullanıcı>". `--help`: açıklama "NFR-01 yük testi: tohum verili bir sunucuya 5 eşzamanlı personel gibi istek atar ve işlem türü başına p50, p95 ve hata sayısını raporlar."; `--base-url` "Waitress adresi, ör. http://127.0.0.1:8000"; `--user` "Personel kullanıcı adı"; `--password-file` "Parolanın bulunduğu dosya"; `--db` "Sunucunun SQLite veritabanı (salt okunur açılır)"; `--workers` "İş parçacığı sayısı; varsayılan 5"; `--duration` "Süre (saniye); varsayılan 120"; `--seed` "Rastgele üretecin tohumu; varsayılan 42"; "pozitif bir tam sayı olmalı: <değer>".
- **2026-11-01, PR #6 yerel doğrulaması ve onaylar** (kullanıcı, soru penceresi):
  - **Metinler:** "G17–G18 uygulayıcının seçtiği kullanıcıya görünen metinler" listesinin tamamı onaylandı.
  - **Birleştirme:** Kitap dosyası commit'lendikten ve testler yeniden geçtikten sonra PR #6'nın `main`'e birleştirilmesi onaylandı.
  - **Kitap dosyası:** Filtre sürümü 1'in yabancı baskı sorunu yerelde düzeltildi ("yerelde yalnız doğrulama" kuralına kullanıcının onayladığı istisna). Baskı düzeyi seçildi ve 5xx ile zaman aşımında yeniden deneme eklendi: [ADR-0059](../decisions/0059-demo-books-turkish-edition.md), TC-357, TC-358. ADR-0033'ün durum satırı güncellendi. Kanıt G17'de.
  - **Uyarlanan testler:** TC-214…TC-216 ve TC-340'ın test yardımcısı (`doc`) artık eser ve eşleşen Türkçe baskıyı üretir; beklenen `ol_id`'ler `OL…M` oldu, sınanan davranış değişmedi.
- **2026-11-01, G19 — açılıştan önce verilen kararlar (kullanıcı onayı 2026-11-01):**
  - **Kritik:**
    - [ADR-0060](../decisions/0060-install-doc-common-body-two-platforms.md), kurulum belgesinin yapısı: `docs/kurulum.md` ortak bir gövde ve iki eşit ayrıntıda platform bölümünden (Windows, Linux) oluşur; ortak adımlar bir kez yazılır. Reddedilenler: Windows ayrıntılı, Linux kısa; iki ayrı belge (ortak adımlar kayar).
    - [ADR-0061](../decisions/0061-access-by-static-ip.md), erişim adresi: Personel uygulamaya sunucunun sabit IP'siyle erişir (`https://192.168.x.y`); IP yönlendiricide DHCP rezervasyonuyla sabitlenir. `LIBRARY_HOST` ve `LIBRARY_ALLOWED_HOSTS` bu IP'dir; `tls internal` IP sertifikası üretir. Personel bilgisayarlarına masaüstü kısayolu konur. Reddedilenler: hosts dosyasında ad (bilgisayar başına yönetici işi); yönlendiricide DNS kaydı (destek belirsiz).
    - [ADR-0062](../decisions/0062-service-account.md), servis hesabı: Windows'ta `library-svc` yerel kullanıcısı (WinSW `<serviceaccount>`), Linux'ta `library` sistem kullanıcısı. Veri klasörü, gizli değer dosyaları ve Caddy veri klasörü (CA anahtarı) ACL ya da izinle yalnız bu hesaba açılır. Reddedilenler: Windows sanal hesabı `NT SERVICE\…` (WinSW 2.x'te belirsiz); LocalSystem ya da root (aşırı yetki).
    - [ADR-0063](../decisions/0063-tool-versions-winsw-caddy.md), araç sürümleri: WinSW 2.12.0 (XML biçimi buna göre). Caddy'nin yazım anındaki son kararlı 2.x sürümü (2.11.7) belgeye yazılır, indirme bağlantısı o sürüme sabitlenir; güncelleme elle. Reddedilenler: WinSW 3.x alfa; sürüm sabitlememek.
    - [ADR-0064](../decisions/0064-release-zip-and-update-procedure.md), dağıtım yolu ve güncelleme: Kod sunucuya bir etiketten `git archive` ile üretilen zip olarak (USB ya da ağ) gelir; sunucuda git ve GitHub erişimi gerekmez. Belgede ilk kurulum ve güncelleme yordamı vardır. Güncelleme: servisi durdur → `backup_db` → zip'i aç → `pip install -r requirements.txt` → `migrate` → `collectstatic` → servisi başlat → kontrol. Reddedilenler: `git clone` (özel depo için sunucuya anahtar); yalnız ilk kurulum.
    - [ADR-0065](../decisions/0065-caddy-no-access-log.md), Caddy logu: Erişim logu tutulmaz (Caddyfile'da `log` yönergesi yok). Yalnız süreç hata logu WinSW'ye ve journald'a gider. Gerekçe: arama GET sorgu dizgesi üye adı ve telefonu taşır (KVKK, FR-25 saklama kuralı dışı kişisel veri); işlem izi denetim kaydındadır. Reddedilenler: maskeli erişim logu; tam erişim logu.
    - [ADR-0066](../decisions/0066-deploy-files-consistency-tests.md), dağıtım dosyalarının otomatik testleri: pytest tutarlılık testleri yazılır (`deploy/library.env.example` ve iki WinSW XML'indeki `<env>` adları ile ayarların okuduğu `LIBRARY_*` kümesi aynı, §6.4 listesi; Caddy'ye özgü `LIBRARY_HOST` ve `LIBRARY_BIND` ayrıca; XML'lerin zorunlu öğeleri; systemd unit'lerinde ve Caddyfile'da zorunlu satırlar ve `log` yokluğu; TC-319'un metin koşulları otomatik, elle okuma da kalır). Reddedilen: yalnız elle TC'ler.
  - **Küçük kararlar (onaylı):**
    1. **Yollar:** Windows `C:\Kutuphane\{app,venv,data,static,secrets,caddy,winsw}`. Linux `/opt/library/{app,venv}`, `/var/lib/library/{data,static}`, `/etc/library/library.env` (0640, `root:library`). Yedek ve dışa aktarma klasörleri harici diskte, elle açılır.
    2. Caddy de aynı servis hesabıyla çalışır; Linux'ta `AmbientCapabilities=CAP_NET_BIND_SERVICE`.
    3. **Yeniden başlatma:** WinSW `onfailure restart` 10 sn, 3 deneme, `resetfailure` 1 gün. systemd `Restart=on-failure`, `RestartSec=5`. Caddy uygulama servisine bağlı: Windows `<depend>library-app</depend>`, Linux `After=` ve `Wants=`.
    4. **Loglar:** WinSW `roll-by-size` 10 MB × 8 dosya; Linux journald.
    5. **systemd sıkılaştırma:** `NoNewPrivileges=yes`, `PrivateTmp=yes`, `ProtectSystem=strict`, `ReadWritePaths=` yalnız veri, yedek ve dışa aktarma klasörleri (Caddy unit'inde kendi veri klasörü).
    6. **Güvenlik duvarı (yalnız belge):** Windows'ta 80/443 gelen kuralı, Private profil ve `LocalSubnet`; Linux'ta LAN alt ağıyla sınırlı `ufw` örneği. Yönlendiricide dışarı port açılmaz (NFR-08).
    7. **Kök CA:** Her personel bilgisayarında `certutil -addstore -f Root root.crt`; Firefox kurumsal kök notu; kök sertifikanın Caddy veri klasöründeki yeri belgede.
    8. **Ortam dosyası:** `library.env.example`'da her değişkene bir Türkçe açıklama satırı, gizli değerler boş. WinSW `<env>` değerleri `__DOLDUR__`. `SECRET_KEY` üretimi: `python -c "import secrets; print(secrets.token_urlsafe(50))"`.
    9. **Sürüm arşivi:** `git archive --format=zip --prefix=library/ <etiket> -o library-<etiket>.zip`; etiket `vX.Y.Z`. G19'da yalnız belgelenir; etiket faz 6'da kullanıcı onayıyla atılır.
    10. **Testler:** `tests/test_deploy_files.py`; yeni TC'ler TC-359'dan başlar.
    11. **README:** Mevcut "Veri kaynakları" ve "Demo verisi" korunur (TC-352); "Geliştirme ortamı", "Testler" ve "Belgeler" (kurulum ve kılavuz bağlantıları) eklenir; girişteki "G19'da eklenecek" cümlesi kaldırılır.
    12. **Kullanım kılavuzu:** Yalnız metin. Masa işleri: giriş, ödünç ("üyeye adını sor" adımı, ADR-0032), iade, uzatma, üye kaydı ve rıza (geçmiş tarihli rıza olayı geçerli durumu değiştirmez, ADR-0047), ödeme, kayıp ve hasar, etiket ve kart basımı. Yönetici bölümü: kapalı günler (geçmiş kapalı tarihler silinmez, ADR-0040), ayarlar, yedek ve dışa aktarma uyarıları.
  - **Yerel doğrulama kararı (ADR değil):** Bulut oturumundan sonraki yerel Windows doğrulamasında resmî taşınabilir Caddy ikilisi scratchpad'e indirilir; `caddy validate` ve geçici portlarda waitress + Caddy ile `/static/css/app.css` → 200, `/admin/` → 404 kontrol edilir. Servis kaydı ve sisteme kurulum yapılmaz; tam kurulum faz 6'dadır. Bulutta Caddy ikilisi indirilebilirse `caddy validate` ve `caddy adapt` orada da çalıştırılır; indirilemezse not edilir.
  - **Plan G19'dan değişmeyenler:** Caddyfile'ın dört kuralı, uygulama servisinin komutu (KL-5) ve `LIBRARY_SCHEDULER_ENABLED=1`, `docs/kurulum.md`'deki architecture §8'in 7 adımı, migration öncesi `backup_db`, geri yükleme yordamı (AC-28 süresi ölçülür), koruma kopyası KVKK notu (ADR-0054), USB rotasyonu, parolanın çevrimdışı saklanması, CA kök sertifikası, NTP, SQLite'ın yerel diskte tutulması, yedek ve dışa aktarma klasörlerinin elle açılması.
  - **Plana işlenenler:** G19 bölümünün "Gereksinimler", "Dosyalar", "Davranış", "Testler" ve "Doğrulama" satırları; §2'de ADR-0060…0066; §3'te ADR-0060…0066 (sıradaki numara 0067); §5'te TC sayısı; §7'de yeni TC'ler. Yeni otomatik TC'ler `docs/test-plan.md`'de TC-359…TC-366. Elle TC'ler (TC-225…TC-234, TC-319) faz 6'da yapılır, durumları "Planlandı" kalır.
  - **Açılışta sabitlenen uygulama seçimleri** (kararların doğrudan sonucu; onaya sunulan metinler grubun sonunda bu bölüme eklenir):
    - Caddyfile ve WinSW XML'leri sürüm arşiviyle gelir. Caddy, Caddyfile'ı doğrudan uygulama klasöründen okur (`C:\Kutuphane\app\deploy\Caddyfile`, `/opt/library/app/deploy/Caddyfile`); güncelleme Caddyfile'ı da günceller.
    - Caddy'nin veri klasörü `XDG_DATA_HOME` ve `XDG_CONFIG_HOME` ile servis hesabının profili yerine sabit bir yere alınır: Windows `C:\Kutuphane\caddy`, Linux `/var/lib/library/caddy` (Linux'ta küçük karar 1'in listesine eklenen klasör). Kök sertifika `<veri klasörü>\caddy\pki\authorities\local\root.crt`'dedir.
    - Caddyfile'ın genel seçeneklerinde `skip_install_trust` vardır: servis hesabı yönetici olmadığı için Caddy'nin kök sertifikayı sunucunun kendi güven deposuna yükleme denemesi başarısız olur ve loga hata yazar; kök sertifika personel bilgisayarlarına elle yüklenir (küçük karar 7).
    - WinSW `<env>` değerlerinde yalnız kuruma özgü ya da gizli değerler (`LIBRARY_SECRET_KEY`, `LIBRARY_ALLOWED_HOSTS`, `LIBRARY_HOST`, `LIBRARY_BIND`, yedek ve dışa aktarma klasörleri, `LIBRARY_EMAIL_*`) ve hesap parolası `__DOLDUR__`'dur; küçük karar 1'in sabit yolları ve `LIBRARY_SCHEDULER_ENABLED=1` dolu gelir.
    - `<depend>` yalnız Caddy servisinin XML'indedir; uygulama servisi başka bir servise bağlı değildir. ADR-0066'nın zorunlu öğe listesi buna göre okunur.
    - Linux'ta harici disk `/mnt/library-backup`'a bağlanır (`/etc/fstab`); yedek ve dışa aktarma klasörleri `/mnt/library-backup/{backups,exports}`, dışa aktarma parola dosyası `/etc/library/export-passphrase.txt` (0640, `root:library`). Windows'ta harici disk örneği `E:\Kutuphane\{backups,exports}`, parola dosyası `C:\Kutuphane\secrets\export-passphrase.txt`.
    - Elle çalıştırılan `manage.py` komutları servisin ortamıyla çalışır: Windows'ta PowerShell ortamı WinSW XML'indeki `<env>` öğelerinden yükler, Linux'ta komut `library` kullanıcısıyla ve `library.env` yüklenerek çalışır.
    - Kurulum belgesinin içeriği de otomatik denetlenir (TC-366): 7 adımın komutları, güncelleme sırası, geri yükleme ve KVKK notu, iki platform bölümü, sabit Caddy sürümü.
- **2026-11-01, G19 — uygulama ayrıntıları (bulut oturumu):**
  - **TDD:** `tests/test_deploy_files.py` (TC-359…TC-366, 20 test) dosyalardan önce yazıldı ve kırmızı görüldü (19 failed). TC-359 ayarlar ile architecture §6.4'ün mevcut eşitliğini sabitleyen koruma testidir; baştan geçti.
  - **Değişken kümeleri:** Ayarların okuduğu adlar `library_site/settings/*.py` içindeki `env("…")` çağrılarından, §6.4 listesi `docs/architecture.md`'deki satırdan okunur; ikisi aynı kümeyi verir (`DJANGO_SETTINGS_MODULE` dahil 14 ad). Uygulama XML'i bu kümeyi, Caddy XML'i yalnız Caddyfile'daki `{$LIBRARY_*}` adlarını (`LIBRARY_HOST`, `LIBRARY_BIND`, `LIBRARY_STATIC_ROOT`) ve `XDG_DATA_HOME`/`XDG_CONFIG_HOME`'u, `library.env.example` §6.4 ile iki Caddy değişkenini taşır. TC-364 ayrıca uygulama unit'inin `ReadWritePaths=` kümesini `library.env.example`'daki veritabanı klasörü, yedek ve dışa aktarma klasörleriyle karşılaştırır.
  - **Caddyfile:** `caddy fmt` genel seçenek bloğundan önceki boş satırı istedi; satır kaldırıldı ve `caddy validate` uyarısız geçti. Statik dışı yollar `handle { reverse_proxy 127.0.0.1:8000 }` içindedir (`handle_path` ile karşılıklı dışlayıcı). Canlı denemede `bind`'in HTTP→HTTPS yönlendirme dinleyicisini de LAN adresine bağladığı (`<IP>:80`) ve yönetim ucunun `localhost:2019`'da kaldığı görüldü; ek genel seçenek gerekmedi.
  - **systemd:** Yedek ve dışa aktarma yolları `ReadWritePaths=`'te `-` önekiyle yazıldı: disk takılı değilken servis yine başlar, yedek komutu klasörü bulamayıp hata verir ve ana sayfada uyarı çıkar (G14 davranışı). Caddy unit'i `Type=notify` (Caddy'nin resmî unit'i gibi), `UMask=0077` (CA anahtarı); uygulama unit'i `UMask=0027`. Caddy ikilisi `/usr/local/bin/caddy`.
  - **WinSW:** Exe, XML ile aynı adı alır (`library-app.exe`, `library-caddy.exe`); loglar `C:\Kutuphane\winsw\logs` (`<logpath>`), boyut eşiği `10240` KB. `<serviceaccount>` 2.x biçimindedir: `<domain>.</domain>`, `<user>`, `<password>`, `<allowservicelogon>true</allowservicelogon>`.
  - **Kurulum belgesi:** Windows'ta `icacls` komutları yerel dilden bağımsız olsun diye Administrators ve SYSTEM'i SID'leriyle (`*S-1-5-32-544`, `*S-1-5-18`) verir. Elle komut oturumu Windows'ta WinSW XML'inden, Linux'ta `library.env`'den yüklenir ve `LIBRARY_SCHEDULER_ENABLED=0` yapılır; Windows'ta konsol UTF-8'e alınır (STATUS "Windows konsolu" tuzağı). Caddy arşivlerinin SHA-512 değerleri `checksums.txt`'ten alınıp belgeye yazıldı. Linux komutları Debian 12 içindir (Python 3.11 paket deposunda).
  - **Kılavuz:** Ekran adları şablonlardan ve formlardan alındı (ör. "Üye kartı, üye no, telefon ya da ad", "Onayla", "İade al", "Uzat", "Ödemeyi kaydet", engel metinleri). İlk girişte parola değişimi yalnız yöneticinin açtığı ya da sıfırladığı hesaplarda istenir (`create_staff`, `reset_password`); `createsuperuser` ile açılan ilk yönetici istenmez.
  - **README:** "Belgeler" bölümü girişin hemen altına, "Geliştirme ortamı" ve "Testler" sona eklendi; "Veri kaynakları" ve "Demo verisi" değişmedi (TC-352 geçiyor).
  - **Dosya listesi dışında değişen:** Yok. `docs/architecture.md` değişmedi.
  - **Bulut ağı:** `caddyserver.com` ve GitHub API engelliydi; sürüm `git ls-remote --tags` ile bulundu (son kararlı etiket `v2.11.7`), ikililer GitHub sürüm indirmelerinden alındı.
- **2026-11-01, G19 uygulayıcının seçtiği kullanıcıya görünen metinler** (PR'da onaya sunulur). Uygulamaya yeni arayüz ya da hata metni eklenmedi. Planın, ADR'lerin ve açılış kararlarının vermediği, kurulum sırasında görünen adlar ve açıklamalar:
  - **WinSW servisleri:** `library-app` görünen adı "Kütüphane uygulaması", açıklaması "Kütüphane ödünç sistemi: waitress uygulama sunucusu ve zamanlayıcı."; `library-caddy` görünen adı "Kütüphane Caddy", açıklaması "Kütüphane ödünç sistemi: Caddy ile HTTPS ve statik dosyalar."
  - **systemd:** `Description=Kütüphane ödünç sistemi (waitress)` ve `Description=Kütüphane ödünç sistemi (Caddy)`.
  - **Windows:** Güvenlik duvarı kuralının adı "Kutuphane HTTPS"; `library-svc` hesabının açıklaması "Kütüphane servis hesabı"; parola istemi "library-svc parolası".
  - **`deploy/library.env.example`:** Dosya başlığı ve her değişkenin üstündeki Türkçe açıklama satırları (küçük karar 8); örnek değerler `192.168.1.10`, `smtp.kurum.example`, `kutuphane@kurum.example`, `/mnt/library-backup/{backups,exports}`.
  - **Dağıtım dosyalarındaki açıklama yorumları:** Caddyfile, iki WinSW XML'i ve iki unit'in baş ve satır yorumları.
  - **Belgeler:** `docs/kurulum.md` ve `docs/kullanim-kilavuzu.md`'nin metinleri ve README'nin yeni bölümleri ("Belgeler", "Geliştirme ortamı", "Testler").
- **2026-11-01, PR #7 yerel doğrulaması ve onaylar** (kullanıcı, soru penceresi):
  - **Yerel doğrulama:** Plan §11'deki karar uyarınca yapıldı; kanıt G19'da. Caddy indirme komutunu auto mode sınıflandırıcısı reddettiği için hazırlanan betiği kullanıcı `!` önekiyle çalıştırdı; HTTPS kontrolleri Schannel `curl`'ün iptal denetimi yüzünden yeniden (`--ssl-no-revoke` ve Python `ssl`) çalıştırıldı.
  - **Metinler:** "G19 uygulayıcının seçtiği kullanıcıya görünen metinler" listesinin tamamı onaylandı.
  - **Birleştirme:** PR #7'nin `main`'e birleştirilmesi onaylandı.

## 12. Faz 6 doğrulama

- **Başlangıç:** 2026-11-01. Dal `feature/phase6-verification`. Ortam ve kapsam [ADR-0067](../decisions/0067-phase6-trial-project-single-windows-machine.md).
- **Faz 6 küçük kararları (onaylandı 2026-11-01):**
  1. Dal `feature/phase6-verification`; PR ile `main`'e birleşir.
  2. Ortam ve kapsam kararları tek ADR'de (ADR-0067).
  3. Faz 6 kaydı ayrı plan dosyası yerine bu bölümde; kabul tablosu burada.
  4. TC durumları `docs/test-plan.md`'de "Geçti", "Kaldı" ya da "Kapsam dışı (deneme projesi)".
  5. Yedek ve dışa aktarma klasörleri `C:\Kutuphaneackups` ve `C:\Kutuphane\exports` (makinede yalnız C: var); uygulama `C:\Kutuphanepp`.
  6. `main` üzerine annotated `v1.0.0-rc.1`; push ayrıca onaylanır; zip ADR-0064 komutuyla.
  7. Kurulumda takılınan her adım §12.2'de bulgu olarak kaydedilir; belge düzeltmesi `docs:` commit'iyle, kod değişirse `v1.0.0-rc.2`.
  8. TC-223 `docs/kurulum.md` "Yük testi" notuna göre ayrı bir test veritabanında, `--profile load` ile; `127.0.0.1` `LIBRARY_ALLOWED_HOSTS`'a geçici eklenir, sonra kaldırılır.
  9. Servisler, `library-svc`, kök sertifika, Firefox ve `C:\Program Files\Python311`'in (ADR-0068) temizliği faz 6 sonunda sorulur.
  10. `spec-reviewer` elle TC'lerden sonra çalıştırılır.
- **Kabul tablosu kararları (kullanıcı, 2026-11-02):**
  11. AC tablosunun sütunları: AC | FR | Otomatik kanıt | Elle kanıt | Sonuç | Not. Otomatik kanıtta AC'yi açıkça anan TC'ler tek tek, FR'ye bağlı diğerleri sayıyla yazılır.
  12. Sonuç değerleri: "Geçti", "Geçti (kısmi, ADR-0067)", "Kapsam dışı (ADR-0067)", "Kaldı".
  13. NFR-01…NFR-13 ayrı bir tabloda: hedef, ölçülen değer ya da kanıt, sonuç.
  14. G01'in "Planlandı" kalan altı TC'si (TC-01, 02, 03, 224, 235, 236) tablodan önce koşulur ve durumları test-plan'da güncellenir.

### 12.1 Elle TC'ler

| TC | Kapsam | Not |
|---|---|---|
| TC-223 | Tam | Yük testi, ayrı test veritabanı (küçük karar 8) |
| TC-225 | Tam | Geri yükleme süresi |
| TC-226 | Kapsam dışı | İkinci bilgisayar yok |
| TC-227 | Kapsam dışı | USB okuyucu yok |
| TC-228 | Kapsam dışı | Etiket kağıdı ve okuyucu yok |
| TC-229 | Kısmi | Yalnız dinlenen portlar; LAN dışı deneme kapsam dışı |
| TC-230 | Kısmi | `root.crt` bu makineye `docs/kurulum.md` "Personel bilgisayarları" adımlarıyla eklenir; ayrı personel bilgisayarı kapsam dışı |
| TC-231 | Tam | Chrome, Edge, Firefox; 1366 px |
| TC-232 | Kapsam dışı | Kurum SMTP hesabı yok |
| TC-233 | Kapsam dışı | Çok günlük çalışma yok; telafi mantığı otomatik testlerde (ADR-0053) |
| TC-234 | Tam | Tohum üye örneklemi |
| TC-319 | Tam | Kılavuz ve README okuması |

#### 12.1.1 Sonuçlar (kullanıcı koştu, 2026-11-01/02 kaydedildi)

Sıra TC-234 → TC-225 → TC-223 → TC-231 → TC-319 (TC-225 sayımları demo verisi değişmeden alındı).

- **TC-234 Geçti.** `tc234_sample.py … 25` → `members=200`, `@example.invalid` dışı e-posta 0, `000` ile başlamayan telefon 0, çıkış 0. 25 satırın hepsinde telefon `000 …`, e-posta (varsa) `uye<no>@example.invalid`. Kullanıcı notu: `seed/` ad ve soyad listelerinin rastgele birleşimi iki satırda tanınmış kişilerin ad-soyadını üretti (23, 94); telefon ve e-posta sentetik olduğu için gerçek bir kişiye ait kişisel veri yok, ölçüt karşılandı (kullanıcı kararı).
- **TC-225 Geçti.** Sayımlar `200 592 500`; `backup_db` → `C:\Kutuphane\backups\library-20261101.sqlite3`. Servisler durduruldu, veritabanı silindi, `restore_backup … --yes` → "Geri yüklendi: üye=200, nüsha=592, ödünç=500", servisler Running. "Önceki veritabanı korundu" satırı ve pre-restore dosyası yok (silinmiş veritabanı için beklenen). Belge 8. adım kontrolleri `https://127.0.0.2/`'de: giriş 200, üye ve kitap araması 200 (50'şer satır), `/uyeler/1/` ve `/uyeler/2/` 200 (5'er açık ödünç), `/gecikenler/` 200 (10 kayıt). Süre 6,1 s (< 1 saat).
- **TC-223 Geçti.** Ayrı veritabanı `C:\Kutuphane\loadtest\library-load.sqlite3` (küçük karar 8): 15 000 kitap (300 Open Library + 14 700 sentetik), 20 000 nüsha, 5 000 üye, 3 000 açık ödünç (300 gecikmiş), 97 000 kapalı. `explain_s1_s3.py`: S1 `sqlite_autoindex_copy_1`, S2 `loan_member_closed`, S3 `ledger_entry_member_id_482a4ddc` indeksini kullanıyor; `SCAN` yalnız skaler alt sorgu dallarında; çıkış 0. `loadtest.py --workers 5 --duration 120` (`http://127.0.0.1:8001`, TLS yok, ADR-0031): p95 kitap arama 150,2 ms, ödünç 128,7, iade 137,1, uzatma 112,5, üye arama 146,2; 9 582 istek, hata 0, "Sonuç: geçti", çıkış 0. waitress-serve durduruldu, parola dosyası silindi; test veritabanı temizliğe kadar kalıyor.
- **TC-229 Geçti (kısmi), TC-230 Geçti (kısmi).** Yeniden koşulmadı; kanıt §12.4 adım 16–19 ve B8/B9 doğrulaması (kullanıcı kararı 2026-11-01).
- **TC-231 Geçti (`v1.0.0-rc.2`, 2026-11-02; ilk denemede B10 ile Kaldı).** Hata sayfası kısmının yeniden denemesi aşağıda §12.2 B10 "Test ortamında doğrulama"da; aşağıdaki ilk deneme bulguları geçerli kalıyor.
  - **İlk deneme (rc.1, Kaldı):** Chrome 156.0.8078.74, Edge 156.0.4314.58, Firefox 159.0; 1366 × 768. Giriş ve hesap, yönetim, üye, katalog, ödünç ve borç ekranlarının hepsi ile ödünç verme (son tarih 16.11.2026), uzatma (30.11.2026), iade ve ödeme alma (1,00 TL) akışları denendi. Üç tarayıcıda da yatay taşma yok (`scrollWidth == clientWidth`), işlevler hatasız, uygulama ekranlarında `lang="tr"` ve metinler Türkçe; `/admin/` → 404. Kalma nedeni: 404 gövdesi Django'nun İngilizce varsayılanı (B10). `/denetim/`'de Hedef ve Ayrıntılar sütunlarının teknik değerleri (`ledger_entry #68`, JSON) tasarımdaki gibi; bulgu değil.
- **TC-319 Geçti.** Kılavuz: "Üyeye adını sorun" (satır 29, 102), "Geçmiş kapalı tarihleri silmeyin" (satır 129), geçmiş tarihli rıza notu ve örnek senaryo (satır 69). README: "Demo verisi"nde `migrate` → `createsuperuser` → `load_seed_data --profile demo --actor <ad>` sırası (satır 17–31); "Veri kaynakları" (satır 12–15) Open Library CC0 atfı, sabit ad listeleri, `000` önekli telefon ve `@example.invalid` açıklamasıyla.

### 12.2 Kurulum bulguları

- **B1 (§12.4 adım 2, 2026-11-01): Kişisel Python 3.11 kuruluyken "Install for all users" kurulamıyor.**
  - **Gözlem:** Python 3.11 serisinin Windows yükleyicisi olan son sürüm 3.11.9'dur (3.11.10+ yalnız kaynak). Makinede 3.11.9 kullanıcı başına kurulu (`py -0p` → `AppData\Local\Programs\Python\Python311`). `python-3.11.9-amd64.exe` aynı sağlayıcı anahtarını (`CPython-3.11`) görüp Modify/Repair/Uninstall ekranını açıyor; "Customize installation" çıkmıyor, Advanced Options'ta `InstallAllUsersState = disable`, `TargetDir` kullanıcı profilinde kilitli.
  - **Belge eksikleri:** (a) "Install for all users" kutucuğunun "Customize installation → Next → Advanced Options" ekranında olduğu yazmıyor. (b) Kişisel kurulum varsa önce kaldırılması gerektiği yazmıyor. (c) `py -3.11 -m venv`, PEP 514 gereği HKCU kaydını HKLM'ye tercih edebilir; servis hesabının okuyamadığı Python'la venv kurulur.
  - **Kontrol listesi hatası:** §12.4 adım 2'deki "Mevcut kurulumu kaldırma" talimatı yanlıştı (iki kurulumun yan yana durabileceği varsayılmıştı).
  - **Çözüm:** `docs/kurulum.md` Windows "Python ve sanal ortam" (a), (b), (c) için düzeltildi (`docs:`); venv komutu `& "C:\Program Files\Python311\python.exe" -m venv`. Test ortamında Python resmi NuGet paketinden kuruldu ([ADR-0068](../decisions/0068-phase6-python-from-nuget-package.md)); §12.4 adım 2 ve 9 güncellendi. Kod değişmedi.
  - **Doğrulama (§12.4 adım 9):** `pyvenv.cfg` → `home = C:\Program Files\Python311`, `version = 3.11.9`; NuGet paketindeki `ensurepip` venv'e pip'i kurdu, `requirements.txt`'teki 16 paket hatasız yüklendi.
- **B2 (§12.4 adım 8, 2026-11-01): "Sürüm arşivinin açılması" kod blokları yalnız güncellemeyi gösteriyor.**
  - **Gözlem:** Windows metni "ilk kurulumda klasörü silip arşivi açın" diyor ama kod bloğunda `Remove-Item C:\Kutuphane\app` yok, yalnız güncellemenin `Rename-Item C:\Kutuphane\app app-old` satırı var. Linux'ta `/opt/library/app` ilk kurulumda hiç oluşturulmuyor; bloktaki `sudo mv /opt/library/app /opt/library/app-old` ilk kurulumda `No such file or directory` verir. Test ortamında §12.4 adım 8 doğru sırayı verdiği için kurulum takılmadı.
  - **Çözüm:** `docs/kurulum.md` iki platformda da ilk kurulum ve güncelleme komutları ayrı bloklara bölündü (`docs:`). Kod değişmedi.
- **B3 (B2 incelemesi, 2026-11-01): Linux'ta `library.env`, arşiv açılmadan önce arşivden kopyalanıyor.**
  - **Gözlem:** Linux "Klasörler ve izinler" bloğu `/opt/library/app/deploy/library.env.example`'ı kopyalıyor; `/opt/library/app` ise sonraki "Sürüm arşivinin açılması"nda oluşuyor. İlk kurulumda `install: cannot stat` verir. Test ortamında Linux yok (ADR-0067); belge okumasıyla bulundu.
- **B4 (§12.4 adım 11, 2026-11-01): `LIBRARY_SECRET_KEY` komutu çıplak `python` kullanıyor.**
  - **Gözlem:** Ortak gövdedeki `python -c "import secrets; …"` temiz bir Windows sunucuda Microsoft Store kısayoluna (`WindowsApps\python.exe`) düşer: belgedeki "all users" kurulumunda "Add Python to environment variables" işaretlenmiyor, `C:\Kutuphane\venv\Scripts` de bu adımda `PATH`'te değil. Debian 12'de `python-is-python3` yoksa `python` komutu hiç yok. Test ortamında kişisel Python 3.11.9 kullanıcı `PATH`'inde olduğu için anahtar hatasız üretildi (öngörü (e) gerçekleşti).
- **B5 (§12.4 adım 11–12, 2026-11-01): WinSW XML'leri kullanılmadan önce kopyalanmıyor.**
  - **Gözlem:** "Hazırlık" XML'lerin doldurulmasını, kurulum adımı 2'deki "Komutların elle çalıştırılması" da `C:\Kutuphane\winsw\library-app.xml`'in okunmasını istiyor; XML'lerin `C:\Kutuphane\winsw\`'e kopyalandığı satır ise kurulum adımı 5'in ("Servisler") altında. Test ortamında §12.4 adım 11 kopyayı öne aldığı için takılmadı.
- **B3–B5 ortak kök ve çözüm (kullanıcı onayı, 2026-11-01):** "Ortam değişkenleri" Hazırlık'taydı; yani Python, sanal ortam ve ortam dosyalarının yerine konmasından önce. `docs/kurulum.md` yeniden sıralandı (`docs:`): ortam değişkenleri, sanal ortamdan sonra kurulum adımı 2 oldu (eski 2–7 → 3–8). İki platform bölümüne de "Python ve sanal ortam"dan sonra "Ortam dosyası" eklendi: Windows'ta XML kopyası, `C:\Kutuphane\venv\Scripts\python.exe -c …` ve doldurma; Linux'ta `library.env` kopyası (B3, "Klasörler ve izinler"den taşındı), `/opt/library/venv/bin/python -c …` ve `sudoedit`. Windows "Servisler"de yalnız exe kopyaları kaldı. Dışa aktarma parola dosyası "Klasörler ve izinler"de kaldı. `docs/architecture.md` §8'deki adım listesi de sekiz adıma güncellendi. Kod değişmedi; `tests/test_deploy_files.py` 20 passed.
- **B6 (§12.4 adım 11, 2026-11-01): `__DOLDUR__` kontrolü yanlış pozitif veriyor.**
  - **Gözlem:** Belge "bütün `__DOLDUR__` değerlerini doldurun" diyor ama kontrol komutu vermiyor. Akla gelen `Select-String "__DOLDUR__" C:\Kutuphane\winsw\*.xml`, iki XML'in baştaki açıklama yorumundaki (satır 6: "`__DOLDUR__` değerlerini kurulumda doldurun.") metni de yakaladığı için bütün alanlar dolu olsa da 2 satır döndürüyor. `Select-String 'value="__DOLDUR__"|>__DOLDUR__<'` boş döndü (doğru sonuç).
- **B7 (§12.4 adım 15, 2026-11-01): `w32tm` komutları `w32time` servisi durmuşken hata veriyor (öngörü (b) gerçekleşti).**
  - **Gözlem:** `w32time` Manual/Stopped iken belgedeki iki komut da `The following error occurred: Hizmet başlatılmadı. (0x80070426)` verdi. `Start-Service w32time` sonrası `w32tm /resync` → "The command completed successfully."; `w32tm /query /status` → `Source: time.windows.com,0x9`, Stratum 5, son eşitleme 1.11.2026 19:50:20. Belge servisin durumunu ve başlangıç türünü ele almıyor; saat dilimi kontrolü için de komut vermiyor (`Get-TimeZone` → `Turkey Standard Time`, UTC+03:00, beklenen).
- **B8 (§12.4 adım 16, 2026-11-01): Caddy yönetim ucu `127.0.0.1:2019`'u dinliyor; belgedeki kontrol komutu bunu göstermiyor (öngörü (d) gerçekleşti).**
  - **Gözlem:** `netstat -ano | findstr ":2019"` → `TCP 127.0.0.1:2019 LISTENING 532` (Caddy). Belgenin ortak gövdesi "Caddy yalnız `<IP>:80` ve `<IP>:443`'ü dinler", Windows "Kontrol"ü "`127.0.0.1:8000` ve `<IP>:443`, `<IP>:80` dışında bir dinleme adresi olmamalıdır" diyor. Belgedeki `findstr ":8000 :443 :80"` `:2019`'u hiç göstermediği için kendi iddiasını doğrulayamıyor; ayrıca dinleme dışı satırları (makinenin dış `:443` bağlantıları) da eşliyor. G19'da bu uç görülmüş, "ek genel seçenek gerekmedi" denmişti (§11); belge metni güncellenmemişti. Ayrıca `UDP 127.0.0.2:443` (HTTP/3) dinleniyor; güvenlik duvarı kuralı yalnız TCP açtığı için LAN'dan HTTP/3 kapalı kalır, tarayıcılar TCP'ye düşer. Diğer dinlemeler beklendiği gibi: `127.0.0.1:8000` (PID 15024), `127.0.0.2:80` ve `127.0.0.2:443` (PID 532).
- **B9 (§12.4 adım 17, 2026-11-01): Ortak gövdedeki `curl -k` Windows PowerShell 5.1'de çalışmıyor (öngörü (c) gerçekleşti).**
  - **Gözlem:** `curl -k https://127.0.0.2/static/css/app.css` → `Invoke-WebRequest : A parameter cannot be found that matches parameter name 'k'.` (`curl`, `Invoke-WebRequest` takma adı). `/admin/` → 404 ve `http://` → HTTPS kontrolleri için belgede komut yok. `curl.exe` ile üç kontrol de beklendiği gibi: `/static/css/app.css` → 200, `/admin/` → 404, `http://127.0.0.2/` → `308 https://127.0.0.2/`.
- **B6–B9 çözümü (kullanıcı onayı, 2026-11-01; dördünde de önerilen seçenek):** Yalnız `docs/kurulum.md` değişti (`docs:`); Caddyfile, XML'ler, kod ve sürüm arşivi aynı, `v1.0.0-rc.2` gerekmedi.
  - **B6:** Windows "Ortam dosyası"na dar desenli kontrol eklendi: `Select-String 'value="__DOLDUR__"|>__DOLDUR__<' C:\Kutuphane\winsw\*.xml` boş olmalı. Depodaki örneklerde desen 12 yer tutucunun hepsini yakaladı, yalnız iki yorum satırını dışarıda bıraktı (geniş desen 14). Linux örneğinde `__DOLDUR__` yok.
  - **B7:** Windows "NTP": `Set-Service w32time -StartupType Automatic`, `Start-Service w32time`, `w32tm /resync`, `w32tm /query /status`, `Get-TimeZone`; hata metni ve beklenen saat dilimi değerleri yazıldı. Linux `timedatectl set-ntp true` servisi zaten açtığı için değişmedi.
  - **B8:** Caddyfile'a `admin off` eklenmedi: uç yalnız loopback'te, NFR-08 (LAN dışı erişim) ihlal edilmiyor ve kod değişikliği rc.2 gerektirirdi. Ortak gövde artık "ağa açık dinleme yalnız `<IP>:80` ve `<IP>:443`; waitress `127.0.0.1:8000`, Caddy yönetim ucu `127.0.0.1:2019`" diyor. İki platformun "Kontrol"ü Caddy'nin bütün dinlemelerini ve 80/443/8000/2019 portlarını listeleyen komuta geçti (Windows `Get-NetTCPConnection -State Listen … -or $_.OwningProcess -eq (Get-Process caddy).Id`; Linux `ss -ltnp | grep -E ':(80|443|8000|2019)\b|"caddy"'`); beklenen tam dört satır. Süreç adıyla süzülmedi: `waitress-serve.exe` yalnız başlatıcıdır, soketi alt `python` süreci tutar.
  - **B9:** Ortak gövde yalnız beklenen sonuçları söylüyor (200, 404, 308); komutlar platform "Kontrol"üne taşındı (ADR-0060 yapısı): Windows `curl.exe … -o NUL`, Linux `curl … -o /dev/null`.
  - **Doğrulama (bu makinede, Windows PowerShell 5.1.26100, servisler çalışırken):** Windows dinleme komutu `127.0.0.2:80`, `127.0.0.2:443`, `127.0.0.1:2019` (Caddy, PID 13520), `127.0.0.1:8000` (python, PID 12372) olmak üzere dört satır verdi; üç `curl.exe` → `200`, `404`, `308 https://127.0.0.2/`. Linux komutları çalıştırılmadı (Linux ortamı yok, ADR-0067).
- **B10 (TC-231, 2026-11-02): Hata sayfaları İngilizce (NFR-09 "Yalnız Türkçe").**
  - **Gözlem:** `/admin/` 404 gövdesi "Not Found / The requested resource was not found on this server." Projede `templates/400.html`, `403.html`, `404.html`, `500.html` yok; Django 5.2.18'in `django.views.defaults` sayfaları gettext'ten geçmeyen sabit İngilizce metin (`Not Found`, `403 Forbidden`, `Bad Request (400)`, `Server Error (500)`). Etki `/admin/` ile sınırlı değil: uygulama görünümlerindeki `get_object_or_404`/`Http404` (olmayan üye, kitap ya da nüsha) ve `accounts/permissions.py`'deki `PermissionDenied` (yönetici olmayan personel, yönetici yolu) aynı sayfaları gösteriyor. Otomatik testler bu sayfaların dilini sınamıyordu.
  - **Karar (kullanıcı onayı, 2026-11-02, önerilen seçenek):** Türkçe hata şablonları, test önce (TDD); kod değiştiği için `v1.0.0-rc.2` (küçük karar 7), test ortamında güncelleme ve TC-231'in hata sayfası kısmının yeniden denenmesi. Ayrıntılar küçük karar listesiyle onaylanacak.
  - **Küçük kararlar (onaylandı 2026-11-02, 1–9):** (1) dal `feature/phase6-verification`; (2) `tests/test_error_pages.py`, TC-367 (işleyiciler) ve TC-368 (gerçek yollar), önce kırmızı; (3) 400/403/404 `base.html`'den türer, 500 bağımsız (`extends`, `url`, `static` yok; `server_error` bağlamsız çizilir, 500 sayfasının yedeği yok); (4) metinler: 404 "Sayfa bulunamadı" / "Aradığınız sayfa ya da kayıt bulunamadı. Adresi kontrol edin." + "Ana sayfa"; 403 "Erişim izni yok" / "Bu sayfayı açma yetkiniz yok. Gerekiyorsa bir yöneticiye başvurun."; 400 "Geçersiz istek" / "İstek işlenemedi. Adresi kontrol edip yeniden deneyin."; 500 "Sunucu hatası" / "Beklenmeyen bir hata oluştu. İşlemi yeniden deneyin; sorun sürerse yöneticiye bildirin."; (5) CSRF sayfası denetlenir; (6) ADR yok; (7) `test:`, `fix:`, `docs:` commit'leri; (8) `v1.0.0-rc.2` dal HEAD'ine, etiket ve push ayrıca onaylanır; (9) test ortamı `docs/kurulum.md` "Güncelleme" ile güncellenir, TC-231'in hata sayfası kısmı üç tarayıcıda yeniden denenir.
  - **Uygulamada çıkan iki soru (kullanıcı onayı, ikisinde de önerilen):** (a) Django'nun CSRF sayfasının gövdesi gettext ile Türkçe, ama şablonda sabit `<html lang="en">` ve `<title>403 Forbidden</title>` var → `templates/403_csrf.html` eklendi: "Form güvenlik kontrolünden geçemedi" / "Sayfayı yenileyip formu yeniden gönderin; sorun sürerse tarayıcıda çerezlerin açık olduğunu kontrol edin." (`csrf_failure` istek bağlamı vermez; menü boş kalır). (b) `accounts/tests/test_views.py`'nin dar URLconf'u `base.html`'in menü bağlantılarını (`administration:home`) çözemediği için 403 şablonu `NoReverseMatch` veriyordu → test URLconf'una `path("", include("library_site.urls"))` eklendi; test amacı değişmedi.
  - **Çözüm ve doğrulama (2026-11-02):** `f0e1a71` (`test:`, 7 test önce kırmızı), `96ba347` (`fix:`, beş şablon). Tam koşu 1049 passed (1042 + 7); dört kapsam eşiği çıkış 0 (domain %100, yetki %100, servis %99, operations %99); proje %97; `makemigrations --check` temiz. Not: bu oturumda pytest'in varsayılan geçici kökü (`%TEMP%\pytest-of-Mehmet Emin`, Haziran 2026'dan, ACL okunamıyor) `WinError 5` verdiği için koşu `--basetemp=<scratchpad>\pytest-tmp` ile yapıldı; kodla ilgisi yok, klasöre dokunulmadı.
  - **Sürüm (2026-11-02, kullanıcı onayı):** annotated `v1.0.0-rc.2` → `6cbd3a1` (yalnız yerel). `git archive --format=zip --prefix=library/ v1.0.0-rc.2` → `library-v1.0.0-rc.2.zip`, 617 417 bayt, SHA-256 `bc5239f34ddf85861cc9257fd407d5f7dfa69ba35ea55a9c36150426c6543ee1`. rc.1 → rc.2 farkı yalnız şablonlar, testler ve belgeler (`deploy/`, `requirements.txt`, migration aynı).
  - **Test ortamında güncelleme (2026-11-02, kullanıcı koştu, `docs/kurulum.md` "Güncelleme" 1–9):** `library-app` ve `library-caddy` Stopped; `backup_db` → "Yedek alındı: C:\Kutuphane\backups\library-20261102.sqlite3", "Silinen eski yedek: 0"; zip'in `Get-FileHash` değeri beklenenle aynı (`BC5239F3…6543EE1`); `app` → `app-old`, arşiv açılıp `library` → `app`; `pip install -r requirements.txt` hepsi "Requirement already satisfied"; `migrate` "No migrations to apply"; `collectstatic --noinput` "2 static files copied to 'C:\Kutuphane\static'" (depodaki iki statik dosyanın ikisi; `git diff v1.0.0-rc.1 v1.0.0-rc.2 -- static` boş, `git archive` dosya zamanını commit zamanı yaptığı için yeniden kopyalandılar); adım 7 atlandı (`deploy/` aynı); iki servis Running; `curl.exe` → `200`, `404`, `308 https://127.0.0.2/`. Belgeden tek sapma Claude'un eklediği iki `Set-Location` (`C:\Kutuphane` ve `C:\Kutuphane\app`, "klasör kullanımda" hatasını önlemek için); komutlar onlarla koşuldu ve hata çıkmadı, belge değişmedi.
  - **Test ortamında doğrulama (TC-231 hata sayfası kısmı, 2026-11-02, kullanıcı koştu):** Önce `admin` ile `/personel/yeni/`'den yönetici olmayan görevli (CLERK) personel hesabı `gorevli` açıldı, ilk giriş parola değişimi yapıldı. Kontroller gerçek tarayıcı motorlarında otomasyonla yapıldı: Chrome 156 ve Edge 156 CDP, Firefox 159.0 Marionette; her sayfada `<title>`, `<h1>`, `document.documentElement.lang`, personel menüsü ve Çıkış düğmesi ile İngilizce metin araması okundu. Üç tarayıcıda da aynı sonuç: (1) anonim `/admin/` → 404, "Sayfa bulunamadı" / "Sayfa bulunamadı · Kütüphane", menü yok; (2) `admin` ile `/uyeler/999999/` → 404, "Sayfa bulunamadı", menü ve Çıkış var; (3) `gorevli` ile `/personel/` → 403, "Erişim izni yok" / "Erişim izni yok · Kütüphane", menü ve Çıkış var. Hepsinde `lang` = `"tr"`, İngilizce metin yok. 400, 500 ve CSRF sayfaları elle denenmedi; TC-367 ve TC-368 otomatik sınıyor. B10 kapandı, TC-231 Geçti.
- **Spec incelemesi (faz 6 adım 4, 2026-11-02, küçük karar 10):** `spec-reviewer` alt ajanı SRS, tasarım belgeleri, test planı, plan ve ADR'lere karşı uygulamanın tamamını ve testleri okudu. Bulgu çıkmadı, dört soru çıktı; Claude dördünü de kodda doğruladı. Kullanıcı dördünde de önerilen seçeneği seçti:
  1. **AC-25 ile ADR-0018 çelişiyordu:** AC-25 borç hareketlerinin "üye bağı" kaldırılır diyordu. Kod ADR-0018'i ve data-design I6'yı izliyor (yalnız `loan_id` boşalır). AC-25 metni ADR'ye uyduruldu (`docs:`), kod değişmedi.
  2. **Kapalı son tarih (B11, aşağıda).**
  3. **E-posta değişince rıza:** Rıza GIVEN kalıyor, yeni olay yazılmıyor. Davranış [ADR-0070](../decisions/0070-email-change-keeps-consent.md) ile kayda geçti. Davranışı sınayan mevcut adsız test TC-371 olarak numaralandı. Kod değişmedi.
  4. **KL-46 hata tablosu boştu:** B1–B9'un hepsi belge kusuruydu ("Kod değişmedi"), kod hatası olanlar yalnız B10 ve B11. Test-plan §8'e HT-01 (B10, Düşük) ve HT-02 (B11, Kritik: para hesabı) "Kapandı" olarak yazıldı.
- **B11 (spec incelemesi, 2026-11-02): Ödünçten sonra kapatılan son tarih gecikme günü sayılıyor (FR-12, ADR-0040).**
  - **Gözlem:** `late_days` kapalı tarihleri `(due_on, on]` aralığında düşüyordu. FR-07 son tarihi ödünç verilirken açık güne kaydırdığı için son tarih ancak sonradan kapatılırsa kapalı olabilir. Örnek: son tarih 11-16, sonradan 11-16 kapatılıyor, 11-17'de iade → 1 gün, 5,00 TL ceza. TC-277 bu sınırı "son tarih düşülmez" diye sınıyordu.
  - **Karar (kullanıcı onayı, 2026-11-02, önerilen seçenek):** Düzeltme ve yeni ADR. TC-277'nin bu satırı sınadığı söylenince kullanıcı "Düzelt, TC-277 değişsin" ile kararını onayladı. [ADR-0069](../decisions/0069-closed-due-date-not-a-late-day.md): aralık `[due_on, on]`. Haftalık kapalı günler, OVERDUE_1 penceresi ve uzatmadaki gecikme kontrolü ADR-0040'taki gibi kalıyor.
  - **Küçük kararlar (onaylandı 2026-11-02, 1–9):**
    - (1) Dal `feature/phase6-verification`.
    - (2) ADR-0069 ve ADR-0070.
    - (3) TC-277'nin ilk satırı 3; TC-369 (birim), TC-370 (servis, `add_closed_date` ile), TC-371.
    - (4) TC-371'in TDD sapması (aşağıdaki sapma nedeniyle oluşmadı).
    - (5) Dosya yerleri.
    - (6) Belgeler: SRS AC-25 ve sözlük, test-plan, plan, STATUS. FR-12'nin metni zaten doğru olduğu için değişmedi.
    - (7) `test:`, `fix:`, `docs:` commit'leri.
    - (8) Dal HEAD'ine yerel `v1.0.0-rc.3`. Gecikme gününü sınayan elle TC olmadığı için test ortamı güncellenmiyor; kurulu sürüm rc.2 kalıyor.
    - (9) Tam koşu, kapsam eşikleri ve `makemigrations --check`.
  - **Uygulamadaki sapma:** `members/tests/test_services.py`'deki `test_changing_email_keeps_consent` TC-371'in davranışını zaten sınıyordu. İkinci bir test yazılmadı; bu test `test_tc371_…` adıyla numaralandı. Kullanım kılavuzunun gecikme günü paragrafına ve `docs/architecture.md`'nin karmaşıklık tablosuna ADR-0069 eklendi.
  - **Çözüm ve doğrulama (2026-11-02):** `ca0ee78` (`test:`; TC-277[closed0], TC-369, TC-370 önce kırmızı: TC-370'te `fine_kurus` 500), `29febed` (`fix:`, `circulation/domain.py`'de tek koşul). Tam koşu 1051 passed (1049 + TC-369 + TC-370); kapsam ve migration sonuçları §12.3.1'de.
- **Bulgu olmayan gözlem (§12.4 adım 18):** Firefox 159'da `security.enterprise_roots.enabled` ilk değeri `true`; Caddy CA'sı `certutil` ile Windows deposuna eklenince Firefox uyarısız açtı. Belgenin koşullu Firefox adımı ("kullanmıyorsa") doğru; değiştirilmedi.

### 12.4 Kurulum kontrol listesi (2026-11-01)

Ana kaynak `docs/kurulum.md`'dir; bu liste yalnız sırayı ve ADR-0067'nin getirdiği sapmaları gösterir.
Her adımda **belgeyi oku, komutu belgeden al**. Belgede takıldığın, belirsiz bulduğun ya da hata veren her yeri not et ve Claude'a yaz: bunlar §12.2'ye bulgu olarak girer.

Sabit değerler:

| Ne | Değer |
|---|---|
| IP (`LIBRARY_HOST`, `LIBRARY_BIND`, `LIBRARY_ALLOWED_HOSTS`) | `127.0.0.2` |
| Yedek klasörü (`LIBRARY_BACKUP_DIR`) | `C:\Kutuphane\backups` |
| Dışa aktarma klasörü (`LIBRARY_EXPORT_DIR`) | `C:\Kutuphane\exports` |
| Sürüm arşivi | `library-v1.0.0-rc.1.zip` (`git archive --format=zip --prefix=library/ v1.0.0-rc.1 -o library-v1.0.0-rc.1.zip`, depo klasöründe) |

#### A. Hazırlık (normal kullanıcı)

1. Bir indirme klasörü aç, ör. `C:\Users\Mehmet Emin\Downloads\kutuphane-kurulum`, ve sürüm arşivini buraya kopyala.
2. **Python 3.11.9, NuGet paketinden** ([ADR-0068](../decisions/0068-phase6-python-from-nuget-package.md), bulgu B1). Bu makinedeki 3.11.9 yalnız kullanıcı başına kurulu ve python.org yükleyicisi kaldırmadan "all users" kurmuyor; kişisel kurulumu kaldırma, ona dokunma. Yönetici PowerShell'de, indirme klasöründe:
   ```powershell
   Invoke-WebRequest -UseBasicParsing https://www.nuget.org/api/v2/package/python/3.11.9 -OutFile python.3.11.9.zip
   (Get-FileHash python.3.11.9.zip -Algorithm SHA512).Hash
   # Beklenen: E353A7EFD159EF98AB9CE1011854A30D5D778F59D96FC9BB11B07CED2990B355F030486B0707F798C73C4420173AB111876A96EAD5981718B604C4CDD71C558D
   Expand-Archive python.3.11.9.zip .\python-nuget
   New-Item -ItemType Directory "C:\Program Files\Python311"
   Copy-Item .\python-nuget\tools\* "C:\Program Files\Python311" -Recurse
   & "C:\Program Files\Python311\python.exe" -c "import sys; print(sys.version)"
   ```
3. Caddy 2.11.7 Windows zip'ini ve WinSW 2.12.0 `WinSW-x64.exe`'yi belgedeki bağlantılardan indirme klasörüne indir.
4. Firefox'u mozilla.org'dan kur (TC-231, TC-230).

#### B. Kurulum (Yönetici olarak açılmış PowerShell, indirme klasöründe)

Belgenin "İlk kurulum" sırası, komutlar "Windows" bölümünden:

5. **Sabit IP:** Atla (ADR-0067).
6. **Hesap:** Belgedeki gibi. Parolayı bir yere not et; XML'lere yazılacak.
7. **Klasörler ve izinler:** İlk `New-Item` ve dört `icacls` satırı belgedeki gibi.
   **Sapma (harici disk yok):** `E:` komutları yerine:
   ```powershell
   New-Item -ItemType Directory -Force C:\Kutuphane\backups, C:\Kutuphane\exports
   icacls C:\Kutuphane\backups /grant "library-svc:(OI)(CI)M"
   icacls C:\Kutuphane\exports /grant "library-svc:(OI)(CI)M"
   ```
   Parola dosyası belgedeki gibi (`notepad ...`, ilk satır parola, UTF-8).
8. **Sürüm arşivi:** "İlk kurulumda klasörü silip arşivi açın": `Remove-Item C:\Kutuphane\app`, sonra `Expand-Archive` ve `Rename-Item` (zip adı `library-v1.0.0-rc.1.zip`).
9. **Python ve sanal ortam:** Belgedeki iki komut (venv komutu B1 düzeltmesiyle `& "C:\Program Files\Python311\python.exe" -m venv C:\Kutuphane\venv`). Ardından şunu çalıştır ve çıktıyı bana yaz:
   ```powershell
   Get-Content C:\Kutuphane\venv\pyvenv.cfg
   ```
   `home` satırı `C:\Program Files\Python311` göstermeli. `AppData` gösteriyorsa bu bir bulgudur; durup bana yaz.
10. **Caddy:** Özeti karşılaştır, zip'i aç (belge "Caddy").
11. **Servis dosyaları:** WinSW kopyaları ve XML'ler (belge "Servisler", ilk blok). XML'leri doldur:
    - `<password>` (iki XML): `library-svc` parolası
    - `LIBRARY_SECRET_KEY`: belgedeki `python -c ...` komutunun çıktısı
    - `LIBRARY_ALLOWED_HOSTS`, `LIBRARY_HOST`, `LIBRARY_BIND`: `127.0.0.2`
    - `LIBRARY_BACKUP_DIR`: `C:\Kutuphane\backups`; `LIBRARY_EXPORT_DIR`: `C:\Kutuphane\exports`
    - **SMTP (kurum hesabı yok, TC-232 kapsam dışı):** `LIBRARY_EMAIL_HOST` = `127.0.0.1`, `LIBRARY_EMAIL_USER` = `test`, `LIBRARY_EMAIL_PASSWORD` = `test`, `LIBRARY_EMAIL_FROM` = `kutuphane@example.invalid`. 09.00 hatırlatma görevi bağlanamayıp hata kaydı yazabilir; beklenen.
12. **migrate, collectstatic, ilk yönetici:** "Komutların elle çalıştırılması" bloğuyla bir oturum aç, sonra `migrate`, `collectstatic --noinput`, `createsuperuser`.
    **Test ortamı olduğu için** aynı oturumda demo verisini yükle (TC-231, TC-234 için):
    ```powershell
    python manage.py load_seed_data --profile demo --actor <createsuperuser'da verdiğin ad>
    ```
13. **Servisler:** Yedek klasörleri hazır; belgedeki `install`, `install`, `Start-Service library-caddy`, `Get-Service`. İki servis "Running" olmalı. Değilse `C:\Kutuphane\winsw\logs` içindeki son logları bana yaz.
14. **Güvenlik duvarı:** Atla (ADR-0067).
15. **NTP:** Belgedeki iki `w32tm` komutu; çıktıyı bana yaz. (Not: bu makinede `w32time` servisi şu an durmuş görünüyor; belgenin bu durumu karşılayıp karşılamadığına bakacağız.)

#### C. Kontrol (belge "İlk kurulum → Kontrol" ve "Windows → Kontrol")

16. `netstat` komutu (belge "Kontrol"); çıktıyı bana yaz. `<IP>` yerine `127.0.0.2`.
17. Belgedeki `curl -k https://<IP>/static/css/app.css` ve `/admin/` kontrolleri, IP `127.0.0.2`. Komutu **belgede yazdığı gibi** dene; PowerShell'de hata verirse bana yaz.
18. **Personel bilgisayarı adımları bu makinede** (belge "Personel bilgisayarları"): `root.crt`'yi `certutil -addstore -f Root root.crt` ile ekle (Yönetici komut istemi), Firefox adımı, kısayol isteğe bağlı.
19. Chrome, Edge ve Firefox'ta `https://127.0.0.2/` sertifika uyarısı olmadan açılmalı; `http://127.0.0.2/` HTTPS'e yönlenmeli.

Bitince ya da bir yerde takılınca bana yaz: hangi adım, ne çıktı. Kalan TC'leri (TC-223, TC-225, TC-231, TC-234, TC-319, TC-229 ve TC-230'un kalanı) ondan sonra birlikte yaparız.

### 12.3 Kabul tablosu

Biçim küçük kararlar 11–14'te. 2026-11-02'de dolduruldu.

#### 12.3.1 Test koşusu

- **Tam koşu (2026-11-02, `29febed`, B11 sonrası):** `python -m coverage run --branch -m pytest -q --basetemp=<scratchpad>` → `1051 passed`, çıkış 0 (1049 + TC-369, TC-370; TC-371 mevcut testin numaralanması). Kapsam eşiklerinin dördü de çıkış 0: domain %100 (383 satır, 110 dal), iki servis %99 (411 satır; 4 satır, 2 kısmi dal eksik), yetki %100, operations %99; `pdf/sheets.py` %100; proje %97. `makemigrations --check --dry-run` → "No changes detected". Aşağıdaki tablo ve önceki koşu değişmedi; ölçümler aynı.
- **Tam koşu (2026-11-02, `78b2d7d`):** Kod `96ba347` ve `v1.0.0-rc.2` ile aynı; sonraki commit'ler yalnız `docs/`. `python -m coverage run --branch -m pytest -q --basetemp=<scratchpad>` → `1049 passed`, çıkış 0 (`slow` dahil); proje toplam kapsamı %97. `python manage.py makemigrations --check --dry-run` → "No changes detected", çıkış 0. `--basetemp`'in nedeni: yereldeki `%TEMP%\pytest-of-Mehmet Emin` klasörüne erişim engelli (`WinError 5`); testlerin kendisiyle ilgisi yok (STATUS "Kum havuzu").
- **G01'in altı TC'si (küçük karar 14):** `python -m pytest tests/test_prod_settings.py -k "tc01 or tc02 or tc03 or tc235 or tc236" -v` → `19 passed` (TC-236 her zorunlu değişken için ayrı parametre). TC-224 aşağıdaki kapsam ölçümü. Altısı test-plan'da "Geçti (faz 6)".
- **Kapsam hedefleri (test-plan §4), aynı koşudan; her biri `coverage report --include=… --fail-under=…` çıkış 0:**

| Bileşen | Ölçüt | Hedef | Ölçülen |
|---|---|---|---|
| `*/domain.py` (TC-224, NFR-13) | Dal | ≥ %90 | %100 (383 satır, 110 dal, eksik 0) |
| `billing/services.py`, `circulation/services.py` | Dal | ≥ %85 | %99 (411 satır, 74 dal; 4 satır, 2 kısmi dal eksik) |
| `accounts/permissions.py`, `accounts/middleware.py` | Dal | %100 | %100 (46 satır, 10 dal) |
| `operations/*` | Dal | ≥ %80 | %99 (831 satır, 138 dal; 8 satır, 3 kısmi dal eksik) |
| `pdf/sheets.py` | Satır | ≥ %80 | %100 (111 satır) |

#### 12.3.2 Kabul ölçütleri (SRS §6)

"Otomatik kanıt" sütunundaki bütün TC'ler test-plan'da "Geçti" ve 12.3.1'deki tam koşuda geçiyor; "FR'ye bağlı n TC daha", Gereksinim sütununda FR'yi anıp AC'yi anmayan otomatik TC'lerin sayısıdır. Elle sonuçlar §12.1.1'de; kapsam dışı TC'ler [ADR-0067](../decisions/0067-phase6-trial-project-single-windows-machine.md)'de.

| AC | FR | Otomatik kanıt | Elle kanıt | Sonuç | Not |
|---|---|---|---|---|---|
| AC-01 | FR-01 | TC-44, TC-47; FR'ye bağlı 10 TC daha | — | Geçti | — |
| AC-02 | FR-02 | TC-115, TC-126, TC-286; 4 TC daha | — | Geçti | — |
| AC-03 | FR-03 | TC-57, TC-177, TC-254, TC-255, TC-371; 7 TC daha | TC-319 Geçti (kılavuzda geçmiş tarihli rıza notu) | Geçti | — |
| AC-04 | FR-04 | TC-39, TC-62, TC-66; 14 TC daha | — | Geçti | — |
| AC-05 | FR-05 | TC-64; 11 TC daha | — | Geçti | — |
| AC-06 | FR-06 | TC-71 (30 etiketli PDF, barkodlar çözücüyle okunuyor); 7 TC daha | TC-228 Kapsam dışı | Geçti (kısmi, ADR-0067) | Basılı etiketin gerçek okuyucuyla okunması denenmedi: etiket kağıdı ve okuyucu yok |
| AC-07 | FR-07 | TC-105; 8 TC daha | TC-231 akışında son tarih 16.11.2026 (2026-11-02 + 14 gün) | Geçti | — |
| AC-08 | FR-08 | TC-116…TC-119, TC-126, TC-127, TC-284; 7 TC daha | — | Geçti | — |
| AC-09 | FR-09 | TC-111, TC-135; 4 TC daha | TC-231 akışında iade, üç tarayıcıda | Geçti | — |
| AC-10 | FR-10 | TC-121, TC-123, TC-141, TC-142; 9 TC daha | TC-231 akışında uzatma (30.11.2026) | Geçti | — |
| AC-11 | FR-11 | TC-128 (`autofocus`, form sırası, 303 akışı), TC-281; 5 TC daha | TC-227 Kapsam dışı; TC-319 Geçti ("üyeye adını sorun") | Geçti (kısmi, ADR-0067) | "Fare yok, okuyucuyla" kısmı gerçek okuyucu olmadan denenmedi; ikinci senaryo (nüsha barkodu uyarısı) otomatik |
| AC-12 | FR-12 | TC-110, TC-112, TC-134, TC-136, TC-276, TC-283, TC-369, TC-370; 11 TC daha | TC-319 Geçti ("geçmiş kapalı tarihleri silmeyin") | Geçti | B11 (HT-02) kapandı: kapalı son tarih de düşülür (ADR-0069) |
| AC-13 | FR-13 | TC-80; 11 TC daha | TC-231 akışında ödeme alma (1,00 TL) | Geçti | — |
| AC-14 | FR-14 | TC-86, TC-87; 3 TC daha | — | Geçti | — |
| AC-15 | FR-15 | TC-150; 6 TC daha | — | Geçti | — |
| AC-16 | FR-16 | TC-153, TC-155, TC-272, TC-273, TC-292; 18 TC daha | — | Geçti | — |
| AC-17 | FR-17 | TC-76, TC-98; 4 TC daha | — | Geçti | — |
| AC-18 | FR-18 | TC-174, TC-175, TC-182 (bellek e-posta backend'i); 10 TC daha | TC-232 Kapsam dışı | Geçti | Üç senaryo da otomatik kanıtlı. Kurum SMTP'siyle gelen kutusuna teslim (TC-232) FR-18'in teslim edilebilirlik kısmı, AC senaryolarında yok |
| AC-19 | FR-19 | TC-183; 3 TC daha | — | Geçti | — |
| AC-20 | FR-20 | TC-171; 3 TC daha | TC-225 8. adımda `/gecikenler/` 200 (10 kayıt) | Geçti | — |
| AC-21 | FR-21 | TC-28; 5 TC daha | — | Geçti | — |
| AC-22 | FR-22 | TC-21; 6 TC daha (TC-01 dahil, Geçti (faz 6)) | — | Geçti | — |
| AC-23 | FR-23 | TC-131; 4 TC daha | — | Geçti | — |
| AC-24 | FR-24 | TC-23, TC-106; 3 TC daha | — | Geçti | — |
| AC-25 | FR-25 | TC-201…TC-203, TC-305; 15 TC daha | — | Geçti | 2. senaryonun metni ADR-0018'e uyduruldu (spec incelemesi): borç hareketlerinde yalnız ödünç bağı kalkar |
| AC-26 | FR-26 | TC-91; 11 TC daha | — | Geçti | — |
| AC-27 | FR-27 | TC-06, TC-07, TC-09; 7 TC daha | — | Geçti | — |
| AC-28 | FR-28 | TC-191, TC-320, TC-366; 18 TC daha | TC-225 Geçti: sayılar `200 592 500` aynen geldi, 6,1 s | Geçti | Silinen veritabanı belgedeki adımlarla geri yüklendi |
| AC-29 | FR-29 | TC-217, TC-342, TC-352; 20 TC daha | TC-234 Geçti (25 üyelik örneklem) | Geçti | Rastgele ad birleşimi iki satırda tanınmış kişilerin adını üretti; telefon ve e-posta sentetik, kullanıcı kararıyla ölçüt karşılandı (§12.1.1) |
| AC-30 | FR-37 | TC-25 (8 günde uyarı), TC-193 (doğru parolayla boş ortama geri yükleme, sayılar aynı), TC-194 (yanlış parola reddedilir, veritabanı değişmez); 19 TC daha (şifreli biçim TC-192 dahil) | TC-226 Kapsam dışı | Geçti (kısmi, ADR-0067) | Dosyanın ikinci bilgisayara USB ile taşınıp orada geri yüklenmesi denenmedi: ikinci bilgisayar ve USB disk yok |
| AC-31 | FR-38 | TC-74 (3 kartlı PDF, barkod çözücüyle okunuyor, ad yok); 5 TC daha | TC-228 Kapsam dışı | Geçti (kısmi, ADR-0067) | Basılı kartın gerçek okuyucuyla okunması denenmedi |
| AC-32 | FR-39 | TC-159, TC-161; 2 TC daha | — | Geçti | — |
| AC-33 | FR-40 | TC-259, TC-260, TC-285 | — | Geçti | — |
| AC-34 | FR-41 | TC-248, TC-249; 2 TC daha | — | Geçti | — |
| AC-35 | FR-42 | TC-242, TC-243; 2 TC daha | — | Geçti | — |

**Özet:** 35 AC'nin 31'i Geçti, 4'ü Geçti (kısmi, ADR-0067): AC-06, AC-11, AC-30, AC-31. Kaldı yok. Kısmi kalan kısımların hepsi bu makinede bulunmayan donanıma bağlı (okuyucu, etiket kağıdı, ikinci bilgisayar).

#### 12.3.3 İşlevsel olmayan gereksinimler (SRS §5)

| NFR | Hedef | Ölçülen / kanıt | Sonuç |
|---|---|---|---|
| NFR-01 | p95 < 500 ms, tasarım ölçeğinde, 5 eşzamanlı personel | TC-223: p95 kitap arama 150,2 ms, ödünç 128,7, iade 137,1, uzatma 112,5, üye arama 146,2; 9 582 istek, hata 0 (`--workers 5 --duration 120`; TLS hariç, ADR-0031). Betik mantığı TC-221, TC-222, TC-318, TC-353…TC-356 | Geçti |
| NFR-02 | 20 000 nüsha, 5 000 üye, 100 000 ödünç ile NFR-01 | TC-223 yük veritabanı: 20 000 nüsha, 5 000 üye, 100 000 ödünç (3 000 açık, 97 000 kapalı); S1–S3 `EXPLAIN` indeks kullanıyor. Profil sayıları TC-220, TC-317, TC-346 | Geçti |
| NFR-03 | RPO ≤ 24 saat | Günlük 02:00 yedek tetikleyicisi TC-208, yazma sırasında tutarlı yedek TC-190, kaçırılan yedeğin telafisi TC-336; birkaç günlük gerçek çalışma (TC-233) Kapsam dışı | Geçti (kısmi, ADR-0067) |
| NFR-04 | RTO ≤ 1 saat, test ortamında denenmiş | TC-225: 6,1 s; TC-320, TC-366 | Geçti |
| NFR-05 | Kaçırılan günlük görevler sonraki çalışmada, tekrar gönderimsiz | TC-178, TC-179, TC-209…TC-213, TC-310…TC-314, TC-335…TC-339, TC-361, TC-362, TC-364 (ADR-0053); servisin bir gece kapalı kaldığı gerçek çalışma (TC-233) Kapsam dışı | Geçti (kısmi, ADR-0067) |
| NFR-06 | Tuzlu, yavaş tek yönlü özet; düz parola yok | TC-03 Geçti (faz 6): parola `argon2$argon2id$` önekiyle saklanıyor. Test-plan'ın bu NFR'ye bağladığı HTTPS kanıtları: Caddyfile `tls internal` TC-363, sertifika zinciri TC-230 Geçti (kısmi: bu makine) | Geçti |
| NFR-07 | Her yönetici uç noktasına görevliyle 403, otomatik | TC-11, TC-31…TC-33, TC-368 | Geçti |
| NFR-08 | Yalnız FR-01 alanları; LAN dışından erişim yok | Veri minimizasyonu TC-52, TC-206, TC-330, TC-331, TC-342, TC-359…TC-364. TC-229 Geçti (kısmi): yalnız `127.0.0.2:80/443`, `127.0.0.1:8000`, `127.0.0.1:2019` dinleniyor (B8); LAN dışından gerçek deneme yapılmadı | Geçti (kısmi, ADR-0067) |
| NFR-09 | Yalnız Türkçe; güncel Chrome, Edge, Firefox; ≥ 1366 px | TC-231 Geçti (rc.2): Chrome 156, Edge 156, Firefox 159, 1366 × 768, taşma yok; TC-235 Geçti (faz 6); hata sayfaları TC-367, TC-368 (B10) | Geçti |
| NFR-10 | "istanbul", "İSTANBUL", "İstanbul" aynı sonuç | TC-34, TC-36, TC-47, TC-67 | Geçti |
| NFR-11 | Fare olmadan en fazla 3 etkileşim | TC-128 (odak ve form akışı); gerçek okuyucuyla deneme (TC-227) Kapsam dışı | Geçti (kısmi, ADR-0067) |
| NFR-12 | Kuruş hassasiyeti, kayan nokta hatası yok | TC-14…TC-17, TC-102, TC-238…TC-240 | Geçti |
| NFR-13 | İş kuralı modüllerinde dal kapsamı ≥ %90 | TC-224 Geçti (faz 6): `*/domain.py` %100 (12.3.1) | Geçti |

**Özet:** 13 NFR'nin 9'u Geçti, 4'ü Geçti (kısmi, ADR-0067): NFR-03, NFR-05, NFR-08, NFR-11. Kaldı yok.

**Test-plan §7 faz 6 çıkışı:** Must FR'lerin TC'leri geçiyor; her AC'nin kanıtı var; §4 kapsam hedefleri tutuyor; elle TC'ler yapıldı ya da ADR-0067 ile kapsam dışı; §8 hata tablosunda açık hata yok (HT-01 ve HT-02 kapandı). `spec-reviewer` 2026-11-02'de çalıştı: bulgu yok, dört soru (§12.2).
