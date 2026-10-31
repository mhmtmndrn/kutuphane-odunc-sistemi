# Durum (devir notu)

- **Güncelleme:** 2026-10-31
- **Aşama:** eng-process faz 4 (plan ve onay kapısı) sürüyor. Kararlar tamam: ADR-0026…0035 ve 16 maddelik küçük karar listesi onaylandı (plan §3). Yazılacaklar: görevler, test planı, risk kaydı, izlenebilirlik, kontroller ve onay kapısı. Plan: `docs/plans/2026-10-31-kutuphane-odunc-sistemi.md`.
- **Dal:** `feature/requirements`. Faz 4 karar dokümanları **commit'lenmedi**: SRS, mimari, veri tasarımı, plan, STATUS ve 10 ADR. Son commit `531bd9c`.

## Sıradaki adım

1. **Oturum başında sor (AskUserQuestion):** Faz 4 karar dokümanları `feature/requirements` dalına `docs: add phase 4 decisions and SRS updates` mesajıyla commit'lensin mi?
2. **Sonra:** `eng-process` skill'ini çalıştır ve faz 4'e devam et (`phases/04-plan.md`). Faz 4'te yeni karar sorulmaz; plan §3'teki kararlar uygulanır. Sırayla:
   - **Görevler (plan §4):** Bağımlılık sırasıyla yazılır. Her görevde dosyalar, arayüzler (tam imzalar), gereksinim ID'leri, testler, doğrulama komutu ve başarı çıktısı bulunur. Girdiler: [SRS](srs.md), [mimari](architecture.md) §3 ve §6, [veri tasarımı](data-design.md), [ADR'ler](decisions/), klasör yapısı [ADR-0034](decisions/0034-project-layout-flat.md). URL tam listesi görevlere yazılır (küçük karar 15).
   - **`docs/test-plan.md`:** `test-designer` subagent'ıyla yazılır. Ona SRS ve plan yolları, TDD ve ilk boş numara olarak TC-01 verilir.
   - **`docs/risk-register.md`:** Plan §6'daki R-01…R-06 taşınır; R-06 ADR-0033 ile kapatılır. Yeni riskler eklenir.
   - **İzlenebilirlik (plan §7):** 32 FR ve 13 NFR → tasarım öğesi, görev, test.
   - **Tutarlılık kontrolü (plan §8):** Bilinen bir bulgu var: architecture §3'teki `due_date` karmaşıklık satırına ADR-0028'deki 366 günlük üst sınır yazılmalı.
   - **İnşa kontrolü:** Taze bir general-purpose subagent'la yapılır.
   - **Onay kapısı:** Kod, kullanıcı planı onaylamadan yazılmaz.

## Açık sorular ve riskler

- **SRS açık soru 5:** Sunucu donanımı ve işletim sistemi belli değil; Windows ve Linux kurulumu birlikte destekleniyor (ADR-0010).
- **SRS açık soru 6, R-05:** 2 yıllık saklama süresi kurumun KVKK politikasıyla teyit edilmeli.
- **SRS açık soru 8:** KYGM Z39.50 erişimi doğrulanmadı; gerekirse kullanıcı kendisi sorar.
- **Kurulum ön koşulu:** Kurumdan SMTP gönderen hesabı alınmalı (ADR-0004).

## Nerede kaldık

- **SRS:** [docs/srs.md](srs.md), onaylandı. Faz 2, 3 ve 4 değişiklikleri işlendi. Kapsamda 32 FR (23 Must, 9 Should), 7 Won't, 13 NFR ve 32 AC var; sayım `grep` ile doğrulandı.
- **Tasarım:** [architecture.md](architecture.md) ve [data-design.md](data-design.md); faz 4 kararlarıyla güncellendi.
- **ADR'ler:** [0001–0035](decisions/), hepsi kabul edildi. Faz 1–4 karar özeti planın 3. bölümünde.
- **Araştırma:** [ISBN meta veri](research/2026-10-31-isbn-meta-veri-apileri.md), [demo veri seti](research/2026-10-31-demo-kitap-veri-seti.md).
- Henüz kod yok.

## Son güncellemeden bu yana yapılanlar

- **2026-10-31: Faz 4 kararları** (commit'lenmedi):
  - Faz 2 ve faz 3 dokümanları commit'lendi: `57d5c45`, `531bd9c`. Faz 2–3 değişiklikleri satır düzeyinde iç içe olduğu için faz 2 commit'i yalnız raporları içeriyor (plan §11).
  - Faz 3 varsayımları kapandı: (a) ADR-0001'e not eklendi, (b) architecture §10'a teyit yazıldı, (c) küçük karar 6, (d) ADR-0028.
  - Kritik kararlar:
    - Raftaki nüsha işaretleme, yeni FR-39 ve AC-32 ([0026](decisions/0026-shelf-copy-status-marking.md)).
    - "Para iadesi" FR-26'ya eklendi ve terim sabitlendi ([0027](decisions/0027-refund-audit-term.md)).
    - Açık gün kuralı ve 366 günlük sınır ([0028](decisions/0028-open-weekday-rule-shift-bound.md)).
    - Statik dosyalar Caddy ile sunulur ([0029](decisions/0029-static-files-caddy.md)).
    - Barkod testi pypdfium2 ve zxing-cpp ile yapılır ([0030](decisions/0030-barcode-decode-test.md)).
    - Yük ölçümü stdlib betiğiyle yapılır ([0031](decisions/0031-load-test-stdlib-script.md)).
    - Kartta ad yok, kayıp kart yeniden basılır ([0032](decisions/0032-member-card-content-reprint.md)).
    - Demo verisi 300 kayıtlık filtreli JSON ([0033](decisions/0033-demo-books-one-time-fetch.md)).
    - Düz kök klasör yapısı ([0034](decisions/0034-project-layout-flat.md)).
    - Kütüphane adı ayar alanı ([0035](decisions/0035-library-name-setting.md)).
  - Küçük karar listesi (16 madde) onaylandı ve plan §3'e yazıldı.
  - `tool-scout`: `pyright-lsp` eklentisi user kapsamında ve `npm i -g pyright` (1.1.414) kuruldu; diğer adaylar reddedildi (auto memory). LSP yeni oturumda yüklenir.
- **2026-10-31: Faz 3 tamamlandı.** Stack Python 3.11, Django 5.2 LTS, SQLite WAL, waitress; ADR 0001–0025 (plan §3).
- **2026-10-31: Faz 2 tamamlandı.** FR-30 Won't oldu (Open Library %52 < %60); raporlar `docs/research/` altında.
- **2026-10-31: Faz 1 tamamlandı** ve SRS onaylandı.

## Nasıl çalıştırılır ve test edilir

Henüz kod yok. Planlanan komutlar (küçük karar 11):
- Testler: `coverage run --branch -m pytest`.
- NFR-13 kapsamı: `coverage report --include="*/domain.py" --fail-under=90`.
- Yavaş PDF testleri `slow` işaretiyle ayrılır.

Yapılandırma için [architecture.md](architecture.md) §6 ve §8'e bakın.

Faz 2 ölçüm betiği depoya alınmadı (eski scratchpad'de kaldı); yöntem raporda yazılı.

## Tuzaklar

- **Kitapyurdu ISBN alanı:** Geçersiz ISBN-10'lar büyük olasılıkla "978" öneki atılmış ISBN-13'tür. Kural ADR-0008'de; AC-04 örneği `6053609322` → `9786053609322`.
- **"İade" terimi:** Yalnız kitap iadesi demektir. Para için "para iadesi" yazılır, kodda `REFUND` kullanılır (ADR-0027).
- **Windows konsolu:** `python -I`, `PYTHONIOENCODING`'i yok sayar; cp1254 konsolda Türkçe çıktı bozulur. Çıktıyı UTF-8 bir dosyaya yaz.
- **Bash aracında heredoc:** Türkçe kesme işareti (`'`) içeren uzun heredoc'lar "unexpected EOF" verdi. Dokümanları Write aracıyla yaz.
- **SQLite ve Django:** `DecimalField` SQLite'ta REAL'e düşebilir; tutarlar kuruş olarak tutulur (ADR-0016). Veritabanı ağ paylaşımına konmaz (WAL).
- **Python sürümü:** Makinede Python 3.11.9 var; Django 6.x 3.12 ve üstünü istediği için 5.2 LTS seçildi.
