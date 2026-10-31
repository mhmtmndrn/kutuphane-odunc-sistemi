# Araştırma: Ücretsiz ISBN meta veri kaynaklarının Türkçe kitap kapsamı

- **Tarih:** 2026-10-31
- **Hizmet ettiği karar:** FR-30'un tutulup tutulmayacağı ve önceliği; SRS açık soru 1. Karar eşiği ve kapsam: [görev planı, bölüm 3](../plans/2026-10-31-kutuphane-odunc-sistemi.md) (başlık ve yazar isabeti ≥ %60 ise FR-30 tutulur).
- **Kapsam:** Ücretsiz ve anahtarsız global kaynaklar ile Türk kaynakları; ücretli servisler kapsam dışı. Ölçüm 2026-10-31'de yapıldı.
- **Önceki rapor:** yok

## Sorular

1. Ücretsiz ISBN meta veri kaynakları Türkçe kitapları ne oranda kapsıyor (başlık ve yazar isabeti)?
2. Bu kaynakların erişim şartları (anahtar, hız sınırı, yerel saklama, lisans) FR-30'a uygun mu?
3. Türk kaynaklarında (Milli Kütüphane, TO-KAT, KYGM, isbn.gov.tr) programatik erişim yolu var mı?

## Özet

- **S1:** En iyi kaynak Open Library. 25 ISBN'lik tabakalı örneklemde başlık ve yazar isabeti **13/25 (%52)**, %95 Wilson aralığı [%33, %70]. LC SRU 2/25 (%8) ve Wikidata 0/25 isabet aldı. LC'nin bulduğu iki kitabı Open Library de bulduğu için zincirleme kullanım oranı artırmıyor (birleşik %52). Nokta tahmini %60 eşiğinin **altında**, ama n = 25 olduğundan aralık eşiği de içine alıyor. Güven: orta.
- **S2:** Open Library ve LC SRU anahtarsız çalışıyor ve yerel saklamaya izin veriyor; Wikidata CC0. Google Books ToS'u kalıcı yerel kopyayı yasaklıyor, bu yüzden kullanıcı kararıyla **kapsam dışı** bırakıldı (2026-10-31). Güven: orta.
- **S3:** Hiçbir Türk kaynağında herkese açık API, SRU ya da Z39.50 yok. KYGM Koha için sabit IP'ye Z39.50 açıldığı iddiası doğrulanamadı. Kullanıcı kararıyla bu konu **açık soru** olarak kalıyor ve faz 2 onu beklemiyor. Güven: orta (KYGM için düşük).
- **Ne değişiyor:** Planda kayıtlı karar kuralına göre FR-30 eşiği geçemedi. FR-30'un düşürülmesi ya da Could olarak kalması kullanıcının kararı; SRS bu karar verilmeden değiştirilmedi. FR-30 tutulursa iki tasarım girdisi var:
  - **Dönen veri elle düzeltilebilir olmalı.** Bulunan kayıtların yaklaşık üçte birinde Türkçe karakter kayıp.
  - **ISBN-10 girişi normalize edilmeli.** Kitapyurdu kaynaklı bozuk ISBN-10'lara bakınız: S1 bulguları.

## Bulgular

### S1: Kapsam

**Yöntem**
- **Örneklem:** 25 ISBN, 5 tabaka × 5 (klasik, güncel çok satan, çocuk, akademik, küçük yayınevi). Her ISBN kitapyurdu ürün sayfasından alındı ve kontrol hanesiyle doğrulandı.
- **Ölçüm betiği:** standart kütüphaneyle yazılmış bir Python betiği; yalnız anahtarsız uçlar, saniyede en fazla 1 istek. Komut: `python -I isbn_coverage.py out.json`, 2026-10-31. Betik ve ham JSON depoya alınmadı (faz 2 küçük kararı 3).
- **İsabet tanımı:** Başlık ve yazar doğru (faz 2 küçük kararı 4).
  - Betik eşleşmeyi Türkçe büyük-küçük harfe ve aksanlara duyarsız biçimde, alt dize karşılaştırmasıyla arıyor; yazarda soyadını arıyor.
  - Bulunan her kayıt ham JSON'dan elle gözden geçirildi.
- **Sorgulanan uçlar:**
  - **Open Library:** `/api/books?jscmd=data`. Kayıpların ikisi `/isbn/<isbn>.json` ile yeniden denendi; ikisi de 404 döndü, yani kayıplar gerçek.
  - **LC SRU:** `https://lx2.loc.gov/sru/lcdb`, `bath.isbn` sorgusu. ISBN-13 ile bulunamazsa ISBN-10 da denendi.
    - Sözdizimi bilinen bir kitapla doğrulandı: 9780140449136 → 1 kayıt.
  - **Wikidata:** Tek bir toplu SPARQL sorgusu. Türk öneklerinden (978-975, 978-605, 978-625, 978-9944) P212 ve P957 değerleri çekildi (425 ISBN), eşleştirme yerelde yapıldı.
    - Eşleştirme kodu dizindeki 9789750849282 (Veba Geceleri, Orhan Pamuk) ile doğrulandı.

**Sonuçlar**
- **Open Library:**
  - 13/25 bulundu. Betik 11'ini isabet saydı.
  - Elle inceleme sonucu 13/25 (%52), çünkü betik iki yanlış negatif verdi:
    - *İnce Memed 1*: kaynak "Ince Memed I." döndürüyor; fark Roma rakamından.
    - *Tutunamayanlar'ın Politik Psikolojisi*: kaynak "Tutunamayanlarin" döndürüyor; normalizasyon kesme işaretini ayırdığı için eşleşmiyor.
  - Yanlış pozitif bulunmadı.
  - Güven: orta (örneklem küçük).
- **Tabaka bazında (Open Library, elle düzeltilmiş):**
  - Klasik 4/5
  - Güncel 2/5
  - Çocuk 3/5
  - Akademik 1/5
  - Küçük yayınevi 3/5

  Akademik yayınlar ve yeni çok satanlar en zayıf iki tabaka.
- **LC SRU:** 2/25, ikisi de küçük yayınevi tabakasından (Ketebe, Okuyan Us). Bu ikisi Open Library'de de var. Güven: orta.
- **Wikidata:** 0/25. Türk önekli ISBN sayısı yalnız 425, örneklemle hiç kesişmedi. Güven: yüksek (eşleştirme doğrulandı).
- **Hiçbir kaynakta bulunamayan 12 kitap:**
  - 2025–2026 baskıları: Başka Türlü Büyüseydim, Tanpınar'ı Okudukça Okuyorum, Timaş çocuk kitapları
  - Boğaziçi Üniversitesi Yayınevi'nin üç kitabı
  - Dergah'ın yeni baskısı (Saatleri Ayarlama Enstitüsü)

  Open Library, aynı eserin başka baskılarına sahip olsa bile yeni baskının ISBN'ini çoğu zaman bilmiyor. Örnek: "Saatleri Ayarlama Enstitüsü" araması 5 eser döndürüyor, ama 9786258437249 bunların hiçbirinde yok.
- **Önceki ölçümle karşılaştırma:**
  - Önceki ölçüm: Open Library 10/22 isabet (%45). Örneklemde 3 geçersiz ISBN vardı ve elle düzeltme yapılmamıştı.
  - Bu ölçüm: geçersiz 3 ISBN yerine aynı tabakadan geçerli ISBN'ler kondu (Pegem, Alakarga, Dost) ve elle düzeltme yapıldı.
  - Sonuç %52'ye çıktı; eşiğin altında kalması değişmedi.

**Meta veri kalitesi (Open Library'de bulunan 13 kayıt)**
- **Başlıkta Türkçe karakter kaybı:** 4/13. Örnekler: "Martiya Ucmayi Ogreten Kedi", "Herkes Icin Istatistik 1".
- **Yazar adında Türkçe karakter kaybı:** 3/13. Örnekler: "Oguz Atay", "Yusuf Atilgan".
- **Yayınevi alanı:** 13/13 dolu, ama kalitesi düşük:
  - 3 kayıtta Türkçe harfler tümüyle düşmüş: "Yap Kredi Yaynlar", "Gn Kitapl", "Can ocuk Yaynlar". Bu bozulma klasik mojibake deseni değil; harf düşmesi biçiminde.
  - 2 kayıtta yayınevi yerine dağıtıcı (Edition Orient) yazıyor.
- **Yıl alanı:** 13/13 dolu. Biçim tutarsız ("2021-06", "Oct 31, 2019", "1992"). Yıl bazen kitapyurdu'nun gösterdiği baskı tarihinden farklı (Hukuk Felsefesi: OL 2016, kitapyurdu 2025). Güven: düşük; baskı ve tekrar baskı ayrımı doğrulanmadı.
- **LC SRU:** Dublin Core yanıtından yayınevi ve yıl ayrıştırılamadı (yalnız başlık ve yazar). MARCXML şeması denenmedi.

**Kaynak verisinin güvenilirliği**
- Kitapyurdu'dan alınan 4 ISBN-10 kontrol hanesinden kaldı: 9750227059, 6057746177, 9752982925 ve değiştirme sırasında bulunan 9750234361.
- Dördünün de başına "978" eklenince geçerli bir ISBN-13 oluyor. Rastgele bir dizinin bunu sağlama olasılığı 1/10, dördünün birden sağlaması 10⁻⁴.
- Yorum: kitapyurdu büyük olasılıkla ISBN-13'ün "978" önekini atıp ISBN-10 diye gösteriyor. Güven: orta; dört örnek var, kitapyurdu'nun veri kaynağı bilinmiyor.
- Tasarım girdisi: Personel ISBN'i bu tür sitelerden kopyalarsa sistem aynı hatayla karşılaşır.

### S2: Erişim şartları

- **Open Library:**
  - Anahtar gerekmiyor. Sınır 1 istek/sn; uygulama adı ve e-posta içeren User-Agent ile 3 istek/sn. Toplu indirme için API değil döküm kullanılmalı ([Developers/API](https://openlibrary.org/developers/api)) · Güven: yüksek
  - Bakımcılar API'nin iyi ölçeklenmediğini yazıyor ve önbellek kullanılmasını istiyor ([issue #10585](https://github.com/internetarchive/openlibrary/issues/10585)) · Güven: orta
  - Lisans: yeni telif iddiası yok ([Licensing](https://openlibrary.org/developers/licensing)); katkılar CC0 ([FAQ](https://openlibrary.org/help/faq/using)) · Güven: orta (bkz. [demo veri seti raporu](2026-10-31-demo-kitap-veri-seti.md))
- **LC SRU:**
  - Kimlik doğrulama yok. Şemalar: marcxml, mods, dc. Hız sınırı belgelenmemiş ([LC Z39.50/SRU](https://www.loc.gov/z3950/lcserver.html)) · Güven: orta
  - Türkçe kapsamı 2/25 ölçüldü (S1).
- **Wikidata SPARQL:**
  - CC0. Sorgu süresi 60 sn, en fazla 5 paralel sorgu, User-Agent zorunlu ([User Manual](https://www.mediawiki.org/wiki/Wikidata_Query_Service/User_Manual); [Licensing](https://www.wikidata.org/wiki/Wikidata:Licensing)) · Güven: yüksek
- **Google Books v1:** Kapsam dışı (kullanıcı kararı, 2026-10-31).
  - API anahtarı ya da token gerekiyor ([Using the API](https://developers.google.com/books/docs/v1/using)); anahtarsız 22 isteğin hepsi HTTP 429 döndü.
  - Google API ToS §5e veritabanı kurmayı ve kalıcı kopyayı yasaklıyor; §8b sözleşme bitince silmeyi şart koşuyor ([Google APIs Terms](https://developers.google.com/terms)).
  - "Powered by Google" ibaresi zorunlu ([Branding](https://developers.google.com/books/branding)).
  - Güven: orta
- **WorldCat:** Abonelik gerekiyor, ücretsiz katman yok, kapsam dışı · Güven: orta

### S3: Türk kaynakları

- **Milli Kütüphane KAŞİF:** yalnız web arayüzü; API, SRU ya da Z39.50 belgelenmemiş ([Katalog Tarama](https://www.millikutuphane.gov.tr/page/Katalog-Tarama)) · Güven: orta
- **TO-KAT:** yalnız web; protokol ya da kullanım koşulu yayımlanmamış ([TO-KAT](https://www.millikutuphane.gov.tr/page/ULUSAL-TOPLU-KATALOG--TO-KAT-)) · Güven: orta
- **KYGM Koha (koha.ekutuphane.gov.tr):** OPAC var. Bir arama özetinde "Z39.50 için sabit IP'yi koha@ktb.gov.tr'ye bildirin" ifadesi geçiyor, ama birincil kaynakta doğrulanamadı · Güven: düşük
- **isbn.gov.tr:** herkese açık sorgu API'si yok · Güven: orta
- **YORDAM:** Z39.50 kanıtı bulunamadı · Güven: düşük
- Kazıma, faz 2 küçük kararı 5 gereği önerilmiyor.

## Karşılaştırma

| Aday | Ölçülen isabet (n = 25) | Anahtar | Yerel saklama | Hız sınırı | Türkçe karakter | Durum |
|---|---|---|---|---|---|---|
| Open Library | 13 (%52) | Yok | İzin var (CC0, orta güven) | 1/sn (UA ile 3/sn) | 4/13 başlıkta kayıp | Aday |
| LC SRU | 2 (%8) | Yok | İzin var | Belgelenmemiş | Korunuyor (2/2) | Katkısı yok (OL'nin alt kümesi) |
| Wikidata | 0 | Yok | CC0 | 60 sn/sorgu, 5 paralel | — | Katkısı yok |
| Google Books | Ölçülemedi (429) | Gerekli | ToS §5e yasaklıyor | Belgelenmemiş | — | Kapsam dışı (kullanıcı kararı) |
| Türk kaynakları | — | — | — | — | — | Programatik erişim yok; KYGM açık soru |

## Pratik durum

| Aday | Son sürüm / döküm | Bilinen sorunlar | Lisans | Donanım | Windows / Python |
|---|---|---|---|---|---|
| Open Library | Aylık döküm, son ol_dump_2026-09-30 ([dumps](https://openlibrary.org/developers/dumps)) | API ölçeklenmesi ([#10585](https://github.com/internetarchive/openlibrary/issues/10585)); yeni kayıtlarda kodlama bozulması | CC0 (orta güven) | İnternet erişimi | Standart kütüphaneyle çalıştı |
| LC SRU | Belirtilmemiş | Belgeler eski | Kısıtlama belirtilmemiş | İnternet erişimi | Standart kütüphaneyle çalıştı |
| Wikidata SPARQL | Canlı | 60 sn sorgu sınırı | CC0 | İnternet erişimi | Standart kütüphaneyle çalıştı |

## Açık sorular

1. **FR-30 düşürülsün mü, yoksa Could olarak kalsın mı?** Nokta tahmini %52, eşik %60; ama %95 aralığı [%33, %70] eşiği de içeriyor. Kesin bir yanıt için daha büyük bir örneklem gerekir; n = 100 aralığı yaklaşık ±10 puana indirir. Kullanıcının kararı.
2. **KYGM Z39.50:** Erişim gerçekten var mı ve şartları ne? Kullanıcı isterse koha@ktb.gov.tr'ye kendisi sorar; yanıt gelirse yeniden değerlendirilir.
3. **Sunucunun internet erişimi:** Sunucu kütüphane LAN'ında çalışacak (SRS bölüm 7). Dış API'ye çıkışı olup olmadığı bilinmiyor; FR-30 tutulursa bu bir ön koşul.

## Kaynaklar

1. [Open Library Developers/API](https://openlibrary.org/developers/api): birincil, erişim 2026-10-31
2. [Open Library Licensing](https://openlibrary.org/developers/licensing): birincil, erişim 2026-10-31
3. [Open Library FAQ, Using](https://openlibrary.org/help/faq/using): birincil, erişim 2026-10-31
4. [Open Library Data Dumps](https://openlibrary.org/developers/dumps): birincil, erişim 2026-10-31
5. [internetarchive/openlibrary issue #10585](https://github.com/internetarchive/openlibrary/issues/10585): birincil, erişim 2026-10-31
6. [Google Books API, Using the API](https://developers.google.com/books/docs/v1/using): birincil, erişim 2026-10-31
7. [Google APIs Terms of Service](https://developers.google.com/terms): birincil, erişim 2026-10-31
8. [Google Books Branding](https://developers.google.com/books/branding): birincil, erişim 2026-10-31
9. [Library of Congress Z39.50/SRU](https://www.loc.gov/z3950/lcserver.html): birincil, erişim 2026-10-31
10. [Wikidata Query Service User Manual](https://www.mediawiki.org/wiki/Wikidata_Query_Service/User_Manual): birincil, erişim 2026-10-31
11. [Wikidata Licensing](https://www.wikidata.org/wiki/Wikidata:Licensing): birincil, erişim 2026-10-31
12. [Milli Kütüphane, Katalog Tarama](https://www.millikutuphane.gov.tr/page/Katalog-Tarama): birincil, erişim 2026-10-31
13. [Milli Kütüphane, TO-KAT](https://www.millikutuphane.gov.tr/page/ULUSAL-TOPLU-KATALOG--TO-KAT-): birincil, erişim 2026-10-31
14. Kitapyurdu ürün sayfaları (örneklem; bağlantılar Ek A'da): ikincil, erişim 2026-10-31

## Ek A: Ham sonuç tablosu

`İsabet*`: Betik isabet saymadı, elle incelemede başlık ve yazar doğru bulundu (bkz. S1). `—`: Kaynakta bulunamadı.

| # | Tabaka | ISBN | Başlık | Yayınevi | Open Library | LC SRU | Wikidata |
|---|---|---|---|---|---|---|---|
| 1 | Klasik | [9789750807145](https://www.kitapyurdu.com/kitap/ince-memed-1/57300.html) | İnce Memed 1 | Yapı Kredi Yayınları | İsabet\* | — | — |
| 2 | Klasik | [9786257999267](https://www.kitapyurdu.com/kitap/kurk-mantolu-madonna/525566.html) | Kürk Mantolu Madonna | Türkiye İş Bankası Kültür Yayınları | İsabet | — | — |
| 3 | Klasik | [9789754700114](https://www.kitapyurdu.com/kitap/tutunamayanlar-butun-eserleri-1/18252.html) | Tutunamayanlar | İletişim Yayınları | İsabet | — | — |
| 4 | Klasik | [9786258437249](https://www.kitapyurdu.com/kitap/saatleri-ayarlama-enstitusu/698820.html) | Saatleri Ayarlama Enstitüsü | Dergah Yayınları | — | — | — |
| 5 | Klasik | [9789750802447](https://www.kitapyurdu.com/kitap/aylak-adam/28933.html) | Aylak Adam | Can Yayınları | İsabet | — | — |
| 6 | Güncel | [9789750868702](https://www.kitapyurdu.com/kitap/romanin-bes-gunu/767268.html) | Roma'nın Beş Günü | Yapı Kredi Yayınları | İsabet | — | — |
| 7 | Güncel | [9786258593822](https://www.kitapyurdu.com/kitap/baska-turlu-buyuseydim/771714.html) | Başka Türlü Büyüseydim | Doğan Kitap | — | — | — |
| 8 | Güncel | [9786050849998](https://www.kitapyurdu.com/kitap/diclenin-sandali/768919.html) | Dicle'nin Sandalı | Timaş Yayınları | — | — | — |
| 9 | Güncel | [9786256989498](https://www.kitapyurdu.com/kitap/cumhuriyetin-ilk-sabahi/649012.html) | Cumhuriyet'in İlk Sabahı | Kronik Kitap | — | — | — |
| 10 | Güncel | [9786051981833](https://www.kitapyurdu.com/kitap/gece-yarisi-kutuphanesi/582550.html) | Gece Yarısı Kütüphanesi | Domingo Yayınevi | İsabet | — | — |
| 11 | Çocuk | [9786258618136](https://www.kitapyurdu.com/kitap/mudurun-ucan-perugu/757062.html) | Müdürün Uçan Peruğu | Timaş Çocuk Yayınları | — | — | — |
| 12 | Çocuk | [9786259029221](https://www.kitapyurdu.com/kitap/gizli-dedektifler-okulu/757375.html) | Gizli Dedektifler Okulu | Timaş İlk Genç | — | — | — |
| 13 | Çocuk | [9786054603947](https://www.kitapyurdu.com/kitap/postayla-gelen-deniz-kabugu/346303.html) | Postayla Gelen Deniz Kabuğu | Günışığı Kitaplığı | İsabet | — | — |
| 14 | Çocuk | [9789756227640](https://www.kitapyurdu.com/kitap/eyvah-kitap/87483.html) | Eyvah Kitap! | Günışığı Kitaplığı | İsabet | — | — |
| 15 | Çocuk | [9789755109428](https://www.kitapyurdu.com/kitap/martiya-ucmayi-ogreten-kedi/16956.html) | Martıya Uçmayı Öğreten Kedi | Can Çocuk Yayınları | İsabet | — | — |
| 16 | Akademik | [9786057827654](https://www.kitapyurdu.com/kitap/bilim-devrimleri-15001700-arasinda-avrupada-bilginin-donusumu/765157.html) | Bilim Devrimleri | Boğaziçi Üniversitesi Yayınevi | — | — | — |
| 17 | Akademik | [9786057827050](https://www.kitapyurdu.com/kitap/cagatay-edebiyati-antolojisi-gazeller/751215.html) | Çağatay Edebiyatı Antolojisi | Boğaziçi Üniversitesi Yayınevi | — | — | — |
| 18 | Akademik | [9786057827647](https://www.kitapyurdu.com/kitap/uluslararasi-guvenlik/765158.html) | Uluslararası Güvenlik | Boğaziçi Üniversitesi Yayınevi | — | — | — |
| 19 | Akademik | [9786055885939](https://www.kitapyurdu.com/kitap/ben-bir-okul-uydurdum/138711.html) | Ben Bir Okul Uydurdum | Pegem Akademi Yayıncılık | — | — | — |
| 20 | Akademik | [9786254395673](https://www.kitapyurdu.com/kitap/herkes-icin-istatistik-1/588361.html) | Herkes İçin İstatistik 1 | Nobel Akademik Yayıncılık | İsabet | — | — |
| 21 | Küçük yayınevi | [9786258159035](https://www.kitapyurdu.com/kitap/ahmet-hamdi-tanpinarin-saatleri-ayarlama-enstitusu-bir-tahlil/622889.html) | Saatleri Ayarlama Enstitüsü Bir Tahlil | Ketebe Yayınevi | İsabet | İsabet | — |
| 22 | Küçük yayınevi | [9786257370653](https://www.kitapyurdu.com/kitap/klasik-okumalari-ii-tutunamayanlar-cagi/611842.html) | Tutunamayanlar Çağı | Sel Yayıncılık | — | — | — |
| 23 | Küçük yayınevi | [9786255719652](https://www.kitapyurdu.com/kitap/tanpinari-okudukca-okuyorum/760308.html) | Tanpınar'ı Okudukça Okuyorum | Alakarga Sanat Yayınları | — | — | — |
| 24 | Küçük yayınevi | [9786055134426](https://www.kitapyurdu.com/kitap/quottutunamayanlarquotin-politik-psikolojisi/336527.html) | Tutunamayanlar'ın Politik Psikolojisi | Okuyan Us Yayınları | İsabet\* | İsabet | — |
| 25 | Küçük yayınevi | [9789752984554](https://www.kitapyurdu.com/kitap/hukuk-felsefesi/266645.html) | Hukuk Felsefesi | Dost Kitabevi | İsabet | — | — |

**Değiştirilen örneklem kayıtları** (geçersiz ISBN-10 → aynı tabakadan geçerli ISBN-13):
- **Akademik:** Seçkin, Medeni Hukuk Bilgisi (9750227059) → Pegem, Ben Bir Okul Uydurdum. Seçkin'in denenen ikinci kitabı da (9750234361) geçersiz çıktı.
- **Küçük yayınevi:** Alakarga, Tutunamayanlar Üzerine Yedi Ders (6057746177) → Alakarga, Tanpınar'ı Okudukça Okuyorum.
- **Küçük yayınevi:** Dost, Tutunamayanlar ve Hukuk (9752982925) → Dost, Hukuk Felsefesi.
