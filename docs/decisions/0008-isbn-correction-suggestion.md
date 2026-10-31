# ADR-0008: ISBN girişinde düzeltme önerisi ve normalize ISBN-13 saklama

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 3, 2. tur. Kullanıcı soru penceresinden seçti.

## Bağlam

FR-04'te ISBN isteğe bağlıdır. Faz 2 ölçümünde Kitapyurdu benzeri sitelerin ISBN-13'ü "978" önekini atarak gösterdiği görüldü; dört örneğin dördünde doğrulandı ([rapor](../research/2026-10-31-isbn-meta-veri-apileri.md)). Personel ISBN'i bu sitelerden kopyalarsa, kontrol hanesi tutmayan bir ISBN-10 girer.

## Değerlendirilen seçenekler

1. **Düzeltme öner, personel onaylasın** (seçildi): Başına "978" eklendiğinde geçerli bir ISBN-13 oluşuyorsa öneri gösterilir; personel onaylamadan kayıt olmaz. Yanlış otomatik düzeltme riski yok.
2. **Sessizce otomatik düzelt:** Daha az tıklama gerektirir, ama nadiren yanlış ISBN'i fark ettirmeden kaydedebilir.
3. **Yalnızca reddet:** En basit yol, ama personel doğru ISBN'i kendisi aramak zorunda kalır.

## Karar

- ISBN girişindeki tire ve boşluklar atılır. Kalan değer 10 ya da 13 haneli olmalıdır; ISBN-10'da son hane X olabilir.
- Geçerli bir ISBN-10 ISBN-13'e çevrilir. Saklanan değer her zaman tiresiz ISBN-13'tür.
- Kontrol hanesi tutmayan 10 haneli bir girişte:
  - "978" ile birleşen değer geçerli bir ISBN-13 ise form kaydı reddeder ve "978…" önerisini tek tıkla kabul edilebilir şekilde gösterir.
  - Geçerli değilse yalnız hata gösterilir.
- Geçersiz 13 haneli giriş reddedilir.

## Sonuçlar

- **Olumlu:** Arama tek biçim üzerinden yapılır. Hatalı kopyalama kayıt anında yakalanır.
- **Olumsuz / riskler:** Doğrulama mantığı tablo güdümlü birim testleriyle kapsanmalıdır.

## İzlenebilirlik

- **Gereksinim:** FR-04
- **Bağlantılı:** —
