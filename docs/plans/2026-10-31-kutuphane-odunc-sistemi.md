# Görev planı: Kütüphane ödünç alma sistemi

- **Tarih:** 2026-10-31
- **İz:** Tam
- **Durum:** Faz 1, 2 ve 3 tamamlandı (2026-10-31); sıradaki faz 4 (plan ve onay kapısı)

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
| docs/srs.md | Faz 1'de oluşturuldu, onaylandı (2026-10-31); faz 2 ve faz 3 değişiklikleri onayla işlendi |
| docs/architecture.md | Faz 3'te oluşturuldu (2026-10-31) |
| docs/data-design.md | Faz 3'te oluşturuldu (2026-10-31) |
| docs/decisions/0001…0025 | Faz 3'te yazıldı (2026-10-31) |
| docs/test-plan.md | Faz 4'te oluşturulacak |
| docs/risk-register.md | Faz 1–4'te oluşturulacak |

## 3. Kararlar

Faz 0'da verilen süreç kararları: Tam iz, yukarıdaki artefakt seti, TDD. Faz 3 kararları aşağıda ve ADR-0001…0025'te.

Faz 1 kapsam kararları SRS'te kaynaklarıyla birlikte duruyor (tek üye tipi, yönetici ve görevli rolleri, rezervasyon yok, yerel sunucu, ayarlanabilir kurallar, KVKK). Stack ve servis seçimleri faz 3'te ADR olacak.

**Küçük kararlar (onaylandı 2026-10-31):**

1. Varsayılan ayarlar: günlük ceza 5,00 TL; ödünç başına ceza üst sınırı 150,00 TL; borç eşiği 50,00 TL (eşik dahil engeller); saklama süresi 2 yıl.
2. Gecikme günü = iade tarihi − son tarih (takvim günü); son tarihte iade 0 gün.
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
- (c) Ortam değişkeni adları, `.libx` scrypt parametreleri ve çıkış kodları (architecture §6): faz 4 karar listesinde.
- (d) En az bir açık hafta günü kuralı: faz 4'te sorulacak.

**Faz 4'e devreden açık noktalar:**

- Raftaki nüshayı hasarlı, kayıp ya da kayıttan düşmüş işaretleme SRS'te yok.
- FR-26 listesine "iade" eklenmeli (ADR-0020).
- Varsayılan ödünç süresi ve ödünç limiti belirlenmeli (AC-23'teki örnek 14 gün, AC-08'deki örnek 3).
- Statik dosyaların sunumu belirlenmeli (öneri: Caddy `file_server`).
- Kart ölçüsü, yerleşimi ve kartta ad bulunup bulunmayacağı belirlenmeli (ADR-0025).
- Etiket ölçüleri ve barkod okunabilirlik test aracı belirlenmeli (ADR-0014).
- Demo veri boyutu ve temizlik ölçütü belirlenmeli; 500 kayıtlık alt sınır teyit edilmeli (R-06).
- NFR-01 yük setinin nasıl üretileceği belirlenmeli.
- waitress iş parçacığı sayısı belirlenmeli.

## 4. Görevler

Faz 4'te yazılacak.

## 5. Testler

Faz 4'te yazılacak.

## 6. Riskler

| ID | Risk | Olasılık | Etki | Tetik | Azaltma |
|---|---|---|---|---|---|
| R-01 | ISBN API'leri Türkçe kitapları yeterince kapsamıyor | Gerçekleşti | Düşük | Faz 2 ölçümünde düşük isabet (%52) | Kapandı (2026-10-31): FR-30 Won't oldu, kitap girişi elle yapılıyor |
| R-06 | Open Library'den gelen demo verisinde Türkçe karakter kaybı ve bozuk yayınevi alanı var; lisans belirsizliği orta güvende | Yüksek | Düşük | Ölçümde kayıtların ~1/3'ünde karakter kaybı | Seçim ya da temizlik adımı (faz 3–4'te karar); yalnız bibliyografik alanlar, kaynak notu, sentetik yedek |
| R-02 | Hatırlatma e-postaları spam'e düşüyor ya da zamanlanmış görev atlanıyor | Orta | Orta | Uygulama sürekli çalışmıyor; SPF/DKIM yok | Kurum SMTP hesabı (ADR-0004); açılışta telafi ve pencereli hatırlatma (ADR-0007); elle hatırlatma ve geciken listesi |
| R-03 | Kütüphanede barkod okuyucu ya da etiket yazıcısı yok | Düşük | Düşük | Kurulum sırasında donanım eksik | Elle kod girişi ve arama |
| R-04 | Sunucu ve harici yedek diski aynı binada; yangın ya da hırsızlıkta ikisi birden gider | Düşük | Yüksek | Bina olayı | Haftalık şifreli dışa aktarma ve USB rotasyonu, 7 günü geçince uyarı (ADR-0006, ADR-0011, FR-37); bina olayında RPO ≤ 7 gün |
| R-05 | Varsayılan saklama süresi kurumun KVKK politikasıyla çelişiyor | Orta | Orta | Kurum teyidi farklı süre veriyor | Süre ayar olduğu için yalnız değer değişir (FR-23) |

## 7. İzlenebilirlik

Faz 4'te doldurulacak.

## 8. Tutarlılık kontrolü

Faz 4'te yapılacak.

## 9. Önerilen commit noktaları

- Kök commit (`main`): `chore: set up project docs skeleton`. Onaylandı 2026-10-31; AGENTS.md'deki dal kuralına tek istisna.
- `feature/requirements`: `docs: add approved SRS and phase 1 plan updates`.
- `feature/requirements`: `docs: add phase 2 research reports` (onaylandı ve commit'lendi 2026-10-31).
- `feature/requirements`: `docs: add phase 3 ADRs, architecture and data design` (onaylandı ve commit'lendi 2026-10-31). SRS, plan ve STATUS'taki faz 2 ve faz 3 değişiklikleri de bu commit'te.

## 10. Onay

Henüz yok.

## 11. Sapmalar

- **2026-10-31, commit bölümü:** Faz 2 commit'i yalnız iki araştırma raporunu içeriyor; mesajındaki "and SRS updates" kısmı çıkarıldı. Sebebi, SRS, plan ve STATUS'taki faz 2 ve faz 3 değişikliklerinin aynı satırlarda iç içe olması. Bunları ayırmak, hiç var olmamış bir ara sürümü geçmişe yazmak demekti. Bu yüzden üç dosya faz 3 commit'ine alındı.
