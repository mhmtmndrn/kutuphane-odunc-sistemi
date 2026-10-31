# ADR-0010: Windows'ta servis olarak çalıştırma için WinSW, Linux'ta systemd

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 3, 3. tur. Kullanıcı soru penceresinden seçti.

## Bağlam

Uygulama ve Caddy, sunucu açıldığında kendiliğinden başlamalı ve çökerse yeniden başlamalı. Zamanlayıcı da uygulamanın içinde çalışıyor (ADR-0007). Sunucunun işletim sistemi belli değil.

## Değerlendirilen seçenekler

1. **WinSW** (seçildi): MIT lisanslı, tek exe ve XML yapılandırma, bakımı aktif. Caddy belgeleri de Windows için bunu öneriyor. İki servis aynı yöntemle kurulur.
2. **NSSM:** Kamu malı, yaygın ve basit. Son sürümü 2017'den; bakımı durmuş.

## Karar

- Windows'ta waitress ve Caddy, ayrı WinSW servisleri olarak kurulur. Çökmede yeniden başlatma açıktır.
- Linux'ta aynı iki süreç systemd unit dosyalarıyla çalışır; `Restart=on-failure` kullanılır.
- Örnek servis dosyaları depoda tutulur ve kurulum belgesinde anlatılır.

## Sonuçlar

- **Olumlu:** İki platformda da otomatik başlatma ve yeniden başlatma sağlanır. Tek süreç kuralı (ADR-0007) servis tanımında güvenceye alınır.
- **Olumsuz / riskler:** Windows'ta yeni bir dağıtım bağımlılığı (WinSW exe'si) eklenir.

## İzlenebilirlik

- **Gereksinim:** FR-18, FR-25, FR-28; NFR-05
- **Bağlantılı:** ADR-0005, ADR-0007, ADR-0012
