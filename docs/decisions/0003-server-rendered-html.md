# ADR-0003: Arayüz sunucu tarafında üretilen HTML ve az JS ile kurulur

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 3, 1. tur. Kullanıcı soru penceresinden seçti.

## Bağlam

Arayüzü yalnız personel, masaüstü tarayıcıyla ve yalnız Türkçe kullanır (NFR-09). Ödünç ve iade akışları barkod okuyucunun klavye girişiyle, en fazla 3 etkileşimde tamamlanmalı (FR-11, NFR-11).

## Değerlendirilen seçenekler

1. **Sunucuda HTML ve az vanilla JS** (seçildi): Tek kod tabanı. Django'nun oturum, CSRF ve test istemcisi doğrudan kullanılır. Okutma akışında JS yalnız odak yönetimi ve Enter ile gönderim için gerekir.
2. **SPA (React + TS) ve JSON API:** Daha zengin etkileşim sağlar. Buna karşılık iki kod tabanı, bir build zinciri ve API kimlik doğrulaması getirir. Masaüstü personel uygulamasında kazancı düşük.

## Karar

- Sayfalar Django şablonlarıyla sunucuda üretilir.
- JS bağımlılıksız vanilla JS'tir ve okutma akışının odak ve gönderim davranışıyla sınırlıdır.
- Ön yüz için ek bir kütüphane ya da build zinciri eklenmez. Eklemek yeni bir karar gerektirir.

## Sonuçlar

- **Olumlu:** Yüzey küçük. Uçtan uca testlerin çoğu Django test istemcisiyle yazılır. Dağıtılacak bir ön yüz paketi yok.
- **Olumsuz / riskler:** Her etkileşim tam sayfa isteğidir. Okutma akışında algılanan gecikme NFR-01 sınırında izlenmeli.

## İzlenebilirlik

- **Gereksinim:** FR-11; NFR-01, NFR-09, NFR-11
- **Bağlantılı:** ADR-0001
