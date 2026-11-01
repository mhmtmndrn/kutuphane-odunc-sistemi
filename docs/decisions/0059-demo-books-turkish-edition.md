# ADR-0059: Demo kitap kaydı eserden değil, eşleşen Türkçe baskıdan alınır (filtre sürümü 2)

- **Durum:** Kabul edildi (2026-11-01)
- **Kaynak:** Kullanıcı, 2026-11-01'de PR #6'nın (`feature/seed-load`) yerel doğrulamasında soru penceresinden üç ayrı soruyla seçti: önce "filtre v2, yerelde", ardından baskı düzeyi, son olarak sunucu hatalarında yeniden deneme.

## Bağlam

- ADR-0033'teki betik Open Library arama API'sini `language:tur isbn:978605*` sorgusuyla çağırır. API eser (work) döndürür. Eserin `title` alanı çoğu zaman özgün dildeki başlıktır, `isbn` alanı ise eserin bütün baskılarının ISBN'lerini birleştirir.
- Filtre sürümü 1 ile yerelde çekilen 300 kaydın 43'ünün ISBN'i Türk yayıncı öneki taşımıyordu (978-605 ya da 978-975 dışında). Bu kayıtların çoğunun başlığı da yabancıydı: "Den skrattande polisen", "Smaragdgrün", "Momo oder Die seltsame Geschichte…". Bu başlıklar 3. kuraldan `ö` ve `ü` sayesinde geçiyordu. İngilizce özgün başlıklı eserler ise 3. kurala takılıyordu. Kitabın Türkçe baskısı olsa bile ("Atomik Alışkanlıklar" gibi) kayıt atılıyordu.
- `editions` alanları istendiğinde sunucu yavaşlıyor: sayfa başına yaklaşık 11–12 sn sürüyor ve bazı sayfalar HTTP 500 dönüyor. İki tam deneme bu yüzden çıkış 1 ile bitti.
- Aynı aramada `editions` alanı istenirse API, sorguya uyan baskıları (`editions.docs`) döndürür. Bunların her biri kendi `key`, `title`, `isbn` ve `language` alanını taşır. Örnek: *Atomic Habits* eseri için "Atomik Alışkanlıklar", `['tur']`, 9786052998380.

## Değerlendirilen seçenekler

1. **Baskı düzeyi** (seçildi): Kaydın başlığı, ISBN'i ve OL kimliği eşleşen Türkçe baskıdan alınır. ADR-0033'ün beş kuralı bu baskıya uygulanır. Başlık ve ISBN aynı baskıya ait olur ve sorunun kök nedeni çözülür.
2. **Dar düzeltme:** Eser başlığı korunur. ISBN listeden Türk önekiyle seçilir, yabancı harf (`äåßéñø…`) içeren başlık atılır. Daha az değişiklik gerekir, ama yabancı başlığa Türk baskısının ISBN'i yapışabilir.
3. **Olduğu gibi kabul:** Sınırlama belgelenir. Demoda yaklaşık 43 yabancı başlık görünür.

## Karar

- `scripts/fetch_demo_books.py` aramada `editions`, `editions.key`, `editions.title`, `editions.isbn` ve `editions.language` alanlarını ister. Eserin `title` ve `isbn` alanları istenmez.
- Her eser için `editions.docs` içinde `language` listesinde `tur` geçen ilk baskı seçilir. Böyle bir baskı yoksa kayıt atılır.
- ADR-0033'ün beş kuralı aynı sırayla uygulanır. Başlık ve ISBN bu baskıdan, yazar (`author_name`) ve yıl (`first_publish_year`) eserden gelir.
- Kaydın `ol_id` alanı baskının kimliğidir (`OL…M`). Kayıt alanları ve dosya biçimi değişmez.
- `_meta.filter_version` 2 olur. Sorgu ve diğer `_meta` alanları değişmez.
- HTTP 5xx cevabı ya da zaman aşımı alınırsa aynı sayfa en çok 3 kez daha, sırasıyla 2, 4 ve 8 sn beklenerek istenir. Denemeler tükenirse ya da hata 4xx veya başka bir ağ hatasıysa betik bugünkü gibi "Open Library'ye erişilemedi: <neden>" ile çıkış 1 verir ve dosya yazılmaz. Reddedilenler: sayfa boyutunu 50'ye indirmek (500'leri önleyeceği kesin değil, istek sayısı iki katına çıkar), komutu elle tekrar çalıştırmak.

## Sonuçlar

- **Olumlu:**
  - Demo kitapları Türkçe baskıların başlığını ve ISBN'ini taşır.
  - Özgün başlığı İngilizce olan çeviriler de dosyaya girebilir.
  - `Book.source_ol_id` doğrudan ISBN'in ait olduğu baskıyı gösterir.
- **Olumsuz / riskler:**
  - Yıl alanı baskı yılı değil, eserin ilk yayın yılıdır (ADR-0033'teki gibi).
  - Baskı başlıklarındaki Türkçe karakter kaybı ("Dönüsüm") ADR-0033'ün bilinen sınırlaması olarak kalır. 3. kural bu kayıtların yalnız bir kısmını eler.
  - `editions` alanının içeriği Open Library'nin arama davranışına bağlıdır. Betik testlerde sahte cevaplarla, yerelde gerçek cevapla doğrulandı.

## İzlenebilirlik

- **Gereksinim:** FR-29; AC-29. Testler: TC-357 (baskı düzeyi), TC-358 (yeniden deneme); TC-214…TC-216 ve TC-340 baskı düzeyine uyarlandı.
- **Bağlantılı:** ADR-0033 (kısmen değiştirir), ADR-0056
