# ADR-0043: Personel kendi parolasını değiştirir; yöneticinin verdiği parola ilk girişte değiştirilir

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 4, 5. tur. Kullanıcı soru penceresinden seçti; iki alt sorunun ikisine de "evet" dedi (inşa kontrolü bulgusu §8.1-7).

## Bağlam

FR-21 yalnız yöneticinin parolayı sıfırlamasını tanımlıyordu. Personel kendi parolasını değiştiremiyordu. Yöneticinin belirlediği parola da sonsuza dek geçerli kalabiliyordu.

## Değerlendirilen seçenekler

1. **Kendi parolasını değiştirme ekranı ve zorunlu değişiklik bayrağı** (seçildi): Şemaya bir alan ve bir ara katman eklenir.
2. **Yalnız değiştirme ekranı:** Yöneticinin bildiği parola kullanılmaya devam edebilir.
3. **Hiçbiri:** Mevcut durum.

## Karar

- Yeni gereksinim FR-41 ve kabul ölçütü AC-34 eklenir.
- `staff_user.must_change_password bool NOT NULL DEFAULT False` alanı eklenir. `create_staff` ve `reset_password` bu alanı True yapar; `createsuperuser` False bırakır.
- `/parola/` (GET, POST; bütün personel) ekranı mevcut parolayı ve iki kez yeni parolayı ister. KL-9'daki doğrulayıcılar uygulanır.
- Başarılı değişiklikten sonra bayrak False olur ve oturum korunur (`update_session_auth_hash`). `STAFF_CHANGED` kaydı `change = "password_changed"` ile yazılır; aktör personelin kendisidir.
- `accounts.middleware.ForcePasswordChangeMiddleware`, bayrağı True olan oturumdan gelen istekleri `/parola/` adresine yönlendirir. `/parola/`, `/cikis/` ve statik dosyalar bu kuralın dışındadır.

## Sonuçlar

- **Olumlu:** Yöneticinin bildiği parola kısa süre geçerli kalır. Personel parolasını kendi değiştirebilir.
- **Olumsuz / riskler:** Bir alan, bir ara katman ve bir ekran eklenir. NFR-07 testi `/parola/` yolunu görevliye açık bir yol olarak görür.

## İzlenebilirlik

- **Gereksinim:** FR-41 (yeni), FR-21, FR-26, FR-27, NFR-06; AC-34
- **Bağlantılı:** ADR-0009
