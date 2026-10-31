# ADR-0047: Rıza olaylarının sıra kuralı

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 4, 5. tur. Kullanıcı soru penceresinden seçti (inşa kontrolü bulgusu §8.1-13).

## Bağlam

ADR-0022 rızayı olay geçmişi olarak tutuyor. Ama birkaç nokta belirsizdi: geçerli durumun hangi olaydan alınacağı, geçmiş tarihli ve tekrarlayan olayların kabul edilip edilmeyeceği, e-posta silindiğinde rızaya ne olacağı.

## Değerlendirilen seçenekler

Kullanıcı aşağıdaki kuralların bütününü seçti. Alternatif olarak yalnız `recorded_at`'e göre sıralama ve tekrarlara izin verme sunulmuştu.

## Karar

- **Geçerli durum,** `(effective_on, recorded_at, id)` değeri en büyük olan olaydır. Hiç olay yoksa rıza yoktur.
- **Gelecek tarihli olay** "Rıza tarihi gelecekte olamaz" mesajıyla reddedilir. Geçmiş tarihli olay kabul edilir.
- **Tekrarlayan olay:** Eylemi geçerli durumla aynı olan olay reddedilir. Mesajlar "Üyenin rızası zaten var" ve "Üyenin rızası zaten yok" olur.
- Her eklemeden sonra `member.has_email_consent` geçerli durumdan yeniden hesaplanır. Bu yüzden geçerli olaydan eski tarihli bir olay durumu değiştirmez.
- **E-posta silinirse:** `update_member` e-postayı NULL yapar. Geçerli durum GIVEN ise aynı işlemde otomatik bir WITHDRAWN olayı yazılır; `effective_on` bugün, `recorded_by` işlemi yapan personel olur.

## Sonuçlar

- **Olumlu:** Rıza durumu tek bir kuralla belirlenir. E-postası olmayan üyede rıza açık kalmaz.
- **Olumsuz / riskler:** Geçmiş tarihli olaylar geçmişe yazılır, ama geçerli durumu yalnız en yeni tarihli olay belirler. Bu davranış kullanım kılavuzunda açıklanır.

## İzlenebilirlik

- **Gereksinim:** FR-03, NFR-08; AC-03
- **Bağlantılı:** ADR-0022; KL-12
