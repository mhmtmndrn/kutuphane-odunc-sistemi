# ADR-0049: Kilitli hesaba giriş denemesi 429 ile, giriş şablonu ve kilit mesajıyla cevaplanır

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Kullanıcı, 2026-10-31 faz 5 oturumunda soru penceresinden seçti.

## Bağlam

- ADR-0009 hesap kilidini django-axes ile uyguluyor. Plan G02, kilitli hesabın giriş ekranında "Hesap geçici olarak kilitlendi. 15 dakika sonra yeniden deneyin." mesajını görmesini istiyor, ama durum kodunu belirtmiyor.
- django-axes kilitli isteğe varsayılan olarak 429 (Too Many Requests) ve kendi düz metin cevabını döndürür.
- Kullanıcılar yalnız kütüphane personelidir. Uygulama LAN'da, waitress arkasında çalışır; 429'u özel olarak işleyen bir ara katman yoktur.

## Değerlendirilen seçenekler

1. **429 ile aynı giriş şablonu** (seçildi): Personel aynı formu ve mesajı görür. Durum kodu anlamca doğrudur; loglarda ve testlerde kilit, hatalı parolayla gelen 200'den ayrılır. Formu 429 ile çizen küçük bir lockout callable gerekir.
2. **200 ile form ve mesaj:** `AXES_LOCKOUT_CALLABLE` formu normal sayfa gibi döndürür. Tarayıcıdaki görünüm aynıdır, ama kilit durum kodundan anlaşılmaz; testler yalnız mesaj metnine dayanır.

## Karar

- Kilitli kullanıcı adıyla gelen giriş POST'u **HTTP 429** ile cevaplanır.
- Cevabın gövdesi `templates/registration/login.html` şablonudur: giriş formu yeniden gösterilir ve form hatası olarak tam şu mesaj yer alır: "Hesap geçici olarak kilitlendi. 15 dakika sonra yeniden deneyin."
- Bu davranış `AXES_LOCKOUT_CALLABLE` ile verilen bir fonksiyonla uygulanır. axes'in varsayılan düz metin cevabı kullanıcıya gösterilmez.
- Kilitli hesapla doğru parola girilse de cevap aynıdır (TC-07, TC-08).

## Sonuçlar

- **Olumlu:**
  - Testler kilidi durum koduyla (429) ve mesajla iki yönden doğrular.
  - Loglarda kilitli denemeler hatalı parola denemelerinden ayrılır.
- **Olumsuz / riskler:**
  - axes'in callable imzası sürüme bağlıdır. `requirements.txt`'teki sabit axes sürümüne göre yazılır; sürüm yükseltmesinde TC-07 ve TC-08 bunu yakalar.

## İzlenebilirlik

- **Gereksinim:** FR-27, AC-27. Plan G02; TC-07, TC-08.
- **Bağlantılı:** ADR-0009, ADR-0050
