# ADR-0063: WinSW 2.12.0 ve sabitlenmiş bir Caddy 2.x sürümü kullanılır

- **Durum:** Kabul edildi (2026-11-01)
- **Kaynak:** Kullanıcı, 2026-11-01 yerel oturumunda soru penceresinden seçti (G19 açılışı).

## Bağlam

- WinSW (ADR-0010) ve Caddy (ADR-0005) Python bağımlılığı değildir; `requirements.txt`'te sabitlenemez. Sürüm belirtilmezse iki kurulum farklı ikilileri alabilir.
- WinSW'nin son kararlı sürümü 2.12.0'dır; 3.x serisi hâlâ alfa sürümüdür ve XML biçimi 2.x'ten farklıdır (ör. `<serviceaccount>` alt öğeleri).
- Caddy 2.x geriye uyumlu küçük sürümler yayımlar. G19 yazılırken (2026-11-01) son kararlı sürüm 2.11.7'dir.

## Değerlendirilen seçenekler

1. **WinSW 2.12.0 ve yazım anındaki Caddy sürümü, sabit bağlantıyla** (seçildi): XML'ler 2.12.0 biçimine göre yazılır. Caddy'nin sürümü belgeye yazılır, indirme bağlantısı o sürüme sabitlenir; güncelleme elle yapılır.
2. **WinSW 3.x alfa:** Daha yeni özellikler. Reddedildi: alfa sürümü üretim servisi için uygun değil, XML biçimi değişebilir.
3. **Sürüm sabitlememek:** Belge "son sürümü indirin" der. Reddedildi: kurulumlar tekrarlanamaz; yeni bir sürüm yapılandırmayı bozabilir.

## Karar

- Windows'ta WinSW 2.12.0 (`WinSW-x64.exe`) kullanılır; iki XML de bu sürümün biçimindedir.
- Caddy sürümü 2.11.7'dir. `docs/kurulum.md` sürümü ve iki platformun indirme bağlantısını (`https://github.com/caddyserver/caddy/releases/download/v2.11.7/…`) verir, indirilen arşivin SHA-512 özetinin yayımlanan `checksums.txt` ile karşılaştırılmasını ister.
- Caddy ve WinSW'nin güncellenmesi elle yapılır: yeni sürüm bir test ortamında `caddy validate` ile denenir, belge ve bağlantı aynı commit'te güncellenir.

## Sonuçlar

- **Olumlu:** Kurulum tekrarlanabilir; XML biçimi belli bir sürüme dayanır.
- **Olumsuz / riskler:** Güvenlik düzeltmeleri kendiliğinden gelmez; Caddy sürümlerinin izlenmesi yöneticinin işidir (belgede not).

## İzlenebilirlik

- **Gereksinim:** NFR-05, NFR-06. Plan G19.
- **Bağlantılı:** ADR-0005, ADR-0010, ADR-0062
