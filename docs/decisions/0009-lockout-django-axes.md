# ADR-0009: Hesap kilidi django-axes ile uygulanır

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 3, 3. tur. Kullanıcı soru penceresinden seçti.
- **Ek kararlar:** ADR-0049 (kilitli hesaba cevap), ADR-0050 (kilit süresi uzamaz).

## Bağlam

FR-27, 5 ardışık hatalı denemede hesabın geçici olarak kilitlenmesini istiyor. Kilit süresi küçük karar 9'a göre 15 dakika. Django'da bu davranış yerleşik değil.

## Değerlendirilen seçenekler

1. **django-axes** (seçildi): Jazzband projesi, MIT lisanslı, bakımı aktif. Kullanıcı adına göre kilit, başarılı girişte sayacın sıfırlanması ve süre ayarı hazır.
2. **Özel kod:** Bağımlılık gerektirmez, ~80 satır ve testleri. Güvenlik açısından kritik kodu kendimiz taşırız.

## Karar

django-axes şu ayarlarla kullanılır:

- `AXES_FAILURE_LIMIT = 5`
- `AXES_COOLOFF_TIME = 15 dakika`
- `AXES_LOCKOUT_PARAMETERS = ["username"]`
- `AXES_RESET_ON_SUCCESS = True`

AC-27 bu yapılandırmaya karşı otomatik testle doğrulanır. Yönetici kilidi elle kaldırabilir.

## Sonuçlar

- **Olumlu:** Kilit mantığı denenmiş bir kütüphaneden gelir.
- **Olumsuz / riskler:**
  - Yeni bağımlılık ve ek tablolar.
  - Kullanıcı adına göre kilit, bir saldırganın hesabı kasıtlı olarak kilitlemesine izin verir. LAN içinde ve personel kullanımında bu kabul edilebilir bir risktir.

## İzlenebilirlik

- **Gereksinim:** FR-27
- **Bağlantılı:** ADR-0001
