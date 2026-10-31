# ADR-0015: Alan başına Django app ve ORM'siz domain kuralları

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 3, 5. tur. Kullanıcı soru penceresinden seçti.

## Bağlam

İş kuralları (son tarih, ceza, engeller, uzatma, borç) TDD ile yazılacak ve bu modüllerde dal kapsamı en az %90 olacak (NFR-13). Yönetici işlemleri sunucu tarafında ayrılmalı (FR-22). Sistemde sekiz ayrı sorumluluk alanı var.

## Değerlendirilen seçenekler

1. **Alan başına Django app ve saf domain** (seçildi): Sınırlar açık. İş kuralları ORM'den bağımsız saf fonksiyonlar olduğu için hızlı test edilir ve kapsamları ayrı ölçülür.
2. **Tek Django app ve bir domain modülü:** Daha az dosya ve import gerektirir. Modeller tek yerde büyür ve sınırları yalnız konvansiyon korur.

## Karar

- Django app'leri ve sorumlulukları:
  - `accounts`: personel hesapları, roller, giriş.
  - `members`: üyeler ve rıza.
  - `catalog`: kitaplar, nüshalar, barkod ve etiket.
  - `circulation`: ödünç, iade, uzatma, kayıp ve hasar.
  - `billing`: borç defteri, ödeme, af, iptal.
  - `notifications`: hatırlatmalar.
  - `administration`: ayarlar, kapalı günler, denetim kaydı.
  - `operations`: yedek, dışa aktarma, anonimleştirme, zamanlayıcı, tohum veri.
- Her app'in iş kuralları ORM ve HTTP'ye bağımlı olmayan saf fonksiyonlarda durur.
- Veritabanı işlemlerini servis katmanı yapar. View'lar yalnız servisleri çağırır.
- Bağımlılık yönü ve arayüzler `docs/architecture.md` bölüm 3'te tanımlıdır. Döngüsel import yasaktır.
- NFR-13 kapsamı domain modülleri üzerinden ölçülür.

## Sonuçlar

- **Olumlu:** Kural testleri veritabanısız ve hızlı çalışır. Yetki denetimi servis sınırında tek noktada toplanır.
- **Olumsuz / riskler:**
  - Daha fazla dosya.
  - App'ler arası çağrılar servis arayüzleri üzerinden yürütülmezse sınırlar aşınır. Kod incelemesinde kontrol edilir.

## İzlenebilirlik

- **Gereksinim:** FR-22; NFR-07, NFR-13
- **Bağlantılı:** ADR-0001
