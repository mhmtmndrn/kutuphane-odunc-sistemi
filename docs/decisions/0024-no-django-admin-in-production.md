# ADR-0024: Personel arayüzünde Django admin paneli kullanılmaz

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 3, 7. tur. Kullanıcı soru penceresinden seçti.

## Bağlam

Ayar, kapalı gün ve personel ekranları (FR-21, FR-23, FR-24) için Django'nun hazır admin paneli kullanılabilirdi. Ancak yönetici işlemleri sunucu tarafında görevliye kapalı olmalı ve otomatik testle doğrulanmalı (FR-22, NFR-07). Bu işlemler denetim kaydına da yazılmalı (FR-26). Arayüz yalnız Türkçe (NFR-09).

## Değerlendirilen seçenekler

1. **Bütün ekranlar özel** (seçildi): Tek görünüm ve tek yetki yüzeyi olur. FR-22, NFR-07 ve FR-26 tek yerde test edilir. Ayar ve personel ekranları için ek efor gerektirir.
2. **Yönetici ekranları için admin paneli:** Ekranlar hazır gelir. Ancak görünüm farklı olur, ikinci bir yetki yüzeyi oluşur ve denetim kaydı için admin kancaları gerekir.

## Karar

- Bütün personel işlevleri özel view'lar ve servisler üzerinden sunulur.
- `django.contrib.admin` yalnız geliştirme ayarlarında açıktır. Üretim ayarlarında URL'ye bağlanmaz.
- Üretimde admin URL'sinin 404 döndüğü bir testle doğrulanır.

## Sonuçlar

- **Olumlu:** Yetki ve denetim kaydı tek yoldan geçer. Arayüz bütünlüklü olur.
- **Olumsuz / riskler:** Yönetici ekranları için birkaç form ve liste sayfası daha yazılır.

## İzlenebilirlik

- **Gereksinim:** FR-21, FR-22, FR-23, FR-24, FR-26; NFR-07, NFR-09
- **Bağlantılı:** ADR-0003, ADR-0015
