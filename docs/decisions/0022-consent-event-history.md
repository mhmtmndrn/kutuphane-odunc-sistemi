# ADR-0022: E-posta rızası olay geçmişi tablosunda tutulur

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 3, 6. tur. Kullanıcı soru penceresinden seçti.

## Bağlam

FR-03, rızanın verildiği ve geri alındığı tarihin kaydedilmesini istiyor. KVKK'ya göre açık rızanın ispatı veri sorumlusuna düşüyor. Rıza birden çok kez verilip geri alınabilir.

## Değerlendirilen seçenekler

1. **Rıza olay geçmişi tablosu** (seçildi): Her verme ve geri alma ayrı bir satırdır (tarih, işlemi yapan personel). Geçmiş eksiksiz kalır.
2. **Üyede iki tarih alanı:** FR-03'ü harfi harfine karşılar ve en basit yoldur. Ancak rıza tekrar verildiğinde eski tarihler kaybolur.

## Karar

- `consent_event` tablosu her rıza değişikliğini tutar: üye, işlem (verildi ya da geri alındı), geçerlilik tarihi, kayıt zamanı ve personel.
- Üyedeki güncel rıza durumu son olaydan türetilir. Hatırlatma sorgusunu sadeleştirmek için üye kaydında bilinçli olarak denormalize bir alan da tutulur. Bu alan olay eklemesiyle aynı işlemde güncellenir (veri tasarımı bölüm 3).
- Üye kaydında son verme ve geri alma tarihleri bu tablodan gösterilir (AC-03).

## Sonuçlar

- **Olumlu:** Rızanın ispatı için eksiksiz bir iz kalır. AC-03 sağlanır.
- **Olumsuz / riskler:**
  - Denormalize alanın tutarlılığı tek bir servis fonksiyonuna bağlıdır; testle korunur.
  - Anonimleştirmede olayların akıbeti küçük karar olarak belirlenir.

## İzlenebilirlik

- **Gereksinim:** FR-03, FR-18, FR-19, FR-25; AC-03
- **Bağlantılı:** ADR-0018
