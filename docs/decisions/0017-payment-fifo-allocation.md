# ADR-0017: Ödemeler borç kalemlerine en eski kalemden başlayarak dağıtılır (FIFO)

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 3, 4. tur. Kullanıcı soru penceresinden seçti.

## Bağlam

FR-13 kısmi ödemeyi kabul ediyor. AC-16 ise kayıp bedelinin "ödenmemiş kısmının" iptal edilmesini istiyor. Bunun için her ödemenin hangi borç kalemine düştüğü bilinmeli. SRS dağıtım kuralı tanımlamıyor.

## Değerlendirilen seçenekler

1. **Otomatik, en eski kalem önce (FIFO)** (seçildi): Personel ek bir seçim yapmaz. Kural deterministiktir ve test edilebilir.
2. **Personel kalemi seçer:** Masada esneklik sağlar. Her ödemede bir adım daha ekler ve tutarsız seçim riski taşır.
3. **Otomatik, önce cezalar sonra bedel:** Bulunan nüshada iade edilecek tutarı azaltır. Kural daha karmaşık ve sezgisel değil.

## Karar

- Bir ödeme, üyenin açık borç kalemlerine (ceza ve bedel) oluşturulma zamanı ve kimlik sırasıyla dağıtılır. Dağıtım, ayrı bir dağıtım tablosuna yazılır.
- Bir kalemin ödenmemiş kısmı, kalem tutarından kaleme yapılan dağıtımların toplamı çıkarılarak bulunur.
- Bulunan nüshada yapılan iptal (FR-16) FIFO'ya uymaz; doğrudan ilgili bedel kalemine dağıtılır.
- Affın nasıl dağıtılacağı ayrı bir kararla belirlenir.
- Karmaşıklık: üyenin açık kalem sayısı k için ödeme başına O(k) zaman ve O(k) ek satır. Tasarım ölçeğinde k birkaç kalemi geçmez.

## Sonuçlar

- **Olumlu:** AC-16 hesaplanabilir. Borç dökümü (FR-17) kalem bazında gösterilebilir.
- **Olumsuz / riskler:** Dağıtım tablosu ile hareketler arasındaki tutarlılık değişmezleri (bölüm 5, veri tasarımı) testlerle korunmalı.

## İzlenebilirlik

- **Gereksinim:** FR-13, FR-16, FR-17
- **Bağlantılı:** ADR-0016
