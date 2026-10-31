# ADR-0012: Uygulama sunucusu olarak waitress

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 3, 3. tur. Kullanıcı soru penceresinden seçti.

## Bağlam

Django uygulamasını Windows ve Linux'ta aynı biçimde sunacak bir WSGI/ASGI sunucusu gerekiyor. Uygulama içi zamanlayıcının tek kopya çalışması için tek süreç gerekiyor (ADR-0007). gunicorn Windows'ta çalışmadığı için elendi.

## Değerlendirilen seçenekler

1. **waitress (WSGI)** (seçildi): Saf Python ve ZPL lisanslı. Windows ve Linux'ta aynı davranır. Tek süreçte çok iş parçacığıyla çalışır.
2. **uvicorn (ASGI):** Async desteği sunar. Bu sistemde async ihtiyacı yok ve Django ORM'de sync/async geçiş karmaşıklığı getirir.

## Karar

- waitress, tek süreç ve birden çok iş parçacığıyla yalnız `127.0.0.1` üzerinde dinler.
- Dış erişim yalnız Caddy üzerinden olur (ADR-0005).

## Sonuçlar

- **Olumlu:** Platformlar arası tek çalışma biçimi. Tek süreç, zamanlayıcının tek kopya çalışmasını sağlar.
- **Olumsuz / riskler:**
  - Tek süreçte bir çökme tüm uygulamayı durdurur; servis yöneticisi yeniden başlatır (ADR-0010).
  - SQLite yazmaları iş parçacıkları arasında sıralanır; ölçek için yeterli.

## İzlenebilirlik

- **Gereksinim:** NFR-01, NFR-05
- **Bağlantılı:** ADR-0005, ADR-0007, ADR-0010
