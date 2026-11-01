# ADR-0061: Personel uygulamaya sunucunun sabit IP adresiyle erişir

- **Durum:** Kabul edildi (2026-11-01)
- **Kaynak:** Kullanıcı, 2026-11-01 yerel oturumunda soru penceresinden seçti (G19 açılışı).

## Bağlam

- Caddy, `tls internal` ile site adresine sertifika üretir (ADR-0005). Tarayıcının sertifikayı kabul etmesi için personelin yazdığı adres, sertifikadaki adla aynı olmalıdır.
- Django, `ALLOWED_HOSTS` dışındaki `Host` başlığını reddeder; `CSRF_TRUSTED_ORIGINS` de bu listeden üretilir (`prod.py`).
- Küçük bir kütüphanede yerel bir DNS sunucusu yoktur. Yaklaşık 5 personel bilgisayarı vardır.
- Sunucunun adresi DHCP ile değişirse personel uygulamaya ulaşamaz ve sertifika geçersiz olur.

## Değerlendirilen seçenekler

1. **Sabit IP** (seçildi): Sunucunun IP'si yönlendiricide DHCP rezervasyonuyla sabitlenir; personel `https://192.168.x.y` adresini kullanır. Caddy `tls internal` IP adresine de sertifika üretir. Bilgisayar başına ayar gerekmez; masaüstü kısayolu yeterlidir.
2. **hosts dosyasında ad:** Her personel bilgisayarının hosts dosyasına `kutuphane` gibi bir ad yazılır. Reddedildi: bilgisayar başına yönetici işi; yeni bilgisayarda unutulur.
3. **Yönlendiricide DNS kaydı:** Yerel ad yönlendiricinin DNS'ine eklenir. Reddedildi: ev ve küçük ofis yönlendiricilerinde bu özelliğin varlığı belirsiz.

## Karar

- Sunucunun LAN IP adresi yönlendiricide DHCP rezervasyonuyla sabitlenir.
- `LIBRARY_HOST`, `LIBRARY_BIND` ve `LIBRARY_ALLOWED_HOSTS` bu IP adresidir (ör. `192.168.1.10`). Caddyfile'daki site adresi `{$LIBRARY_HOST}`'tur; `tls internal` bu IP için sertifika üretir.
- Her personel bilgisayarına `https://<IP>/` adresini açan bir masaüstü kısayolu konur.
- Kurulum belgesi DHCP rezervasyonunu ve kısayolu bir adım olarak yazar. IP değişirse üç değişken ve kısayollar birlikte güncellenir.

## Sonuçlar

- **Olumlu:** Personel bilgisayarlarında hosts ya da DNS ayarı gerekmez; sertifika, `Host` başlığı ve `ALLOWED_HOSTS` aynı değere dayanır.
- **Olumsuz / riskler:**
  - Yönlendirici değişirse ya da rezervasyon silinirse adres değişebilir; belge bunun belirtisini (bağlantı hatası) ve düzeltmesini yazar.
  - Adres akılda kalıcı değildir; kısayol bunu telafi eder.

## İzlenebilirlik

- **Gereksinim:** NFR-06, NFR-08. Plan G19.
- **Bağlantılı:** ADR-0005, ADR-0012
