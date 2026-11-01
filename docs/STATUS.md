# Durum (devir notu)

- **Güncelleme:** 2026-11-01 (faz 6 kurulumu bitti: plan §12.4 adım 1–19; bulgular B1–B9, hepsi `docs/kurulum.md` düzeltmesiyle kapandı; B6–B9 düzeltmeleri commit'lenmedi)
- **Aşama:** eng-process **faz 6 (doğrulama)**, plan §12. Faz 5 tamam (PR #1…#7, G01–G19, `main` = `b3cc2a1`). Proje artık bir **deneme projesi**: gerçek kütüphanede kullanılmayacak, kurulmuş temel gereksiz değiştirilmez (ADR-0067). Kalan: faz 6 ve faz 7 (kapanış).
- **Sıradaki adım (kullanıcı "devam et" diyerek gelecek):** eng-process faz 6, plan §12.1.
  1. **Commit onayı iste (ilk iş):** Çalışma ağacında commit'lenmemiş `docs/kurulum.md`, plan §12.2 (B6–B9) ve bu dosya var. Önerilen mesaj: `docs: record install findings B6-B9 and fix the control, NTP and placeholder checks`. Onaysız commit'leme; push ayrıca sorulur.
  2. Ardından elle TC'ler (plan §12.1): TC-223, 225, 231, 234, 319 tam; TC-229, 230 kısmi. TC-229'un "dinlenen portlar" kısmı ve TC-230'un bu makinedeki kısmı adım 16–19 çıktılarıyla zaten karşılanmış olabilir; TC'ye geçerken kullanıcıyla netleştir. Sonra tam test koşusu, kabul tablosu (§12.3), `spec-reviewer`, bulgular, `v1.0.0` ve temizlik sorusu (küçük karar 9). Her yeni takılma §12.2'ye **B10**'dan başlayan numarayla girer; düzeltme biçimi AskUserQuestion ile sorulur.
- **Kullanıcı tercihi:** Plan ve STATUS'a yönlendirme yerine, sıradaki adımın komutlarını doğrudan, kopyalanabilir hâlde ve nerede çalıştırılacağıyla birlikte ver.
- **Git:** Dal `feature/phase6-verification`. Push edildi: `4179afe`, `6dfe30e`, `25c5c78`, annotated `v1.0.0-rc.1` → `b3cc2a1`. **Yerelde, push edilmedi:** `54fd1bf` (B1, ADR-0068) ve `7423b31` (B2–B5; kurulum belgesinin yeniden sıralanması, architecture §8). Push'u sormadan yapma.
- **Kurulmuş test ortamı (§12.4 adım 1–19 tamam, ayrıntı plan §12.2):** `C:\Kutuphane\{app,venv,caddy,winsw,backups,exports,static}`; Python `C:\Program Files\Python311` (NuGet, ADR-0068); servisler `library-app` ve `library-caddy` Running; `https://127.0.0.2/` Chrome, Edge ve Firefox 159'da uyarısız, `http://` → 308 HTTPS; kök sertifika Windows deposunda (Firefox `security.enterprise_roots.enabled` zaten `true`). İlk yönetici `admin`; demo verisi: 300 kitap, 592 nüsha, 200 üye, 150 açık ödünç (10 gecikmiş), 350 kapalı. `w32time` Otomatik'e alınmadı, yalnız başlatıldı. Dinleme: `127.0.0.2:80/443`, `127.0.0.1:8000` (waitress), `127.0.0.1:2019` (Caddy yönetim ucu, B8'de kabul edildi).
- **Sürüm arşivi:** `C:\Users\MEHMET~1\AppData\Local\Temp\claude\C--Users-Mehmet-Emin-AppData-Local-Temp-ai-config-evals-at-02-manual\55dd558d-6ee3-4fff-8dbc-862017410a75\scratchpad\library-v1.0.0-rc.1.zip` (596 538 bayt, SHA-256 `d43b5ed5ad943f7938df96ea530f9cf97c0f954ad7d06d9264ceb5e087e912c3`). Kaybolursa depo klasöründe `git archive --format=zip --prefix=library/ v1.0.0-rc.1 -o <scratchpad>\library-v1.0.0-rc.1.zip`.
- **Kurulum öngörüleri:** Beşi de gerçekleşti ve kapandı: (a) B1, (b) B7, (c) B9, (d) B8, (e) B4.
- **Test planı:** 348 TC "Geçti"; TC-226, 227, 228, 232, 233 "Kapsam dışı (deneme projesi, ADR-0067)"; elle kalan TC-223, 225, 229 (kısmi), 230 (kısmi), 231, 234, 319 "Planlandı".
- **Son doğrulama (faz 5 sonu, 2026-11-01, yerel Windows 11, Python 3.11.9):** 1042 passed, `slow` 7, migration temiz, dört kapsam eşiği çıkış 0, proje %97; Caddy + waitress `127.0.0.2`'de geçici denendi, servis kaydı yapılmadı. Ayrıntı plan G19 ve §11; PR #5…#7 notları git geçmişinde.
- **Plan:** [docs/plans/2026-10-31-kutuphane-odunc-sistemi.md](plans/2026-10-31-kutuphane-odunc-sistemi.md) (faz 6: §12).
- **Repo:** https://github.com/mhmtmndrn/kutuphane-odunc-sistemi (özel). Dallar: `main` (`b3cc2a1`), `feature/phase6-verification` (açık), `feature/foundation`, `feature/catalog-members`, `feature/circulation`, `feature/notifications`, `feature/operations` ve `feature/seed-load` (kapandı), `feature/deploy` (kapandı).
- **Bulut kredisi (ADR-0048):** 100 $, yaklaşık 2026-11-05'te sıfırlanıyor (R-16).
- **Bulut oturumu:** Her grup için kullanıcı yeni bir bulut oturumu açar, Claude açılış istemini hazırlar (KL-38). Oturum kritik soruyu oturumun içinde sorar; planın vermediği metinleri seçip §11'de listeler ve PR'da onaya sunar (plan §11, 2026-11-01 kararları).
  - **Tarayıcı (önerilen):** claude.ai/code; repo `mhmtmndrn/kutuphane-odunc-sistemi`, ortam **Default** (Trusted ağ; pip için PyPI gerekir).
  - **Terminal:** depo klasöründe `claude --cloud "<istem>"`; yerel commit'ler önce push edilmeli.
  - Kaynak: https://code.claude.com/docs/en/claude-code-on-the-web.

## Bu oturumda sorulan ve cevaplanan

- **Kurulum bulguları B6–B9 (2026-11-01, kullanıcı onayı, dördünde önerilen seçenek):** Yalnız `docs/kurulum.md` değişti, kod ve zip aynı (rc.2 yok). B6 dar `__DOLDUR__` kontrolü; B7 `w32time`'ı Otomatik yapıp başlatma ve `Get-TimeZone`; B8 `admin off` eklenmedi, belge `127.0.0.1:2019`'u yerel dinleme olarak yazıyor, kontrol komutu Caddy'nin bütün dinlemelerini listeliyor; B9 `curl` komutları platform "Kontrol"üne (Windows `curl.exe`). Windows komutları bu makinede doğrulandı, Linux'takiler çalıştırılmadı. ADR yazılmadı. Ayrıntı plan §12.2.
- **Kurulum bulguları B3–B5 (2026-11-01, kullanıcı onayı):** Üçünün kökü aynı: "Ortam değişkenleri" Hazırlık'taydı, venv'den ve ortam dosyalarının yerine konmasından önce. "Tek yeniden sıralama" seçildi (yerinde küçük yamalar ve yalnız kayıt seçilmedi); B2–B5 tek `docs:` commit'inde (`7423b31`). Ayrıntı plan §12.2. ADR yazılmadı: ADR-0060'ın yapısı (ortak gövde, iki platformda aynı alt başlıklar) korundu.
- **Kurulum bulgusu B1 (2026-11-01, kullanıcı onayı):** Kişisel Python 3.11.9 kuruluyken python.org yükleyicisi "all users" kurmuyor. [ADR-0068](decisions/0068-phase6-python-from-nuget-package.md): test ortamında Python resmi NuGet paketinden `C:\Program Files\Python311`'e açılır (kişisel kurulum ve 281 paketlik geliştirme ortamı korunur; paket ve venv scratchpad'de doğrulandı). `docs/kurulum.md` düzeltildi: Advanced Options yolu, kişisel kurulumu önce kaldırma notu, açık yollu venv komutu. Sıradaki ADR 0069.
- **Faz 6 açılışı (2026-11-01, kullanıcı onayı):** Proje bir deneme projesidir; gerçek bir kütüphanede kullanılmayacak, kurulmuş temel gereksiz yere değiştirilmez. [ADR-0067](decisions/0067-phase6-trial-project-single-windows-machine.md): bu Windows 11 makinesi, yalnız Windows, `127.0.0.2`, kurulumu kullanıcı yapar, `v1.0.0-rc.1` → `v1.0.0`, Firefox kurulur; TC-226/227/228/232/233 kapsam dışı, TC-229/230 kısmi. On küçük karar plan §12'de. Sıradaki ADR 0068.
- **G19 açılışından önce (2026-11-01, kullanıcı onayı):** Yedi kritik karar: [ADR-0060](decisions/0060-install-doc-common-body-two-platforms.md) (kurulum belgesinin yapısı), [ADR-0061](decisions/0061-access-by-static-ip.md) (sabit IP), [ADR-0062](decisions/0062-service-account.md) (servis hesabı), [ADR-0063](decisions/0063-tool-versions-winsw-caddy.md) (WinSW 2.12.0, Caddy 2.11.7), [ADR-0064](decisions/0064-release-zip-and-update-procedure.md) (sürüm zip'i ve güncelleme), [ADR-0065](decisions/0065-caddy-no-access-log.md) (erişim logu yok), [ADR-0066](decisions/0066-deploy-files-consistency-tests.md) (tutarlılık testleri). On iki küçük karar ve yerel doğrulama kararı plan §11'de. Oturum içinde yeni kritik soru çıkmadı; sıradaki ADR 0067.
- **G17–G18 açılışından önce (2026-11-01, kullanıcı onayı):** Üç kritik karar: [ADR-0056](decisions/0056-open-library-fetch-network-blocked.md) (Open Library'ye erişilemezse JSON olmadan devam; gerçek dosya yerel doğrulamada), [ADR-0057](decisions/0057-seed-phone-numbers.md) (tohum telefonları `000 ddd dd dd`) ve [ADR-0058](decisions/0058-loadtest-seed-only-guard.md) (yük betiği `@example.invalid` dışı e-postalı üye görürse istek atmadan çıkış 1). On iki küçük karar (README, bugüne göre tarihler, demo ve yük profilleri, domain fonksiyonları ve tek işlem, sentetik kitap, audit yok ve Allocation, çıktı, rıza, betiğin yeniden seçimi, `scripts/` paketi, duman testi) plan §11'de. Yeni davranışların testleri TC-340…TC-356. Sıradaki ADR numarası 0060 (ADR-0059 yerel doğrulamada yazıldı).
- **G14–G16 açılışından önce (2026-11-01, kullanıcı onayı):** Üç kritik karar: [ADR-0053](decisions/0053-hourly-catch-up.md) (açılışa ek saatlik telafi; `misfire_grace_time=3600`, `coalesce=True`), [ADR-0054](decisions/0054-restore-keeps-pre-restore-copy.md) (geri yükleme mevcut veritabanını `<db>.pre-restore-YYYYMMDD-HHMMSS` olarak bırakır) ve [ADR-0055](decisions/0055-reminder-log-error-cleared-on-unlink.md) (bağ koparılırken `reminder_log.error` NULL). Dokuz küçük karar (komut argümanları ve geçersiz tarih, magic bayt, migration yok, `.tmp` + `os.replace`, tek işçili zamanlayıcı, komut sarmalayıcı ve stderr `LOGGING`, "Saklama" bağlantısı, `Member.display_name`, ilk istisnada durma) plan §11'de.
- **G13 açılışından önce (2026-11-01):** [ADR-0052](decisions/0052-smtp-timeout.md) ve yedi küçük karar; plan §11.

## G19 sapmaları ve dikkat edilecekler (ayrıntı plan §11)

- **Caddyfile yeri:** Caddy yapılandırmayı uygulama klasöründen okur (`…\app\deploy\Caddyfile`, `/opt/library/app/deploy/Caddyfile`); güncelleme onu da günceller. Genel seçeneklerde `skip_install_trust` var (servis hesabı yönetici değil).
- **Caddy veri klasörü:** `XDG_DATA_HOME`/`XDG_CONFIG_HOME` ile Windows'ta `C:\Kutuphane\caddy`, Linux'ta `/var/lib/library/caddy`; kök sertifika `<klasör>/caddy/pki/authorities/local/root.crt`.
- **WinSW `<env>`:** Yalnız kuruma özgü ve gizli değerler `__DOLDUR__`; sabit yollar dolu. `<depend>` yalnız Caddy XML'inde.
- **Linux yedek diski:** `/mnt/library-backup/{backups,exports}`, `ReadWritePaths=`'te `-` önekiyle (disk yokken servis başlar, yedek hata verir).
- **Yeni ortam değişkeni eklenirse:** `tests/test_deploy_files.py` (TC-359…TC-362) ayarları, architecture §6.4'ü, `library.env.example`'ı ve iki XML'i birlikte günceller; biri eksikse test kırmızı olur.
- **Dosya listesi dışında değişen:** Yok.

## G17–G18 sapmaları ve dikkat edilecekler (ayrıntı plan §11)

- **Kitap dosyası:** `seed/books_openlibrary.json` yerel doğrulamada çekilip commit'lendi (ADR-0056, ADR-0059; filtre sürümü 2). Dosya yokken `load_seed_data` "Kitap dosyası bulunamadı" ile çıkış 1 verir. Testler `operations/tests/data/books_sample.json`'u (12 kayıt) ve testin ürettiği dosyaları kullanır (`seed.BOOKS_FILE` yaması).
- **Barkod:** `catalog.domain.copy_barcode` barkodun tek kaynağı oldu; `add_copies` de onu kullanır (dosya listesi dışı değişiklik).
- **Kimlikler açık:** Tohum veri id'leri 1'den yazar (tablolar boş). Zaman damgaları tarihlerden türetilir; `timezone.now()` kullanılmaz, aynı gün ve tohum aynı veriyi verir.
- **Demo borçluları:** Gecikmeli iade oranı demo profilinde de %10 (35 FINE); 5 borçlunun en son gecikmeli iadesinin cezası ödenmemiş, diğerleri FINE + PAYMENT.
- **Yük betiği:** Üye adayları açık ödüncü olmayan ve bakiyesi 0 olan aktif üyelerdir. Kural ihlali 200 döndüğü için hata sayılır. `Secure` çerezler düz HTTP'de de gönderilir (prod ayarlarında waitress'e Caddy'siz bağlanmak için); faz 6'da `LIBRARY_ALLOWED_HOSTS` waitress adresini içermeli. İstek yapılmamış tür sonucu "kaldı" yapar.
- **`testpaths`:** `pyproject.toml` artık klasör listesi verir (bütün app'ler, `scripts`, `tests`). Yeni bir app eklenirse listeye de eklenmeli; TC-355 eksikliği yakalar.
- **Dosya listesi dışında değişenler:** `catalog/domain.py`, `catalog/services.py` (`copy_barcode`); `pyproject.toml`'daki `slow` açıklaması.

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

Baştaki "Sıradaki adım" maddesine bakın (kurulum adım 13–19, bulgular, elle TC'ler, doğrulama, faz 7).

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
- **ADR'ler:** [0001–0068](decisions/), hepsi kabul edildi; özet plan §3. Sıradaki numara 0069.
- **Plan:** §3 kararlar ve KL-1…KL-46; §4 görevler G01–G19; §7 izlenebilirlik; §8 tutarlılık; §11 sapmalar ve metinler.
- **Test planı:** [docs/test-plan.md](test-plan.md): 366 TC (TC-320…TC-339 G14–G16, TC-340…TC-356 G17–G18 açılışında, TC-357…TC-358 ADR-0059 ile, TC-359…TC-366 G19 açılışında eklendi); 348'i "Geçti". Elle TC'ler: TC-223, TC-225…TC-234, TC-319 (faz 6).
- **Araştırma:** [ISBN meta veri](research/2026-10-31-isbn-meta-veri-apileri.md), [demo veri seti](research/2026-10-31-demo-kitap-veri-seti.md).

## Geçmiş (özet)

- **2026-11-01, faz 6 yerel oturumları:** ADR-0067, ADR-0068, plan §12 ve §12.4 kontrol listesi, `v1.0.0-rc.1`; kurulum adım 1–12 ve bulgular B1–B5 (`54fd1bf`, `7423b31`).
- **2026-11-01, `feature/deploy` bulut oturumu (G19):** İlk commit `docs:` (bayat STATUS satırları, ADR-0060…0066, açılış kararları, TC-359…TC-366), ardından TDD ile (testler önce kırmızı) tek `feat:` commit'i, sonra handoff `docs:`; her biri push edildi. Caddy 2.11.7 bulutta indirilebildi: `caddy validate` ve waitress + Caddy canlı denemesi geçti. Oturum içinde yeni kritik soru çıkmadı. PR #7 açıldı, birleştirilmedi.
- **2026-11-01, `feature/seed-load` bulut oturumu:** İlk commit `docs:` (bayat STATUS satırları, ADR-0056…0058, açılış kararları, TC-340…TC-356), ardından G17 ve G18 görev başına TDD (testler önce kırmızı) ve birer `feat:` commit'i, sonra handoff `docs:`; her biri push edildi. Open Library bulut ağında engelliydi (ADR-0056). Demo verisi test istemcisiyle, yük betiği waitress'e karşı 10 saniyelik duman testiyle elle doğrulandı. Oturum içinde yeni kritik soru çıkmadı (sıradaki ADR 0059). PR açıldı, birleştirilmedi.
- **2026-11-01, `feature/operations` bulut oturumu:** İlk commit `docs:` (bayat STATUS satırları, ADR-0053…0055, açılış kararları, TC-320…TC-339), ardından G14, G15, G16 görev başına TDD (testler önce kırmızı) ve birer `feat:` commit'i, sonra handoff `docs:`; her biri push edildi. Ekranlar Playwright ile, zamanlayıcı `waitress-serve` ile elle doğrulandı. Oturum içinde yeni kritik soru çıkmadı. PR açıldı, birleştirilmedi.
- **2026-10-31/11-01, PR #1…#4 (G01–G13):** Yerel Windows doğrulamaları (219, 515, 784, 852 passed), metinler onaylandı; merge commit'leri `1a93f2d`, `b6bd69d`, `d0c4555`, `c2e5bc8`. PR #1'de inceleme düzeltmeleri D1–D4 (ADR-0051, 106 onaylı metin).
- **2026-11-01, `feature/notifications` bulut oturumu:** İlk commit `docs:` (bayat STATUS satırları, ADR-0052, G13 açılış kararları), ardından G13 TDD ile (20 TC önce kırmızı) tek `feat:` commit'i, sonra `docs:` (test planı, plan kutusu, §11, STATUS); her biri push edildi. Ekran Playwright ile göz kontrolünden geçti. PR açıldı, birleştirilmedi.
- **2026-11-01, `feature/circulation` bulut oturumu:** İlk commit `docs:` (STATUS ve pasifleştirme koruması kararı), ardından G10, G09, G11, G12 görev başına TDD ve `feat:` commit'i, her biri push edildi. TC-91 için bir soru soruldu (denetim listesinde TL). Ekranlar geliştirme sunucusunda Playwright ile açılıp göz kontrolünden geçti. PR açıldı, birleştirilmedi.
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
- Tohum veri: `python manage.py load_seed_data --profile demo|load --actor <ad> [--seed 42]` (boş veritabanında; `seed/books_openlibrary.json` gerekir). Demo kitapları: `python scripts/fetch_demo_books.py --out seed/books_openlibrary.json --limit 300`.
- Yük testi: `python scripts/loadtest.py --base-url http://127.0.0.1:8000 --user <ad> --password-file <dosya> --db <veritabanı> --workers 5 --duration 120` (yalnız tohum verili veritabanında, ADR-0058).
- Dağıtım dosyaları: `python -m pytest tests/test_deploy_files.py -q`; Caddyfile `caddy validate --config deploy/Caddyfile --adapter caddyfile` (`LIBRARY_HOST`, `LIBRARY_BIND`, `LIBRARY_STATIC_ROOT` tanımlıyken). Kurulum: [docs/kurulum.md](kurulum.md).
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
- **Bulutta Caddy:** `caddyserver.com` ve GitHub API engelli; sürüm `git ls-remote --tags https://github.com/caddyserver/caddy` ile, ikili `https://github.com/caddyserver/caddy/releases/download/v<sürüm>/…` ile alınır.
- **Kum havuzu:** pytest geçici klasörü engellenirse `PYTEST_DEBUG_TEMPROOT` yalnız kabukta scratchpad'e yönlendirilir.
- **SQLite yedeği ve işlem:** `sqlite3.Connection.backup`, kaynak bağlantı açık bir işlemdeyse dönmeden bekler; yedeği hiçbir zaman `transaction.atomic()` içindeki Django bağlantısından alma (G14 ayrı bağlantı kullanır).
- **`operations` testleri:** Komut testleri `ops` fixture'ıyla (`file_db` ve `django_db(transaction=True)`) dosya veritabanında koşar; scrypt maliyeti `backup.KDF_PARAMS` yamasıyla düşürülür (TC-192 gerçek değerlerle). Kilit testleri kilidi alt süreçte tutar (`operations/tests/support.py`).
- **Kilit dosyası:** `<LIBRARY_DB_PATH>.app.lock` kalıcıdır, silinmesi gerekmez; kilit süreç ölünce kalkar. `runserver` de kilidi tutar.
- **Tohum veri testleri:** `operations/tests/test_seed.py`'deki yük profili testleri (TC-220, TC-317, TC-346) modül kapsamlı tek bir yüklemeyi paylaşır (~16 sn); yüklemeyi işlem içinde yapıp geri aldığı için diğer testlerin veritabanını kirletmez.
- **Dev ve test istemcisi:** `setup_test_environment()` `ALLOWED_HOSTS`'u `testserver`'a çevirir; dev veritabanına karşı test istemcisi kullanırken `HTTP_HOST` verme. Gerçek dev sunucusu (DEBUG) `localhost` ve `127.0.0.1`'i kabul eder.
