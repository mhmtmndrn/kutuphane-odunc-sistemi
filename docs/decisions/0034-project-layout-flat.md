# ADR-0034: Proje düz kök yerleşimini kullanır

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 4, 4. tur. Kullanıcı soru penceresinden önizlemeli seçenekle seçti.

## Bağlam

App'ler ve katmanları ADR-0015 ile architecture §3'te tanımlandı. Deponun kök yerleşimi ise tanımlı değildi.

## Değerlendirilen seçenekler

1. **Düz kök** (seçildi): App'ler depo kökünde durur. Django'nun varsayılan yerleşimidir ve import yolları kısa olur.
2. **src/ yerleşimi:** Paket sınırı daha net olur, ama `manage.py` ve pytest için yol ayarı gerekir.

## Karar

```
manage.py
pyproject.toml            # pytest ve coverage ayarları
requirements.txt          # üretim, sabit sürümler
requirements-dev.txt      # -r requirements.txt + test araçları
library_site/
  settings/ base.py dev.py test.py prod.py
  urls.py wsgi.py
accounts/ administration/ members/ catalog/
billing/ circulation/ notifications/ operations/
  (her app) domain.py services.py views.py urls.py models.py forms.py
            templates/<app>/  tests/ test_domain.py test_services.py test_views.py
templates/                # base.html, giriş sayfası
static/
seed/books_openlibrary.json
scripts/fetch_demo_books.py scripts/loadtest.py
deploy/Caddyfile deploy/winsw/ deploy/systemd/
tests/support/            # barcode.py, factories.py
docs/
```

- Etiket ve kart için paylaşılan PDF yardımcısının yeri faz 4 küçük karar listesindedir.

## Sonuçlar

- **Olumlu:** Django belgeleriyle aynı yerleşim; ek yol ayarı gerekmez.
- **Olumsuz / riskler:** Kökte daha çok klasör olur.

## İzlenebilirlik

- **Gereksinim:** NFR-13
- **Bağlantılı:** ADR-0015, ADR-0025, ADR-0030
