# ADR-0019: Arama için Türkçe harf düşürme ve diakritik katlama

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 3, 4. tur. Kullanıcı soru penceresinden seçti.

## Bağlam

NFR-10, Türkçe İ/i ve I/ı kurallarına uyan, büyük/küçük harf duyarsız bir arama istiyor. SQLite'ın `LOWER` ve `LIKE` işlemleri yalnız ASCII için doğru çalışıyor (ADR-0002). Open Library'den gelen demo kayıtlarının yaklaşık üçte birinde Türkçe karakter kaybı var (R-06).

## Değerlendirilen seçenekler

1. **Türkçe harf düşürme ve diakritik katlama** (seçildi): İ/i ve I/ı doğru dönüştürülür; ayrıca ş→s, ğ→g, ç→c, ö→o, ü→u, ı→i katlanır. "sefiller" araması "Şefiller"i bulur ve karakteri kaybolmuş kayıtlar da yakalanır.
2. **Yalnız Türkçe harf düşürme:** NFR-10'u tam karşılar. Ancak "sefiller" araması "Şefiller"i bulmaz.

## Karar

- `normalize_tr(text)` fonksiyonu sırasıyla şunları yapar:
  1. "İ" harfini "i", "I" harfini "ı" yapar, sonra metni küçük harfe çevirir.
  2. ı, ş, ğ, ç, ö, ü harflerini sırasıyla i, s, g, c, o, u yapar.
  3. NFKD ayrıştırmasından sonra kalan birleşik işaretleri atar (â, î, û gibi).
  4. Boşlukları teke indirir.
- Üye ve kitap tablolarında, kaydetme sırasında doldurulan bir `search_key` sütunu bulunur. Arama terimi aynı fonksiyondan geçer ve `search_key LIKE '%terim%'` ile aranır.
- Telefon için yalnız rakamlardan oluşan ayrı bir normalize sütun tutulur. Barkod ve ISBN tam eşleşmeyle aranır.
- Karmaşıklık: N satır ve ortalama anahtar uzunluğu L için tam tarama O(N·L). N = 20.000 kitapta bu birkaç milisaniye sürer; indeks gerekmez (NFR-01).

## Sonuçlar

- **Olumlu:** Arama platformdan ve veritabanı yerelinden bağımsızdır. NFR-10'un bütün örnekleri sağlanır. R-06'ya karşı dayanıklıdır.
- **Olumsuz / riskler:**
  - Az sayıda yanlış pozitif olabilir ("kır" araması "kir"i de bulur). Personel aracı olduğu için kabul edilebilir.
  - Sütun her kayıtta güncellenmelidir; bu iş model katmanında tek noktada yapılır.

## İzlenebilirlik

- **Gereksinim:** FR-01, FR-04; NFR-01, NFR-10; R-06
- **Bağlantılı:** ADR-0002
