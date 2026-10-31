# Durum (devir notu)

- **Güncelleme:** 2026-11-01 (faz 5, `feature/circulation` tamam, PR açık)
- **Aşama:** eng-process **faz 5**. `feature/foundation` (G01–G04, PR #1) ve `feature/catalog-members` (G05–G08, PR #2) birleşti (`main` = `b6bd69d`). Grup `feature/circulation` (G10 → G09 → G11 → G12; KL-39) **tamam**; `main`'e PR açıldı, kullanıcı incelemesi ve yerel Windows koşusu bekleniyor. **Birleştirilmedi.**
  - **G10:** `d6ed61b`: `circulation/domain.py` (son tarih, gecikme günü, ceza, engeller, üye alanı yorumlama, nüsha durum makinesi) ve `Loan` modeli/migration'ı (kısmi benzersiz indeks, CHECK'ler, `copy_found_on`).
  - **G09:** `d1d16f4`: `billing` app'i: defter ve dağıtım tabloları, FIFO ödeme, af, otomatik ve elle iptal, para iadesi, döküm ekranı.
  - **G11:** `42ecf3a`: ödünç, iade, uzatma, pasifleştirme, geciken listesi servisi; ödünç ve iade ekranları, `scan.js`; üye ayrıntısına açık ödünçler, bakiye ve pasifleştirme formu.
  - **G12:** `64199d1`: kayıp, hasarlı, raftaki nüsha işaretleme, bulundu, onarıldı, kayıttan düşme; nüsha ekranı.
  - Sonuç (bulut, Linux, Python 3.11.18): `python -m pytest -q` → 784 passed (`slow` dahil); `python -m pytest circulation billing -q` → 260 passed; `makemigrations --check --dry-run` → "No changes detected"; dal kapsamı: `*/domain.py` %100, `billing/services.py` %100, `circulation/services.py` %98, `members/services.py` %100, `accounts/permissions.py` ve `accounts/middleware.py` %100; `circulation` + `billing` + `members` toplam %99.
  - Test planında 224 TC "Geçti" (101 + bu grubun 123'ü).
  - Plan: [docs/plans/2026-10-31-kutuphane-odunc-sistemi.md](plans/2026-10-31-kutuphane-odunc-sistemi.md). G09–G12 kutuları kanıtıyla işaretli; uygulama ayrıntıları ve onay bekleyen metinler §11'de ("G09–G12 onay bekleyen metinler").
- **Repo:** https://github.com/mhmtmndrn/kutuphane-odunc-sistemi (özel). Dallar: `main` (`b6bd69d`), `feature/foundation` ve `feature/catalog-members` (kapandı), `feature/circulation` (PR açık).
- **Bulut kredisi (ADR-0048):** 100 $, yaklaşık 2026-11-05'te sıfırlanıyor (R-16).
- **Bulut oturumu:** Her grup için kullanıcı yeni bir bulut oturumu açar, Claude açılış istemini hazırlar (KL-38). Oturum kritik soruyu oturumun içinde sorar; planın vermediği metinleri seçip §11'de listeler ve PR'da onaya sunar (plan §11, 2026-11-01 kararları).
  - **Tarayıcı (önerilen):** claude.ai/code; repo `mhmtmndrn/kutuphane-odunc-sistemi`, ortam **Default** (Trusted ağ; pip için PyPI gerekir).
  - **Terminal:** depo klasöründe `claude --cloud "<istem>"`; yerel commit'ler önce push edilmeli.
  - Kaynak: https://code.claude.com/docs/en/claude-code-on-the-web.

## Bu oturumda sorulan ve cevaplanan

- **Açılıştan önce (2026-11-01):** Pasifleştirme koruması: anonimleştirilmiş üye "Anonimleştirilmiş üye pasifleştirilemez", pasif üye "Üye zaten pasif" ile reddedilir; `deactivated_on` (ADR-0045) üzerine yazılmaz; form yalnız aktif üyede görünür. §11'e yazıldı, G11'de testleriyle uygulandı.
- **G09, TC-91:** Denetim listesi ayrıntıları ham JSON'du, TC "5,00 TL" bekliyordu. Kullanıcı önerilen seçeneği seçti: `details_text` filtresi `amount_kurus` ve `fee_kurus` değerlerini TL olarak gösterir; saklanan JSON değişmez. G03 ekranında küçük gösterim değişikliği; §11'e yazıldı, ADR gerekmedi.
- Kritik karar (yeni bağımlılık, şema dışı değişiklik, plandan farklı arayüz, güvenlik ödünleşimi) çıkmadı; yeni ADR yok (sıradaki numara hâlâ 0052).

## G09–G12 sapmaları ve dikkat edilecekler (ayrıntı plan §11)

- `make_loan` G11 yerine G09'da eklendi (TC-92…TC-96 LOST ödünçlü bedel istiyor). Factory'lerin varsayılan personeli `kayit.test`.
- Eşzamanlılık testleri (TC-103, TC-145…TC-148) `tests/support/concurrency.py`'deki `file_db` fixture'ıyla geçici dosya veritabanında, `run_parallel` ile iki iş parçacığında koşar. **Windows'ta yerel koşuda** bu testlerin geçici dosyayı silebildiği (bağlantıların kapandığı) özellikle izlenmeli.
- Plana ek servisler: `billing`: `get_entry`, `loan_fee`, `StatementRow` alanları; `circulation`: `copies_matching`, `get_loan`, `copy_loans`; `circulation.domain`: `STATUS_LABELS`, `transition_error`.
- `cancel_unpaid` denetim kaydı yazmaz (otomatik iptali `COPY_FOUND` izler); `CANCELLATION` yalnız elle iptalde.
- Uzatma reddi, üye ayrıntısından gelse de ödünç ekranını o üyeyle 200 olarak gösterir (view'lar başka app'in view'ını import edemez).
- `tests/support/urls.py`'deki G02 `/odunc/` yer tutucusu kaldırıldı; gerçek ödünç ekranı yolu karşılıyor.
- Kitap ayrıntısındaki barkodlar nüsha ekranına bağlandı; base menüsüne ve ana sayfaya "Ödünç" ve "İade" eklendi.
- `catalog.urls` `circulation.urls`'ten önce kalmalı (`/nushalar/etiket/`); bunu bir test sabitler.

## Sıradaki adım

1. **PR incelemesi (kullanıcı):** `feature/circulation` → `main` PR'ını incele, §11'deki "G09–G12 onay bekleyen metinler" listesini onayla ya da düzelt, yerelde Windows'ta `python -m pytest -q` (beklenen 784 passed) ve `python manage.py makemigrations --check --dry-run` çalıştır. Birleştirme kullanıcı onayıyla.
2. **Sonraki grup:** `feature/notifications`: **G13** (geciken listesi ekranı `/gecikenler/`, otomatik ve elle hatırlatmalar; `circulation.services.overdue_loans` hazır). G13'ün açık noktaları açılış isteminden önce kullanıcıya sorulur; istem yeni bir bulut oturumunda verilir.
   - Genel sıra: G01 → G12 (tamam), G13, G14…G16, G17…G18, G19.
3. **Onay bekleyen küçük temizlik (önceki oturumdan):** Yerel `worktree-agent-a4c3b8e184eb5859a` dalı silinebilir; boş `.claude/worktrees/agent-a4c3b8e184eb5859a` klasörü elle silinir.

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
- **ADR'ler:** [0001–0051](decisions/), hepsi kabul edildi; özet plan §3.
- **Plan:** §3 kararlar ve KL-1…KL-46; §4 görevler G01–G19; §7 izlenebilirlik; §8 tutarlılık; §11 sapmalar ve metinler.
- **Test planı:** [docs/test-plan.md](test-plan.md): 319 TC; 224'ü "Geçti". Elle TC'ler: TC-223, TC-225…TC-234, TC-319 (faz 6).
- **Araştırma:** [ISBN meta veri](research/2026-10-31-isbn-meta-veri-apileri.md), [demo veri seti](research/2026-10-31-demo-kitap-veri-seti.md).

## Geçmiş (özet)

- **2026-11-01, `feature/circulation` bulut oturumu:** İlk commit `docs:` (STATUS ve pasifleştirme koruması kararı), ardından G10, G09, G11, G12 görev başına TDD ve `feat:` commit'i, her biri push edildi. TC-91 için bir soru soruldu (denetim listesinde TL). Ekranlar geliştirme sunucusunda Playwright ile açılıp göz kontrolünden geçti. PR açıldı, birleştirilmedi.
- **2026-10-31/11-01, PR #2 (G05–G08):** Katalog, üyeler, PDF; yerel Windows doğrulaması (515 passed), metinler onaylandı, merge commit `b6bd69d`.
- **2026-10-31, PR #1 (G01–G04):** Bulut oturumunda G02–G04, inceleme düzeltmeleri D1–D4 (ADR-0051, 106 onaylı metin, TC-32 bütün yönetici yolları, kural ihlalinde 200), yerel Windows doğrulaması (219 passed) ve merge commit `1a93f2d`.
- **2026-10-31, faz 4 ve öncesi:** Test planı (319 TC), plan (G01–G19, KL-1…KL-46), ADR-0026…0048, faz 3 kararları (ADR-0001…0025), faz 2 araştırmaları, faz 1 SRS. Ayrıntı git geçmişinde ve plan §8–§10'da.

## Nasıl çalıştırılır ve test edilir

- `pip install -r requirements-dev.txt`, `python manage.py migrate`, `python manage.py createsuperuser` (ilk yönetici), `python manage.py runserver` → `/giris/`.
- Testler: `python -m pytest -q` (yavaş PDF ve barkod testleri `slow` işaretli ve varsayılan koşuda dahil; yalnız onlar için `-m slow`).
- Yetki kapsamı: `coverage report --include="accounts/permissions.py,accounts/middleware.py" --fail-under=100`.
- NFR-13 kapsamı: `coverage run --branch -m pytest`, ardından `coverage report --include="*/domain.py" --fail-under=90`.
- Servis hedefi: `coverage report --include="billing/services.py,circulation/services.py" --fail-under=85`; diğer hedefler test planı §4.
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
- **Kum havuzu:** pytest geçici klasörü engellenirse `PYTEST_DEBUG_TEMPROOT` yalnız kabukta scratchpad'e yönlendirilir.
