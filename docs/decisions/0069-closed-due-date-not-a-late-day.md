# ADR-0069: Kapalı son tarih gecikme günü sayılmaz

- **Durum:** Kabul edildi (2026-11-02)
- **Kaynak:** Faz 6, adım 4. `spec-reviewer` incelemesinin 2. sorusu (bulgu B11, HT-02). Kullanıcı soru penceresinde "Düzelt: B11 + yeni ADR" seçeneğini seçti. TC-277'nin bu sınırı sınadığı söylendiğinde "Düzelt, TC-277 değişsin" ile kararını onayladı.

## Bağlam

- ADR-0040 tek tek kapalı tarihleri gecikme gününden düşüyor. Formül `due_on < d ≤ on` olduğu için son tarih gününün kendisi düşülmüyordu. TC-277 bu sınırı "son tarih düşülmez" diye sınıyordu.
- FR-07 son tarihi ödünç verilirken ilk açık güne kaydırıyor. Bu yüzden son tarih ancak ödünç verildikten sonra kapatılırsa kapalı bir güne denk gelebilir.
- **Örnek:** Son tarih 2026-11-16. Ödünç verildikten sonra 11-16 kapalı tarih yapılıyor. Üye 11-17'de iade ediyor. Eski formülle 1 gecikme günü, yani 5,00 TL ceza çıkıyordu. Üye son tarihte iade edemediği hâlde ceza alıyordu. Bu, ADR-0040'ın amacına ("kütüphanenin kapalı olduğu tarih için üyeye ceza yazılmaz") aykırıydı.

## Değerlendirilen seçenekler

1. **Aralığı `[due_on, on]` yapmak** (seçildi): Tek satırlık değişiklik. ADR-0040'ın amacını bütün durumlarda tutturur. TC-277'nin ilk satırının beklenen değeri 4'ten 3'e değişir.
2. **Bilinen sınırlama olarak kaydetmek:** Kod değişmez. Kullanım kılavuzuna "açık bir ödüncün son tarihini kapalı tarih yapmayın" uyarısı yazılır.
3. **Bilinçli davranış saymak:** TC-277 sınırı zaten kayıt altına alıyor. ADR-0040'a yalnız gerekçe notu eklenir.

## Karar

- `late_days(due_on, on, closed_dates) = max(0, (on − due_on).days − |{d ∈ closed_dates : due_on ≤ d ≤ on}|)`.
- `on ≤ due_on` ise sonuç 0'dır (değişmedi).
- ADR-0040'ın geri kalanı geçerli:
  - Haftalık kapalı günler gecikme günü sayılmaya devam eder.
  - Son tarih değişmez.
  - Kural iade cezası, kayıp ya da hasarda birikmiş ceza, geciken listesi ve tohum verisi hesaplarında kullanılır.
  - OVERDUE_1 hatırlatma penceresi ile uzatmadaki "ödünç gecikmiş" kontrolü takvim gününe göre kalır.
- Karmaşıklık O(c) kalır; c, kapalı tarih sayısıdır.

## Sonuçlar

- **Olumlu:** Kapalı olduğu gün için üyeye hiçbir durumda ceza yazılmaz.
- **Olumsuz / riskler:**
  - **Takvim günüyle süren kontroller:** Son tarih kapatılmışsa, ertesi gün ödünç geciken listesinde 0 gecikme günü ve 0 TL birikmiş cezayla görünür; uzatma da "ödünç gecikmiş" diye reddedilir. Aynı asimetri ADR-0040'ta son tarihten sonra kapatılan günler için zaten vardı; bu ADR kapsamı değiştirmez.
  - **Yazılmış cezalar:** Daha önce yazılmış cezalar değişmez. Değişiklik yalnız bundan sonraki hesapları etkiler.

## İzlenebilirlik

- **Gereksinim:** FR-12, FR-15, FR-20, FR-24; AC-12
- **Test:** TC-277 (ilk satır 3), TC-369, TC-370
- **Bağlantılı:** ADR-0040 (bu ADR onu tamamlar); plan §12.2 B11; test-plan §8 HT-02
