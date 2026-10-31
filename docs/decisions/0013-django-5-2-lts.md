# ADR-0013: Django sürümü 5.2 LTS

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 3, 5. tur. Kullanıcı soru penceresinden seçti.

## Bağlam

Framework Django (ADR-0001). Geliştirme makinesinde Python 3.11.9 kurulu. Sistem uzun süre az bakımla çalışacak.

## Değerlendirilen seçenekler

1. **Django 5.2 LTS** (seçildi): Nisan 2028'e kadar güvenlik desteği alıyor ve Python 3.11 ile çalışıyor.
2. **Django 6.x:** En yeni özellikleri içeriyor, ama Python 3.12 ve üstünü istiyor. Destek penceresi daha kısa.

## Karar

- Django 5.2.x kullanılır. Yama sürümleri izlenir; sürümün tam numarası bağımlılık dosyasında sabitlenir.
- Python sürümü 3.11'dir.
- Nisan 2028'den önce bir sonraki LTS'e geçiş ayrı bir ADR ile planlanır.

## Sonuçlar

- **Olumlu:** Uzun destek penceresi var. Sunucuya mevcut Python sürümü kurulabilir.
- **Olumsuz / riskler:** 2028 öncesinde bir sürüm yükseltmesi gerekecek.

## İzlenebilirlik

- **Gereksinim:** SRS bölüm 7 (çapraz platform)
- **Bağlantılı:** ADR-0001
