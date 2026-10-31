# ADR-0035: Kütüphane adı bir ayar alanıdır

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 4, 4. tur. Kullanıcı soru penceresinden seçti.

## Bağlam

Üye kartında (ADR-0032) ve nüsha etiketinde kütüphane adı basılacak. Bu adın kaynağı tanımlı değildi.

## Değerlendirilen seçenekler

1. **Ayarlarda alan** (seçildi): Yönetici adı arayüzden değiştirir ve değişiklik denetim kaydına düşer.
2. **Ortam değişkeni:** Şema değişmez, ama adı değiştirmek için servis yapılandırmasına dokunmak gerekir.
3. **Ad basılmaz.**

## Karar

- `library_settings` tablosuna `library_name varchar(80) NOT NULL` eklenir. Boş değer kabul edilmez; migration'daki varsayılan değer "Kütüphane"dir.
- FR-23'ün ayar listesine "kütüphane adı" eklenir. Alan, diğer ayarlar gibi `update_settings` üzerinden değişir ve denetim kaydına yazılır.
- Etikette ve kartta ad 80 karakteri aşmaz; sığmazsa yazı boyutu küçültülmez, metin "…" ile kısaltılır.

## Sonuçlar

- **Olumlu:** Kurulum sonrası yeniden adlandırma kolaydır ve izlenir.
- **Olumsuz / riskler:** Şemaya bir sütun eklenir; data-design §2.1 güncellenir.

## İzlenebilirlik

- **Gereksinim:** FR-06, FR-23, FR-26, FR-38; AC-23
- **Bağlantılı:** ADR-0032
