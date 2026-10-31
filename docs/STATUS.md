# Durum (devir notu)

- **Güncelleme:** 2026-10-31
- **Aşama:** eng-process faz 3 (tasarım) tamamlandı; sıradaki faz 4 (plan ve onay kapısı). Plan: `docs/plans/2026-10-31-kutuphane-odunc-sistemi.md`. Faz 1–3 kararları planın 3. bölümünde.
- **Dal:** `feature/requirements`. Faz 2 ve faz 3 dokümanları kullanıcı onayıyla commit'lendi (2026-10-31; plan §9 ve §11).

## Sıradaki adım

1. **Oturum başı soruları yanıtlandı (2026-10-31):** Commit'ler yapıldı. `tool-scout` taraması faz 4 başında yapılacak. Faz 3 varsayımlarından (a) ve (b) onaylandı (plan §3). (c) faz 4 karar listesine girecek, (d) faz 4'te sorulacak.
2. **Sonra:** `tool-scout` taramasını yap, `eng-process` skill'ini çalıştır ve faz 4'ten başla. Faz dosyası: `phases/04-plan.md`.
   - Girdiler: [SRS](srs.md), [mimari](architecture.md), [veri tasarımı](data-design.md), [ADR'ler](decisions/) ve planın 3. bölümündeki "Faz 4'e devreden açık noktalar".
   - Önce açık noktaları kullanıcıya sor:
     - Kritik olanlar AskUserQuestion ile sorulacak: raftaki nüshayı işaretleme ve FR-26'ya "iade" eklenmesi.
     - Küçükler tek bir karar listesinde toplanacak.
   - Ardından şunları yaz: görevler, `docs/test-plan.md` (büyük özellik olduğu için `test-designer` subagent'ı kullanılabilir), `docs/risk-register.md`, izlenebilirlik ve tutarlılık kontrolü.
   - Onay kapısı: kod, kullanıcı planı onaylamadan yazılmaz.

## Açık sorular ve riskler

- **Faz 4'e devreden açık noktalar** (plan bölüm 3):
  - Raftaki nüshayı işaretleme ve FR-26'ya "iade" eklenmesi.
  - Varsayılan ödünç süresi ve limit.
  - Statik dosyaların sunumu.
  - Kart ve etiket ölçüleri, barkod test aracı.
  - Demo veri boyutu (R-06; 500 kayıtlık alt sınır teyit edilmedi).
  - NFR-01 yük seti, waitress iş parçacığı sayısı.
- **SRS açık soru 5:** Sunucu donanımı ve işletim sistemi belli değil. Bu yüzden Windows ve Linux kurulumu birlikte destekleniyor (ADR-0010).
- **SRS açık soru 6, R-05:** 2 yıllık saklama süresi kurumun KVKK politikasıyla teyit edilmeli.
- **SRS açık soru 8:** KYGM Z39.50 erişimi doğrulanmadı. Gerekirse kullanıcı kendisi sorar.
- **Faz 4 küçük kararı:** Open Library atıf notunun yeri.
- **Kurulum ön koşulu:** Kurumdan SMTP gönderen hesabı alınmalı (ADR-0004).

## Nerede kaldık

- **SRS:** [docs/srs.md](srs.md), onaylandı. Faz 3 değişiklikleri kullanıcı onayıyla işlendi:
  - FR-04'e ISBN kuralı eklendi.
  - FR-37 eklendi (şifreli dışa aktarma) ve AC-30 yazıldı.
  - FR-38 eklendi (üye kartı PDF'i) ve AC-31 yazıldı.
  - AC-25'e senaryo eklendi; açık soru 3 ve 4 kapatıldı.
  - Sayım: kapsam içinde 31 FR (23 Must, 8 Should), 7 Won't, 13 NFR. Sayım `grep` ile doğrulandı.
- **Tasarım:** [architecture.md](architecture.md) (C4 seviye 1–3, akışlar, durum modeli, arayüz sözleşmeleri, dağıtım) ve [data-design.md](data-design.md) (şema, 3NF/BCNF, indeksler, işlemler, kritik sorgular).
- **ADR'ler:** [0001–0025](decisions/), hepsi kabul edildi. Özeti planın 3. bölümünde ve mimarinin 9. bölümünde.
- **Araştırma:** [ISBN meta veri](research/2026-10-31-isbn-meta-veri-apileri.md), [demo veri seti](research/2026-10-31-demo-kitap-veri-seti.md).
- Henüz kod yok.

## Son güncellemeden bu yana yapılanlar

- **2026-10-31: Faz 3 tamamlandı.** Yedi soru turunda kullanıcı kararları alındı (plan bölüm 3, "Faz 3 kararları"):
  - Stack: Python 3.11, Django 5.2 LTS, SQLite (WAL), waitress, sunucuda üretilen HTML ([0001](decisions/0001-python-django.md), [0002](decisions/0002-sqlite-wal.md), [0003](decisions/0003-server-rendered-html.md), [0012](decisions/0012-app-server-waitress.md), [0013](decisions/0013-django-5-2-lts.md)).
  - Altyapı: kurum SMTP, Caddy ve yerel CA ile HTTPS, APScheduler, WinSW/systemd, django-axes, reportlab, cryptography (ADR 0004, 0005, 0007, 0009, 0010, 0011, 0014).
  - Veri ve kurallar: tam sayı kuruş, FIFO ödeme dağıtımı, kaleme yönelik af, bakiye-nötr iade, ödünç anındaki ceza oranı, rıza geçmişi, arşiv sayacı, Türkçe arama normalizasyonu (ADR 0016–0023).
  - Kapsam: haftalık şifreli USB yedeği (0006), üye kartı PDF'i (0025), üretimde admin paneli yok (0024), ISBN düzeltme önerisi (0008), app sınırları (0015).
  - 16 maddelik küçük karar listesi onaylandı (plan bölüm 3).
- **2026-10-31: Faz 2 tamamlandı.** FR-30 Won't oldu (Open Library isabeti %52 < %60 eşiği), AC-29 düzeltildi, Google Books kapsam dışı kaldı. Ayrıntılar planın 3. bölümünde ve raporlarda.
- **2026-10-31 (önceki):** Faz 1 tamamlandı ve SRS onaylandı.

## Nasıl çalıştırılır ve test edilir

Henüz kod yok. Planlanan araçlar: pytest, pytest-django, `coverage --branch` (NFR-13 kapsamı `domain.py` modülleri üzerinden ölçülecek). Komutlar ve yapılandırma [architecture.md](architecture.md) bölüm 6 ve 8'de.

Faz 2 ölçüm betiği depoya alınmadı ve eski oturumun scratchpad'inde kaldı (kalıcı değil). Yöntem raporda yazılı.

## Tuzaklar

- **Kitapyurdu ISBN alanı:** Geçersiz ISBN-10'lar büyük olasılıkla "978" öneki atılmış ISBN-13'tür. Kural ADR-0008'de; AC-04 örneği `6053609322` → `9786053609322`.
- **Windows konsolu:** `python -I` modu `PYTHONIOENCODING`'i yok sayar ve konsol cp1254 olduğu için Türkçe çıktı bozulur. Çıktıyı UTF-8 bir dosyaya yaz.
- **Bash aracında heredoc:** İçinde Türkçe kesme işareti (`'`) geçen uzun heredoc'lar "unexpected EOF" hatasıyla ayrıştırılamadı. Doküman dosyalarını Write aracıyla yaz, toplu düzenlemeyi de scratchpad'deki bir Python betiğiyle yap.
- **SQLite ve Django:** `DecimalField` SQLite'ta REAL'e düşebilir; tutarlar kuruş olarak tutulur (ADR-0016). Veritabanı dosyası ağ paylaşımına konmaz (WAL).
- **Python sürümü:** Makinede Python 3.11.9 var. Django 6.x Python 3.12 ve üstünü istediği için 5.2 LTS seçildi.
