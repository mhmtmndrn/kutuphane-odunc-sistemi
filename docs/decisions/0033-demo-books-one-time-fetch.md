# ADR-0033: Demo kitapları bir kez çekilir, filtrelenir ve depoda JSON olarak tutulur (300 kayıt)

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 4, 3. tur. Kullanıcı soru penceresinden iki ayrı soruyla seçti. R-06'nın açık noktaları bu ADR'yle kapandı.

## Bağlam

FR-29'daki demo kitapları Open Library'den gelecek (CC0, orta güven; [rapor](../research/2026-10-31-demo-kitap-veri-seti.md)). Open Library API'si saniyede 1 istekle sınırlı ve toplu indirme için tasarlanmamış. Ölçülen kayıtların yaklaşık üçte birinde Türkçe karakter kaybı var. Bazı kayıtlarda kodlama bozulması (`¿`) ve harf düşmüş yayınevi görülüyor.

## Değerlendirilen seçenekler

- Elde etme:
  1. **Bir kerelik çekme ve depoda JSON** (seçildi): Yükleme çevrimdışı çalışır, sonucu deterministiktir ve testler ağa bağlı değildir.
  2. **Yüklemede canlı çekme:** Ağ gerektirir, yavaştır ve sonucu her seferinde değişebilir.
  3. **Yalnız sentetik veri:** Demo gerçekçi görünmez.
- Boyut ve temizlik:
  1. **300 kayıt, otomatik filtre** (seçildi).
  2. **500 kayıt, aynı filtre.**
  3. **200 kayıt, elle gözden geçirme.**

## Karar

- `scripts/fetch_demo_books.py` standart kütüphaneyle yazılır.
  - Open Library arama API'sini `language:tur isbn:978605*` sorgusuyla, sayfa sayfa ve iki istek arasında en az 1 saniye bekleyerek çağırır.
  - `User-Agent` başlığında proje adını gönderir.
  - Filtreden geçen ilk 300 kaydı `seed/books_openlibrary.json` dosyasına yazar.
- Filtre (sırayla uygulanır):
  1. Başlığı ya da yazarı boş olan kayıt atılır.
  2. Başlıkta ya da yazarda `¿`, `Ã`, `Å` veya `�` geçen kayıt atılır.
  3. Başlıkta ve yazarda hiç Türkçe harf (`çğıİöşüÇĞÖŞÜ`) geçmeyen kayıt atılır.
  4. ISBN, `catalog.domain.parse_isbn` ile geçerli bir ISBN-13 değilse kayıt atılır.
  5. Aynı ISBN tekrar ederse ilk kayıt tutulur.
- Kayıt alanları: `ol_id`, `title`, `author`, `year` (boş olabilir) ve `isbn13`. Harf düşmesi tespit edilemediği için yayınevi alınmaz.
- Dosyanın `_meta` alanında kaynak, sorgu, çekim tarihi, lisans notu ve filtre sürümü bulunur.
- `load_seed_data` yalnız bu dosyayı okur ve ağa çıkmaz. Dosyada 300'den az kayıt varsa eksik kısım sentetik kitaplarla tamamlanır ve bu durum çıktıda yazılır.

## Sonuçlar

- **Olumlu:** Demo verisi gerçekçi ve tekrarlanabilir olur; testler ağdan bağımsız kalır.
- **Olumsuz / riskler:**
  - 3. filtre, Türkçe harf içermeyen sağlam kayıtları da eler. Demo için kabul edildi.
  - JSON dosyası depoda yaklaşık 50 KB yer tutar.

## İzlenebilirlik

- **Gereksinim:** FR-29; AC-29
- **Bağlantılı:** ADR-0008, ADR-0019
