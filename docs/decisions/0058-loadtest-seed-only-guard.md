# ADR-0058: Yük betiği yalnız tohum verisi taşıyan bir veritabanında çalışır

- **Durum:** Kabul edildi (2026-11-01)
- **Kaynak:** Kullanıcı, 2026-11-01'de `feature/seed-load` (G17–G18) açılış isteminde onayladı.

## Bağlam

- ADR-0031 ve KL-17'ye göre `scripts/loadtest.py` gerçek istekler atar: ödünç verir, iade alır ve uzatır. `--db` ile verilen veritabanından üye ve nüsha seçer.
- Betik yanlışlıkla gerçek kütüphane veritabanına ve çalışan uygulamaya yöneltilirse gerçek üyeler adına ödünç ve iade kayıtları oluşur. Bu kayıtlar defteri ve geçmişi bozar ve geri alınması zordur.
- Tohum verisindeki her e-posta `uye<no>@example.invalid` biçimindedir (plan G17); gerçek bir üyenin e-postası bu alan adıyla bitmez.

## Değerlendirilen seçenekler

1. **E-posta alan adına göre koruma** (seçildi): Betik, istek atmadan önce `--db` içindeki e-postaları okur. Basit, ek şema ya da işaret gerektirmez.
2. **Veritabanında bir "tohum" işareti:** Kesin olur, ama yeni bir tablo ya da ayar alanı ve migration gerektirir.
3. **Koruma yok, yalnız belge:** İnsan hatasına açıktır.

## Karar

- Betik, `--db` veritabanını salt okunur açtıktan sonra ve hiçbir HTTP isteği atmadan önce `member` tablosunu okur.
- E-postası boş olmayan ve `@example.invalid` ile bitmeyen tek bir üye bile varsa betik stderr'e "Tohum verisi olmayan veritabanı" yazar ve çıkış 1 verir. Giriş dahil hiçbir istek atılmaz.
- E-postası boş (NULL) üyeler korumayı tetiklemez; anonimleştirilmiş üyelerin e-postası da boştur.

## Sonuçlar

- **Olumlu:** Gerçek üyesi olan bir veritabanına yöneltilen betik istek atmadan durur.
- **Olumsuz / riskler:**
  - Koruma e-postaya dayanır. Bütün üyeleri e-postasız (ya da yalnız `@example.invalid` e-postalı) olan gerçek bir veritabanı korumadan geçer; bu durumu yakalayamaz. Faz 6 ölçümü yalnız `load_seed_data --profile load` ile kurulmuş ayrı bir veritabanında yapılmalıdır.
  - `--db` ile `--base-url`'nin aynı veritabanını gösterdiği denetlenmez; ikisinin eşleşmesi ölçümü yapanın sorumluluğundadır.

## İzlenebilirlik

- **Gereksinim:** NFR-01, NFR-02. Plan G18, §11 (G17–G18 açılış kararları).
- **Bağlantılı:** ADR-0031, ADR-0057
