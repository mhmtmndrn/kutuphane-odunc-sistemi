# ADR-0007: Günlük görevleri uygulama içi APScheduler 3.x tetikler

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 3, 2. tur. Kullanıcı soru penceresinden seçti.

## Bağlam

Zamanlanmış işler:

- 09:00'da hatırlatma (FR-18).
- Günlük anonimleştirme (FR-25).
- Günlük yedek (FR-28).
- Haftalık şifreli dışa aktarma (ADR-0006).

Sunucu kapalıyken kaçırılan görevler sonraki çalışmada telafi edilmeli ve hatırlatma tekrar gönderilmemeli (NFR-05). Çözüm Windows ve Linux'ta aynı davranmalı.

## Değerlendirilen seçenekler

1. **Uygulama içi APScheduler 3.x** (seçildi): Tek dağıtım birimi, iki işletim sisteminde aynı davranış. Uygulama açılırken kaçırılan görevleri telafi edebilir. Ek bir bağımlılıktır; uygulama çökerse görev de durur, ama servis yöneticisi uygulamayı yeniden başlatır.
2. **OS zamanlayıcısı (Task Scheduler, cron):** Web uygulamasından bağımsız çalışır ve bağımlılık gerektirmez. İki işletim sistemi için ayrı kurulum adımları gerekir.

## Karar

- Her görev, tek başına çalıştırılabilen idempotent bir Django management command olarak yazılır.
- APScheduler 3.x `BackgroundScheduler`, bu komutların mantığını Europe/Istanbul saatine göre `CronTrigger` ile tetikler.
- Zamanlayıcı yalnız tek süreçli waitress'te başlar (ADR-0012). Testlerde ve yönetim komutlarında başlamaz.
- Telafi APScheduler'ın misfire ayarına bırakılmaz:
  - Her görev "bugün itibarıyla vadesi gelen iş" sorgusuyla çalışır.
  - Tekrarı, ödünç ve hatırlatma tipi başına benzersiz kısıtlı bir gönderim kaydı önler.
  - Uygulama açılışında son çalışma tarihi bugünden eskiyse görev bir kez hemen çalıştırılır.

## Sonuçlar

- **Olumlu:** Kurulum adımı tektir. Görev mantığı zamanlayıcıdan bağımsız olarak test edilir. Gerekirse OS zamanlayıcısına geçmek yalnız tetikleyici değişikliğidir.
- **Olumsuz / riskler:**
  - Yeni bağımlılık: APScheduler 3.x. 4.x sürümü API'yi değiştiriyor, bu yüzden 3.x sabitlenir.
  - Uygulama birden çok süreçle çalıştırılırsa görevler çift çalışır. Benzersiz kısıt çift gönderimi engeller, ama tek süreç kuralı kurulum belgesine yazılır.

## İzlenebilirlik

- **Gereksinim:** FR-18, FR-25, FR-28; NFR-05
- **Bağlantılı:** ADR-0004, ADR-0006, ADR-0012
