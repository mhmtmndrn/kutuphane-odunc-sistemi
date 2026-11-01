# ADR-0067: Faz 6 deneme projesi olarak tek Windows makinesinde yapılır; kaynak gerektiren elle TC'ler kapsam dışıdır

- **Durum:** Kabul edildi (2026-11-01)
- **Kaynak:** Kullanıcı, 2026-11-01 yerel oturumunda faz 6 açılış sorularına soru penceresinden cevap verdi; "sen karar ver" dediği adres ve kısmi TC konularında önerilen seçenekleri açıkça onayladı.

## Bağlam

- Faz 6, `docs/kurulum.md` ile bir test ortamına tam kurulum ve elle TC'leri (TC-223, TC-225…TC-234, TC-319) ister.
- Kullanıcı projeyi artık bir deneme projesi olarak görüyor: şimdilik gerçek bir kütüphanede kullanılmayacak. Kurulmuş temel (SRS, ADR'ler, kurulum belgesi) gereksiz yere değiştirilmeyecek.
- Elde ikinci bir bilgisayar, USB barkod okuyucu, etiket kağıdı, kurum SMTP hesabı ya da günlerce açık kalacak bir makine yok. Geliştirme makinesi Windows 11 Home'dur ve yalnız C: sürücüsü vardır. Firefox kurulu değildir.
- ADR-0064'e göre kod sunucuya bir `vX.Y.Z` etiketinden üretilen zip ile gelir; ilk etiket faz 6'da kullanıcı onayıyla atılır.

## Değerlendirilen seçenekler

1. **Bu Windows 11 makinesi, yalnız Windows, adres `127.0.0.2`, kaynak gerektiren TC'ler kapsam dışı** (seçildi): Hemen başlanır; ev ağına port açılmaz. LAN, donanım ve çok günlük çalışma isteyen TC'ler yapılamaz.
2. **Ayrı bir LAN makinesi ya da sanal makine:** Gerçek sunucuya daha yakın. Reddedildi: eldeki kaynaklar ve projenin deneme niteliği buna değmiyor.
3. **Makinenin LAN IP'si:** Belgedeki DHCP ve güvenlik duvarı adımları birebir izlenir. Reddedildi: ikinci bir bilgisayar olmadan ek bir şey kanıtlamaz, 80/443'ü ev ağına açar.
4. **Linux da kurulur:** Reddedildi; faz 6 süresini ikiye katlar, systemd dosyaları G19'da `systemd-analyze verify` ve canlı denemeyle kısmen doğrulandı.
5. **Etiket olarak doğrudan `v1.0.0` ya da etiketsiz HEAD zip'i:** Reddedildi; ilki sınanmamış kodu üretim etiketiyle işaretler, ikincisi ADR-0064'ten sapar.

## Karar

- **Ortam:** Geliştirme makinesi (Windows 11, Python 3.11). Yalnız Windows kurulumu yapılır; Linux tam kurulumu kapsam dışıdır.
- **Kurulumu yapan:** Kullanıcı, `docs/kurulum.md`'yi adım adım izler; Claude kontrol listesini hazırlar, kanıtları toplar ve TC'leri işler. Belgede takılınan her adım plan §12'de bulgu olarak kaydedilir.
- **Adres:** `LIBRARY_HOST`, `LIBRARY_BIND` ve `LIBRARY_ALLOWED_HOSTS` = `127.0.0.2`. DHCP rezervasyonu, güvenlik duvarı kuralı ve personel kısayolu adımları uygulanmaz.
- **Klasörler:** Uygulama `C:\Kutuphane\app`; yedek ve dışa aktarma klasörleri `C:\Kutuphane\backups` ve `C:\Kutuphane\exports` (harici disk yok).
- **Sürüm:** `main` üzerine annotated `v1.0.0-rc.1` etiketi atılır, kurulum bu etiketin ADR-0064 komutuyla üretilen zip'inden yapılır. Faz 6'da kod değişirse `v1.0.0-rc.2` atılır. `v1.0.0` yalnız faz 6 geçince atılır. Her etiketin push'u ayrıca onaylanır.
- **TC kapsamı:**
  - Tam yapılır: TC-223, TC-225, TC-231 (Chrome, Edge, Firefox; Firefox kullanıcı tarafından kurulur), TC-234, TC-319.
  - Kısmen yapılır: TC-229 (yalnız dinlenen portlar), TC-230 (Caddy `root.crt`'si CurrentUser deposuna eklenir; üç tarayıcıda uyarı çıkmadığı ve HTTP→HTTPS yönlendirmesi kontrol edilir). Eksik kısımları kapsam dışıdır.
  - Kapsam dışı (deneme projesi): TC-226, TC-227, TC-228, TC-232, TC-233. TC-233'ün telafi mantığı (ADR-0053) otomatik testlerle kapsanır.
- **Durum işareti:** `docs/test-plan.md`'de "Geçti", "Kaldı" ya da "Kapsam dışı (deneme projesi)".
- **Temizlik:** Servisler, `library-svc` hesabı, kök sertifika ve Firefox'un kalıp kalmayacağı faz 6 sonunda kullanıcıya sorulur.

## Sonuçlar

- **Olumlu:** Faz 6 dış kaynak beklemeden biter. WinSW servisleri, servis hesabı, ACL'ler, Caddy sertifikası ve tarayıcı zinciri ilk kez gerçek bir Windows kurulumunda sınanır. Kurulum belgesinin bir insan tarafından izlenebilirliği sınanır.
- **Olumsuz / riskler:**
  - Barkod okuyucu (NFR-11, R-12), etiket baskısı, gerçek SMTP (R-11), LAN erişimi, Linux kurulumu ve çok günlük çalışma sınanmamış kalır. Proje gerçek kullanıma alınırsa bu TC'ler o kurulumda yapılmalıdır.
  - Geliştirme makinesine servisler ve bir yerel hesap kurulur; temizlik ayrıca yapılmalıdır.

## İzlenebilirlik

- **Gereksinim:** NFR-01, NFR-02, NFR-04, NFR-06, NFR-08, NFR-09, FR-28, FR-29. Plan §12.
- **Bağlantılı:** ADR-0010, ADR-0053, ADR-0061, ADR-0062, ADR-0064
