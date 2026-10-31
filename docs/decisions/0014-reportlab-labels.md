# ADR-0014: Etiket PDF'i ve Code 128 barkodu için reportlab

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 3, 5. tur. Kullanıcı soru penceresinden seçti.

## Bağlam

FR-06, A4 sayfa başına 3×8 = 24 etiketten oluşan bir PDF istiyor. Etiketteki barkod Code 128 ve 8 haneli (FR-05). AC-06'ya göre basılan barkod okutulduğunda doğru kod okunmalı.

## Değerlendirilen seçenekler

1. **reportlab** (seçildi): BSD lisanslı. Code 128 yerleşik geliyor. Tek bağımlılık ve olgun bir proje. API'si alçak seviyeli.
2. **fpdf2 + python-barcode:** PDF API'si daha basit. İki bağımlılık gerekiyor ve fpdf2 LGPL-3.0 lisanslı.

## Karar

- Etiket PDF'i reportlab ile üretilir. Barkod reportlab'in Code 128 sınıfıyla çizilir.
- Etiket yerleşimi (kenar boşlukları, etiket boyu) parametrelerle tanımlanır. Değerler faz 4'te belirlenir.
- Okunabilirlik, üretilen PDF'teki barkodun bir çözücüyle okunmasıyla test edilir. Test aracı faz 4'te belirlenir.

## Sonuçlar

- **Olumlu:** Tek bağımlılık ve izin verici lisans.
- **Olumsuz / riskler:**
  - Yerleşim kodu alçak seviyeli.
  - Etiket kağıdı markasına göre ölçülerin ayarlanması gerekebilir.

## İzlenebilirlik

- **Gereksinim:** FR-05, FR-06
- **Bağlantılı:** ADR-0001
