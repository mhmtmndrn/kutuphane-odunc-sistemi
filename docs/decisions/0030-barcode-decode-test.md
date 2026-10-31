# ADR-0030: Barkod okunabilirliği pypdfium2 ve zxing-cpp ile otomatik test edilir

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 4, 2. tur. Kullanıcı soru penceresinden seçti. ADR-0014'te faz 4'e bırakılan test aracı kararı bu ADR'yle verildi.

## Bağlam

AC-06 ve AC-31, üretilen PDF'teki barkod "okutulduğunda" doğru değerin okunmasını istiyor. reportlab yalnız PDF üretir; barkodun okunup okunmadığını doğrulamaz.

## Değerlendirilen seçenekler

1. **pypdfium2 ve zxing-cpp** (seçildi): PDF görüntüye çevrilir, barkodlar zxing-cpp ile çözülür ve beklenen değerlerle karşılaştırılır. pypdfium2 5.14 (BSD-3-Clause/Apache-2.0) ve zxing-cpp 3.1 (Apache-2.0), Windows cp311 için wheel olarak yayımlanıyor. Pillow zaten reportlab'ın bağımlılığı. Bu seçenek uçtan uca kanıt sağlar.
2. **Bağımlılıksız birim testi:** Çizilen Code 128 nesnesinin değeri doğrulanır, okunabilirlik yalnız elle taramayla kanıtlanır.

## Karar

- `pypdfium2` ve `zxing-cpp` yalnız `requirements-dev.txt` dosyasına, sabit sürümle eklenir; üretime girmez.
- Yardımcı: `tests/support/barcode.py: decode_pdf_barcodes(pdf: bytes, dpi: int = 300) -> list[str]`. Değerleri sayfa sırasıyla, her sayfada yukarıdan aşağı ve soldan sağa döndürür.
- Gerçek okuyucuyla elle tarama ve basılı çıktı kontrolü, faz 6'da ayrıca yapılır.

## Sonuçlar

- **Olumlu:** Etiket ve kart PDF'lerinin okunabilirliği her test koşusunda kanıtlanır.
- **Olumsuz / riskler:** Yazıcı ve kağıt farkları yazılım testinde görülmez; bu yüzden faz 6'daki elle tarama gereklidir. Bu testler yavaş olduğu için `slow` işaretiyle ayrılır.

## İzlenebilirlik

- **Gereksinim:** FR-06, FR-38; AC-06, AC-31
- **Bağlantılı:** ADR-0014, ADR-0025
