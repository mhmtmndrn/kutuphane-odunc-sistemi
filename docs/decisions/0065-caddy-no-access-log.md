# ADR-0065: Caddy erişim logu tutulmaz

- **Durum:** Kabul edildi (2026-11-01)
- **Kaynak:** Kullanıcı, 2026-11-01 yerel oturumunda soru penceresinden seçti (G19 açılışı).

## Bağlam

- Üye ve kitap aramaları GET isteğidir; sorgu dizgesi üye adını ve telefonunu taşıyabilir (ör. `/uyeler/?q=…`).
- Caddy'nin erişim logu her isteğin URI'sini yazar. Bu log, saklama kuralının (FR-25, ADR-0018) dışında kalan bir kişisel veri kaydı olur; anonimleştirme görevi ona ulaşmaz (NFR-08, KVKK).
- İşlem izi zaten uygulamanın denetim kaydındadır (FR-26). Caddy'nin süreç hata logu (başlama, sertifika, bağlantı hataları) URI taşımaz.

## Değerlendirilen seçenekler

1. **Erişim logu yok** (seçildi): Caddyfile'da `log` yönergesi bulunmaz. Yalnız sürecin hata logu Windows'ta WinSW log dosyasına, Linux'ta journald'a gider.
2. **Maskeli erişim logu:** `log` yönergesi sorgu dizgesini filtreyle siler. Reddedildi: filtre yapılandırması hataya açık; yeni bir yol ya da parametre maskeden kaçabilir.
3. **Tam erişim logu:** Sorun gidermede yararlı. Reddedildi: arama sorgularındaki kişisel veriyi süresiz saklar.

## Karar

- `deploy/Caddyfile` hiçbir yerde `log` yönergesi içermez; bu, otomatik bir testle denetlenir (ADR-0066).
- Caddy'nin kendi süreç logu (stderr) WinSW'nin `roll-by-size` log dosyalarına ve journald'a gider.

## Sonuçlar

- **Olumlu:** Sunucuda arama sorgularını taşıyan bir log oluşmaz.
- **Olumsuz / riskler:** İstek düzeyinde sorun giderme için erişim logu yoktur; gerekirse geçici olarak açılır ve sonra silinir (belgede not).

## İzlenebilirlik

- **Gereksinim:** NFR-08, FR-25, FR-26. Plan G19.
- **Bağlantılı:** ADR-0005, ADR-0018, ADR-0066
