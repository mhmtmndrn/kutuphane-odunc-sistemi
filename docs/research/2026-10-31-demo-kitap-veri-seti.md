# Araştırma: Demo ve geliştirme için açık lisanslı Türkçe kitap veri seti

- **Tarih:** 2026-10-31
- **Hizmet ettiği karar:** FR-29'un kitap verisi kaynağı; SRS açık soru 2. Lisans koşulu: [görev planı, bölüm 3](../plans/2026-10-31-kutuphane-odunc-sistemi.md) (yalnız CC0, kamu malı ya da ODbL).
- **Kapsam:** Türkçe kitap içeren, yerel olarak saklanıp dağıtılabilen bibliyografik veri. Üye verisi her durumda sentetik (FR-29), bu yüzden bu raporun konusu değil.
- **Önceki rapor:** yok. İlgili rapor: [ISBN meta veri kaynakları](2026-10-31-isbn-meta-veri-apileri.md).

## Sorular

1. Lisansı CC0, kamu malı ya da ODbL olan ve Türkçe kitap içeren açık bir veri seti var mı?
2. Bu set demo için yeterince kayıt sağlıyor mu, verinin kalitesi nasıl?

## Özet

- **S1:** Evet: **Open Library**. FAQ ve CC wiki katkıların CC0 olduğunu söylüyor; Licensing sayfası ise yalnız "yeni telif iddiası yok" diyor ve bazı katkılarda mevcut hak sorunları olabileceği uyarısını veriyor. Kullanıcı bu belirsizliği bir koşulla kabul etti (2026-10-31): yalnız bibliyografik alanlar alınacak, kapaklar alınmayacak, her kayıtta OL kimliği tutulacak ve bir atıf notu konacak. Güven: orta.
  - Wikidata CC0, ama ISBN'li Türkçe kayıt sayısı az.
  - Diğer adaylar lisans koşulunu karşılamıyor ya da lisansları doğrulanamadı.
- **S2:** Kayıt sayısı yeterli: Open Library'de `language:tur` ile 123.342, `language:tur isbn:978605*` ile 23.947 eser var. Ancak kalite sorunlu: kayıtların yaklaşık üçte birinde Türkçe karakter kayıp, yayınevi alanında harf düşmesi var. Seçim ya da temizlik adımı gerekiyor. Güven: orta.
- **Ne değişiyor:** Sentetik kitap verisi zorunlu değil, FR-29 açık veriyle karşılanabilir. Bir tutarsızlık var: AC-29 "sentetik üyeler, kitaplar ve nüshalar yüklenir" diyor, FR-29 ise kitap verisinin açık veri setinden de gelebileceğini söylüyor. AC-29'un düzeltilmesi kullanıcının onayına bağlı (bkz. Açık sorular).

## Bulgular

### S1: Lisans

- **Open Library:**
  - FAQ, katkıların CC0 olduğunu söylüyor ([FAQ, Using](https://openlibrary.org/help/faq/using)); CC wiki de bunu doğruluyor ([CC Case Studies](https://wiki.creativecommons.org/wiki/Case_Studies/Open_Library)) · Güven: orta
  - Licensing sayfası açıkça CC0 demiyor: yalnız yeni telif iddiası olmadığını yazıyor ve "existing rights issues on some contributions" uyarısı veriyor ([Licensing](https://openlibrary.org/developers/licensing)) · Güven: orta
  - Yorum (doğrulanmadı): Uyarı büyük olasılıkla kapak görselleri ve açıklama metinleriyle ilgili. Başlık, yazar, yayınevi, yıl ve ISBN olgusal veriler. Bu nedenle kullanıcı kararıyla yalnız bu alanlar alınacak · Güven: düşük
- **Wikidata:** CC0 ([Licensing](https://www.wikidata.org/wiki/Wikidata:Licensing)) · Güven: yüksek
- **Milli Kütüphane, KYGM, data.gov.tr:** Açık lisanslı döküm bulunamadı; data.gov.tr bağlantıyı reddetti · Güven: düşük
- **Kaggle "Turkish Book Dataset":** Lisans doğrulanamadı, büyük olasılıkla kazıma verisi. Lisans koşulunu karşılamadığı için **kabul edilemez** · Güven: orta
- **LoC MDSConnect:** Lisans beyanı yok · Güven: düşük
- **ODbL:** Bilgi için: share-alike yükümlülüğü getiriyor. ODbL lisanslı bir Türkçe kitap kaynağı bulunamadı.

### S2: Hacim ve kalite

- **Open Library hacmi:**
  - Arama API'si `language:tur` ile 123.342 eser, `language:tur isbn:978605*` ile 23.947 eser döndürüyor ([sorgu](https://openlibrary.org/search.json?q=language:tur+isbn:978605*)). Sayılar eser düzeyinde, baskı düzeyinde değil · Güven: orta
  - Aylık TSV dökümleri yayımlanıyor: editions dosyası ~9.2 GB (gz), en son döküm ol_dump_2026-09-30 ([Data Dumps](https://openlibrary.org/developers/dumps)) · Güven: yüksek
  - Küçük bir demo seti için 9.2 GB'lık dökümü indirmek gerekmiyor. Arama API'si saniyede 1 istek sınırıyla kullanılabilir; API toplu indirme için değil, yalnız küçük bir alt küme çekmek için kullanılmalı ([Developers/API](https://openlibrary.org/developers/api)) · Güven: orta
- **Open Library kalitesi** (25 ISBN'lik ölçümde bulunan 13 kayıt, bkz. [ISBN raporu](2026-10-31-isbn-meta-veri-apileri.md)):
  - Başlıkta Türkçe karakter kaybı 4/13, yazar adında 3/13.
  - Yayınevi alanında 3 kayıtta harf düşmesi var ("Yap Kredi Yaynlar"); 2 kayıtta yayınevi yerine dağıtıcı yazıyor.
  - Yeni kayıtlarda "Bask¿" gibi kodlama bozulmaları görülüyor.
  - Güven: orta
- **Wikidata hacmi:**
  - Researcher'ın SPARQL sorgusu ISBN'li Türkçe kitap için ~330–349 kayıt buldu.
  - Bu oturumdaki toplu sorgu, Türk önekli (978-975/605/625/9944) 425 ISBN döndürdü. Bu sayı dile göre değil ISBN önekine göre; aynı eserin birden çok ISBN'i olabilir.
  - Önceki oturumda kullanılan 500 kayıtlık alt sınıra yetmiyor · Güven: orta
- **Sentetik veri:** Zorunlu değil. Açık veri hem gerçekçi hem lisans açısından uygun.

## Karşılaştırma

| Aday | Lisans | Lisans koşuluna uyum | Türkçe hacim | Kalite | Durum |
|---|---|---|---|---|---|
| Open Library | CC0 (orta güven) | Uyuyor (kullanıcı kabulü, kaynak notuyla) | ~24 bin eser (978605) | Türkçe karakter kaybı, yayınevi bozulması | Aday |
| Wikidata | CC0 | Uyuyor | ~350–425 ISBN | Yayınevi ve yıl çoğunlukla boş (ölçülmedi) | Tek başına yetersiz |
| Kaggle "Turkish Book Dataset" | Doğrulanamadı | Uymuyor | — | — | Kabul edilemez |
| Milli Kütüphane, KYGM, data.gov.tr | Döküm yok | — | — | — | Uygun değil |
| Sentetik | Sorunsuz | Uyuyor | Sınırsız | Gerçekçi değil | Yedek seçenek |

## Pratik durum

| Aday | Son sürüm / döküm | Bilinen sorunlar | Lisans | Donanım | Windows / Python |
|---|---|---|---|---|---|
| Open Library | ol_dump_2026-09-30 (aylık) | Kodlama bozulması; API ölçeklenmesi ([#10585](https://github.com/internetarchive/openlibrary/issues/10585)) | CC0 (orta güven) | Döküm için ~9.2 GB disk; API için gerekmez | Standart kütüphaneyle erişildi |
| Wikidata | Canlı | 60 sn sorgu sınırı | CC0 | — | Standart kütüphaneyle erişildi |

## Açık sorular

1. **AC-29'un düzeltilmesi:** AC-29 kitapların sentetik olacağını söylüyor, FR-29 ise açık veri setine izin veriyor. AC-29 "kitaplar lisansı uygun açık veri setinden (Open Library, CC0) ya da sentetik olarak yüklenir; her kitap kaydında kaynak kimliği tutulur" biçiminde düzeltilsin mi? SRS değişikliği olduğu için kullanıcının onayı gerekiyor.
2. **Demo setinin boyutu:** 500 kayıtlık alt sınır önceki oturumda araştırma brifinde kullanıldı, ama planda kayıtlı değil. Setin boyutu ve kayıtların hangi ölçütle seçileceği (örneğin yalnız Türkçe karakterleri sağlam kayıtlar) faz 3–4'te karara bağlanmalı.
3. **Atıf notunun yeri ve biçimi:** README, tohum veri dosyasının başlığı ya da ikisi birden olabilir. Bu küçük bir karar; faz 4'teki karar listesine girecek.

## Kaynaklar

1. [Open Library FAQ, Using](https://openlibrary.org/help/faq/using): birincil, erişim 2026-10-31
2. [Open Library Licensing](https://openlibrary.org/developers/licensing): birincil, erişim 2026-10-31
3. [Creative Commons wiki, Case Studies/Open Library](https://wiki.creativecommons.org/wiki/Case_Studies/Open_Library): ikincil, erişim 2026-10-31
4. [Open Library Data Dumps](https://openlibrary.org/developers/dumps): birincil, erişim 2026-10-31
5. [Open Library Developers/API](https://openlibrary.org/developers/api): birincil, erişim 2026-10-31
6. [Open Library search, language:tur isbn:978605*](https://openlibrary.org/search.json?q=language:tur+isbn:978605*): birincil, erişim 2026-10-31
7. [internetarchive/openlibrary issue #10585](https://github.com/internetarchive/openlibrary/issues/10585): birincil, erişim 2026-10-31
8. [Wikidata Licensing](https://www.wikidata.org/wiki/Wikidata:Licensing): birincil, erişim 2026-10-31
