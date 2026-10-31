# Görev planı: Kütüphane ödünç alma sistemi

- **Tarih:** 2026-10-31
- **İz:** Tam
- **Durum:** Faz 4 tamamlandı, onay kapısı geçildi. Kararlar alındı (ADR-0026…0048; küçük karar listesi onaylandı, 2026-10-31). Görevler, risk kaydı, test planı (319 TC), izlenebilirlik ve tutarlılık kontrolü yazıldı; inşa kontrolü ayıklandı (§8.1). Plan, test planı ve KL-1…KL-46 onaylandı (2026-10-31); faz 5 başladı: G01 tamam (2026-10-31); G02 kararları ADR-0049, ADR-0050 ve §11'de.

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
| docs/architecture.md, docs/data-design.md | Faz 4 tutarlılık düzeltmeleri (§8) |
| docs/test-plan.md | Faz 4'te oluşturuldu (2026-10-31): 319 TC, test taslağından revize edildi |
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
- [ ] Tamamlandı

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
    - §4.1'deki yönetici yollarının listesi, testteki sabit bir listeyle karşılaştırılır. Böylece yanlışlıkla işaretsiz kalan bir yönetici view'ı da yakalanır.
  - Bu test sonraki görevlerin URL'lerini de kapsar. Her görev kendi yönetici yollarını sabit listeye ekler.
- **Testler:** TC-27…TC-33, TC-237, TC-248…TC-252 (13 TC; `docs/test-plan.md` §6)
- **Doğrulama:** `python -m pytest accounts tests/test_authorization.py -q` → hepsi geçer.
- [ ] Tamamlandı

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
- [ ] Tamamlandı

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
- [ ] Tamamlandı

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
- [ ] Tamamlandı

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
- [ ] Tamamlandı

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
- [ ] Tamamlandı

### Görev G10: Ödünç domain'i

- **Gereksinimler:** FR-07, FR-08, FR-10, FR-11 (üye alanı), FR-12, FR-24 (kaydırma), NFR-13; AC-07, AC-08, AC-10, AC-11 (2. senaryo), AC-12, AC-24 (1. senaryo); ADR-0023, ADR-0028, ADR-0037 (`copy_found_on`), ADR-0040, ADR-0046; data-design §2.4; küçük karar 3 (faz 1); KL-6, KL-29, KL-35, KL-39.
- **Dosyalar:** oluştur `circulation/{__init__,apps,domain,models}.py`, `circulation/migrations/0001_initial.py` (`Loan`; kısmi benzersiz indeks `UniqueConstraint(fields=["copy"], condition=Q(closed_on__isnull=True))`, data-design §4'teki indeksler, `copy_found_on` ve CHECK kısıtı; ADR-0037, KL-39), `circulation/tests/test_domain.py`.
- **Arayüzler:** sunar
  - `NoOpenDayError(RuleViolation)`: mesajı ADR-0028'deki metindir.
  - `due_date(start: date, period_days: int, is_closed: Callable[[date], bool]) -> date`. Aday tarih `start + period_days` olur. `i = 0…366` için `aday + i` kontrol edilir ve ilk açık gün döner; hiçbiri açık değilse `NoOpenDayError` fırlatılır. En kötü durum O(366).
  - `late_days(due_on: date, on: date, closed_dates: AbstractSet[date]) -> int`: `max(0, (on − due_on).days − |{d ∈ closed_dates : due_on < d ≤ on}|)` (ADR-0040). O(c).
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
- [ ] Tamamlandı

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
- [ ] Tamamlandı

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
- [ ] Tamamlandı

### Görev G13: Geciken listesi ve hatırlatmalar

- **Gereksinimler:** FR-18, FR-19, FR-20, FR-03 (AC-03'ün 2. koşulu), NFR-05 (pencereler); AC-03, AC-18, AC-19, AC-20; ADR-0004, ADR-0007, ADR-0039; küçük kararlar 6 ve 7 (faz 3); KL-1, KL-11, KL-13, KL-23, KL-28.
- **Dosyalar:** oluştur `notifications/{__init__,apps,models,domain,services,views,urls}.py`, migration (`reminder_log.due_on` ve data-design §2.6'daki `(loan_id, kind, due_on)` kısmi benzersiz indeksi dahil, ADR-0039), `notifications/templates/notifications/overdue.html`, `notifications/templates/notifications/email/{due_soon,overdue}_{subject,body}.txt`, `notifications/management/commands/send_reminders.py`, `notifications/tests/*`.
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
- [ ] Tamamlandı

### Görev G14: Yedek, şifreli dışa aktarma ve geri yükleme

- **Gereksinimler:** FR-28, FR-37, NFR-03, NFR-04; AC-28, AC-30; ADR-0002, ADR-0006, ADR-0011; küçük kararlar 13, 14 ve 15 (faz 3), küçük karar 6 (faz 4); KL-4, KL-14, KL-24.
- **Dosyalar:** oluştur `operations/{__init__,apps,domain,libx,backup,applock}.py`, `operations/management/commands/{backup_db,export_backup,restore_backup}.py`, `operations/tests/*`.
- **Arayüzler:**
  - domain:
    - `backup_name(on: date) -> str`
    - `backups_to_delete(names: list[str], run_on: date, keep_days: int = 30) -> list[str]`. Adı desene uymayan dosyalara dokunulmaz.
    - `latest_backup(names: list[str]) -> str | None`
    - `exports_to_delete(names: list[str], run_on: date, keep_days: int = 56) -> list[str]` (KL-24). Adı desene uymayan dosyalara dokunulmaz.
  - `libx.encrypt(plaintext: bytes, passphrase: str, n=2**17, r=8, p=1) -> bytes` ve `libx.decrypt(blob: bytes, passphrase: str) -> bytes`. Biçim architecture §6.3'tedir. Hatalı parola ya da bozuk dosya `LibxError("Parola hatalı ya da dosya bozuk")`, bilinmeyen sürüm `LibxError("Desteklenmeyen dosya sürümü")` verir.
  - `backup.backup_db(run_on: date) -> Path`. `sqlite3.Connection.backup` önce geçici bir dosyaya yazılır, sonra `os.replace` ile yerine konur. Ardından eski yedekler silinir.
  - `backup.export_backup(run_on: date, passphrase_file: Path) -> Path`. Başarılı yazımdan sonra eski dışa aktarmaları siler (KL-24).
  - `backup.restore(path: Path, passphrase_file: Path | None) -> RestoreCounts(members, copies, loans)`
  - `applock.hold_app_lock(db_path: Path) -> IO` ve `applock.try_lock(db_path: Path) -> bool` (KL-4).
- **Davranış:**
  - Parola dosyasının içeriğinin sonundaki satır sonu atılır. Boş parola hatadır.
  - `restore_backup PATH [--passphrase-file PATH] --yes` şu adımları izler:
    1. `--yes` yoksa çıkış 2. PATH yoksa "Dosya bulunamadı: <yol>" ile çıkış 1 (KL-41).
    2. Uygulama kilidi alınamıyorsa "Uygulama çalışıyor; önce servisi durdurun" mesajıyla çıkış 1.
    3. `.libx` dosyası çözülür.
    4. Geçici dosyada `PRAGMA integrity_check = ok` ve `django_migrations` tablosunun varlığı doğrulanır.
    5. `-wal` ve `-shm` dosyaları silinir, dosya `os.replace` ile yerine konur.
    6. Sayımlar yazılır.
  - `backup_db` ve `export_backup`, `run_job` içinde çalışır (`BACKUP`, `EXPORT`).
- **Testler:** TC-186…TC-200, TC-299…TC-304 (21 TC; `docs/test-plan.md` §6)
- **Doğrulama:** `python -m pytest operations -q` → hepsi geçer. Elle: dev veritabanında `python manage.py backup_db`, ardından `export_backup` ve `restore_backup <libx> --yes` → çıkış 0 ve yazılan sayımlar yedekten önceki sayımlarla aynı.
- [ ] Tamamlandı

### Görev G15: Saklama süresi ve anonimleştirme

- **Gereksinimler:** FR-25, NFR-08; AC-25; ADR-0018, ADR-0045; küçük kararlar 4 ve 8 (faz 3); KL-34.
- **Dosyalar:** değiştir `operations/domain.py`, `operations/services.py`, `members/views.py`, `members/urls.py`; oluştur `operations/management/commands/anonymize_expired.py`, `members/templates/members/retention_pending.html`, testler.
- **Arayüzler:**
  - domain `add_years(d: date, years: int) -> date`: 29 Şubat, 28 Şubat'a düşer.
  - domain `is_expired(start: date, years: int, today: date) -> bool`: `add_years(start, years) < today` (küçük karar 4).
  - `anonymize_expired(today: date) -> AnonymizeCounts(members, loans, deferred)`. Her kayıt kendi işleminde işlenir:
    - **Borçlu üye:** `billing.services.member_balance(member) > 0` ise üye atlanır ve `deferred` artar (ADR-0045).
    - **Üye:** `full_name`, `phone`, `phone_digits` ve `email` alanları NULL, `search_key` boş, `has_email_consent` False olur. `consent_event` satırları silinir ve `anonymized_at` doldurulur.
    - **Ödünç:** `member` NULL olur ve `member_unlinked_at` doldurulur. Üyenin `archived_loan_count` sayacı 1 artar. Bağlı `ledger_entry.loan` alanları NULL olur.
  - Komut `anonymize_expired [--date …]`, `run_job(Job.ANONYMIZE, …)` içinde çalışır.
  - `deferred_members(today) -> list[DeferredRow]` ve `/uyeler/saklama/` listesi (KL-34).
- **Davranış:** Anonim üye ekranda "Anonimleştirilmiş üye" olarak görünür. Toplam ödünç sayısı, bağlı ödünçlerle `archived_loan_count` toplamıdır ve üye ayrıntısında gösterilir.
- **Testler:** TC-201…TC-207, TC-305…TC-309 (12 TC; `docs/test-plan.md` §6)
- **Doğrulama:** `python -m pytest operations -q` → hepsi geçer.
- [ ] Tamamlandı

### Görev G16: Zamanlayıcı ve telafi

- **Gereksinimler:** FR-18 (09:00), FR-25, FR-28, FR-37 (haftalık), NFR-03, NFR-05; ADR-0007, ADR-0012; küçük kararlar 13 ve 14 (faz 3), küçük karar 14 (faz 4); KL-5.
- **Dosyalar:** oluştur `operations/scheduler.py`, `operations/tests/test_scheduler.py`; değiştir `library_site/wsgi.py`.
- **Arayüzler:**
  - `SCHEDULE: list[ScheduledJob(job: Job, command: str, cron: dict)]`: BACKUP 02:00, ANONYMIZE 02:30, REMINDERS 09:00, EXPORT pazartesi 03:00 (Europe/Istanbul).
  - `jobs_due_for_catch_up(now: datetime, last_success: dict[Job, date | None]) -> list[Job]` (domain'de, saf):
    - Günlük görev için koşul: bugünün planlanan saati geçmiş ve `last_success < bugün`.
    - Haftalık görev için koşul: en son pazartesi 03:00 geçmiş ve `last_success` o pazartesiden eski.
    - Sıra: BACKUP, ANONYMIZE, EXPORT, REMINDERS.
  - `start_scheduler() -> BackgroundScheduler`. Görevler `call_command(command)` ile çalışır; telafi görevleri tek seferlik `date` tetikleyicisiyle hemen kuyruğa alınır.
- **Davranış:**
  - `wsgi.py` önce `hold_app_lock` çağırır (her zaman). Kilit alınamazsa `RuntimeError("Uygulama zaten çalışıyor: <kilit yolu>")` fırlatır ve süreç başlamaz (R-09). Ardından `LIBRARY_SCHEDULER_ENABLED == "1"` ise `start_scheduler()` çalışır (KL-5).
  - Testlerde ve yönetim komutlarında zamanlayıcı başlamaz, çünkü bunlar `wsgi.py`'yi yüklemez.
  - Görev istisnası loglanır ve zamanlayıcıyı durdurmaz.
- **Testler:** TC-208…TC-213, TC-310…TC-314 (11 TC; `docs/test-plan.md` §6)
- **Doğrulama:** `python -m pytest operations/tests/test_scheduler.py -q` → hepsi geçer. Elle: `LIBRARY_SCHEDULER_ENABLED=1` ile `waitress-serve` başlatılır → logda dört görevin sonraki çalışma zamanları ve gerekiyorsa telafi satırları görünür.
- [ ] Tamamlandı

### Görev G17: Tohum veri

- **Gereksinimler:** FR-29, NFR-02 (yük verisi); AC-29; ADR-0031, ADR-0033, ADR-0038; küçük kararlar 12 ve 13 (faz 4); KL-16, KL-27.
- **Dosyalar:** oluştur `scripts/fetch_demo_books.py`, `seed/books_openlibrary.json` (betik bir kez çalıştırılır, çıktısı depoya girer), `seed/first_names.txt`, `seed/last_names.txt`, `operations/seed.py`, `operations/management/commands/load_seed_data.py`, testler; değiştir `README.md` (Veri kaynakları bölümü).
- **Arayüzler:**
  - `scripts/fetch_demo_books.py --out seed/books_openlibrary.json --limit 300`
  - `filter_records(raw: Iterable[dict]) -> list[dict]`: ADR-0033'teki beş filtre aynı sırayla uygulanır. Ağ çağrısı içermediği için birim testiyle doğrulanır.
  - `operations.seed.load(profile: Literal["demo", "load"], seed: int, actor: StaffUser) -> SeedCounts`
  - Komut `load_seed_data --profile demo|load --actor <kullanıcı adı> [--seed 42]`. Varsayılan `demo` ve 42'dir. `--actor` eksikse çıkış 2; kullanıcı yoksa ya da pasifse "Personel bulunamadı ya da pasif: <ad>" ile çıkış 1 (ADR-0038). Üye ya da kitap tablosu boş değilse "Veritabanı boş değil" mesajıyla çıkış 1.
- **Davranış:**
  - Demo ve yük profillerinin ayrıntısı KL-16'dadır.
  - Tohum veri ORM ile doğrudan yazılır ve tutarlı durum üretir: açık ödüncün nüshası Ödünçtedir, kapalı ödüncün nüshası Raftadır.
  - Sentetik üye e-postaları `uye<no>@example.invalid` biçimindedir; gerçek bir alıcıya ulaşmaz.
  - Personel hesabı oluşturulmaz. Bütün `created_by`, `closed_by` ve `recorded_by` alanları `--actor` personelidir (ADR-0038).
- **Testler:** TC-214…TC-220, TC-315…TC-317 (10 TC; `docs/test-plan.md` §6)
- **Doğrulama:** `python -m pytest operations -q -k seed` → hepsi geçer. Boş dev veritabanında `createsuperuser` sonrası `python manage.py load_seed_data --profile demo --actor <ad>` → "kitap=300, nüsha=…, üye=200, açık ödünç=150 (gecikmiş 10)" ve çıkış 0. İkinci çalıştırmada çıkış 1.
- [ ] Tamamlandı

### Görev G18: Yük testi betiği

- **Gereksinimler:** NFR-01, NFR-02; ADR-0031; KL-17.
- **Dosyalar:** oluştur `scripts/loadtest.py`, `scripts/tests/test_loadtest.py` (yüzdelik hesabı ve karışım seçimi için birim testleri).
- **Arayüzler:**
  - `scripts/loadtest.py --base-url URL --user U --password-file F --db PATH --workers 5 --duration 120 [--seed 42]`
  - `percentile(values: list[float], p: float) -> float`: en yakın sıra yöntemi.
  - `pick_operation(rng) -> str`: ağırlıklar %40/20/20/10/10.
- **Davranış:**
  - KL-17'ye göre çalışır.
  - Rapor işlem türü başına `istek, p50, p95, hata` sütunlarını içerir.
  - Bütün türlerde p95 < 500 ms ve hata = 0 ise çıkış 0, değilse 1.
- **Testler:** TC-221…TC-223, TC-318 (4 TC; `docs/test-plan.md` §6)
- **Doğrulama:** `python -m pytest scripts -q` → hepsi geçer. Ölçümün kendisi faz 6'da yapılır.
- [ ] Tamamlandı

### Görev G19: Dağıtım dosyaları ve kullanıcı belgeleri

- **Gereksinimler:** FR-28 (geri yükleme adımı belgesi), NFR-04, NFR-08 (LAN), ADR-0005, ADR-0006, ADR-0010, ADR-0029, ADR-0032 ("adı sor" adımı), ADR-0038 (demo sırası), ADR-0040 (kapalı tarih notu), ADR-0047 (rıza notu); KL-21, KL-27, KL-29.
- **Dosyalar:** oluştur `deploy/Caddyfile`, `deploy/winsw/library-app.xml`, `deploy/winsw/library-caddy.xml`, `deploy/systemd/library-app.service`, `deploy/systemd/library-caddy.service`, `deploy/library.env.example`, `docs/kurulum.md`, `docs/kullanim-kilavuzu.md`; değiştir `README.md`.
- **Davranış:**
  - **Caddyfile:**
    - Site adresi `{$LIBRARY_HOST}` ve `tls internal` ile tanımlanır.
    - `handle_path /static/*` bloğu `root * {$LIBRARY_STATIC_ROOT}` ve `file_server` kullanır.
    - Diğer yollar `reverse_proxy 127.0.0.1:8000` ile waitress'e gider.
    - `bind`, LAN arayüzünün adresidir (`{$LIBRARY_BIND}`).
  - **Servisler:** Uygulama servisinin komutu KL-5'tedir. Çökmede yeniden başlatma açıktır. Ortam değişkenleri architecture §6.4'tedir.
  - **`docs/kurulum.md`** architecture §8'deki 7 adımı içerir. Ayrıca şunları içerir:
    - Migration öncesinde elle `backup_db` çalıştırılması.
    - Yedekten geri yükleme yordamı: servisi durdur, `restore_backup`, servisi başlat ve sayımları kontrol et. AC-28'de bu yordamın süresi ölçülür.
    - USB rotasyonu, parolanın çevrimdışı saklanması, CA kök sertifikasının yüklenmesi, NTP ayarı ve SQLite dosyasının yerel diskte tutulması.
  - **`docs/kullanim-kilavuzu.md`**, masa işlerini adım adım anlatır. Ödünçte "üyeye adını sor" adımı da buradadır. Ayrıca şu notları içerir: geçmiş kapalı tarihler silinmez (ADR-0040); geçmiş tarihli rıza olayı geçerli durumu değiştirmez (ADR-0047).
- **Testler:** TC-225…TC-234, TC-319 (11 TC; `docs/test-plan.md` §6)
- **Doğrulama:** Faz 6'da test ortamına kurulum yapılır ve şunlar kontrol edilir:
  - `curl -k https://<host>/static/css/app.css` → 200.
  - `/admin/` → 404.
  - LAN dışından erişim olmamalı.
  - AC-28 geri yükleme süresi < 1 saat olmalı.
- [ ] Tamamlandı

## 5. Testler

Test planı: [docs/test-plan.md](../test-plan.md). 319 TC (TC-01…TC-319); seviyeler, teknikler, kapsam hedefleri, ortam ve giriş-çıkış ölçütleri orada. Her görevin TC listesi görevin **Testler** satırındadır. Elle TC'ler (TC-223, TC-225…TC-234, TC-319) faz 6'da yapılır.

## 6. Riskler

Riskler [docs/risk-register.md](../risk-register.md) dosyasına taşındı (2026-10-31). R-01 ve R-06 kapandı, R-07…R-14 eklendi. En önemli açık riskler: R-04 (bina olayı), R-10 (saat dilimi verisi), R-13 (çalışan uygulamaya geri yükleme), R-02 ve R-11 (e-posta). R-15 ve R-16 bulut oturumu kararıyla eklendi (ADR-0048).

## 7. İzlenebilirlik

Kapsam içindeki 35 FR ve 13 NFR'nin her biri bir tasarım öğesine, göreve ve teste bağlı. Test sütunu `docs/test-plan.md` §6'nın "Gereksinim" sütunundan üretildi (AC'ler FR'lerine eşlendi). Her görev en az bir gereksinime hizmet ediyor; TC-02 ve TC-236 architecture §6.4'e bağlı.

| Gereksinim | Tasarım öğesi | Görev | Test |
|---|---|---|---|
| FR-01 | `members`: `create_member`, `update_member`, `search_members`; `member` tablosu | G06 | TC-35, TC-44…TC-52, TC-261 |
| FR-02 | `circulation.services.deactivate_member`, `members.services.set_inactive`, `Blocker.MEMBER_INACTIVE` | G06, G10, G11 | TC-53…TC-56, TC-115, TC-126, TC-286 |
| FR-03 | `consent_event`, `set_consent`, `update_member` (ADR-0022, ADR-0047); S6 rıza koşulu | G06, G13 | TC-57…TC-59, TC-177, TC-254…TC-258, TC-319 |
| FR-04 | `catalog.domain`: `parse_isbn`, `normalize_tr`; `create_book`, `search_books`; `book` tablosu | G05, G07 | TC-35, TC-37…TC-43, TC-60…TC-63, TC-66…TC-68, TC-253, TC-264 |
| FR-05 | `copy` tablosu, `add_copies`, `COPY_TRANSITIONS`, `check_transition` | G07, G10, G12 | TC-64…TC-65, TC-71, TC-163…TC-169, TC-262…TC-263 |
| FR-06 | `pdf.sheets.render_sheet`, `LABEL_LAYOUT`, `label_pdf`, `copies_for_labels` (ADR-0036) | G08 | TC-69…TC-72, TC-228, TC-265…TC-267, TC-269 |
| FR-07 | `circulation.domain.due_date`, `closed_day_predicate`, `check_out` | G03, G10, G11 | TC-104…TC-105, TC-107…TC-109, TC-124, TC-133, TC-140 |
| FR-08 | `checkout_blockers`, `check_out`, `loan` kısmi benzersiz indeksi | G10, G11 | TC-114, TC-116…TC-119, TC-124…TC-127, TC-145…TC-146, TC-149, TC-280, TC-284 |
| FR-09 | `check_in`, iade ekranı | G11 | TC-111, TC-134…TC-135, TC-138, TC-147, TC-283 |
| FR-10 | `renew_blockers`, `renewed_due_date`, `renew` | G10, G11 | TC-120…TC-123, TC-139…TC-144, TC-148, TC-280, TC-288 |
| FR-11 | Ödünç ve iade ekranları, `scan.js`, `classify_member_input` (ADR-0046) | G10, G11, G19 | TC-128…TC-130, TC-227, TC-279, TC-281…TC-282, TC-319 |
| FR-12 | `late_days` (ADR-0040), `fine`, `loan` oran kopyası (ADR-0023) | G10, G11, G12 | TC-13, TC-110…TC-113, TC-132, TC-134, TC-136…TC-137, TC-152, TC-246, TC-276…TC-278, TC-283, TC-319 |
| FR-13 | `allocate_fifo`, `record_payment`, `allocation` tablosu (ADR-0017) | G09 | TC-78…TC-85, TC-100, TC-103, TC-290 |
| FR-14 | `waive` (ADR-0021) | G09 | TC-86…TC-90 |
| FR-15 | `mark_lost`, `mark_damaged`, `post_charge` | G12 | TC-150…TC-152, TC-162, TC-289…TC-290, TC-293 |
| FR-16 | `mark_found`, `repair`, `withdraw`, `cancel_unpaid`, `refund`, `cancel_fee_manual`, `loan.copy_found_on` (ADR-0037, ADR-0041) | G09, G12 | TC-92…TC-97, TC-153…TC-158, TC-162, TC-168…TC-169, TC-270…TC-275, TC-291…TC-292 |
| FR-17 | `balance`, `member_balance` (S3), `statement`, döküm ekranı | G09 | TC-76…TC-77, TC-98…TC-99, TC-101 |
| FR-18 | `due_reminder_kind`, `send_due_reminders`, `reminder_log` (ADR-0039), `send_reminders` | G13, G16 | TC-173…TC-176, TC-178, TC-180…TC-182, TC-185, TC-208, TC-232, TC-294…TC-296 |
| FR-19 | `send_manual_reminders`, `/gecikenler/hatirlat/` | G13 | TC-183…TC-184, TC-297…TC-298 |
| FR-20 | `overdue_loans` (S5), `/gecikenler/` | G11, G13 | TC-171…TC-172, TC-287, TC-298 |
| FR-21 | `accounts.services`: `create_staff`, `set_role`, `deactivate_staff`, `reset_password`, `unlock_staff` | G02, G04 | TC-12, TC-27…TC-29, TC-237, TC-252 |
| FR-22 | `require_role`, `staff_view`, `tests/test_authorization.py` | G02, G03, G04 | TC-01, TC-11, TC-21, TC-31, TC-275, TC-308 |
| FR-23 | `LibrarySettings`, `update_settings`, ayar ekranı | G03, G08, G11 | TC-18…TC-20, TC-73, TC-131 |
| FR-24 | `WeeklyClosedDay`, `ClosedDate`, `validate_weekly_closed` (ADR-0028) | G03, G10 | TC-22…TC-24, TC-106, TC-246 |
| FR-25 | `anonymize_expired`, `add_years`, `deferred_members` (ADR-0018, ADR-0045) | G15, G16 | TC-201…TC-208, TC-305…TC-309 |
| FR-26 | `audit.record_audit`, `AuditEvent`, `/denetim/` | G03, G04, G06, G09, G12 | TC-18, TC-22, TC-26…TC-27, TC-91, TC-93, TC-157…TC-158, TC-170, TC-247, TC-259, TC-273 |
| FR-27 | Django `LoginView`, django-axes, oturum ayarları (ADR-0009) | G02 | TC-04…TC-10, TC-12, TC-30, TC-237 |
| FR-28 | `backup_db`, `restore_backup`, `applock`; kurulum belgesi | G14, G16, G19 | TC-186…TC-191, TC-199…TC-200, TC-208, TC-225, TC-301…TC-302 |
| FR-29 | `fetch_demo_books`, `filter_records`, `operations.seed`, `load_seed_data` (ADR-0033, ADR-0038) | G17 | TC-214…TC-219, TC-234, TC-315…TC-316 |
| FR-37 | `libx`, `export_backup`, `export_age_warning` (ADR-0006, ADR-0011) | G03, G14, G16 | TC-25, TC-192…TC-198, TC-208, TC-226, TC-244…TC-245, TC-299…TC-300, TC-303…TC-304, TC-310 |
| FR-38 | `CARD_LAYOUT`, `member_card_pdf`, `members_for_cards` (ADR-0032, ADR-0036) | G08 | TC-69, TC-74…TC-75, TC-228, TC-266, TC-268…TC-269 |
| FR-39 | `mark_shelf_copy`, `withdraw` (ADR-0026) | G12 | TC-159…TC-161, TC-293 |
| FR-40 | `reactivate_member` (ADR-0042) | G06, G11 | TC-259…TC-260, TC-285 |
| FR-41 | `change_own_password`, `ForcePasswordChangeMiddleware`, `must_change_password` (ADR-0043) | G02, G04 | TC-248…TC-251 |
| FR-42 | `backup_warning`, `jobs.last_finished`, `last_success_at` (ADR-0044) | G03 | TC-241…TC-243, TC-245 |
| NFR-01 | data-design §4 indeksleri, `scripts/loadtest.py` (ADR-0031) | G18 | TC-221…TC-223, TC-318 |
| NFR-02 | `load_seed_data --profile load` | G17, G18 | TC-220, TC-223, TC-317 |
| NFR-03 | BACKUP 02:00, `backup_db`, telafi | G14, G16, G19 | TC-190, TC-233 |
| NFR-04 | `restore_backup`, `docs/kurulum.md` | G14, G19 | TC-225 |
| NFR-05 | `jobs_due_for_catch_up`, `run_job`, `reminder_log` tekrar engeli | G03, G13, G16 | TC-178…TC-179, TC-209…TC-213, TC-233, TC-310…TC-314 |
| NFR-06 | `Argon2PasswordHasher`, Caddy `tls internal` (ADR-0005) | G01, G19 | TC-03, TC-230 |
| NFR-07 | `require_role`, `tests/test_authorization.py` | G04 | TC-11, TC-31…TC-33 |
| NFR-08 | `member` alanları, anonimleştirme, Caddy LAN bağlaması | G06, G15, G19 | TC-52, TC-206, TC-229…TC-230 |
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
  - django-axes `axes.W006` uyarısı ("AXES_LOCKOUT_PARAMETERS 'ip_address' içermiyor") gerekçe yorumuyla `base.py`'de `SILENCED_SYSTEM_CHECKS` listesine alındı; `prod.py` bu listeyi genişletir. Gerekçe ADR-0009'daki kullanıcı adına göre kilit: Caddy arkasında bütün istekler 127.0.0.1'den gelir, IP'ye göre kilit bütün personeli birden kilitler. G01'deki `check --deploy` çıktısı bu yüzden "(3 silenced)" oldu.
  - Kilitli hesabın 5. hatalı denemesi de 429 alır (axes kilidi bu denemede koyar); TC-07 6. denemeyi doğrular.
