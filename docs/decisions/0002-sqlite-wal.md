# ADR-0002: Veritabanı olarak SQLite (WAL modu)

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 3, 1. tur. Kullanıcı soru penceresinden seçti.

## Bağlam

Tasarım ölçeği 20.000 nüsha, 5.000 üye, 100.000 ödünç ve en fazla 5 eşzamanlı personel (NFR-01, NFR-02). Hedefler:

- Günlük yedek, RPO ≤ 24 saat, RTO ≤ 1 saat (FR-28, NFR-03, NFR-04).
- Sunucunun bakımını yapacak bir veritabanı yöneticisi yok.
- Türkçe büyük/küçük harf duyarsız arama (NFR-10).

## Değerlendirilen seçenekler

1. **SQLite, WAL modu** (seçildi): Servis ve yapılandırma gerekmiyor. Online backup API ile tek dosyalık tutarlı yedek alınıyor; geri yükleme dosya kopyalamaktan ibaret. Yazmalar sıralı yapılıyor ama 5 personel için yeterli. Yerleşik Türkçe büyük/küçük harf dönüşümü yok.
2. **PostgreSQL:** Ölçek ve eşzamanlılık sınırı yok. Ancak ayrı servis kurulumu, `pg_dump`/`pg_restore` tabanlı yedek ve sürüm bakımı getiriyor. `lower()` davranışı da OS yereline bağlı.

## Karar

- Veritabanı SQLite'tır ve WAL modunda çalışır.
- Kilitlenme hatalarını önlemek için yazma işlemleri `IMMEDIATE` modda başlar. Django'nun SQLite `transaction_mode` ve `init_command` seçenekleri kullanılır.
- Yedek, Python `sqlite3` backup API'si ile alınır.
- NFR-10 için arama sütunlarının nasıl normalize edileceği veri tasarımında karara bağlanır.

## Sonuçlar

- **Olumlu:** İşletim yükü sıfıra yakın. Yedek ve geri yükleme basit ve hızlı. Geliştirme, test ve üretim ortamı aynı motoru kullanır.
- **Olumsuz / riskler:**
  - Çok sunuculu kuruluma ve yüksek yazma eşzamanlılığına geçiş kapanır. Gerekirse PostgreSQL'e taşıma Django migration'larıyla orta zorlukta yapılır.
  - Veritabanı dosyası ağ paylaşımında tutulmamalı; WAL ağ dosya sistemlerinde güvenilir değil.

## İzlenebilirlik

- **Gereksinim:** FR-28; NFR-01, NFR-02, NFR-03, NFR-04, NFR-10
- **Bağlantılı:** ADR-0001, ADR-0006, ADR-0011
