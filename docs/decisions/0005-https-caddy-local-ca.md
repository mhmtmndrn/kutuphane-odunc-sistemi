# ADR-0005: LAN içinde HTTPS için Caddy ters proxy ve yerel CA

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 3, 2. tur. Kullanıcı soru penceresinden seçti. SRS açık soru 4'ü kapatır.

## Bağlam

Personel parolası ve üye verisi LAN üzerinden taşınıyor. Kütüphanede okurlara açık bir ağ aynı ağ kesitinde olabilir. NFR-08, sistemin LAN dışından erişime kapalı olmasını istiyor. Uygulama sunucusu waitress (ADR-0012) TLS sunmuyor.

## Değerlendirilen seçenekler

1. **Caddy ve yerel CA** (seçildi): Caddy, Windows ve Linux'ta tek binary olarak çalışıyor. `tls internal` ile yerel bir CA kurup sertifikaları kendisi yeniliyor. Kök sertifika personel bilgisayarlarına (~5 makine) bir kez yüklenir.
2. **Düz HTTP:** Kurulum gerektirmiyor. Ancak parola ve oturum çerezi LAN'da açık dolaşır.
3. **CA yüklemeden kendinden imzalı sertifika:** Trafik şifreli ama tarayıcılar sürekli uyarı gösterir ve personeli uyarıyı geçmeye alıştırır.

## Karar

- Caddy, `tls internal` ile HTTPS'i sonlandırır ve istekleri yalnız `127.0.0.1` üzerinde dinleyen waitress'e iletir.
- HTTP istekleri HTTPS'e yönlendirilir.
- Django tarafında `SESSION_COOKIE_SECURE` ve `CSRF_COOKIE_SECURE` açılır; `SECURE_PROXY_SSL_HEADER` ve `ALLOWED_HOSTS` yapılandırılır.
- Caddy'nin kök sertifikasının personel bilgisayarlarına yüklenmesi kurulum belgesinde adım adım yazılır.

## Sonuçlar

- **Olumlu:** Parola ve oturum çerezi şifreli taşınır. Sertifika yenileme otomatiktir.
- **Olumsuz / riskler:**
  - Yeni bağımlılık: Caddy binary'si.
  - Yeni bir personel bilgisayarı eklendiğinde kök sertifika o makineye de yüklenmeli.
  - Caddy'nin veri dizini CA özel anahtarını içerir; yedeğe alınmalı ve erişimi kısıtlanmalıdır.

## İzlenebilirlik

- **Gereksinim:** FR-27; NFR-06, NFR-08
- **Bağlantılı:** ADR-0010, ADR-0012
