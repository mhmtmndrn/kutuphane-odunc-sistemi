# ADR-0041: Bağı koparılmış bedel yöneticinin gerekçeli iptaliyle kapatılır

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 4, 5. tur. Kullanıcı soru penceresinden seçti (inşa kontrolü bulgusu §8.1-5).

## Bağlam

Saklama görevi ödüncün bağını koparınca (ADR-0018) `mark_found` bağlı bedeli bulamaz ve bedelin ödenmemiş kısmı borçta kalır. Af ile kapatmak mümkündü, ama af anlam olarak iptalden farklıdır ve dökümde ayrı görünür.

## Değerlendirilen seçenekler

1. **Yöneticinin gerekçeyle elle girdiği CANCELLATION** (seçildi): Yeni bir form ve servis gerekir. Dökümde "İptal" olarak görünür.
2. **Af:** Yeni ekran gerekmez, ama kayıt anlam olarak yanlış olur.

## Karar

- `billing.services.cancel_fee_manual(actor, fee: LedgerEntry, reason: str) -> LedgerEntry` yalnız yöneticiye açıktır.
- Yalnız `kind = FEE`, `loan_id IS NULL` ve ödenmemiş kısmı 0'dan büyük olan bedel iptal edilebilir. İptal, ödenmemiş kısmın tamamını kapsar.
- Hata mesajları:
  - Boş gerekçe: "İptal için gerekçe zorunlu".
  - Ödüncüne bağlı bedel: "Bu bedel ödüncüne bağlı; nüshayı Bulundu olarak işaretleyin".
  - Ödenmemiş kısmı olmayan bedel: "Bedelin ödenmemiş kısmı yok".
- CANCELLATION hareketinin `reason` alanı doldurulur. Yeni denetim eylemi `CANCELLATION` yazılır.
- Yol `/borclar/<no>/iptal/` (POST, yönetici) olur. Form, döküm ekranında yalnız yöneticiye ve yalnız uygun bedeller için görünür.
- Bu iptal para iadesine yol açmaz (ADR-0037).

## Sonuçlar

- **Olumlu:** Kayıt doğru anlamı taşır, gerekçe ve denetim izi kalır.
- **Olumsuz / riskler:** Nüshanın gerçekten bulunduğunu sistem doğrulayamaz; bunun yerine gerekçe ve denetim kaydı iz bırakır. Bir form, bir yol ve bir denetim eylemi eklenir.

## İzlenebilirlik

- **Gereksinim:** FR-16, FR-17, FR-26; AC-16, AC-26
- **Bağlantılı:** ADR-0018, ADR-0021, ADR-0037
