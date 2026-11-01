# ADR-0070: E-posta adresi değişince rıza korunur

- **Durum:** Kabul edildi (2026-11-02)
- **Kaynak:** Faz 6, adım 4. `spec-reviewer` incelemesinin 3. sorusu. Kullanıcı soru penceresinde "Böyle kalsın, ADR'ye yaz" seçeneğini seçti.

## Bağlam

- FR-03 ve ADR-0047 yalnız e-posta adresinin silinmesini düzenliyor. Adres silinince geçerli rıza GIVEN ise otomatik bir WITHDRAWN olayı yazılıyor.
- Adresin başka bir adresle değiştirilmesi için kural yoktu. `update_member` bu durumda rızayı GIVEN bırakıyor ve yeni rıza olayı yazmıyor; hatırlatmalar yeni adrese gidiyor. Bu davranışı adsız bir test sınıyordu.

## Değerlendirilen seçenekler

1. **Rıza korunur** (seçildi): Rıza, üyenin e-postayla hatırlatma almayı kabul etmesidir; belirli bir adrese bağlı değildir. Kod değişmez, personele ek adım yüklenmez.
2. **Adres değişince rıza geri alınır:** Otomatik bir WITHDRAWN olayı yazılır, personel rızayı yeniden girer. Kod, test ve ADR gerekir; her adres düzeltmesinde fazladan bir adım olur.
3. **Karar ertelenir:** Yalnız plan §12.2'ye not düşülür.

## Karar

- `update_member` e-posta adresini boş olmayan başka bir adresle değiştirdiğinde rıza durumu değişmez ve rıza olayı yazılmaz.
- Adres silindiğinde ADR-0047'nin kuralı geçerli: geçerli durum GIVEN ise aynı işlemde WITHDRAWN yazılır.

## Sonuçlar

- **Olumlu:** Yazım hatası düzeltmesi gibi adres değişiklikleri hatırlatmaları kesmez. Rıza kuralı tek yerde kalır.
- **Olumsuz / riskler:** Adres başka bir kişiye ait bir adresle değiştirilirse hatırlatmalar o adrese gider. Adresin üyeye ait olduğunu doğrulamak personelin sorumluluğundadır.

## İzlenebilirlik

- **Gereksinim:** FR-03; AC-03
- **Test:** TC-371
- **Bağlantılı:** ADR-0022, ADR-0047
