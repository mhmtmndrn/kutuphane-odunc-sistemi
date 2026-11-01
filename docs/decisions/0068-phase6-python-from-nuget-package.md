# ADR-0068: Faz 6 test ortamında servis Python'u resmi NuGet paketinden `C:\Program Files\Python311`'e açılır

- **Durum:** Kabul edildi (2026-11-01)
- **Kaynak:** Kullanıcı, 2026-11-01 yerel oturumunda kurulum bulgusu B1 üzerine soru penceresinde "NuGet paketi" seçeneğini seçti; kayıt ve belge düzeltmesi önerilerini "onaylıyorum" ile onayladı.

## Bağlam

- `docs/kurulum.md` (Windows, "Python ve sanal ortam") Python 3.11'in python.org yükleyicisiyle "Install for all users" kurulmasını ister; servis hesabı `library-svc` kullanıcı profilindeki bir Python'u okuyamaz (ADR-0062).
- Faz 6 test makinesinde (ADR-0067) Python 3.11.9 yalnız geliştiricinin kullanıcısı için kurulu (`C:\Users\Mehmet Emin\AppData\Local\Programs\Python\Python311`). Python 3.11 serisinin Windows yükleyicisi olan son sürüm 3.11.9'dur.
- Yükleyici (WiX Burn) kurulu sürümü `CPython-3.11` sağlayıcı anahtarıyla tanır ve Modify ekranını açar: "Install for all users" kutucuğu pasif, hedef yol kullanıcı profilinde kilitlidir (plan §12.2, bulgu B1). Kişisel kurulum kaldırılmadan "all users" kurulumu yapılamaz.
- Kişisel kuruluma 281 paket ve bir başka projenin venv'i (`Desktop\test_server\TEKNOFEST_TEST_SERVER\venv`) bağlıdır; bu projenin geliştirme ortamı da oradadır.

## Değerlendirilen seçenekler

1. **Resmi NuGet paketi** (seçildi): python.org'un nuget.org'da yayımladığı `python` 3.11.9 paketi (yazar Python Software Foundation) `C:\Program Files\Python311`'e açılır; venv açık yolla kurulur. Kayıt defterine ve kişisel kuruluma dokunmaz. Yükleyici adımı sınanmaz.
2. **Kişisel kurulumu kaldırıp "all users" kurmak:** Belgeye en sadık yol. Reddedildi: geliştirme ortamını (281 paket, bağlı venv) bozar; deneme projesi için bedeli yüksek.
3. **`library-svc`'ye kişisel Python klasöründe okuma izni:** En hızlısı. Reddedildi: servis bir kullanıcı profiline bağlanır, belgenin Python adımı hiç sınanmaz.

## Karar

- Test ortamında Python, `https://www.nuget.org/api/v2/package/python/3.11.9` paketinden kurulur. Paket indirildikten sonra SHA-512 özeti nuget.org kataloğundaki `packageHash` ile karşılaştırılır (onaltılık: `E353A7EFD159EF98AB9CE1011854A30D5D778F59D96FC9BB11B07CED2990B355F030486B0707F798C73C4420173AB111876A96EAD5981718B604C4CDD71C558D`). Paketin `tools\` klasörü `C:\Program Files\Python311`'e kopyalanır.
- Sanal ortam belgedeki düzeltilmiş komutla kurulur: `& "C:\Program Files\Python311\python.exe" -m venv C:\Kutuphane\venv`. `pyvenv.cfg`'nin `home` satırı `C:\Program Files\Python311` olmalıdır.
- NuGet yolu `docs/kurulum.md`'ye eklenmez; belge python.org yükleyicisiyle kalır. Belgeye yalnız bulgunun genel düzeltmeleri girer: "Customize installation → Next → Advanced Options" yolu, kişisel kurulum varsa önce kaldırma notu ve `py -3.11` yerine açık yollu venv komutu.
- Doğrulama (2026-11-01, Claude, scratchpad): paket özeti katalogla eşleşti; `3.11.9 64 bit (AMD64)`, `Lib\venv\scripts\nt\python.exe` mevcut, `-m venv` çalıştı, venv içinde pip 24.0, sqlite 3.45.1, OpenSSL 3.0.13.

## Sonuçlar

- **Olumlu:** Geliştirme ortamı korunur. Servis, kullanıcı profilinden bağımsız ve aynı sürüm (3.11.9) bir Python ile çalışır. Belgenin düzeltilmiş venv komutu bu makinede sınanır.
- **Olumsuz / riskler:**
  - Belgenin python.org yükleyicisi adımı ve "Install for all users" yolu bu kurulumda sınanmamış kalır.
  - NuGet paketi `py` başlatıcısını ve kayıt defteri girdilerini içermez; `C:\Program Files\Python311` `PATH`'te değildir. Belgede bu Python'u `py` ile çağıran başka bir komut yoktur.
  - Temizlikte `C:\Program Files\Python311` elle silinmelidir (kaldırıcısı yoktur); faz 6 sonundaki temizlik sorusuna eklenir.

## İzlenebilirlik

- **Gereksinim:** NFR-08. Plan §12.2 (B1), §12.4 adım 2 ve 9.
- **Bağlantılı:** ADR-0062, ADR-0067
