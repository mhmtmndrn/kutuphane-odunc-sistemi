# ADR-0028: En az bir açık hafta günü zorunludur ve son tarih kaydırmasının üst sınırı vardır

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 4, 1. tur. Kullanıcı soru penceresinden seçti. Faz 3 varsayımı (d) bu kararla kapandı.

## Bağlam

FR-07'ye göre son tarih kapalı bir güne denk gelirse ilk açık güne kaydırılır. Haftanın yedi günü de kapalı seçilirse kaydırma döngüsü sonlanmaz. Tek tek kapalı tarihlerle bütün bir yılı kapatmak da teorik olarak mümkün. SRS bu durumu kapsamıyordu.

## Değerlendirilen seçenekler

1. **Kural ve üst sınır** (seçildi): Ayarlarda en az bir hafta günü açık kalmalıdır. Buna ek olarak kaydırma en fazla 366 gün ileri bakar. Sonsuz döngü imkânsız hale gelir.
2. **Yalnız kural:** Tek tarihli kapalı günlerle yılı kapatma yolu açık kalır.
3. **Yalnız üst sınır:** Ayar serbest kalır; sorun ödünç anında hatayla yakalanır.

## Karar

- FR-24'e kural eklenir: Haftalık kapalı günlerin yedisini birden seçen kayıt reddedilir ve "En az bir gün açık kalmalı" mesajı gösterilir.
- `circulation.domain.due_date(start, period_days, is_closed)` aday tarihten itibaren en fazla 366 gün ileri bakar. Açık gün bulamazsa `NoOpenDayError` fırlatır. `check_out` ve `renew` bu hatayı "Önümüzdeki 366 günde açık gün yok; kapalı gün ayarlarını kontrol edin" mesajıyla gösterir ve işlemi yapmaz.
- `due_date` için en kötü durum O(366) zaman ve O(1) alandır.

## Sonuçlar

- **Olumlu:** Döngü her durumda sonlanır; hatalı ayar kaydedilirken ya da işlem masasında yakalanır.
- **Olumsuz / riskler:** 366 sınırı bir sabittir. Ayar olarak açılmaz.

## İzlenebilirlik

- **Gereksinim:** FR-07, FR-10, FR-24; AC-07, AC-24
- **Bağlantılı:** ADR-0015
