# Durum (devir notu)

- **Güncelleme:** 2026-11-01 (faz 5, `feature/circulation` başladı)
- **Aşama:** eng-process **faz 5**. Grup `feature/foundation` (G01–G04) PR #1 ile birleşti. Grup `feature/catalog-members` (G05–G08) **kapandı**: PR #2 birleşti (`main` = `b6bd69d`). Şu anki iş: `feature/circulation` (G10 → G09 → G11 → G12; KL-39), bulut oturumunda.
  - **G05:** `9c0d20a`: `catalog/domain.py` (`normalize_tr`, `parse_isbn`, `isbn10_to_13`).
  - **G06:** `ffc2a16`: `members` app'i: üye modeli, arama, rıza olayları, aktifleştirme, ekranlar.
  - **G07:** `e7f8d03`: kitap ve nüsha modelleri, ISBN öneri akışı, nüsha ekleme, katalog araması.
  - **G08:** `944d3ef`: `pdf/sheets.py`, nüsha etiketi ve üye kartı PDF'leri, seçim kutuları, barkod çözme testleri.
  - Sonuç (bulut, Linux, Python 3.11.18): `python -m pytest -q` → 515 passed (`slow` dahil; `-m slow` → 4 passed); `makemigrations --check --dry-run` → "No changes detected"; dal kapsamı: `*/domain.py` %100, `catalog/services.py` %100, `members/services.py` %100, `pdf/sheets.py` %100, `accounts/permissions.py` ve `accounts/middleware.py` %100; `catalog` + `members` + `pdf` toplam %99.
  - Yerel Windows (R-15, Python 3.11.9, 2026-11-01): `python -m pytest -q` → 515 passed (`-m slow` → 4 passed, barkod çözme Windows'ta da çalışıyor); `makemigrations --check --dry-run` → "No changes detected"; dal kapsamı proje toplamı %99, `*/domain.py`, `catalog/services.py`, `members/services.py`, `pdf/sheets.py`, `accounts/permissions.py`, `accounts/middleware.py` %100.
  - Test planında 101 TC "Geçti" (46 + G05–G08'in 55'i).
  - Plan: [docs/plans/2026-10-31-kutuphane-odunc-sistemi.md](plans/2026-10-31-kutuphane-odunc-sistemi.md). G05–G08 kutuları kanıtıyla işaretli; uygulama ayrıntıları ve onaylı metinler §11'de.
- **Repo:** https://github.com/mhmtmndrn/kutuphane-odunc-sistemi (özel). Dallar: `main` (`b6bd69d`), `feature/foundation` (kapandı), `feature/catalog-members` (kapandı, PR #2 birleşti), `feature/circulation` (çalışılıyor).
- **Bulut kredisi (ADR-0048):** 100 $, yaklaşık 2026-11-05'te sıfırlanıyor (R-16).
- **Bulut oturumu:** Her grup için kullanıcı yeni bir bulut oturumu açar, Claude açılış istemini hazırlar (KL-38). Oturum kritik soruyu oturumun içinde sorar; planın vermediği metinleri seçip §11'de listeler ve PR'da onaya sunar (plan §11, 2026-11-01 kararları).
  - **Tarayıcı (önerilen):** claude.ai/code; repo `mhmtmndrn/kutuphane-odunc-sistemi`, ortam **Default** (Trusted ağ; pip için PyPI gerekir).
  - **Terminal:** depo klasöründe `claude --cloud "<istem>"`; yerel commit'ler önce push edilmeli.
  - Kaynak: https://code.claude.com/docs/en/claude-code-on-the-web.

## Bu oturumda sorulan ve cevaplanan

- **G06, anonimleştirilmiş üyenin güncellenmesi:** Plan vermiyordu; KVKK saklamasının sildiği verinin geri yazılmasına yol açabilirdi. Kullanıcı önerilen seçeneği seçti: `update_member` "Anonimleştirilmiş üye güncellenemez" ile reddeder; anonim üyenin ayrıntısında düzenleme bağlantısı ve rıza formu yok. §11'e küçük karar olarak yazıldı (ADR gerekmedi).
- Kritik karar (yeni bağımlılık, şema dışı değişiklik, plandan farklı arayüz, güvenlik ödünleşimi) çıkmadı; yeni ADR yok (sıradaki numara hâlâ 0052).

## G05–G08 sapmaları ve dikkat edilecekler (ayrıntı plan §11)

- PDF metni reportlab içindeki Vera TTF yazı tipiyle yazılır; temel PDF yazı tiplerinde ş, ğ, ı, İ yok. Yeni bağımlılık yok.
- Plandaki arayüzlere ek yardımcılar: `catalog.services` `get_book`, `book_copies`, `shelf_counts`, `is_barcode`, `suggestion_message`; `pdf.sheets` `item_position`, `fit_text`; `members.domain` `validate_member_fields`, `check_consent_change`; `administration.forms.IntListField`.
- `search_key`/`phone_digits` `Member.save()`'de, `search_key` `Book.save()`'de, `status_changed_at` `Copy.save()`'de yazılır (tek nokta).
- Geçici barkod `"PENDING-"`; nüsha id'leri SQLite `AUTOINCREMENT`'ten gelir. Testler sırayı `sqlite_sequence` ile ayarlar (TC-65, TC-263).
- **G12 için:** `library_site/urls.py`'de `catalog.urls` circulation yollarından önce kalmalı; yoksa `/nushalar/etiket/` `nushalar/<str:barcode>/`'a düşer.
- Üye, kitap ve nüsha oluşturma ve güncelleme denetim kaydı yazmaz (eylem listesinde yoklar); rıza olayları kendi izidir (KL-36).
- Barkod çözen testler (TC-70, TC-71, TC-74) `slow` işaretli; bu oturumda Linux'ta hepsi koştu. Windows'ta yerel koşuda da çalışmaları beklenir (pypdfium2 ve zxing-cpp Windows wheel'leri ADR-0030'da doğrulanmıştı).

## Sıradaki adım

1. **PR #2 tamam (2026-11-01):** Yerel Windows koşusu geçti, G05–G08 metinleri değişmeden onaylandı, birleştirme onaylandı. Sonraki dalın ilk commit'i `main`'in yeni hash'ini bu nota yazar.
2. **Sonraki grup:** `feature/circulation`: **G10 → G09 → G11 → G12** (KL-39). O grubun açık noktaları açılış isteminden önce kullanıcıya sorulur; istem yeni bir bulut oturumunda verilir.
   - G11, üye ayrıntısına açık ödünçleri, bakiyeyi ve pasifleştirme yolunu (`/uyeler/<no>/pasif/`, `circulation.services.deactivate_member` → `members.services.set_inactive`) ekler.
   - Genel sıra: G01 → G08 (tamam), G10 → G09 → G11 → G12, G13…G19.
3. **Onay bekleyen küçük temizlik (önceki oturumdan):** Yerel `worktree-agent-a4c3b8e184eb5859a` dalı silinebilir; boş `.claude/worktrees/agent-a4c3b8e184eb5859a` klasörü elle silinir.

## Açık sorular ve riskler

- **SRS açık soru 5:** Sunucu donanımı ve işletim sistemi belli değil; Windows ve Linux birlikte destekleniyor (ADR-0010).
- **SRS açık soru 6, R-05:** 2 yıllık saklama ve borçlu üyede anonimleştirmenin ertelenmesi (ADR-0045) kurumun KVKK politikasıyla teyit edilmeli.
- **SRS açık soru 8:** KYGM Z39.50 erişimi doğrulanmadı.
- **Kurulum ön koşulu:** Kurumdan SMTP gönderen hesabı alınmalı (ADR-0004, R-11).
- **Etiket kağıdı ve okuyucu:** Basılı etiket ve kartın gerçek okuyucuyla taranması faz 6'da (TC-228); kağıt markasına göre `LABEL_LAYOUT` ölçüleri ayarlanabilir.
- **Riskler:** [docs/risk-register.md](risk-register.md). En önemlileri R-04, R-10 ve R-13; bulut için R-15 ve R-16.

## Nerede kaldık

- **SRS:** [docs/srs.md](srs.md), onaylı. 35 FR (24 Must, 11 Should), 7 Won't, 13 NFR, 35 AC.
- **Tasarım:** [architecture.md](architecture.md) ve [data-design.md](data-design.md).
- **ADR'ler:** [0001–0051](decisions/), hepsi kabul edildi; özet plan §3.
- **Plan:** §3 kararlar ve KL-1…KL-46; §4 görevler G01–G19; §7 izlenebilirlik; §8 tutarlılık; §11 sapmalar ve onaylı metinler.
- **Test planı:** [docs/test-plan.md](test-plan.md): 319 TC; 101'i "Geçti". Elle TC'ler: TC-223, TC-225…TC-234, TC-319 (faz 6).
- **Araştırma:** [ISBN meta veri](research/2026-10-31-isbn-meta-veri-apileri.md), [demo veri seti](research/2026-10-31-demo-kitap-veri-seti.md).

## Geçmiş (özet)

- **2026-10-31, `feature/catalog-members` bulut oturumu:** İlk commit `docs:` (STATUS ve §11'e 2026-11-01 kullanıcı kararları), ardından G05–G08 görev başına TDD ve `feat:` commit'i, her biri push edildi. Ekranlar geliştirme sunucusunda tarayıcıyla açılıp göz kontrolünden geçti (üye arama ve ayrıntı, kitap formu ve ISBN önerisi, kitap ayrıntısı, barkod araması, etiket ve kart PDF'i).
- **2026-10-31, PR #1 (G01–G04):** Bulut oturumunda G02–G04, inceleme düzeltmeleri D1–D4 (ADR-0051, 106 onaylı metin, TC-32 bütün yönetici yolları, kural ihlalinde 200), yerel Windows doğrulaması (219 passed) ve merge commit `1a93f2d`.
- **2026-10-31, faz 4 ve öncesi:** Test planı (319 TC), plan (G01–G19, KL-1…KL-46), ADR-0026…0048, faz 3 kararları (ADR-0001…0025), faz 2 araştırmaları, faz 1 SRS. Ayrıntı git geçmişinde ve plan §8–§10'da.

## Nasıl çalıştırılır ve test edilir

- `pip install -r requirements-dev.txt`, `python manage.py migrate`, `python manage.py createsuperuser` (ilk yönetici), `python manage.py runserver` → `/giris/`.
- Testler: `python -m pytest -q` (yavaş PDF ve barkod testleri `slow` işaretli ve varsayılan koşuda dahil; yalnız onlar için `-m slow`).
- Yetki kapsamı: `coverage report --include="accounts/permissions.py,accounts/middleware.py" --fail-under=100`.
- NFR-13 kapsamı: `coverage run --branch -m pytest`, ardından `coverage report --include="*/domain.py" --fail-under=90`.
- Diğer hedefler (servisler %85, `pdf/sheets.py` satır %80, operations %80): test planı §4.
- Migration kontrolü: `python manage.py makemigrations --check --dry-run`.

## Tuzaklar

- **Görev sırası:** G09, G10'dan sonra yapılır (KL-39); numaralar değişmedi.
- **Python sürümü:** Yerelde 3.11.9, bulutta 3.11.18; Django 6.x 3.12+ istediği için 5.2 LTS (ADR-0013). Bulut imajındaki varsayılan `python` 3.13'tür; sanal ortam `/usr/bin/python3.11` ile kurulur.
- **Arka plan subagent'ları:** Sonuçları yalnız onları başlatan oturuma gelir; büyük çıktılar oturum kapanmadan depoya kopyalanmalı.
- **Kitapyurdu ISBN alanı:** Geçersiz ISBN-10'lar büyük olasılıkla "978" öneki atılmış ISBN-13'tür (ADR-0008; `6053609322` → `9786053609322`).
- **"İade" terimi:** Yalnız kitap iadesi demektir. Para için "para iadesi", kodda `REFUND` (ADR-0027).
- **Windows konsolu:** `python -I`, `PYTHONIOENCODING`'i yok sayar; cp1254 konsolda Türkçe çıktı bozulur. Çıktıyı UTF-8 bir dosyaya yaz.
- **Bash aracında heredoc:** Türkçe kesme işareti içeren uzun heredoc'lar "unexpected EOF" verebilir; dokümanları Write aracıyla ya da dosyaya yazılmış betikle değiştir.
- **SQLite ve Django:** Tutarlar kuruş (ADR-0016). Veritabanı ağ paylaşımına konmaz (WAL). Django'nun SQLite `AutoField`'ı `AUTOINCREMENT`'tir; nüsha barkodu buna dayanır.
- **Windows'ta zoneinfo:** `tzdata` gerekir (R-10, KL-18, TC-235).
- **django-axes ve test istemcisi:** `client.login()` yerine `client.force_login()`; giriş akışını sınayan testler `/giris/`e POST eder.
- **Zaman sabitleme:** `FrozenClock` `django.utils.timezone.now`'ı patch'ler; model alanının `default=timezone.now`'ı patch'i görmez (fonksiyon import anında bağlanır). Zamanı testte sabitlenecek alanlar `save()` içinde `timezone.now()` çağırır (`Copy.status_changed_at`). "Bugün" için `administration.clock.today` `monkeypatch` edilir.
- **Boş POST:** `Form(request.POST or None)` boş POST'ta formu bağlamaz; boş isteğin hata vermesi gereken formlarda `request.POST if request.method == "POST" else None` kullan (G08 seçim formları).
- **Kum havuzu:** pytest geçici klasörü engellenirse `PYTEST_DEBUG_TEMPROOT` yalnız kabukta scratchpad'e yönlendirilir.
