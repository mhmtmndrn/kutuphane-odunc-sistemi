# ADR-0060: Kurulum belgesi ortak bir gövde ve iki eşit ayrıntıda platform bölümünden oluşur

- **Durum:** Kabul edildi (2026-11-01)
- **Kaynak:** Kullanıcı, 2026-11-01 yerel oturumunda soru penceresinden seçti (G19 açılışı).

## Bağlam

- Sunucunun işletim sistemi belli değil (SRS açık soru 5); Windows ve Linux birlikte destekleniyor (ADR-0010).
- Kurulum adımlarının çoğu iki platformda aynıdır: ortam değişkenleri, `migrate`, `collectstatic`, ilk yönetici, kök sertifikanın personel bilgisayarlarına yüklenmesi, yedek ve geri yükleme yordamı, KVKK notları. Servis kaydı, klasör izinleri, güvenlik duvarı ve yollar ise platforma özgüdür.
- Plan G19, `docs/kurulum.md` adında tek bir belge öngörüyor; belgenin yapısını vermiyor.

## Değerlendirilen seçenekler

1. **Ortak gövde ve iki eşit platform bölümü** (seçildi): Ortak adımlar bir kez yazılır; Windows ve Linux bölümleri aynı ayrıntıdadır. Ortak adım değişince tek yer güncellenir.
2. **Windows ayrıntılı, Linux kısa:** Kütüphanenin büyük olasılıkla Windows kullanacağı varsayımına dayanır. Reddedildi: işletim sistemi belli değil ve Linux kurulumu da desteklenen bir yol (ADR-0010); kısa bölüm eksik adım bırakır.
3. **İki ayrı belge:** Her platform kendi baştan sona belgesini alır. Reddedildi: ortak adımlar iki yerde yazılır ve zamanla birbirinden kayar.

## Karar

- `docs/kurulum.md` önce ortak gövdeyi (ön koşullar, klasör düzeni, ortam değişkenleri, ortak kurulum adımları, güncelleme, yedek ve geri yükleme, KVKK notları) verir.
- Platforma özgü adımlar "Windows" ve "Linux" adlı iki bölümde, aynı alt başlıklarla ve eşit ayrıntıda yazılır: hesap, klasörler ve izinler, Python ve sanal ortam, Caddy, servisler, güvenlik duvarı, komutların elle çalıştırılması.
- Ortak gövde platforma özgü bir adıma geldiğinde ilgili bölüme bağlantı verir; aynı adım iki yerde yazılmaz.

## Sonuçlar

- **Olumlu:** Ortak adım tek yerde durur; iki platform aynı ayrıntıda belgelenir.
- **Olumsuz / riskler:** Okur ortak gövde ile platform bölümü arasında gidip gelir. Yalnız tek platformda denenen bir adım (faz 6) öbür platformda doğrulanmamış kalabilir.

## İzlenebilirlik

- **Gereksinim:** FR-28, NFR-04; AC-28. Plan G19.
- **Bağlantılı:** ADR-0010, ADR-0064
