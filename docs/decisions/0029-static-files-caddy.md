# ADR-0029: Statik dosyalar üretimde Caddy file_server ile sunulur

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 4, 1. tur. Kullanıcı soru penceresinden seçti.

## Bağlam

Django üretimde (`DEBUG=False`) statik dosya sunmaz. Caddy zaten ters vekil olarak çalışıyor (ADR-0005).

## Değerlendirilen seçenekler

1. **Caddy file_server** (seçildi): `collectstatic` dosyaları bir klasöre yazar, Caddy de `/static/` yolunu doğrudan sunar. Yeni bağımlılık gerektirmez.
2. **WhiteNoise:** Statik dosyaları Django süreci sunar. Caddy yapılandırması sade kalır, ama yeni bir bağımlılık eklenir.

## Karar

- `STATIC_ROOT` değeri `LIBRARY_STATIC_ROOT` ortam değişkeninden okunur.
- `deploy/Caddyfile` içinde `handle_path /static/*` bloğu `root * {$LIBRARY_STATIC_ROOT}` ve `file_server` ile tanımlanır; diğer yollar waitress'e aktarılır.
- Geliştirmede statik dosyaları `runserver` sunar.
- Kurulum belgesine `collectstatic` adımı ve Caddy'nin klasörü okuma izni eklenir.

## Sonuçlar

- **Olumlu:** Bağımlılık eklenmez; statik istekler Python sürecine ulaşmaz.
- **Olumsuz / riskler:** Caddy ve uygulama yapılandırması aynı klasör yolunda anlaşmalıdır. Kurulum duman testinde bir CSS dosyasının 200 döndüğü kontrol edilir.

## İzlenebilirlik

- **Gereksinim:** NFR-01, NFR-09
- **Bağlantılı:** ADR-0005, ADR-0012
