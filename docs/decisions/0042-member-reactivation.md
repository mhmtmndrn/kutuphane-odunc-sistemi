# ADR-0042: Pasif üye personel tarafından yeniden aktifleştirilebilir

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 4, 5. tur. Kullanıcı soru penceresinden iki soruyla seçti: önce kapsamı (inşa kontrolü bulgusu §8.1-6), sonra rolü.

## Bağlam

FR-02 yalnız pasifleştirmeyi tanımlıyordu. Geri dönen bir üye için tek yol yeni üye kaydı açmaktı. Bu da geçmişin ve borcun ikiye bölünmesi demekti.

## Değerlendirilen seçenekler

- Kapsam: **kapsamda** (seçildi) ya da kapsam dışı.
- Rol:
  1. **Bütün personel** (seçildi): Pasifleştirmeyle simetriktir.
  2. **Yalnız yönetici:** Daha sıkıdır, ama görevli masada yöneticiyi çağırmak zorunda kalır.

## Karar

- Yeni gereksinim FR-40 ve kabul ölçütü AC-33 eklenir.
- `members.services.reactivate_member(actor, member) -> None` bütün personele açıktır.
  - Anonimleştirilmiş üye için "Anonimleştirilmiş üye aktifleştirilemez" mesajıyla reddedilir.
  - Zaten aktif üye için "Üye zaten aktif" mesajıyla reddedilir.
  - Başarılı işlemde `is_active = True` ve `deactivated_on = NULL` yazılır, `MEMBER_REACTIVATED` denetim kaydı (hedef `member`) eklenir.
- Üye ayrıntısında "Aktifleştir" düğmesi yalnız pasif ve anonimleştirilmemiş üyede görünür. Yol `/uyeler/<no>/aktif/` (POST, personel) olur.
- Saklama süresi, üye yeniden pasifleştirildiğinde baştan başlar.

## Sonuçlar

- **Olumlu:** Üyenin geçmişi ve borcu tek kayıtta kalır.
- **Olumsuz / riskler:** Bir yol, bir servis ve bir denetim eylemi eklenir.

## İzlenebilirlik

- **Gereksinim:** FR-40 (yeni), FR-02, FR-25, FR-26; AC-33
- **Bağlantılı:** ADR-0018, ADR-0045
