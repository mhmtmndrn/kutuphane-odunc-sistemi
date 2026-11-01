# Kütüphane ödünç sistemi

Küçük bir kütüphanenin personeli için web tabanlı ödünç sistemi: üyeler, kitaplar ve nüshalar, ödünç ve iade, gecikme cezası. Kurulum ve kullanım belgeleri G19'da eklenecek.

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
