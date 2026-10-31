# ADR-0036: Etiket ve kart için seçim: aralık girişi ve seçim kutuları

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 4, 5. tur. Kullanıcı soru penceresinden seçti.

## Bağlam

FR-06 ve FR-38 "seçilen" nüshaların ve üyelerin PDF'ini istiyor. AC-06'da birden çok kitaptan 30 nüsha seçiliyor. Seçimin hangi ekranda ve nasıl yapılacağı tanımlı değildi. Yeni eklenen nüshalar ardışık barkod alır (küçük karar 3, faz 3), yeni üyeler de ardışık üye no alır.

## Değerlendirilen seçenekler

1. **Aralık girişi ve seçim kutuları** (seçildi): Barkod ya da üye no aralığı girilir. Ayrıca kitap ayrıntısındaki nüsha satırlarında ve üye arama sonuçlarında seçim kutuları bulunur. Şema değişmez; toplu girişten sonra basım tek adımdır.
2. **Filtreli `/nushalar/` listesi:** Yeni bir liste ekranı ve filtreler gerekir; efor daha yüksektir.
3. **"Etiketi basılmamış" kuyruğu:** Hangi etiketin basıldığı izlenir, ama şemaya `copy.label_printed_at` alanı eklenir ve tekrar basım için ayrı bir yol gerekir.

## Karar

- **Etiket:** `/nushalar/etiket/` GET ile aralık formunu gösterir (başlangıç ve bitiş barkodu). POST, ya aralığı ya da seçim kutularından gelen `copy_ids` listesini kabul eder. Kitap ayrıntısında her nüsha satırında bir seçim kutusu ve "Etiket bas" düğmesi bulunur.
- **Kart:** `/uyeler/kart/` GET ile aralık formunu gösterir (başlangıç ve bitiş üye no). POST, ya aralığı ya da `member_nos` listesini kabul eder. Üye arama sonuçlarında her satırda bir seçim kutusu ve "Kart bas" düğmesi bulunur.
- Aralık kuralları, hariç tutulan durumlar ve hata mesajları plan KL-25'tedir.

## Sonuçlar

- **Olumlu:** Şema değişmez. AC-06 senaryosu tek bir aralıkla karşılanır. Seçim kutuları JS olmadan çalışır (ADR-0003).
- **Olumsuz / riskler:** Hangi etiketin basıldığı izlenmez. Tekrar basımı personel kendisi takip eder.

## İzlenebilirlik

- **Gereksinim:** FR-06, FR-38; AC-06, AC-31
- **Bağlantılı:** ADR-0014, ADR-0025, ADR-0032
