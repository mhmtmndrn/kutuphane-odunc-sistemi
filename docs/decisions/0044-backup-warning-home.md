# ADR-0044: Başarısız ya da eskimiş günlük yedek ana sayfada uyarı verir

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 4, 5. tur. Kullanıcı soru penceresinden seçti (inşa kontrolü bulgusu §8.1-8).

## Bağlam

Dışa aktarma için ana sayfa uyarısı vardı (FR-37), ama günlük yedek (FR-28) için yoktu. Yedek sessizce başarısız olursa bu, ancak geri yükleme gerektiğinde fark edilirdi.

## Değerlendirilen seçenekler

1. **Yalnız yöneticiye, dışa aktarma uyarısıyla aynı bileşende uyarı** (seçildi).
2. **Uyarı yok:** Durum yalnız logda ve `job_run` tablosunda kalır.

## Karar

- Yeni gereksinim FR-42 ve kabul ölçütü AC-35 eklenir.
- `administration.domain.backup_warning(last_success_at: datetime | None, last_finished_failed: bool, now: datetime) -> str | None` fonksiyonu kuralları şu sırayla uygular:
  1. Son biten BACKUP çalışması FAILED ise "Son günlük yedek başarısız oldu".
  2. Hiç başarılı yedek yoksa "Günlük yedek henüz alınmadı".
  3. `now − last_success_at > 26 saat` ise "Günlük yedek 26 saatten eski". Tam 26 saat uyarı vermez.
  4. Bunların dışında uyarı yoktur.
- `last_success_at`, son SUCCESS BACKUP kaydının `finished_at` değeridir. "Son biten" çalışma, durumu SUCCESS ya da FAILED olan en son `started_at` kaydıdır.
- 26 saat, 02:00'deki günlük çalışmaya 2 saat tolerans ekler.

## Sonuçlar

- **Olumlu:** Yedek sorunu ertesi gün fark edilir.
- **Olumsuz / riskler:** Ana sayfa her yüklemede iki küçük `job_run` sorgusu yapar; `job_run(job, run_on)` indeksiyle maliyeti ihmal edilir.

## İzlenebilirlik

- **Gereksinim:** FR-42 (yeni), FR-28, NFR-03; AC-35
- **Bağlantılı:** ADR-0006, ADR-0007
