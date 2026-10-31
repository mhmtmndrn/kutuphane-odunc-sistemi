# Durum (devir notu)

- **Güncelleme:** 2026-11-01 (faz 5, G13 tamam; PR açık, onay bekliyor)
- **Aşama:** eng-process **faz 5**. `feature/foundation` (G01–G04, PR #1), `feature/catalog-members` (G05–G08, PR #2) ve `feature/circulation` (G10 → G09 → G11 → G12, PR #3) birleşti; `main` = `d0c4555` (PR #3'ün merge commit'i). Grup `feature/notifications` (**G13**, geciken listesi ve hatırlatmalar) **tamam**; `main`'e PR açıldı, birleştirilmedi.
  - **`92bf48e` (`docs:`):** STATUS'taki bayat satırlar, ADR-0052, G13 açılış kararları (plan §11), G13 dosya listesine `prod.py`, plan §3'te ADR-0052 ve sıradaki numara 0053.
  - **`158d43d` (`feat:` G13):** `notifications` app'i: `ReminderLog` (son tarih başına kısmi benzersiz indeks, ADR-0039), pencere kuralları, `send_due_reminders` (S6 adayları, önce e-posta sonra kendi işleminde kayıt, benzersiz kısıt ihlali `skipped`, SMTP hatası FAILED), `send_manual_reminders` (tekrar engeli yok, `triggered_by`, denetim kaydı yok), KL-13 e-posta şablonları, `send_reminders` komutu (`run_job`, FAILED varsa çıkış 1 ve `job_run` SUCCESS), `/gecikenler/` ve `/gecikenler/hatirlat/`, menü ve ana sayfada "Gecikenler", üretimde `EMAIL_TIMEOUT = 10` (ADR-0052).
  - Sonuç (bulut, Linux, Python 3.11.18): `python -m pytest notifications -q` → 67 passed; `python -m pytest -q` → 852 passed (`slow` dahil; önceki 784); `-m slow` → 4 passed; `makemigrations --check --dry-run` → "No changes detected"; dal kapsamı: `*/domain.py` %100 (`--fail-under=90` geçti), `accounts/permissions.py` ve `accounts/middleware.py` %100, `notifications/services.py` %98 (hedef yok, yalnız rapor; kapsanmayan tek satır ulaşılamayan üyesiz ödünç dalı), `notifications` toplam %99, proje toplamı %99.
  - Dev ayarlarıyla `python manage.py send_reminders --date 2026-11-14` → "gönderilen=2, başarısız=0, atlanan=0", çıkış 0 (konsolda iki e-posta: DUE_SOON ve OVERDUE_1); ikinci koşu "gönderilen=0, başarısız=0, atlanan=0", çıkış 0.
  - `/gecikenler/` geliştirme sunucusunda Playwright ile açıldı ve gözle kontrol edildi: seçim kutuları, "rıza yok"/"e-posta yok" etiketleri, kapalı tarih düşülmüş gecikme günü, boş seçim hatası, elle hatırlatma sonrası ödünç başına mesajlar (gönderildi yeşil, diğerleri sarı).
  - Test planında 244 TC "Geçti" (224 + G13'ün 20'si).
  - Plan: [docs/plans/2026-10-31-kutuphane-odunc-sistemi.md](plans/2026-10-31-kutuphane-odunc-sistemi.md). G13 kutusu kanıtıyla işaretli; uygulama ayrıntıları ve onaya sunulan metinler §11'de ("G13 — uygulama ayrıntıları", "G13 uygulayıcının seçtiği kullanıcıya görünen metinler").
  - **Yerel Windows doğrulaması bekleniyor (R-15):** `python -m pytest -q` (852), `-m slow`, `makemigrations --check --dry-run`, kapsam komutları ve `send_reminders --date 2026-11-14` (konsol backend'i, Türkçe çıktı için UTF-8 dosyaya yaz).
- **Repo:** https://github.com/mhmtmndrn/kutuphane-odunc-sistemi (özel). Dallar: `main` (`d0c4555`), `feature/foundation`, `feature/catalog-members` ve `feature/circulation` (kapandı), `feature/notifications` (G13, PR açık).
- **Bulut kredisi (ADR-0048):** 100 $, yaklaşık 2026-11-05'te sıfırlanıyor (R-16).
- **Bulut oturumu:** Her grup için kullanıcı yeni bir bulut oturumu açar, Claude açılış istemini hazırlar (KL-38). Oturum kritik soruyu oturumun içinde sorar; planın vermediği metinleri seçip §11'de listeler ve PR'da onaya sunar (plan §11, 2026-11-01 kararları).
  - **Tarayıcı (önerilen):** claude.ai/code; repo `mhmtmndrn/kutuphane-odunc-sistemi`, ortam **Default** (Trusted ağ; pip için PyPI gerekir).
  - **Terminal:** depo klasöründe `claude --cloud "<istem>"`; yerel commit'ler önce push edilmeli.
  - Kaynak: https://code.claude.com/docs/en/claude-code-on-the-web.

## Bu oturumda sorulan ve cevaplanan

- **G13 açılışından önce (2026-11-01, kullanıcı onayı):** Kritik karar [ADR-0052](decisions/0052-smtp-timeout.md): üretimde `EMAIL_TIMEOUT = 10` (`prod.py`); SMTP takılırsa waitress ya da zamanlayıcı iş parçacığı süresiz kilitlenmez, zaman aşımı FAILED olarak kaydedilip pencere içinde yeniden denenir. Yedi küçük karar (PRG ve ödünç başına mesaj, boş seçim, SMTP sırasında açık işlem yok, e-postada ödüncün ceza kopyaları, yalnız `SMTPException`/`OSError` FAILED, "Gecikenler" bağlantısı, geçersiz `--date`) plan §11'de.
- Oturum içinde kritik soru çıkmadı; yeni ADR yok (sıradaki numara 0053).

## G13 sapmaları ve dikkat edilecekler (ayrıntı plan §11)

- Plana ek arayüzler: `notifications.services.overdue_list` (`OverdueEntry(row, block)`), `ManualResult`'a `member_no`, `full_name`, `title`; domain `due_ranges`, `contact_block`, `OUTCOME_LABELS`, `counts_text`, `error_text`.
- Elle hatırlatmada bilinmeyen ya da sayısal olmayan kimlik hiçbir şey göndermeden "Ödünç bulunamadı" verir; liste 200 ile gösterilir. "Gecikmemiş" ölçütü listeyle aynıdır (`due_on < bugün` ve açık).
- Komut, FAILED varsa sayımları yazdıktan sonra `CommandError("<n> hatırlatma gönderilemedi", returncode=1)` verir; `call_command` ile çağıran (G16 zamanlayıcısı) bu hatayı yakalamalıdır, `job_run` zaten SUCCESS'tir.
- E-posta şablonları `autoescape off` düz metindir; gönderen `DEFAULT_FROM_EMAIL` (üretimde `LIBRARY_EMAIL_FROM`).
- Komut testleri `notifications/tests/test_commands.py`'de (KL-11'deki üç dosyaya ek).
- `INSTALLED_APPS`, kök `urls.py`, `base.html`, `home.html`, `app.css` (`.message-warning`, `.tag`, `.num`), `tests/test_authorization.py` (`gecikenler/` yolları personel kümesinde) ve `tests/test_prod_settings.py` (ADR-0052 testi) dosya listesi dışında değişti.

## Önceki grup (G09–G12) için hâlâ geçerli notlar

- Eşzamanlılık testleri (TC-103, TC-145…TC-148) `tests/support/concurrency.py`'deki `file_db` fixture'ıyla geçici dosya veritabanında, `run_parallel` ile iki iş parçacığında koşar.
- `cancel_unpaid` denetim kaydı yazmaz; `CANCELLATION` yalnız elle iptalde. Ödünç, iade, uzatma, pasifleştirme ve elle hatırlatma denetim kaydı yazmaz.
- `catalog.urls` `circulation.urls`'ten önce kalmalı (`/nushalar/etiket/`); bunu bir test sabitler.

## Sıradaki adım

1. **G13 PR'ı (kullanıcı):** Yerel Windows doğrulaması (R-15), §11'deki G13 metinlerinin onayı ve birleştirme kararı. Birleşince sonraki dalın ilk commit'i `main`'in yeni hash'ini bu nota yazar.
2. **Sonraki grup:** `feature/operations`: **G14–G16** (yedek, şifreli dışa aktarma ve geri yükleme; saklama ve anonimleştirme; zamanlayıcı ve telafi). G16 `send_reminders`'ı zamanlayıcıdan 09:00'da tetikler (faz 3 küçük karar 13) ve telafide `last_success(Job.REMINDERS)`'ı kullanır. Açık noktalar açılış isteminden önce kullanıcıya sorulur; istem yeni bir bulut oturumunda verilir.
   - Genel sıra: G01 → G13 (tamam), G14…G16, G17…G18, G19.

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
- **ADR'ler:** [0001–0052](decisions/), hepsi kabul edildi; özet plan §3. Sıradaki numara 0053.
- **Plan:** §3 kararlar ve KL-1…KL-46; §4 görevler G01–G19; §7 izlenebilirlik; §8 tutarlılık; §11 sapmalar ve metinler.
- **Test planı:** [docs/test-plan.md](test-plan.md): 319 TC; 244'ü "Geçti". Elle TC'ler: TC-223, TC-225…TC-234, TC-319 (faz 6).
- **Araştırma:** [ISBN meta veri](research/2026-10-31-isbn-meta-veri-apileri.md), [demo veri seti](research/2026-10-31-demo-kitap-veri-seti.md).

## Geçmiş (özet)

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

## Tuzaklar

- **Görev sırası:** G09, G10'dan sonra yapıldı (KL-39); numaralar değişmedi.
- **Python sürümü:** Yerelde 3.11.9, bulutta 3.11.18; Django 6.x 3.12+ istediği için 5.2 LTS (ADR-0013). Bulut imajındaki varsayılan `python` 3.13'tür; sanal ortam `/usr/bin/python3.11` ile kurulur.
- **Eşzamanlılık testleri:** Bellekteki paylaşımlı önbellekli SQLite'ta tablo kilitleri beklemeden hata verir; IMMEDIATE işlem testleri `file_db` ve `django_db(transaction=True)` ister.
- **Defter yalnız eklenir (I6):** `LedgerEntry.save()` güncellemede `ValueError` verir; G15'teki `loan_id` bağ koparma queryset `update` ile yapılır. Testte ilişkili ödüncü queryset ile değiştirirsen kalemi yeniden oku (önbellekteki `fee.loan` bayat kalır).
- **Arka plan subagent'ları:** Sonuçları yalnız onları başlatan oturuma gelir; büyük çıktılar oturum kapanmadan depoya kopyalanmalı.
- **Kitapyurdu ISBN alanı:** Geçersiz ISBN-10'lar büyük olasılıkla "978" öneki atılmış ISBN-13'tür (ADR-0008; `6053609322` → `9786053609322`).
- **"İade" terimi:** Yalnız kitap iadesi demektir. Para için "para iadesi", kodda `REFUND` (ADR-0027).
- **Windows konsolu:** `python -I`, `PYTHONIOENCODING`'i yok sayar; cp1254 konsolda Türkçe çıktı bozulur. Çıktıyı UTF-8 bir dosyaya yaz.
- **Bash aracında heredoc:** Türkçe kesme işareti içeren uzun heredoc'lar "unexpected EOF" verebilir; dokümanları Write aracıyla ya da dosyaya yazılmış betikle değiştir. `pkill -f <desen>` aynı deseni içeren kabuk komutunu da öldürür.
- **SQLite ve Django:** Tutarlar kuruş (ADR-0016). Veritabanı ağ paylaşımına konmaz (WAL). Django'nun SQLite `AutoField`'ı `AUTOINCREMENT`'tir; nüsha barkodu buna dayanır.
- **Windows'ta zoneinfo:** `tzdata` gerekir (R-10, KL-18, TC-235).
- **django-axes ve test istemcisi:** `client.login()` yerine `client.force_login()`; giriş akışını sınayan testler `/giris/`e POST eder.
- **Zaman sabitleme:** `FrozenClock` `django.utils.timezone.now`'ı patch'ler; model alanının `default=timezone.now`'ı (ör. `AuditEvent.occurred_at`) patch'i görmez. Zamanı testte sabitlenecek alanlar `save()` içinde `timezone.now()` çağırır (`Copy.status_changed_at`, `LedgerEntry.created_at`). "Bugün" için `administration.clock.today` `monkeypatch` edilir.
- **Boş POST:** `Form(request.POST or None)` boş POST'ta formu bağlamaz; boş isteğin hata vermesi gereken formlarda `request.POST if request.method == "POST" else None` kullan (G08 seçim formları).
- **E-posta testleri:** Test ayarı bellek backend'idir (`mail.outbox`). SMTP hatası `django.core.mail.backends.locmem.EmailBackend.send_messages` yamalanarak, eşzamanlı çalışma `notifications.services._send` yamalanarak canlandırılır. SMTP sırasında açık işlem olmadığını sınayan test `django_db(transaction=True)` ister.
- **Bulutta yerel `main`:** Klonlanan depodaki yerel `main` dalı bayat olabilir (G13 oturumunda `1a93f2d`'deydi). Yeni dalı `git fetch origin main` ardından `origin/main`'den aç.
- **Kum havuzu:** pytest geçici klasörü engellenirse `PYTEST_DEBUG_TEMPROOT` yalnız kabukta scratchpad'e yönlendirilir.
