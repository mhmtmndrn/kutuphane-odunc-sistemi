# ADR-0053: Kaçan zamanlanmış görevler saatte bir de telafi edilir

- **Durum:** Kabul edildi (2026-11-01). ADR-0007'ye ektir; onun yerini almaz.
- **Kaynak:** Kullanıcı, 2026-11-01'de `feature/operations` (G14–G16) açılış isteminde onayladı.

## Bağlam

- ADR-0007'ye göre görevler (BACKUP 02:00, ANONYMIZE 02:30, REMINDERS 09:00, EXPORT pazartesi 03:00) uygulama içi APScheduler `CronTrigger`'ıyla tetiklenir. Telafi APScheduler'ın misfire ayarına bırakılmaz; plan G16'ya göre `jobs_due_for_catch_up` yalnız uygulama açılışında çalışır.
- Uygulama açıkken de tetikleme kaçabilir: sunucu 02:00'de uykudaysa ya da askıdaysa APScheduler o tetiklemeyi atlar ve uygulama yeniden başlatılmadıkça yedek o gün alınmaz. Uygulama aylarca yeniden başlatılmadan çalışabilir.
- FAILED biten bir görev (ör. yedek diski o an takılı değildi) yalnız açılışta telafi edilirse ertesi günün tetiklemesine kadar yeniden denenmez.
- APScheduler 3.x'te iş, yürütücüye verildiği anda `misfire_grace_time` denetiminden geçer. Varsayılan tolerans 1 saniyedir; tek işçili yürütücüde (G16 küçük karar 5) kuyrukta bekleyen bir iş bu denetimde düşebilir.
- Komutlar idempotenttir (architecture §6.2): yedek aynı gün yeniden alınınca dosyanın üzerine yazılır, hatırlatmanın tekrar engeli `reminder_log`'un benzersiz kısıtındadır (ADR-0039), anonimleştirme yalnız işlenmemiş kayıtları işler (ADR-0018).

## Değerlendirilen seçenekler

1. **Açılışa ek olarak saatlik telafi görevi** (seçildi): `jobs_due_for_catch_up` bir `IntervalTrigger(hours=1)` göreviyle saatte bir de çalışır ve vadesi gelen görevleri açılıştaki sırayla kuyruğa alır. Uygulama açıkken kaçan tetiklemeler ve FAILED görevler en geç bir saat içinde telafi edilir. Sürekli başarısız olan bir görev saatte bir yeniden denenir.
2. **Yalnız geniş misfire toleransı:** Cron görevlerine uzun bir `misfire_grace_time` verilir. Uyanma sonrası kaçan tetiklemenin bir kısmını kurtarır, ama FAILED görevleri yeniden denemez ve telafiyi ADR-0007'nin dışladığı misfire ayarına bırakır.
3. **Yalnız açılışta telafi (plandaki):** Ek kod yok. Uygulama açıkken kaçan tetikleme ve FAILED görev, uygulama yeniden başlatılana ya da ertesi günün tetiklemesine kadar telafi edilmez.

## Karar

- `operations.scheduler.start_scheduler()` açılışta telafiyi bir kez çalıştırır ve ayrıca `catch-up` kimlikli bir `IntervalTrigger(hours=1)` görevi ekler. İkisi de aynı fonksiyonu (`catch_up`) çağırır: son başarılı çalışmalar okunur, `jobs_due_for_catch_up` sonucundaki görevler tek seferlik `DateTrigger` ile BACKUP → ANONYMIZE → EXPORT → REMINDERS sırasıyla kuyruğa alınır.
- Cron ve telafi görevlerinin hepsine `misfire_grace_time=3600` ve `coalesce=True` verilir; kuyrukta bekleyen işler misfire denetiminde düşmez, biriken tetiklemeler tek çalışmaya iner.
- Zamanlayıcı tek işçili yürütücüyle çalışır (`ThreadPoolExecutor(max_workers=1)`, `max_instances=1`; G16 küçük karar 5). Telafi sırası böylece gerçekten korunur ve EXPORT, aynı turdaki BACKUP'ın taze yedeğini görür.
- Cron tetiklemesi ile telafinin aynı görevi iki kez çalıştırması kabul edilir; komutlar idempotent olduğu için zararsızdır.
- `jobs_due_for_catch_up(now, last_success)` imzası ve kuralları değişmez (plan G16).

## Sonuçlar

- **Olumlu:** Uyku, askı ya da geçici bir hata yüzünden kaçan görev en geç bir saat içinde çalışır; NFR-03 (24 saatlik RPO) ve NFR-05 uygulama yeniden başlatılmadan da korunur.
- **Olumsuz / riskler:**
  - Sürekli başarısız olan bir görev (ör. yedek klasörü yok) her saat loga hata yazar ve `job_run`'a bir FAILED satırı ekler. Ana sayfadaki yedek uyarısı (ADR-0044) zaten görünür; log gürültüsü kabul edildi.
  - Saatlik görev her çalışmada dört küçük `job_run` sorgusu yapar; `job_run(job, run_on)` indeksiyle maliyeti ihmal edilir.

## İzlenebilirlik

- **Gereksinim:** FR-18, FR-25, FR-28, FR-37; NFR-03, NFR-05. Plan G16, §11 (G14–G16 açılış kararları).
- **Bağlantılı:** ADR-0007, ADR-0012, ADR-0039, ADR-0044
