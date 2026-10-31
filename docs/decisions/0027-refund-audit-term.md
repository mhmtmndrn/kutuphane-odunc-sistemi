# ADR-0027: Para iadesi denetim kaydına yazılır; "iade" terimi kitap iadesine ayrılır

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 4, 1. tur. Kullanıcı soru penceresinden seçti.

## Bağlam

ADR-0020'ye göre, bulunan kayıp nüsha için ödenmiş bedelin geri verilmesi bir `REFUND` defter hareketi olarak kaydedilir. FR-26'nın denetim kaydı listesinde ise bu işlem yoktu. Ayrıca "iade" kelimesi FR-09'da kitap iadesi anlamında kullanılıyor; iki anlam birbirine karışabilirdi.

## Değerlendirilen seçenekler

1. **"Para iadesi" olarak ekle** (seçildi): Kasadan çıkan para dahil, bütün para hareketleri denetim kaydına girer. Terim sabitlenir.
2. **Ekleme:** Defter kaydı zaten personeli ve zamanı tutuyor; para hareketleri içinde yalnız iade denetim kaydı dışında kalır.

## Karar

- FR-26 listesine "para iadesi" eklenir.
- Dokümanlarda para için "para iadesi" yazılır, kodda `REFUND` kullanılır. Yalın "iade" yalnız kitap iadesi (FR-09, `check_in`) anlamına gelir. Bu kural SRS sözlüğüne eklenir.

## Sonuçlar

- **Olumlu:** Para izi denetim kaydında eksiksiz olur; terim çakışması ortadan kalkar.
- **Olumsuz / riskler:** Yok denecek kadar az; `refund` servisine bir denetim kaydı çağrısı eklenir.

## İzlenebilirlik

- **Gereksinim:** FR-16, FR-26; AC-26
- **Bağlantılı:** ADR-0020
