# ADR-0038: Tohum veride kayıtların sahibi zorunlu `--actor` argümanıyla verilir

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 4, 5. tur. Kullanıcı soru penceresinden seçti (inşa kontrolü bulgusu §8.1-2).

## Bağlam

G17 personel hesabı oluşturmaz. Ama `loan.created_by`, `ledger_entry.created_by` ve `consent_event.recorded_by` alanları NOT NULL'dır.

## Değerlendirilen seçenekler

1. **Zorunlu `--actor <kullanıcı adı>`** (seçildi): Şema ve kısıtlar değişmez. Komuttan önce bir personel hesabının bulunması gerekir.
2. **Pasif bir tohum kullanıcısı:** Komut bunu kendisi oluşturur. Ama denetimde ve personel listesinde gerçek olmayan bir hesap görünür.
3. **Alanları NULL olabilir yapmak:** Gerçek veride iz zayıflar.

## Karar

- Komut biçimi: `load_seed_data --profile demo|load --actor <kullanıcı adı> [--seed 42]`.
- Kullanıcı var ve aktif olmalıdır; rolü önemsizdir. Bu koşul sağlanmazsa "Personel bulunamadı ya da pasif: <ad>" mesajıyla çıkış 1 verilir. `--actor` eksikse argparse çıkış 2 verir.
- Tohum verideki bütün `created_by`, `closed_by` ve `recorded_by` alanlarına bu personel yazılır.

## Sonuçlar

- **Olumlu:** Şema ve NOT NULL kısıtları korunur.
- **Olumsuz / riskler:** Demo kurulumunda önce `createsuperuser` çalıştırılmalıdır. Bu adım kurulum belgesine ve README'ye yazılır.

## İzlenebilirlik

- **Gereksinim:** FR-29; AC-29
- **Bağlantılı:** ADR-0031, ADR-0033
