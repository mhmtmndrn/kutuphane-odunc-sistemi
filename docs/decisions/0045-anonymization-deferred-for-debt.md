# ADR-0045: Borcu olan üyenin anonimleştirilmesi borç kapanana dek ertelenir

- **Durum:** Kabul edildi (2026-10-31). Hukuki teyit bekliyor (SRS açık soru 6).
- **Kaynak:** Faz 4, 5. tur. Kullanıcı soru penceresinden seçti (inşa kontrolü bulgusu §8.1-10).

## Bağlam

FR-25, saklama süresi dolan pasif üyeyi anonimleştiriyor. Borç defteri üyeye bağlı kalır, ama anonim bir üyenin borcu tahsil edilemez, çünkü kim olduğu bilinmez. Borç tahsili için kişisel veriyi daha uzun tutmanın hukuki dayanağı kurumca teyit edilmelidir.

## Değerlendirilen seçenekler

1. **Borç kapanana dek ertelemek** (seçildi): Tahsil imkânı korunur.
2. **Yine de anonimleştirmek:** Borç fiilen tahsil edilemez hale gelir.
3. **Anonimleştirip borcu otomatik olarak affetmek:** Gelir kaybı olur ve aktörü olmayan bir af yazılır.

## Karar

- Saklama süresi dolan bir üyenin bakiyesi 0'dan büyükse anonimleştirme atlanır ve `deferred` sayısına eklenir.
- Borç kapandıktan sonraki ilk görev çalışmasında üye anonimleştirilir.
- Yöneticiye `/uyeler/saklama/` listesi sunulur. Listede bekleyen her üye "borç nedeniyle bekliyor" etiketiyle görünür (KL-34).
- Ödünçlerin üye bağının koparılması (ADR-0018) bu ertelemeden bağımsız olarak devam eder.
- Hukuki teyit, SRS açık soru 6'ya eklenir ve KL'de not edilir.

## Sonuçlar

- **Olumlu:** Borç tahsili mümkün kalır. Bekleyen üyeler yöneticiye görünür.
- **Olumsuz / riskler:** Kişisel veri saklama süresinden uzun tutulabilir. Kurum teyit etmezse bu karar yeniden ele alınır.

## İzlenebilirlik

- **Gereksinim:** FR-25, NFR-08; AC-25
- **Bağlantılı:** ADR-0018, ADR-0042
