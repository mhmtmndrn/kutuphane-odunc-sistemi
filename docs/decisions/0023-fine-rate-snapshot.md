# ADR-0023: Ceza oranı ve üst sınır ödünç anında ödünç kaydına yazılır

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 3, 6. tur. Kullanıcı soru penceresinden seçti.

## Bağlam

Günlük ceza ve ödünç başına üst sınır, yöneticinin değiştirebildiği ayarlardır (FR-12, FR-23). AC-23'e göre ödünç süresi değişse bile mevcut ödünçlerin son tarihi değişmiyor. Ceza oranı için SRS bir kural tanımlamıyor.

## Değerlendirilen seçenekler

1. **Ödünç anındaki oran** (seçildi): Oran ve üst sınır ödünç kaydına yazılır. Son tarihin AC-23'teki davranışıyla tutarlıdır ve üye için öngörülebilirdir.
2. **İade anındaki güncel oran:** Şema daha basit olur. Ancak ayar değişikliği açık ödünçlerin cezasını geriye dönük olarak değiştirir.

## Karar

- Ödünç oluşturulurken o anki `daily_fine_kurus` ve `fine_cap_kurus` değerleri ödünç kaydına kopyalanır.
- İade (FR-09), kayıp/hasar (FR-15) ve geciken listesindeki birikmiş ceza (FR-20) bu değerlerle hesaplanır:
  - ceza = min(gecikme günü × günlük ceza, üst sınır)
  - gecikme günü = max(0, kapanış tarihi − son tarih)
- Bu hesap O(1) bir saf fonksiyondur.

## Sonuçlar

- **Olumlu:** Ayar değişikliği geçmişe etki etmez. Ceza hesabı tek kayıttan, yan etkisiz yapılır.
- **Olumsuz / riskler:** Ödünç tablosuna iki sütun eklenir. Uzatmada kopyanın korunup korunmayacağı küçük karar olarak belirlenir.

## İzlenebilirlik

- **Gereksinim:** FR-09, FR-12, FR-15, FR-20, FR-23; AC-23
- **Bağlantılı:** ADR-0016
