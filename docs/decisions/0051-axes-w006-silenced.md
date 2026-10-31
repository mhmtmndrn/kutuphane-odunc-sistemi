# ADR-0051: django-axes `axes.W006` sistem kontrolü uyarısı susturulur

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Kullanıcı, 2026-10-31'de PR #1 (`feature/foundation`, G02–G04) incelemesinde onayladı.

## Bağlam

- ADR-0009 hesap kilidini yalnız kullanıcı adına göre kurar: `AXES_LOCKOUT_PARAMETERS = ["username"]`.
- django-axes 9, `AXES_LOCKOUT_PARAMETERS` içinde `ip_address` yoksa `axes.W006` sistem kontrolü uyarısını verir. Bu uyarı `python manage.py check` ve `check --deploy` çıktısında görünür.
- Uygulama waitress ile `127.0.0.1:8000`'de dinler ve istekleri Caddy iletir (ADR-0005, ADR-0012). Bu yüzden uygulamaya gelen her isteğin istemci adresi 127.0.0.1'dir.
- G01'in doğrulaması `check --deploy` için "no issues (2 silenced)" sonucunu bekliyordu (`security.W004`, `security.W008`).

## Değerlendirilen seçenekler

1. **Uyarıyı gerekçe yorumuyla susturmak** (seçildi): `axes.W006`, `base.py`'deki `SILENCED_SYSTEM_CHECKS` listesine eklenir; `prod.py` bu listeyi genişletir. Kilit davranışı ADR-0009'daki gibi kalır. `check --deploy` temiz kalır, ama susturulan kontrol sayısı 3 olur.
2. **Kilide `ip_address` eklemek:** Uyarı kaybolur. Ancak bütün istekler 127.0.0.1'den geldiği için IP'ye göre kilit bir kişinin 5 hatalı denemesinde bütün personeli birden kilitler. ADR-0009 ile çelişir.
3. **Uyarıyı olduğu gibi bırakmak:** Kod değişmez, ama `check` ve `check --deploy` her çalışmada uyarı verir; gerçek yeni uyarılar gözden kaçabilir.

## Karar

- `axes.W006`, `library_site/settings/base.py`'deki `SILENCED_SYSTEM_CHECKS` listesinde, bu ADR'ye bağlanan bir yorumla durur.
- `library_site/settings/prod.py`, `base` listesini genişletir ve `security.W004` ile `security.W008`'i ekler.
- `python manage.py check --deploy --settings=library_site.settings.prod` beklenen sonucu: "System check identified no issues (3 silenced)."

## Sonuçlar

- **Olumlu:** Kilit davranışı ADR-0009 ile aynı kalır; sistem kontrolü çıktısı temizdir.
- **Olumsuz / riskler:**
  - axes'in yeni sürümlerinde aynı konuda farklı kodlu bir uyarı çıkarsa ayrıca değerlendirilir.
  - Kullanıcı adına göre kilidin riskleri (kasıtlı kilitleme) ADR-0009'daki gibi kabul edilmiştir.

## İzlenebilirlik

- **Gereksinim:** FR-27, AC-27. Plan G01 (doğrulama notu), G02, §11.
- **Bağlantılı:** ADR-0005, ADR-0009, ADR-0012, ADR-0049, ADR-0050
