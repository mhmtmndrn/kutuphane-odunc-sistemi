# ADR-0031: NFR-01 standart kütüphaneyle yazılmış bir yük betiğiyle ölçülür

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 4, 2. tur. Kullanıcı soru penceresinden seçti.

## Bağlam

NFR-01, tasarım ölçeğinde (NFR-02) ve 5 eşzamanlı personelle p95 yanıt süresinin 500 ms'nin altında olmasını istiyor. Ölçüm faz 6'da yapılacak. SQLite'ın tek yazıcı kilidi ancak eşzamanlı yükte görülür.

## Değerlendirilen seçenekler

1. **Stdlib betik** (seçildi): Sunucuda çalışan, 5 iş parçacıklı bir `urllib` betiği. Yeni bağımlılık gerektirmez.
2. **Locust:** Hazır bir araç ve zengin rapor sunar, ama yeni bir bağımlılık getirir.
3. **Tek iş parçacığı:** Eşzamanlılığı ölçmez; NFR-01'i tam kanıtlamaz.

## Karar

- Veri: `load_seed_data --profile load` komutu 20.000 nüsha, 5.000 üye ve 100.000 ödünç kaydını sentetik olarak üretir.
- Betik: `scripts/loadtest.py --base-url URL --user U --password-file F --workers 5 --duration 120`.
  - Waitress'e Caddy olmadan doğrudan bağlanır (`http://127.0.0.1:<port>`). Böylece uygulama sunucusunun süresi ölçülür.
  - Her iş parçacığı kendi oturumunu açar; girişte CSRF jetonunu `http.cookiejar` ile taşır.
- Senaryo karışımı: kitap arama %40, ödünç %20, iade %20, uzatma %10, üye arama %10.
- Rapor: işlem türü başına istek sayısı, p50, p95 ve hata sayısı. Bütün türlerde p95 < 500 ms ve hata sayısı 0 ise çıkış kodu 0, değilse 1.

## Sonuçlar

- **Olumlu:** Bağımlılık eklenmez; ölçüm tekrarlanabilir ve depoda kalır.
- **Olumsuz / riskler:** Ölçüm Caddy'nin TLS yükünü içermez. LAN'da bu fark ihmal edilebilir sayılır; faz 6 raporunda not edilir.

## İzlenebilirlik

- **Gereksinim:** NFR-01, NFR-02, FR-29
- **Bağlantılı:** ADR-0002, ADR-0012
