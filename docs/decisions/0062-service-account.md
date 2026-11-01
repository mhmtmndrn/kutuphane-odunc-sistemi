# ADR-0062: Servisler ayrı bir yerel hesapla çalışır

- **Durum:** Kabul edildi (2026-11-01)
- **Kaynak:** Kullanıcı, 2026-11-01 yerel oturumunda soru penceresinden seçti (G19 açılışı).

## Bağlam

- Uygulama ve Caddy servis olarak çalışır (ADR-0010). Mimari §8, Caddy'nin CA özel anahtarının ve dışa aktarma parola dosyasının yalnız servis hesabının okuyabileceği izinlerle tutulmasını istiyor; ama servis hesabını tanımlamıyor.
- Veritabanı üye kişisel verisi taşır (NFR-08). Ortam değişkenleri `LIBRARY_SECRET_KEY` ve SMTP parolasını içerir.
- WinSW 2.x, servisi `<serviceaccount>` öğesindeki bir yerel kullanıcıyla kurabilir (ADR-0063).

## Değerlendirilen seçenekler

1. **Ayrı yerel hesap** (seçildi): Windows'ta `library-svc` yerel kullanıcısı, Linux'ta `library` sistem kullanıcısı. Hesabın yetkisi yalnız kendi klasörleridir; hesap ele geçirilse de sistemin geri kalanı korunur.
2. **Windows sanal hesabı (`NT SERVICE\…`):** Parola gerektirmez. Reddedildi: WinSW 2.x'te sanal hesap desteği belgelenmemiş, davranışı belirsiz.
3. **LocalSystem ya da root:** Ek kurulum gerektirmez. Reddedildi: aşırı yetki; uygulamadaki bir açık bütün sistemi açar.

## Karar

- Windows'ta servisler `library-svc` yerel kullanıcısıyla çalışır; iki WinSW XML'i de `<serviceaccount>` öğesini taşır ve "Hizmet olarak oturum aç" hakkı kurulumda verilir (`<allowservicelogon>true</allowservicelogon>`). Hesap Administrators grubuna eklenmez.
- Linux'ta iki unit de `User=library` ve `Group=library` ile çalışır; `library` oturum açamayan bir sistem kullanıcısıdır.
- Caddy de aynı hesapla çalışır; Linux'ta 80 ve 443 portları için `AmbientCapabilities=CAP_NET_BIND_SERVICE` verilir.
- Veri klasörü, gizli değer dosyaları (WinSW XML'leri, `library.env`, dışa aktarma parola dosyası) ve Caddy veri klasörü (CA anahtarı) ACL ya da dosya izniyle yalnız yöneticilere ve bu hesaba açılır. Ayrıntılı komutlar `docs/kurulum.md`'dedir.

## Sonuçlar

- **Olumlu:** En az yetki ilkesi; kişisel veri ve CA anahtarı başka yerel hesaplara kapalıdır.
- **Olumsuz / riskler:**
  - Windows'ta hesabın parolası WinSW XML'ine yazılır; XML'in izni bu yüzden kısıtlanır. Parola süresi dolmayacak biçimde ayarlanır, aksi hâlde servis başlamaz.
  - Yöneticinin elle çalıştırdığı komutların oluşturduğu dosyalar hesaba devralınan izinle açılmalıdır; belge klasör izinlerini devralınabilir verir.

## İzlenebilirlik

- **Gereksinim:** NFR-08; FR-37. Plan G19.
- **Bağlantılı:** ADR-0005, ADR-0010, ADR-0011, ADR-0063
