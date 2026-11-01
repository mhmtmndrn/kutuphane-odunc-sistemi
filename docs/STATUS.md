# Durum (devir notu)

- **Güncelleme:** 2026-11-01 (faz 5, PR #5 birleşti; `feature/seed-load` açıldı)
- **Aşama:** eng-process **faz 5**. `feature/foundation` (G01–G04, PR #1), `feature/catalog-members` (G05–G08, PR #2), `feature/circulation` (G10 → G09 → G11 → G12, PR #3) ve `feature/notifications` (G13, PR #4) ve `feature/operations` (G14 → G15 → G16, PR #5) birleşti; `main` = `8256786` (PR #5'in merge commit'i). Grup `feature/seed-load` (**G17 → G18**: tohum veri ve yük testi betiği) bu dalda sürüyor; açılış kararları ADR-0056…0058 ve plan §11'de.
- **`feature/operations` commit'leri** (her biri push edildi):
  - **`992d59c` (`docs:`):** STATUS'taki bayat satırlar, ADR-0053…0055, plan §11 "G14–G16 — açılıştan önce verilen kararlar", G14–G16 ve G19 bölümlerine dosya ve arayüz ekleri, architecture §3'e `operations → notifications` oku, test planına TC-320…TC-339 ve §7 izlenebilirlik.
  - **`08866de` (`feat:` G14):** `operations` app'i; `backup_db`, `export_backup`, `restore_backup`; `.libx` (scrypt + AES-256-GCM, başlık AAD); `.tmp` + `os.replace`; uygulama kilidi (`fcntl`/`msvcrt`); geri yüklemede `LIBX` magic baytı, doğrulama, koruma kopyası (ADR-0054), migration yok.
  - **`96e0161` (`feat:` G15):** `anonymize_expired` (kayıt başına işlem; bağ koparma, arşiv sayacı, defter bağı ve `reminder_log.error` temizliği, ADR-0055; borçlu üye ertelenir, ADR-0045; ilk istisnada durur), `/uyeler/saklama/` ve yöneticiye "Saklama" bağlantısı, `Member.display_name`, üye ayrıntısında "Toplam ödünç"; TC-32 artık yönetici yollarının plan listesine tam eşitliğini ister.
  - **`832344f` (`feat:` G16):** `operations/scheduler.py` (dört cron görevi, tek işçili yürütücü, açılışta ve saatlik telafi, ADR-0053; komut sarmalayıcı), `wsgi.py`'de uygulama kilidi ve `LIBRARY_SCHEDULER_ENABLED`, `base.py`'de stderr `LOGGING`.
  - Son `docs:` commit'i: bu devir notu, plan §11 ve test planı.
- **Sonuç (bulut, Linux, Python 3.11.18):** `python -m pytest operations -q` → 113 passed; `python -m pytest -q` → 972 passed (`slow` dahil; önceki 852); `-m slow` → 4 passed; `makemigrations --check --dry-run` → "No changes detected"; dal kapsamı: `*/domain.py` %100 (`--fail-under=90` çıkış 0), `accounts/permissions.py` ve `accounts/middleware.py` %100 (`--fail-under=100` çıkış 0), `operations` toplam %99 (test planı §4 hedefi ≥ %80; `scheduler.py`, `domain.py`, `libx.py`, `applock.py`, `cli.py` ve komutlar %100, `backup.py` %99, `services.py` %95), proje toplamı %99.
- **Elle doğrulama (bulut):** G14: dev veritabanında `backup_db` → `export_backup` → `restore_backup <libx> --yes`, sayımlar önce ve sonra 5/7/3, koruma kopyası `var/library.sqlite3.pre-restore-20261101-142040`. G15: `anonymize_expired` → "anonimleştirilen üye=1, bağı koparılan ödünç=2, ertelenen üye=2"; `/uyeler/saklama/`, anonim üyenin ayrıntısı ve aramadaki anonim satır Playwright ile göz kontrolünden geçti. G16: `LIBRARY_SCHEDULER_ENABLED=1 waitress-serve` → logda beş tetikleyicinin sonraki çalışma zamanı, telafi satırları ve görev sonuçları; aynı veritabanında ikinci süreç `AppLockError` ile durdu, uygulama açıkken `restore_backup` reddedildi.
- **Test planı:** 308 TC "Geçti" (244 + G14'ün 31'i + G15'in 17'si + G16'nın 16'sı).
- **Yerel Windows (R-15, Python 3.11.9, 2026-11-01):** TC-302 ve TC-313 (`msvcrt`) → 3 passed; `python -m pytest -q` → 972 passed; `-m slow` → 4 passed; `makemigrations --check --dry-run` → "No changes detected"; dal kapsamı: `*/domain.py` %100 (`--fail-under=90` çıkış 0), `accounts/permissions.py` ve `accounts/middleware.py` %100 (`--fail-under=100` çıkış 0), `operations` toplam %98 (`--fail-under=80` çıkış 0; buluttaki %99'dan fark `applock.py` 29–35, Windows'ta koşmayan `fcntl` dalı), proje toplamı %99. Migrate edilmiş boş geçici veritabanında (scratchpad, `LIBRARY_DB_PATH`) `backup_db` → `export_backup` → `restore_backup <libx> --yes` çıkış 0, koruma kopyası yeniden adlandırmayla oluştu (ADR-0054); `.libx`/SQLite olmayan dosyada "Geçerli bir veritabanı yedeği değil: …", çıkış 1. `python -m waitress` + `LIBRARY_SCHEDULER_ENABLED=1` (prod ayarları; tüm `LIBRARY_*` env'leri gerekir): beş tetikleyici, dört telafi satırı ve görev sonuçları birer kez loglandı; ikinci süreç `AppLockError` ile çıkış 1.
- **Plan:** [docs/plans/2026-10-31-kutuphane-odunc-sistemi.md](plans/2026-10-31-kutuphane-odunc-sistemi.md). G14, G15 ve G16 kutuları kanıtıyla işaretli; açılış kararları, uygulama ayrıntıları ve onaya sunulan metinler §11'de ("G14–G16 — açılıştan önce verilen kararlar", "G14–G16 — uygulama ayrıntıları", "G14–G16 uygulayıcının seçtiği kullanıcıya görünen metinler").
- **G13 (PR #4, birleşti):** 852 test, yerel Windows doğrulaması geçti; ayrıntı plan §11 ve git geçmişinde.
- **Repo:** https://github.com/mhmtmndrn/kutuphane-odunc-sistemi (özel). Dallar: `main` (`8256786`), `feature/foundation`, `feature/catalog-members`, `feature/circulation`, `feature/notifications` ve `feature/operations` (kapandı), `feature/seed-load` (açık).
- **Bulut kredisi (ADR-0048):** 100 $, yaklaşık 2026-11-05'te sıfırlanıyor (R-16).
- **Bulut oturumu:** Her grup için kullanıcı yeni bir bulut oturumu açar, Claude açılış istemini hazırlar (KL-38). Oturum kritik soruyu oturumun içinde sorar; planın vermediği metinleri seçip §11'de listeler ve PR'da onaya sunar (plan §11, 2026-11-01 kararları).
  - **Tarayıcı (önerilen):** claude.ai/code; repo `mhmtmndrn/kutuphane-odunc-sistemi`, ortam **Default** (Trusted ağ; pip için PyPI gerekir).
  - **Terminal:** depo klasöründe `claude --cloud "<istem>"`; yerel commit'ler önce push edilmeli.
  - Kaynak: https://code.claude.com/docs/en/claude-code-on-the-web.

## Bu oturumda sorulan ve cevaplanan

- **G17–G18 açılışından önce (2026-11-01, kullanıcı onayı):** Üç kritik karar: [ADR-0056](decisions/0056-open-library-fetch-network-blocked.md) (Open Library'ye erişilemezse JSON olmadan devam; gerçek dosya yerel doğrulamada), [ADR-0057](decisions/0057-seed-phone-numbers.md) (tohum telefonları `000 ddd dd dd`) ve [ADR-0058](decisions/0058-loadtest-seed-only-guard.md) (yük betiği `@example.invalid` dışı e-postalı üye görürse istek atmadan çıkış 1). On iki küçük karar (README, bugüne göre tarihler, demo ve yük profilleri, domain fonksiyonları ve tek işlem, sentetik kitap, audit yok ve Allocation, çıktı, rıza, betiğin yeniden seçimi, `scripts/` paketi, duman testi) plan §11'de. Yeni davranışların testleri TC-340…TC-356. Sıradaki ADR numarası 0059.
- **G14–G16 açılışından önce (2026-11-01, kullanıcı onayı):** Üç kritik karar: [ADR-0053](decisions/0053-hourly-catch-up.md) (açılışa ek saatlik telafi; `misfire_grace_time=3600`, `coalesce=True`), [ADR-0054](decisions/0054-restore-keeps-pre-restore-copy.md) (geri yükleme mevcut veritabanını `<db>.pre-restore-YYYYMMDD-HHMMSS` olarak bırakır) ve [ADR-0055](decisions/0055-reminder-log-error-cleared-on-unlink.md) (bağ koparılırken `reminder_log.error` NULL). Dokuz küçük karar (komut argümanları ve geçersiz tarih, magic bayt, migration yok, `.tmp` + `os.replace`, tek işçili zamanlayıcı, komut sarmalayıcı ve stderr `LOGGING`, "Saklama" bağlantısı, `Member.display_name`, ilk istisnada durma) plan §11'de.
- **G13 açılışından önce (2026-11-01):** [ADR-0052](decisions/0052-smtp-timeout.md) ve yedi küçük karar; plan §11.

## G14–G16 sapmaları ve dikkat edilecekler (ayrıntı plan §11)

- **Yedeğin kaynağı:** SQLite yedek API'si, kaynak bağlantı bir işlemin içindeyse sonsuza dek bekler. `backup_db` bu yüzden Django bağlantısını değil, veritabanı dosyasına açılan ayrı bir bağlantıyı (`mode=rw`) kullanır. Yedek dosyası `journal_mode=DELETE`'tir (yanında `-wal` yok).
- **Klasörler oluşturulmaz:** Yedek ya da dışa aktarma klasörü yoksa komut "… klasörü bulunamadı" ile çıkış 1 verir (takılı olmayan disk sistem diskine yazılmasın diye). Kurulumda klasörler elle açılır (G19).
- **Geri yükleme:** Kilit geri yükleme boyunca tutulur. `LIBX` ile başlamayan her dosya SQLite olarak denenir. Koruma kopyası `<db>.pre-restore-YYYYMMDD-HHMMSS` veritabanı klasöründe kalır ve elle silinir (KVKK notu G19'da kurulum belgesine).
- **`runserver` de kilidi tutar:** `WSGI_APPLICATION` üzerinden `wsgi.py`'yi yüklediği için geliştirme sunucusu açıkken `restore_backup` reddedilir ve aynı veritabanında ikinci bir sunucu açılmaz. Zamanlayıcı yalnız `LIBRARY_SCHEDULER_ENABLED=1` ile başlar.
- **Log:** `operations` ve `django` logger'ları stderr'e yazar ve `propagate: False`'tur; waitress kök logger'a kendi handler'ını eklediği için aksi hâlde her satır iki kez çıkar. Testlerde `caplog` handler'ı `operations` logger'ına doğrudan eklenir (`operations/tests/test_scheduler.py`).
- **Zamanlayıcı:** Tek işçi; telafi işleri `catch-up-<sıra>-<görev>` kimlikleriyle kuyruğa girer (APScheduler aynı anda vadesi gelenleri kimlik sırasıyla çalıştırır). Açılıştaki telafi hatası uygulamayı durdurmaz, loglanır.
- **Anonimleştirme:** Ödüncün saklama başlangıcı `closed_on`'dur (iade, kayıp, hasar). Bağ koparma adımları queryset `update` iledir (defter yalnız eklenir). `Member.display_name` adın tek kaynağıdır; nüsha ayrıntısındaki ödünç geçmişi yalnız üye no gösterdiği için değişmedi.
- **Yetki testi:** 19 yönetici yolunun hepsi var; TC-32 artık tam eşitlik ister. Yeni bir yönetici yolu eklenirse `tests/test_authorization.py`'deki liste de güncellenmelidir.
- **Dosya listesi dışında değişenler:** Yok; açılışta G14–G16 listelerine eklenenler (`base.py`, `members/models.py`, şablonlar, `circulation/services.py`, `notifications/services.py`, `templates/base.html`, `tests/test_authorization.py`, `operations/domain.py`) dışında dosya değişmedi. `docs/architecture.md` §3'e `operations → notifications` oku eklendi (ADR-0055).

## G13 için hâlâ geçerli notlar

- `send_reminders` FAILED varken `CommandError("<n> hatırlatma gönderilemedi", returncode=1)` verir; G16 zamanlayıcısı bunu yakalayıp loglar, `job_run` SUCCESS'tir.
- E-posta şablonları `autoescape off` düz metindir; gönderen `DEFAULT_FROM_EMAIL` (üretimde `LIBRARY_EMAIL_FROM`). Komut testleri `notifications/tests/test_commands.py`'dedir.

## Önceki grup (G09–G12) için hâlâ geçerli notlar

- Eşzamanlılık testleri (TC-103, TC-145…TC-148) `tests/support/concurrency.py`'deki `file_db` fixture'ıyla geçici dosya veritabanında, `run_parallel` ile iki iş parçacığında koşar.
- `cancel_unpaid` denetim kaydı yazmaz; `CANCELLATION` yalnız elle iptalde. Ödünç, iade, uzatma, pasifleştirme ve elle hatırlatma denetim kaydı yazmaz.
- `catalog.urls` `circulation.urls`'ten önce kalmalı (`/nushalar/etiket/`); bunu bir test sabitler.

## Sıradaki adım

1. **PR #5 birleşti (2026-11-01):** merge commit `8256786`; yerel Windows koşusu geçti, G14–G16 metinleri değişmeden onaylandı.
2. **Bu grup:** `feature/seed-load` (**G17 → G18**). Bulut oturumu G17 ve G18'i uygular, PR'ı açar ama birleştirmez.
3. **Yerel doğrulamada yapılacak (ADR-0056):** Bulutta Open Library'ye erişilemezse `seed/books_openlibrary.json` dala girmez. Kullanıcı yerelde `python scripts/fetch_demo_books.py --out seed/books_openlibrary.json --limit 300` çalıştırır, `_meta` alanını ve kayıt sayısını kontrol eder ve dosyayı `feature/seed-load` dalına commit'ler. PR bu commit gelmeden birleştirilmez.
   - Genel sıra: G01 → G16 (tamam), G17…G18 (bu dal), G19.

## Açık sorular ve riskler

- **SRS açık soru 5:** Sunucu donanımı ve işletim sistemi belli değil; Windows ve Linux birlikte destekleniyor (ADR-0010).
- **SRS açık soru 6, R-05:** 2 yıllık saklama ve borçlu üyede anonimleştirmenin ertelenmesi (ADR-0045) kurumun KVKK politikasıyla teyit edilmeli.
- **SRS açık soru 8:** KYGM Z39.50 erişimi doğrulanmadı.
- **Kurulum ön koşulu:** Kurumdan SMTP gönderen hesabı alınmalı (ADR-0004, R-11).
- **Etiket kağıdı ve okuyucu:** Basılı etiket ve kartın gerçek okuyucuyla taranması faz 6'da (TC-228); okuyucuyla ödünç masası akışı (`scan.js`, NFR-11) da faz 6'da gerçek donanımla denenir (TC-227).
- **Riskler:** [docs/risk-register.md](risk-register.md). En önemlileri R-04, R-10 ve R-13; bulut için R-15 ve R-16.

## Nerede kaldık

- **SRS:** [docs/srs.md](srs.md), onaylı. 35 FR (24 Must, 11 Should), 7 Won't, 13 NFR, 35 AC.
- **Tasarım:** [architecture.md](architecture.md) ve [data-design.md](data-design.md).
- **ADR'ler:** [0001–0058](decisions/), hepsi kabul edildi; özet plan §3. Sıradaki numara 0059.
- **Plan:** §3 kararlar ve KL-1…KL-46; §4 görevler G01–G19; §7 izlenebilirlik; §8 tutarlılık; §11 sapmalar ve metinler.
- **Test planı:** [docs/test-plan.md](test-plan.md): 356 TC (TC-320…TC-339 G14–G16, TC-340…TC-356 G17–G18 açılışında eklendi); 308'i "Geçti". Elle TC'ler: TC-223, TC-225…TC-234, TC-319 (faz 6).
- **Araştırma:** [ISBN meta veri](research/2026-10-31-isbn-meta-veri-apileri.md), [demo veri seti](research/2026-10-31-demo-kitap-veri-seti.md).

## Geçmiş (özet)

- **2026-11-01, `feature/operations` bulut oturumu:** İlk commit `docs:` (bayat STATUS satırları, ADR-0053…0055, açılış kararları, TC-320…TC-339), ardından G14, G15, G16 görev başına TDD (testler önce kırmızı) ve birer `feat:` commit'i, sonra handoff `docs:`; her biri push edildi. Ekranlar Playwright ile, zamanlayıcı `waitress-serve` ile elle doğrulandı. Oturum içinde yeni kritik soru çıkmadı. PR açıldı, birleştirilmedi.
- **2026-11-01, PR #4 (G13):** Yerel Windows doğrulaması (852 passed), metinler onaylandı, merge commit `c2e5bc8`. `feature/operations` açıldı.
- **2026-11-01, `feature/notifications` bulut oturumu:** İlk commit `docs:` (bayat STATUS satırları, ADR-0052, G13 açılış kararları), ardından G13 TDD ile (20 TC önce kırmızı) tek `feat:` commit'i, sonra `docs:` (test planı, plan kutusu, §11, STATUS); her biri push edildi. Ekran Playwright ile göz kontrolünden geçti. PR açıldı, birleştirilmedi.
- **2026-11-01, PR #3 (G09–G12):** Yerel Windows doğrulaması (784 passed), metinler onaylandı, merge commit `d0c4555`.
- **2026-11-01, `feature/circulation` bulut oturumu:** İlk commit `docs:` (STATUS ve pasifleştirme koruması kararı), ardından G10, G09, G11, G12 görev başına TDD ve `feat:` commit'i, her biri push edildi. TC-91 için bir soru soruldu (denetim listesinde TL). Ekranlar geliştirme sunucusunda Playwright ile açılıp göz kontrolünden geçti. PR açıldı, birleştirilmedi.
- **2026-10-31/11-01, PR #2 (G05–G08):** Katalog, üyeler, PDF; yerel Windows doğrulaması (515 passed), metinler onaylandı, merge commit `b6bd69d`.
- **2026-10-31, PR #1 (G01–G04):** Bulut oturumunda G02–G04, inceleme düzeltmeleri D1–D4 (ADR-0051, 106 onaylı metin, TC-32 bütün yönetici yolları, kural ihlalinde 200), yerel Windows doğrulaması (219 passed) ve merge commit `1a93f2d`.
- **2026-10-31, faz 4 ve öncesi:** Test planı (319 TC), plan (G01–G19, KL-1…KL-46), ADR-0026…0048, faz 3 kararları (ADR-0001…0025), faz 2 araştırmaları, faz 1 SRS. Ayrıntı git geçmişinde ve plan §8–§10'da.

## Nasıl çalıştırılır ve test edilir

- `pip install -r requirements-dev.txt`, `python manage.py migrate`, `python manage.py createsuperuser` (ilk yönetici), `python manage.py runserver` → `/giris/`.
- Testler: `python -m pytest -q` (yavaş PDF ve barkod testleri `slow` işaretli ve varsayılan koşuda dahil; yalnız onlar için `-m slow`).
- Yetki kapsamı: `coverage report --include="accounts/permissions.py,accounts/middleware.py" --fail-under=100`.
- NFR-13 kapsamı: `coverage run --branch -m pytest`, ardından `coverage report --include="*/domain.py" --fail-under=90`.
- Servis hedefi: `coverage report --include="billing/services.py,circulation/services.py" --fail-under=85`; diğer hedefler test planı §4 (`notifications/services.py` için hedef yok, yalnız rapor).
- Hatırlatmalar: `python manage.py send_reminders [--date YYYY-MM-DD]` (dev'de konsol backend'i; çıktı "gönderilen=…, başarısız=…, atlanan=…").
- Migration kontrolü: `python manage.py makemigrations --check --dry-run`.
- `operations` kapsamı (hedef ≥ %80, test planı §4): `coverage report --include="operations/*" --fail-under=80`.
- Yedek ve geri yükleme (dev'de `var/backups`, `var/exports` ve `var/export-passphrase.txt` elle açılır): `python manage.py backup_db [--date …]`, `export_backup [--date …] [--passphrase-file PATH]`, `restore_backup PATH [--passphrase-file PATH] --yes` (uygulama ve `runserver` kapalıyken).
- Anonimleştirme: `python manage.py anonymize_expired [--date …]` (çıktı "anonimleştirilen üye=…, bağı koparılan ödünç=…, ertelenen üye=…").
- Zamanlayıcı: `LIBRARY_SCHEDULER_ENABLED=1 waitress-serve --listen=127.0.0.1:8000 --threads=8 library_site.wsgi:application` (dev için ayrıca `DJANGO_SETTINGS_MODULE=library_site.settings.dev`); log stderr'de.

## Tuzaklar

- **Görev sırası:** G09, G10'dan sonra yapıldı (KL-39); numaralar değişmedi.
- **Python sürümü:** Yerelde 3.11.9, bulutta 3.11.18; Django 6.x 3.12+ istediği için 5.2 LTS (ADR-0013). Bulut imajındaki varsayılan `python` 3.13'tür; sanal ortam `/usr/bin/python3.11` ile kurulur.
- **Eşzamanlılık testleri:** Bellekteki paylaşımlı önbellekli SQLite'ta tablo kilitleri beklemeden hata verir; IMMEDIATE işlem testleri `file_db` ve `django_db(transaction=True)` ister.
- **Defter yalnız eklenir (I6):** `LedgerEntry.save()` güncellemede `ValueError` verir; G15'teki `loan_id` bağ koparma queryset `update` ile yapılır. Testte ilişkili ödüncü queryset ile değiştirirsen kalemi yeniden oku (önbellekteki `fee.loan` bayat kalır).
- **Arka plan subagent'ları:** Sonuçları yalnız onları başlatan oturuma gelir; büyük çıktılar oturum kapanmadan depoya kopyalanmalı.
- **Kitapyurdu ISBN alanı:** Geçersiz ISBN-10'lar büyük olasılıkla "978" öneki atılmış ISBN-13'tür (ADR-0008; `6053609322` → `9786053609322`).
- **"İade" terimi:** Yalnız kitap iadesi demektir. Para için "para iadesi", kodda `REFUND` (ADR-0027).
- **Windows konsolu:** `python -I`, `PYTHONIOENCODING`'i yok sayar; cp1254 konsolda Türkçe çıktı bozulur. Çıktıyı UTF-8 bir dosyaya yaz. `manage.py` çıktısı dosyaya yönlendirildiğinde de cp1254 yazılır (`PYTHONIOENCODING=utf-8` verilmezse); dosyayı cp1254 ile oku. Yerel `var/library.sqlite3` boştur (tablo yok); komut denemeleri için scratchpad'de `LIBRARY_DB_PATH` ile geçici bir veritabanı migrate et.
- **Bash aracında heredoc:** Türkçe kesme işareti içeren uzun heredoc'lar "unexpected EOF" verebilir; dokümanları Write aracıyla ya da dosyaya yazılmış betikle değiştir. `pkill -f <desen>` aynı deseni içeren kabuk komutunu da öldürür.
- **SQLite ve Django:** Tutarlar kuruş (ADR-0016). Veritabanı ağ paylaşımına konmaz (WAL). Django'nun SQLite `AutoField`'ı `AUTOINCREMENT`'tir; nüsha barkodu buna dayanır.
- **Windows'ta zoneinfo:** `tzdata` gerekir (R-10, KL-18, TC-235).
- **django-axes ve test istemcisi:** `client.login()` yerine `client.force_login()`; giriş akışını sınayan testler `/giris/`e POST eder.
- **Zaman sabitleme:** `FrozenClock` `django.utils.timezone.now`'ı patch'ler; model alanının `default=timezone.now`'ı (ör. `AuditEvent.occurred_at`) patch'i görmez. Zamanı testte sabitlenecek alanlar `save()` içinde `timezone.now()` çağırır (`Copy.status_changed_at`, `LedgerEntry.created_at`). "Bugün" için `administration.clock.today` `monkeypatch` edilir.
- **Boş POST:** `Form(request.POST or None)` boş POST'ta formu bağlamaz; boş isteğin hata vermesi gereken formlarda `request.POST if request.method == "POST" else None` kullan (G08 seçim formları).
- **E-posta testleri:** Test ayarı bellek backend'idir (`mail.outbox`). SMTP hatası `django.core.mail.backends.locmem.EmailBackend.send_messages` yamalanarak, eşzamanlı çalışma `notifications.services._send` yamalanarak canlandırılır. SMTP sırasında açık işlem olmadığını sınayan test `django_db(transaction=True)` ister.
- **Bulutta yerel `main`:** Klonlanan depodaki yerel `main` dalı bayat olabilir (G13 oturumunda `1a93f2d`'deydi). Yeni dalı `git fetch origin main` ardından `origin/main`'den aç.
- **Kum havuzu:** pytest geçici klasörü engellenirse `PYTEST_DEBUG_TEMPROOT` yalnız kabukta scratchpad'e yönlendirilir.
- **SQLite yedeği ve işlem:** `sqlite3.Connection.backup`, kaynak bağlantı açık bir işlemdeyse dönmeden bekler; yedeği hiçbir zaman `transaction.atomic()` içindeki Django bağlantısından alma (G14 ayrı bağlantı kullanır).
- **`operations` testleri:** Komut testleri `ops` fixture'ıyla (`file_db` ve `django_db(transaction=True)`) dosya veritabanında koşar; scrypt maliyeti `backup.KDF_PARAMS` yamasıyla düşürülür (TC-192 gerçek değerlerle). Kilit testleri kilidi alt süreçte tutar (`operations/tests/support.py`).
- **Kilit dosyası:** `<LIBRARY_DB_PATH>.app.lock` kalıcıdır, silinmesi gerekmez; kilit süreç ölünce kalkar. `runserver` de kilidi tutar.
