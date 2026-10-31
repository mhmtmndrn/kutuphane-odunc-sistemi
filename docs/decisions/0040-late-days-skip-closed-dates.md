# ADR-0040: Gecikme günü tek tek kapalı tarihleri saymaz

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 4, 5. tur. Kullanıcı soru penceresinden iki turda seçti. İlk turda inşa kontrolü bulgusu §8.1-4 soruldu. İkinci turda bu cevabın FR-12 ile çeliştiği söylendi ve kapsam soruldu.

## Bağlam

- FR-12, gecikme gününü takvim günü olarak tanımlıyor; faz 1 küçük karar 2 de aynı.
- Açık bir ödüncün son tarihinden sonraki bir güne kapalı tarih eklenirse (tatil ya da beklenmedik kapanış), üye o gün iade edemez ama ceza işlemeye devam eder.
- Son tarihler ödünç verilirken zaten açık bir güne kaydırılıyor (FR-07). Bu yüzden genel bir "kapalı günleri atla" kuralı haftalık kapalı günleri de etkiler.

## Değerlendirilen seçenekler

- İlk tur: son tarihi kaydırmak, gecikme sayımında kapalı günleri atlamak (seçildi) ya da cezayı aynen işletmek.
- İkinci tur, kapsam:
  1. **Yalnız tek tek kapalı tarihler** (seçildi): Sorunu çözer, FR-12'ye bir istisna ekler.
  2. **Bütün kapalı günler:** Haftalık kapalı günler de düşer. FR-12 baştan değişir ve ceza genel olarak azalır.
  3. **Takvim günü kalsın:** İlk turdaki cevabı geri alır.

## Karar

- `late_days(due_on, on, closed_dates) = max(0, (on − due_on).days − |{d ∈ closed_dates : due_on < d ≤ on}|)`.
- `closed_dates`, `closed_date` tablosundaki tarihlerin kümesidir. Haftalık kapalı günler gecikme günü sayılmaya devam eder. Haftalık kapalı bir güne denk gelen tek tarih de `closed_date` kaydı olduğu için düşülür (KL-29).
- Son tarih değişmez.
- Kural şu hesaplarda kullanılır: iade cezası, kayıp ya da hasarda birikmiş ceza, geciken listesindeki gecikme günü ve birikmiş ceza.
- OVERDUE_1 hatırlatma penceresi ve uzatmadaki "ödünç gecikmiş" kontrolü takvim gününe göre kalır.
- Karmaşıklık O(c); c, kapalı tarih sayısıdır (yılda onlarca).
- FR-12'nin metni, sözlükteki "Gecikme günü" tanımı ve AC-12 güncellenir. Faz 1 küçük karar 2'nin yerini bu ADR alır.

## Sonuçlar

- **Olumlu:** Kütüphanenin kapalı olduğu tarih için üyeye ceza yazılmaz.
- **Olumsuz / riskler:** Açık bir ödüncün cezası artık kapalı tarih kayıtlarına bağlıdır. Geçmiş bir kapalı tarih silinirse ya da eklenirse açık ödüncün cezası değişir; yazılmış ceza değişmez. Geçmiş kapalı tarihlerin silinmemesi kullanım kılavuzuna not olarak yazılır.

## İzlenebilirlik

- **Gereksinim:** FR-12, FR-15, FR-20, FR-24; AC-12
- **Bağlantılı:** ADR-0023, ADR-0028; faz 1 küçük karar 2 (yerini aldı)
