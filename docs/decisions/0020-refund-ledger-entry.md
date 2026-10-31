# ADR-0020: Bulunan nüshada ödenmiş bedelin iadesi sistemde hareket olarak kaydedilir

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 3, 6. tur. Kullanıcı soru penceresinden seçti.

## Bağlam

FR-16 ve AC-16'ya göre kayıp nüsha bulunduğunda bedelin ödenmemiş kısmı iptal edilir; ödenmiş kısım "yöneticinin iade kaydına bırakılır". Para etkileyen işlemler denetim kaydına yazılır (FR-26).

## Değerlendirilen seçenekler

1. **Sistemde iade hareketi** (seçildi): Sistem iade edilebilir tutarı gösterir. Yönetici iadeyi kaydeder ve kayıt denetim kaydına düşer. Para izi eksiksiz kalır.
2. **İade sistem dışında:** Sistem yalnız tutarı gösterir ve bir not düşer. Daha basit, ama kasadan çıkan para sistemde görünmez.

## Karar

- Nüsha bulunduğunda sistem bedel kaleminin ödenmemiş kısmını bir `CANCELLATION` hareketiyle iptal eder. Ödenmiş kısmı da "iade edilebilir" olarak gösterir.
- Yalnız yönetici, bu bedel kalemine bağlı bir `REFUND` hareketi girebilir. Tutarı, kalemin henüz iade edilmemiş ödenmiş kısmını aşamaz.
- `REFUND` bakiyeyi değiştirmez. Bedel ve ödeme aynı tutarda geri alınmış sayılır, bu yüzden borç hesabına girmez; yalnız kasadan çıkan parayı kaydeder.
- `REFUND` denetim kaydına yazılır.

## Sonuçlar

- **Olumlu:** Kasa hareketleri eksiksizdir. AC-16'nın iki adımı da sistemde izlenebilir.
- **Olumsuz / riskler:**
  - Borç defterinde bakiyeye girmeyen bir hareket türü olur. Bakiye sorgusu bu türü açıkça dışlamalı ve test edilmelidir.
  - FR-26'nın işlem listesine "iade" eklenmesi SRS'te bir netleştirmedir; faz 4 tutarlılık kontrolünde işlenir.

## İzlenebilirlik

- **Gereksinim:** FR-16, FR-17, FR-26; AC-16
- **Bağlantılı:** ADR-0016, ADR-0017
