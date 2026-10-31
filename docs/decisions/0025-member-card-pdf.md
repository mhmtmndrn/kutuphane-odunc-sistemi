# ADR-0025: Üye kartı PDF'i kapsama alınır (FR-38)

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 3, 7. tur. Kullanıcı soru penceresinden seçti. SRS'e FR-38 ve AC-31 eklendi.

## Bağlam

AC-11'deki ödünç akışı, görevlinin üye kartını okutmasıyla başlıyor. SRS'te ise üye kartı basımı yoktu; FR-06 yalnız nüsha etiketlerini kapsıyordu. Kartların kaynağı belirsizdi.

## Değerlendirilen seçenekler

1. **Kart PDF'i ekle** (seçildi): Seçilen üyeler için üye numaralı Code 128 kart PDF'i üretilir. FR-06'nın reportlab altyapısı yeniden kullanılır, efor küçüktür.
2. **Kart sistem dışında:** Kapsam değişmez. AC-11 kartın var olduğunu varsayar ya da üye no elle veya aramayla girilir.

## Karar

- FR-38 (Should): Sistem, seçilen üyeler için üye no'yu Code 128 barkodla içeren ve toplu basılacak bir kart PDF'i üretir.
- Kart ölçüsü, sayfa yerleşimi ve kartta üye adının bulunup bulunmayacağı faz 4'te küçük karar olarak belirlenir.
- Etiket ve kart üretimi `catalog` ile `members` arasında paylaşılan bir PDF yardımcısını kullanır.

## Sonuçlar

- **Olumlu:** AC-11 akışı sistemin kendi çıktısıyla uçtan uca sağlanır.
- **Olumsuz / riskler:** Kartta ad basılırsa bu da kişisel veridir. Kaybolan kart için yeniden basım akışı kart yerleşimiyle birlikte faz 4'te ele alınır.

## İzlenebilirlik

- **Gereksinim:** FR-11, FR-38; AC-11, AC-31
- **Bağlantılı:** ADR-0014
