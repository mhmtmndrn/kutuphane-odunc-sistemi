# Kütüphane ödünç sistemi

Küçük bir kütüphanenin personeli için web tabanlı ödünç sistemi: üyeler, kitaplar ve nüshalar, ödünç ve iade, gecikme cezası.

## Belgeler

- [Kurulum ve işletim](docs/kurulum.md): sunucuya kurulum (Windows ve Linux), personel bilgisayarları, güncelleme, yedekler ve yedekten geri yükleme.
- [Kullanım kılavuzu](docs/kullanim-kilavuzu.md): ödünç masasındaki işler ve yönetici işleri.
- Tasarım ve kararlar: [gereksinimler](docs/srs.md), [mimari](docs/architecture.md), [veri tasarımı](docs/data-design.md), [test planı](docs/test-plan.md), [kararlar (ADR)](docs/decisions/), [durum notu](docs/STATUS.md).
- Dağıtım dosyaları `deploy/` klasöründedir: Caddyfile, WinSW servis tanımları, systemd unit'leri ve ortam dosyası örneği.

## Veri kaynakları

- Demo kitaplarının başlık, yazar, yıl ve ISBN bilgileri [Open Library](https://openlibrary.org)'den bir kez çekildi (`scripts/fetch_demo_books.py`, `seed/books_openlibrary.json`). Open Library katalog verisi CC0 (kamu malı) olarak sunulur; teşekkür ederiz. Yalnız bibliyografik alanlar ve her kaydın Open Library kimliği alındı, kapak görselleri alınmadı.
- Üye adları, `seed/` altındaki sabit ad ve soyad listelerinden rastgele birleştirilir. Telefonlar "000" önekli sahte numaralardır, e-postalar `@example.invalid` ile biter; hiçbiri gerçek bir kişiye ulaşmaz.

## Demo verisi

Boş bir veritabanına demo verisi yüklemek için sırasıyla:

```bash
python manage.py migrate
```

```bash
python manage.py createsuperuser
```

```bash
python manage.py load_seed_data --profile demo --actor <ad>
```

`<ad>`, `createsuperuser` ile oluşturulan kullanıcı adıdır; tohum verideki bütün kayıtların sahibi bu personel olur. Komut 300 kitap, 200 üye, 150 açık ve 350 kapalı ödünç yükler. Veritabanında üye ya da kitap varsa çalışmaz. Yük testi verisi için `--profile load` kullanılır.

## Geliştirme ortamı

Python 3.11 gerekir. Depo klasöründe bir sanal ortam kurun ve etkinleştirin (Windows'ta `.venv\Scripts\activate`, Linux'ta `. .venv/bin/activate`):

```bash
python -m venv .venv
```

Etkin sanal ortamda geliştirme bağımlılıklarını yükleyin, veritabanını oluşturun ve geliştirme sunucusunu açın:

```bash
python -m pip install -r requirements-dev.txt
```

```bash
python manage.py migrate
```

```bash
python manage.py createsuperuser
```

```bash
python manage.py runserver
```

Uygulama `http://127.0.0.1:8000/giris/` adresindedir. `manage.py` geliştirme ayarlarını (`library_site.settings.dev`) kullanır: veritabanı ve yedek klasörleri `var/` altındadır, e-postalar konsola yazılır, zamanlayıcı kapalıdır. Yedek komutlarını denemek için `var/backups`, `var/exports` klasörleri ve `var/export-passphrase.txt` dosyası elle oluşturulur.

## Testler

```bash
python -m pytest -q
```

Yavaş PDF, barkod ve yük profili testleri `slow` işaretlidir ve varsayılan koşuya dahildir; yalnız onları koşmak için `python -m pytest -m slow -q`. Migration kontrolü:

```bash
python manage.py makemigrations --check --dry-run
```

Dal kapsamı `coverage run --branch -m pytest` ile ölçülür; hedefler [test planı](docs/test-plan.md) §4'tedir (ör. `coverage report --include="*/domain.py" --fail-under=90`). `tests/test_deploy_files.py`, `deploy/` dosyalarını ayarlarla ve birbirleriyle karşılaştırır.
