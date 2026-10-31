# Durum (devir notu)

- **Güncelleme:** 2026-10-31
- **Aşama:** eng-process **faz 5 (uygulama) başladı**. Onay kapısı 2026-10-31'de geçildi (kullanıcı: "Temiz oturumda uygula"). Plan, test planı (319 TC) ve KL-1…KL-46 onaylı. Henüz kod yok. Plan: [docs/plans/2026-10-31-kutuphane-odunc-sistemi.md](plans/2026-10-31-kutuphane-odunc-sistemi.md) (§10 onay kaydı).
- **Dal:** Faz 4 dokümanları `feature/requirements` dalında commit'lendi; dal `main`'e `--no-ff` ile birleştirildi (ikisi de onaylı, 2026-10-31). Git remote yok.
- **Bulut kredisi (ADR-0048):** 100 $, yaklaşık 2026-11-05'te sıfırlanıyor (R-16). G01–G19 özel GitHub reposundan bulut oturumlarıyla uygulanacak.

## Sıradaki adım

`eng-process` skill'ini çalıştır, **faz 5**'e başla (`phases/05-implement.md`). Sırayla, her adım ayrıca kullanıcı onayıyla:

1. ~~Faz 4 commit'i ve `main` birleştirmesi~~ (yapıldı, 2026-10-31).
2. **Özel GitHub reposu ve push** (ADR-0048): repo oluşturma ve push dışa dönük işlemdir; onay al.
3. **Uygulama:** Görev grupları ve dallar plan §4.0'da. Sıra G01 → G08, sonra **G10 → G09 → G11** → G12 (KL-39: `Loan` modeli G10'da), sonra G13…G19.
   - Her görevde önce görevin **Testler** satırındaki TC'ler kırmızı yazılır (TDD); TC metinleri [docs/test-plan.md](test-plan.md) §6'da.
   - Görev sonu: görevin doğrulama komutu, `python -m pytest -q`, model değişikliğinde `makemigrations --check --dry-run`; commit yalnız onayla (bulut istisnası ADR-0048: görev başına commit ve kendi dalına push, onay `main`'e birleştirmede).
   - Bulut oturumu açılış istemi şablonu KL-38'de; oturum başında `python --version` → 3.11 (R-15).
   - Kritik karar çıkarsa dur ve sor.

## Açık sorular ve riskler

- **SRS açık soru 5:** Sunucu donanımı ve işletim sistemi belli değil; Windows ve Linux birlikte destekleniyor (ADR-0010).
- **SRS açık soru 6, R-05:** 2 yıllık saklama ve borçlu üyede anonimleştirmenin ertelenmesi (ADR-0045) kurumun KVKK politikasıyla teyit edilmeli.
- **SRS açık soru 8:** KYGM Z39.50 erişimi doğrulanmadı; gerekirse kullanıcı kendisi sorar.
- **Kurulum ön koşulu:** Kurumdan SMTP gönderen hesabı alınmalı (ADR-0004, R-11).
- **Riskler:** [docs/risk-register.md](risk-register.md). En önemlileri R-04, R-10 ve R-13; bulut için R-15 ve R-16.

## Nerede kaldık

- **SRS:** [docs/srs.md](srs.md), onaylı. 35 FR (24 Must, 11 Should), 7 Won't, 13 NFR, 35 AC.
- **Tasarım:** [architecture.md](architecture.md) (§3'e KL-1, KL-2, KL-22 işlendi) ve [data-design.md](data-design.md) (I6'ya ADR-0018 istisnası).
- **ADR'ler:** [0001–0048](decisions/), hepsi kabul edildi; özet plan §3. 0048 süreç kararıdır.
- **Plan:** §3 kararlar ve KL-1…KL-46; §4 görevler G01–G19 (her birinde TC listesi); §5 test planı bağlantısı; §7 izlenebilirlik (48 gereksinim → tasarım, görev, TC); §8 tutarlılık (T-01…T-24) ve §8.2 test taslağının 27 sorusunun karşılığı; §9 commit noktaları; §10 onay.
- **Test planı:** [docs/test-plan.md](test-plan.md): 319 TC (TC-01…TC-319), seviyeler, teknikler, kapsam hedefleri, giriş-çıkış ölçütleri, hata kaydı (§8, KL-46). Elle TC'ler: TC-223, TC-225…TC-234, TC-319 (faz 6).
- **Araştırma:** [ISBN meta veri](research/2026-10-31-isbn-meta-veri-apileri.md), [demo veri seti](research/2026-10-31-demo-kitap-veri-seti.md).

## Son güncellemeden bu yana yapılanlar

- **2026-10-31, 6. tur (faz 4 kapanışı, commit'lenmedi):**
  - `docs/test-plan.md` yazıldı. Taslaktaki 234 TC'nin 37'si ADR-0036…0047'ye göre revize edildi, TC-235…TC-319 eklendi. Pasifleştirme TC'leri (TC-53…56) G11'e taşındı. R-10 için TC-235 G01'de.
  - Kontrol: kapsam betiği "requirements=48 acs=35 all covered" verdi; plandaki `grep -c "{{G"` → 0.
  - Yeni KL-39…KL-46 eklendi; KL-3, KL-8, KL-10 genişletildi. Hepsi kapıda onaylandı.
  - Tutarlılık: 24 bulgu (1 Yüksek: T-01 sıralama, KL-39 ile düzeltildi; açık Kritik ya da Yüksek yok).
  - Test tasarımı taslağı kullanıcı kararıyla silindi; içeriği test planında, açık soruları plan §8.2'de.
- **2026-10-31, 5. tur:** İnşa kontrolü ayıklandı; ADR-0036…0048, FR-40…42, AC-33…35, KL-23…38 (plan §8.1).
- **2026-10-31: Faz 4 plan yazımı:** Görevler G01–G19, risk kaydı, KL-1…22, architecture ve data-design tutarlılık düzeltmeleri (plan §8, T-17…T-24).
- **2026-10-31: Faz 4 kararları** (`8c06c2b`): ADR-0026…0035, 16 maddelik küçük karar listesi. `tool-scout`: `pyright-lsp` kuruldu, diğerleri reddedildi (auto memory).
- **2026-10-31: Faz 3** (`531bd9c`): Python 3.11, Django 5.2 LTS, SQLite WAL, waitress; ADR 0001–0025.
- **2026-10-31: Faz 2** (`57d5c45`): FR-30 Won't oldu (Open Library %52 < %60).
- **2026-10-31: Faz 1** (`bfe7836`): SRS onaylandı.

## Nasıl çalıştırılır ve test edilir

Henüz kod yok. Planlanan komutlar (küçük karar 11, plan §4.0, test planı §4):

- Testler: `python -m pytest -q`; yavaş PDF ve barkod testleri `slow` işaretli.
- NFR-13 kapsamı: `coverage run --branch -m pytest`, ardından `coverage report --include="*/domain.py" --fail-under=90`.
- Diğer kapsam hedefleri (servisler %85, yetki %100, operations %80): test planı §4.
- Migration kontrolü: `python manage.py makemigrations --check --dry-run`.

Yapılandırma için [architecture.md](architecture.md) §6 ve §8'e, zorunlu ortam değişkenleri için KL-43'e bakın.

## Tuzaklar

- **Görev sırası:** G09, G10'dan sonra yapılır (KL-39); numaralar değişmedi.
- **Arka plan subagent'ları:** Sonuçları yalnız onları başlatan oturuma gelir. Büyük çıktılar geçici bir dosyaya düşer; oturum kapanmadan depoya kopyalanmaları gerekir.
- **Kitapyurdu ISBN alanı:** Geçersiz ISBN-10'lar büyük olasılıkla "978" öneki atılmış ISBN-13'tür (ADR-0008; `6053609322` → `9786053609322`).
- **"İade" terimi:** Yalnız kitap iadesi demektir. Para için "para iadesi", kodda `REFUND` (ADR-0027).
- **Windows konsolu:** `python -I`, `PYTHONIOENCODING`'i yok sayar; cp1254 konsolda Türkçe çıktı bozulur. Çıktıyı UTF-8 bir dosyaya yaz.
- **Bash aracında heredoc:** Türkçe kesme işareti (`'`) içeren uzun heredoc'lar "unexpected EOF" verdi. Dokümanları Write aracıyla yaz; toplu değişiklik için betiği dosyaya yazıp çalıştır.
- **SQLite ve Django:** `DecimalField` SQLite'ta REAL'e düşebilir; tutarlar kuruş (ADR-0016). Veritabanı ağ paylaşımına konmaz (WAL).
- **Python sürümü:** Makinede 3.11.9; Django 6.x 3.12+ istediği için 5.2 LTS.
- **Windows'ta zoneinfo:** `tzdata` gerekir (R-10, KL-18, TC-235).
