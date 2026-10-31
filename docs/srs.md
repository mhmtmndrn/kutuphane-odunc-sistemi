# Yazılım Gereksinim Belirtimi (SRS-lite): Kütüphane Ödünç Sistemi

- **Güncelleme:** 2026-10-31
- **Durum:** Onaylandı (2026-10-31)
- **İlgili dokümanlar:** [Görev planı](plans/2026-10-31-kutuphane-odunc-sistemi.md)

## 1. Amaç ve kapsam

Küçük bir kütüphanenin personeli için web tabanlı ödünç sistemi. Üyeleri, kitapları ve nüshaları, ödünç verme, iade ve uzatmayı, gecikme cezasını, ödemeleri ve kayıp nüshaları tek yerde tutar. Sistem kütüphanenin yerel ağındaki bir sunucuda çalışır ve yalnızca personel kullanır.

- **Kapsam içi:** Üye yönetimi ve e-posta rızası. Kitap ve nüsha kataloğu. Barkodla ödünç, iade ve uzatma. Kapalı günlere göre son tarih kaydırma. Gecikme cezası, kısmi ödeme, gerekçeli af. Kayıp ve hasarlı nüsha. Geciken ödünç listesi. E-posta hatırlatması. Barkod etiketi basımı. Yönetici ve görevli rolleri. Ayarlar. KVKK anonimleştirmesi. Denetim kaydı. Günlük yedek. Geliştirme ve demo için tohum veri.
- **Kapsam dışı:** Rezervasyon ve bekleme kuyruğu. Üye girişi ve self-servis. Online ödeme. Birden çok üye tipi ve tipe göre kural. Üyelik geçerlilik süresi. Tahsilat, popüler kitap ve üye geçmişi raporları. Mevcut veriyi içe aktarma (kütüphanede veri yok). Mobil ve tablet arayüzü. Çok dilli arayüz. Buluta dağıtım.

## 2. Paydaşlar ve aktörler

| Aktör | Rolü | Temel hedefi |
|---|---|---|
| Görevli | Günlük masa işleri: üye ve katalog kaydı, ödünç, iade, uzatma, ödeme alma | İşlemi hızlı ve hatasız yapmak |
| Yönetici | Görevlinin yaptıklarına ek olarak: ceza affı, kayıp ve hasar bedeli, ayarlar, kapalı günler, personel hesapları | Kuralları yönetmek, para etkileyen işlemleri denetlemek |
| Üye | Sistemi kullanmaz; verisi tutulur, rıza verdiyse e-posta alır | Hatırlatma alıp cezadan kaçınmak |
| Zamanlanmış görevler | Günlük hatırlatma, anonimleştirme, yedek | İnsan müdahalesi olmadan çalışmak |

## 3. Kullanım senaryoları

1. **Ödünç verme:** Görevli üye kartını okutur. Sistem üyeyi ve engel durumunu gösterir. Görevli nüsha barkodunu okutup onaylar, sistem son tarihi gösterir.
2. **İade:** Görevli nüsha barkodunu okutur. Gecikme varsa sistem cezayı hesaplayıp üyenin borcuna yazar ve gösterir.
3. **Ceza tahsilatı:** Görevli üyenin borcunu açar, masada alınan tutarı kaydeder. Gerekirse yönetici gerekçe yazarak affeder.
4. **Gecikme takibi:** Personel geciken ödünç listesini açar. Sistem rıza veren üyelere hatırlatmayı her gün kendisi gönderir.
5. **Kayıp nüsha:** Yönetici nüshayı kayıp olarak işaretler ve bedeli girer. Nüsha bulunursa rafa döner, ödenmemiş bedel iptal edilir.

## 4. İşlevsel gereksinimler

| ID | Gereksinim | Öncelik | Kaynak | Kabul ölçütü |
|---|---|---|---|---|
| FR-01 | Sistem personelin üye oluşturmasını, güncellemesini ve üyeyi üye no, ad soyad ya da telefonla aramasını sağlamalı; üye için yalnız üye no, ad soyad, telefon ve isteğe bağlı e-posta tutulmalı. | Must | AGENTS.md; faz 1 cevabı (asgari veri) | AC-01 |
| FR-02 | Sistem üyenin pasifleştirilmesini sağlamalı; pasif üye ödünç alamamalı. Açık ödüncü olan üye pasifleştirilememeli; borcu olan üye için önce uyarı gösterilmeli. | Must | Faz 1 cevabı (süresiz üyelik, elle pasifleştirme) | AC-02 |
| FR-03 | Sistem üyenin e-posta rızasını, verildiği tarihi ve geri alındığı tarihi kaydetmeli. | Must | Faz 1 cevabı (rıza alanı) | AC-03 |
| FR-04 | Sistem kitap kaydı (başlık, yazar, isteğe bağlı ISBN, yayınevi, yıl) oluşturmayı, güncellemeyi ve kitabı başlık, yazar, ISBN ya da nüsha barkoduyla aramayı sağlamalı. | Must | AGENTS.md | AC-04 |
| FR-05 | Sistem bir kitaba nüsha eklendiğinde nüshaya benzersiz bir barkod üretmeli ve nüshanın durumunu (Rafta, Ödünçte, Kayıp, Hasarlı, Kayıttan düşmüş) tutmalı. Barkod Code 128, 8 haneli sıralı koddur. | Must | AGENTS.md (copies); plan, fırsat taraması | AC-05 |
| FR-06 | Sistem seçilen nüshaların barkod etiketlerini toplu basılacak bir PDF olarak üretmeli (A4, sayfa başına 3×8 = 24 etiket). | Should | Plan, fırsat taraması (barkod masası) | AC-06 |
| FR-07 | Sistem ödünç verirken son tarihi "bugün + ödünç süresi" olarak belirlemeli; bu tarih kapalı bir güne denk gelirse ilk açık güne kaydırmalı. | Must | Faz 1 cevapları (ayarlanabilir süre; takvim günü + kaydırma) | AC-07 |
| FR-08 | Sistem şu durumlarda ödünç vermeyi reddetmeli ve nedenini göstermeli: üye pasifse, açık ödünç sayısı limite ulaştıysa, gecikmiş ödüncü varsa, borcu borç eşiğine ulaştıysa ya da nüsha Rafta değilse. | Must | Faz 1 cevapları (limit; engelleme) | AC-08 |
| FR-09 | Sistem nüsha barkoduyla iade almalı, ödüncü kapatmalı, nüshayı Rafta durumuna almalı ve gecikme varsa cezayı üyenin borcuna yazmalı. | Must | AGENTS.md | AC-09 |
| FR-10 | Sistem bir ödüncü yalnız bir kez uzatmalı; ödünç gecikmişse ya da üyenin ödenmemiş borcu varsa uzatmayı reddetmeli. Yeni son tarih FR-07'deki kaydırma kuralına uymalı. | Must | Faz 1 cevabı (1 kez, gecikmemişse) | AC-10 |
| FR-11 | Sistem ödünç ve iade ekranlarını barkod okuyucunun klavye girişiyle (okut ve Enter) çalışacak şekilde sunmalı; aynı alanlara elle kod girişi ve aramayla seçim de mümkün olmalı. | Should | Plan, fırsat taraması | AC-11 |
| FR-12 | Sistem gecikme cezasını "gecikme günü × günlük ceza" olarak hesaplamalı ve ödünç başına üst sınırla sınırlamalı. Gecikme günü takvim günüdür. | Must | Faz 1 cevapları (günlük + üst sınır; takvim günü) | AC-12 |
| FR-13 | Sistem ceza ve bedel ödemelerini kısmi olarak kabul etmeli; her ödemeyi tutar, tarih ve işlemi yapan personelle kaydetmeli. Borçtan fazla ödeme kabul edilmemeli. | Must | Faz 1 cevabı (kısmi ödeme) | AC-13 |
| FR-14 | Sistem borç affını yalnız yöneticiye açmalı ve gerekçe girilmeden kaydetmemeli. Af kısmi olabilir; af tutarı borcu aşamaz. | Must | Faz 1 cevabı (gerekçeli af) | AC-14 |
| FR-15 | Sistem ödünçteki bir nüshanın yalnız yönetici tarafından kayıp ya da hasarlı işaretlenmesini sağlamalı. İşaretlemede ödünç kapanmalı, o güne kadar biriken gecikme cezası ve yöneticinin girdiği bedel üyenin borcuna yazılmalı. | Must | Faz 1 cevabı (kayıp/hasarlı + bedel) | AC-15 |
| FR-16 | Sistem hasarlı nüshanın yönetici tarafından rafa döndürülmesini (onarıldı) ya da kayıttan düşülmesini sağlamalı. Kayıp işaretli nüsha bulunduğunda nüshayı Rafta durumuna almalı ve bedelin ödenmemiş kısmını iptal etmeli; ödenmiş kısım için iade kaydını yöneticiye bırakmalı. Gecikme cezası geçerli kalmalı. | Should | Faz 1 cevabı (bulunan nüsha) | AC-16 |
| FR-17 | Sistem bir üyenin güncel borcunu ve borç hareketlerini (ceza, bedel, ödeme, af, iptal) göstermeli. | Must | FR-12…FR-16'dan türetildi | AC-17 |
| FR-18 | Sistem her gün 09:00'da çalışan bir görevle son tarihe 2 gün kala ve gecikmenin 1. gününde, e-posta rızası ve adresi olan üyelere şablonlu hatırlatma göndermeli. Her gönderimi kaydetmeli ve aynı hatırlatmayı aynı ödünç için ikinci kez göndermemeli. | Should | Faz 1 cevabı (hatırlatma zamanı); plan | AC-18 |
| FR-19 | Sistem personelin seçilen geciken ödünçler için hatırlatmayı elle tetiklemesini sağlamalı; rıza kuralı burada da geçerli olmalı. | Should | Plan (B planı) | AC-19 |
| FR-20 | Sistem geciken ödünçleri üye, telefon, kitap, son tarih, gecikme günü ve birikmiş cezayla listelemeli. | Must | Faz 1 cevabı (rapor) | AC-20 |
| FR-21 | Sistem yöneticinin personel hesabı oluşturmasını, rol atamasını (Yönetici, Görevli), hesabı pasifleştirmesini ve parolayı sıfırlamasını sağlamalı. | Must | Faz 1 cevapları (roller; kişisel hesap) | AC-21 |
| FR-22 | Sistem yönetici işlemlerini (af, bedel, ayarlar, kapalı günler, personel yönetimi) sunucu tarafında görevliye kapatmalı. | Must | Faz 1 cevabı (roller) | AC-22 |
| FR-23 | Sistem yöneticinin şu ayarları değiştirmesini sağlamalı: ödünç süresi, aynı anda ödünç limiti, günlük ceza, ödünç başına ceza üst sınırı, borç eşiği, saklama süresi. | Must | Faz 1 cevapları | AC-23 |
| FR-24 | Sistem yöneticinin haftalık kapalı günleri ve tek tek kapalı tarihleri tanımlamasını sağlamalı. | Must | Faz 1 cevabı (kapalı günler) | AC-24 |
| FR-25 | Sistem saklama süresi dolan kişisel verileri günlük bir görevle anonimleştirmeli: pasifleştirmenin üzerinden saklama süresi geçen üyeler ve iadesinin üzerinden saklama süresi geçen ödünçlerin üye bağı. Tutarlar ve istatistik için gerekli alanlar kalmalı. | Must | Faz 1 cevabı (ayarlı anonimleştirme) | AC-25 |
| FR-26 | Sistem şu işlemleri işlemi yapan personel ve zaman damgasıyla denetim kaydına yazmalı: ödeme, af, bedel, kayıp/hasar/bulundu, ayar değişikliği, kapalı gün değişikliği, personel hesabı değişikliği. | Must | Faz 1 cevapları (denetim izi; roller) | AC-26 |
| FR-27 | Sistem personel girişini kişisel hesap ve parolayla yapmalı; 30 dakika işlem yapılmazsa oturumu kapatmalı; 5 ardışık hatalı denemede hesabı geçici olarak kilitlemeli. | Must | Faz 1 cevabı (giriş) | AC-27 |
| FR-28 | Sistem veritabanını her gün otomatik olarak harici diske yedeklemeli, son 30 günün yedeklerini tutmalı ve geri yükleme adımını belgelemeli. | Must | Faz 1 cevabı (yedekleme) | AC-28 |
| FR-29 | Sistem geliştirme ve demo için tohum veri yükleyen bir komut sunmalı; üye verisi her durumda sentetik olmalı, kitap verisi lisansı uygun açık bir veri setinden ya da sentetik olmalı. | Should | Faz 1 cevabı (veri yok; veri seti ya da sentetik) | AC-29 |
| FR-30 | Sistem ISBN girilen kitabın meta verisini dış bir kaynaktan otomatik doldurmalı. | Could | Plan, fırsat taraması (fizibilite) | Faz 2 sonrası |
| FR-31 | Rezervasyon ve bekleme kuyruğu. | Won't | Faz 1 cevabı | – |
| FR-32 | Tahsilat, popüler kitap ve üye ödünç geçmişi raporları. | Won't | Faz 1 cevabı (yalnız geciken ödünçler) | – |
| FR-33 | Üye girişi ve self-servis. | Won't | AGENTS.md (yalnız personel) | – |
| FR-34 | Mevcut veriyi CSV ile içe aktarma. | Won't | Faz 1 cevabı (veri yok) | – |
| FR-35 | Üye tipleri ve tipe göre kural; üyelik geçerlilik süresi. | Won't | Faz 1 cevapları | – |
| FR-36 | Online ödeme. | Won't | Faz 1 (tahsilat masada) | – |

## 5. İşlevsel olmayan gereksinimler

| ID | Nitelik | Gereksinim | Ölçüt | Hedef |
|---|---|---|---|---|
| NFR-01 | Performans verimliliği | Arama, ödünç verme, iade ve uzatma isteklerinin yanıt süresi | Sunucuda ölçülen p95 yanıt süresi | Tasarım ölçeğinde (NFR-02) ve 5 eşzamanlı personelle < 500 ms |
| NFR-02 | Performans verimliliği (kapasite) | Tasarım ölçeği | Kayıt sayısı | 20.000 nüsha, 5.000 üye, 100.000 ödünç kaydı ile NFR-01 sağlanır |
| NFR-03 | Güvenilirlik | Veri kaybı sınırı | RPO | ≤ 24 saat (FR-28) |
| NFR-04 | Güvenilirlik | Yedekten geri dönüş | Belgeli adımla geri yükleme süresi (RTO); test ortamında denenmiş | ≤ 1 saat |
| NFR-05 | Güvenilirlik | Sunucu kapalıyken kaçırılan günlük görevler | Sonraki çalışmada telafi | Hâlâ geçerli hatırlatmalar ve anonimleştirmeler sonraki çalışmada yapılır, tekrar gönderim olmaz |
| NFR-06 | Güvenlik | Parola saklama | Algoritma | Tuzlu, yavaş tek yönlü özet (Argon2id ya da bcrypt); düz ya da geri çözülebilir parola yok |
| NFR-07 | Güvenlik | Yetki denetimi | Yönetici uç noktalarına görevli oturumuyla istek | Her yönetici uç noktası için 403; otomatik testle doğrulanır |
| NFR-08 | Güvenlik (gizlilik, KVKK) | Veri minimizasyonu ve erişim | Tutulan alanlar; erişim yolu | Yalnız FR-01 alanları tutulur; sistem LAN dışından erişime kapalıdır |
| NFR-09 | Etkileşim yeteneği | Arayüz dili ve platform | Dil; tarayıcı; ekran | Yalnız Türkçe; Chrome, Edge ve Firefox'un güncel sürümleri; ≥ 1366 px genişlik |
| NFR-10 | Etkileşim yeteneği | Türkçe arama | Büyük/küçük harf ve Türkçe karakter (İ/i, I/ı) duyarlılığı | "istanbul", "İSTANBUL" ve "İstanbul" aynı sonuçları verir |
| NFR-11 | Etkileşim yeteneği | Barkodla ödünç verme verimi | Fare kullanmadan gereken etkileşim sayısı | Üye okut, nüsha okut, Enter ile onay: en fazla 3 etkileşim |
| NFR-12 | İşlevsel uygunluk (doğruluk) | Para hesapları | Hassasiyet | Kuruş hassasiyetinde, kayan nokta yuvarlama hatası olmadan |
| NFR-13 | Bakım yapılabilirlik | İş kurallarının testleri (son tarih, ceza, engeller, uzatma, borç) | Bu modüllerde dal kapsamı | ≥ %90; TDD ile yazılır |

## 6. Kabul ölçütleri

### AC-01 (FR-01)

```gherkin
# language: tr
Senaryo: Üye kaydı ve arama
  Diyelim ki görevli oturum açmış
  Eğer ki "Ayşe Yılmaz" adlı, telefonu "0555 111 22 33" olan bir üye kaydederse
  O zaman sisteme benzersiz bir üye no ile kaydedilir
  Ve "ayşe" araması bu üyeyi döndürür
```

### AC-02 (FR-02)

```gherkin
# language: tr
Senaryo: Pasif üye ödünç alamaz
  Diyelim ki üye pasifleştirilmiş
  Eğer ki görevli bu üyeye Rafta durumundaki bir nüshayı ödünç vermeye çalışırsa
  O zaman işlem "Üye pasif" nedeniyle reddedilir
```

### AC-03 (FR-03)

```gherkin
# language: tr
Senaryo: Rıza verme ve geri alma
  Diyelim ki üyenin e-posta adresi kayıtlı ve rızası yok
  Eğer ki görevli 2026-11-01'de rızayı işaretler, 2026-12-01'de geri alırsa
  O zaman üye kaydında iki tarih de görünür
  Ve 2026-12-01'den sonra üyeye hatırlatma gönderilmez
```

### AC-04 (FR-04)

```gherkin
# language: tr
Senaryo: Kitabı barkodla bulma
  Diyelim ki "Tutunamayanlar" kitabının barkodu "00000042" olan bir nüshası var
  Eğer ki görevli "00000042" ile arama yaparsa
  O zaman sonuçta "Tutunamayanlar" ve nüshanın durumu görünür
```

### AC-05 (FR-05)

```gherkin
# language: tr
Senaryo: Nüsha ekleme
  Diyelim ki bir kitap kaydı var
  Eğer ki görevli bu kitaba iki nüsha eklerse
  O zaman her nüsha farklı bir barkod alır
  Ve iki nüshanın durumu Rafta olur
```

### AC-06 (FR-06)

```gherkin
# language: tr
Senaryo: Etiket PDF'i
  Diyelim ki 30 nüsha seçilmiş
  Eğer ki personel etiket basımı isterse
  O zaman 30 etiket içeren bir PDF üretilir
  Ve her etiketteki barkod okutulduğunda ilgili nüshanın kodu okunur
```

### AC-07 (FR-07)

```gherkin
# language: tr
Senaryo: Son tarih kapalı güne denk gelir
  Diyelim ki ödünç süresi 13 gün olarak ayarlanmış ve pazar günleri kapalı
  Eğer ki ödünç 2026-11-02 (pazartesi) verilirse
  O zaman hesaplanan 2026-11-15 pazar olduğu için son tarih 2026-11-16 (pazartesi) olur
```

### AC-08 (FR-08)

```gherkin
# language: tr
Senaryo taslağı: Ödünç engelleri
  Diyelim ki üyenin durumu "<durum>"
  Eğer ki görevli Rafta durumundaki bir nüshayı ödünç vermeye çalışırsa
  O zaman işlem "<neden>" nedeniyle reddedilir

  Örnekler:
    | durum                                | neden                  |
    | 3 açık ödünç, limit 3                | Ödünç limiti dolu      |
    | 1 gecikmiş ödünç                     | Gecikmiş ödünç var     |
    | borç 50,00 TL, eşik 50,00 TL         | Borç eşiği aşıldı      |

Senaryo: Nüsha rafta değil
  Diyelim ki nüsha Ödünçte durumunda
  Eğer ki görevli nüshayı başka bir üyeye ödünç vermeye çalışırsa
  O zaman işlem "Nüsha rafta değil" nedeniyle reddedilir
```

### AC-09 (FR-09)

```gherkin
# language: tr
Senaryo: Gecikmeli iade
  Diyelim ki son tarihi 2026-11-16 olan bir ödünç var ve günlük ceza 5,00 TL
  Eğer ki nüsha 2026-11-19'da iade edilirse
  O zaman ödünç kapanır ve nüsha Rafta olur
  Ve üyenin borcuna 15,00 TL ceza yazılır
```

### AC-10 (FR-10)

```gherkin
# language: tr
Senaryo: İkinci uzatma reddedilir
  Diyelim ki ödünç bir kez uzatılmış
  Eğer ki görevli ödüncü yeniden uzatmaya çalışırsa
  O zaman işlem "Uzatma hakkı kullanıldı" nedeniyle reddedilir

Senaryo: Borcu olan üye uzatamaz
  Diyelim ki üyenin 2,00 TL ödenmemiş borcu var ve ödünç gecikmemiş
  Eğer ki görevli ödüncü uzatmaya çalışırsa
  O zaman işlem "Ödenmemiş borç var" nedeniyle reddedilir
```

### AC-11 (FR-11)

```gherkin
# language: tr
Senaryo: Barkodla ödünç
  Diyelim ki ödünç ekranı açık ve imleç üye alanında
  Eğer ki okuyucu üye kodunu, ardından nüsha kodunu Enter ile gönderirse ve görevli Enter'a basarsa
  O zaman ödünç kaydedilir ve fare kullanılmamış olur
```

### AC-12 (FR-12)

```gherkin
# language: tr
Senaryo: Ceza üst sınırı
  Diyelim ki günlük ceza 5,00 TL ve üst sınır 150,00 TL
  Eğer ki nüsha son tarihten 40 gün sonra iade edilirse
  O zaman yazılan ceza 150,00 TL olur

Senaryo: Son tarihte iade
  Diyelim ki son tarih 2026-11-16
  Eğer ki nüsha 2026-11-16'da iade edilirse
  O zaman ceza yazılmaz
```

### AC-13 (FR-13)

```gherkin
# language: tr
Senaryo: Kısmi ödeme
  Diyelim ki üyenin borcu 40,00 TL
  Eğer ki görevli 15,00 TL ödeme kaydederse
  O zaman borç 25,00 TL olur
  Ve ödeme kaydında tutar, tarih ve görevlinin adı görünür
```

### AC-14 (FR-14)

```gherkin
# language: tr
Senaryo: Görevli affedemez
  Diyelim ki görevli oturum açmış
  Eğer ki görevli bir borcu affetmeye çalışırsa
  O zaman işlem yetki hatasıyla reddedilir

Senaryo: Gerekçesiz af
  Diyelim ki yönetici oturum açmış
  Eğer ki yönetici gerekçe yazmadan affetmeye çalışırsa
  O zaman af kaydedilmez ve gerekçe istenir
```

### AC-15 (FR-15)

```gherkin
# language: tr
Senaryo: Kayıp işaretleme
  Diyelim ki 10 gün gecikmiş bir ödünç var ve günlük ceza 5,00 TL
  Eğer ki yönetici nüshayı 120,00 TL bedelle kayıp işaretlerse
  O zaman ödünç kapanır ve nüsha Kayıp olur
  Ve üyenin borcuna 50,00 TL ceza ve 120,00 TL bedel yazılır
```

### AC-16 (FR-16)

```gherkin
# language: tr
Senaryo: Kayıp nüsha bulunur
  Diyelim ki kayıp nüshanın 120,00 TL bedelinin 20,00 TL'si ödenmiş
  Eğer ki personel nüshayı bulundu olarak işaretlerse
  O zaman nüsha Rafta olur
  Ve bedelin ödenmemiş 100,00 TL'si iptal edilir
  Ve ödenmiş 20,00 TL yöneticinin iade kaydına bırakılır
```

### AC-17 (FR-17)

```gherkin
# language: tr
Senaryo: Borç dökümü
  Diyelim ki üyeye 15,00 TL ceza yazılmış, 5,00 TL ödenmiş, 5,00 TL affedilmiş
  Eğer ki görevli üyenin borcunu açarsa
  O zaman güncel borç 5,00 TL ve üç hareket tarihleriyle görünür
```

### AC-18 (FR-18)

```gherkin
# language: tr
Senaryo: Son tarihten önce hatırlatma
  Diyelim ki son tarihi 2026-11-16 olan bir ödünç var ve üyenin rızası ve e-postası var
  Eğer ki günlük görev 2026-11-14'te çalışırsa
  O zaman üyeye "son tarih yaklaşıyor" e-postası gönderilir ve gönderim kaydedilir
  Ve görev aynı gün yeniden çalışırsa ikinci e-posta gönderilmez

Senaryo: Rızasız üye
  Diyelim ki üyenin e-postası var ama rızası yok
  Eğer ki günlük görev çalışırsa
  O zaman üyeye e-posta gönderilmez
```

### AC-19 (FR-19)

```gherkin
# language: tr
Senaryo: Elle hatırlatma
  Diyelim ki geciken listede biri rızalı, biri rızasız iki üye seçili
  Eğer ki personel "hatırlatma gönder" derse
  O zaman yalnız rızalı üyeye e-posta gider
  Ve rızasız üye için "rıza yok" bilgisi gösterilir
```

### AC-20 (FR-20)

```gherkin
# language: tr
Senaryo: Geciken ödünç listesi
  Diyelim ki biri 3, biri 10 gün gecikmiş iki ödünç ve bir gecikmemiş ödünç var
  Eğer ki personel geciken ödünç listesini açarsa
  O zaman yalnız iki gecikmiş ödünç gecikme günü ve birikmiş cezayla listelenir
```

### AC-21 (FR-21)

```gherkin
# language: tr
Senaryo: Personel hesabı pasifleştirme
  Diyelim ki "ali" adlı görevli hesabı var
  Eğer ki yönetici hesabı pasifleştirirse
  O zaman "ali" oturum açamaz
```

### AC-22 (FR-22)

```gherkin
# language: tr
Senaryo: Görevli ayar değiştiremez
  Diyelim ki görevli oturum açmış
  Eğer ki görevli ayar değiştirme isteğini doğrudan sunucuya gönderirse
  O zaman sunucu 403 döndürür ve ayar değişmez
```

### AC-23 (FR-23)

```gherkin
# language: tr
Senaryo: Ödünç süresini değiştirme
  Diyelim ki ödünç süresi 14 gün
  Eğer ki yönetici süreyi 21 gün yaparsa
  O zaman sonraki ödünçlerin son tarihi 21 güne göre hesaplanır
  Ve mevcut ödünçlerin son tarihi değişmez
```

### AC-24 (FR-24)

```gherkin
# language: tr
Senaryo: Tek tarih kapalı gün
  Diyelim ki 2027-10-29 (cuma) kapalı tarih olarak tanımlı ve pazar günleri kapalı
  Eğer ki hesaplanan son tarih 2027-10-29 olursa
  O zaman son tarih 2027-10-30 (cumartesi) olur
```

### AC-25 (FR-25)

```gherkin
# language: tr
Senaryo: Pasif üyenin anonimleştirilmesi
  Diyelim ki saklama süresi 2 yıl ve üye 2026-11-01'de pasifleştirilmiş
  Eğer ki anonimleştirme görevi 2028-11-02'de çalışırsa
  O zaman üyenin adı, telefonu ve e-postası silinir
  Ve üyenin ödünç sayısı ve borç tutarları raporlarda kalır
```

### AC-26 (FR-26)

```gherkin
# language: tr
Senaryo: Af denetim kaydına düşer
  Diyelim ki yönetici "ayse.y" oturum açmış
  Eğer ki yönetici bir borcu gerekçeyle affederse
  O zaman denetim kaydında işlem, tutar, gerekçe, "ayse.y" ve zaman damgası görünür
```

### AC-27 (FR-27)

```gherkin
# language: tr
Senaryo: Hatalı denemede kilit
  Diyelim ki "ali" hesabı aktif
  Eğer ki 5 kez ardışık yanlış parola girilirse
  O zaman hesap geçici olarak kilitlenir ve doğru parola da kabul edilmez

Senaryo: Hareketsizlikte oturum kapanır
  Diyelim ki görevli oturum açmış
  Eğer ki 30 dakika işlem yapılmazsa
  O zaman sonraki istek giriş ekranına yönlendirilir
```

### AC-28 (FR-28)

```gherkin
# language: tr
Senaryo: Yedekten geri yükleme
  Diyelim ki günlük yedek harici diske alınmış
  Eğer ki test ortamında veritabanı silinir ve belgedeki adımlarla son yedek geri yüklenirse
  O zaman yedek anındaki üye, nüsha ve ödünç sayıları aynen geri gelir
  Ve işlem 1 saatten kısa sürer
```

### AC-29 (FR-29)

```gherkin
# language: tr
Senaryo: Tohum veri
  Diyelim ki veritabanı boş
  Eğer ki geliştirici tohum veri komutunu çalıştırırsa
  O zaman sentetik üyeler, kitaplar ve nüshalar yüklenir
  Ve hiçbir üye kaydı gerçek bir kişiye ait değildir
```

## 7. Kısıtlar

- Sistem kütüphanenin yerel ağında, sürekli açık bir sunucuda çalışır; bulut yok.
- Yalnız personel kullanır, yalnız Türkçe arayüz ve masaüstü tarayıcı.
- KVKK: asgari veri, e-posta için açık rıza kaydı, ayarlı süreyle anonimleştirme.
- Geliştirme TDD ile yapılır (AGENTS.md).
- Dil, framework, veritabanı ve e-posta servisi faz 3'te seçilecek. Sunucu donanımı ve işletim sistemi belli olmadığından çözüm Windows ve Linux'ta çalışmalı.
- Saat dilimi Europe/Istanbul; gün sınırı yerel gece yarısıdır.

## 8. Sözlük

| Terim | Anlamı |
|---|---|
| Kitap | Bibliyografik kayıt (başlık, yazar, ISBN…); fiziksel değildir |
| Nüsha | Bir kitabın rafta duran tek fiziksel kopyası; benzersiz barkodu vardır |
| Ödünç | Bir nüshanın bir üyeye verildiği, iade ya da kayıp/hasarla kapanan kayıt |
| Son tarih | Ödüncün cezasız iade edilebileceği son gün |
| Gecikme günü | İade (ya da kayıp işaretleme) tarihi ile son tarih arasındaki takvim günü farkı; son tarihte iade 0 gündür |
| Açık gün / kapalı gün | Kütüphanenin açık olduğu gün; kapalı günler haftalık günler ve tek tek tarihlerle tanımlanır |
| Ceza | Gecikme için yazılan, ödünç başına üst sınırlı borç |
| Bedel | Kayıp ya da hasarlı nüsha için yöneticinin girdiği borç |
| Borç | Bir üyenin ödenmemiş ceza ve bedel toplamı |
| Borç eşiği | Borcun bu tutara ulaşması ödünç vermeyi engeller |
| Af | Yöneticinin gerekçe yazarak borcu silmesi |
| Pasif üye | Ayrılmış, ödünç alamayan üye; saklama süresi pasifleştirmeden başlar |
| Anonimleştirme | Kişisel verinin silinmesi; tutar ve sayımlar kalır |
| Görevli / Yönetici | Personel rolleri; ayrım bölüm 2'de |

## 9. Açık sorular

| # | Soru | Neyi etkiliyor | Durum |
|---|---|---|---|
| 1 | Ücretsiz ISBN meta veri API'leri Türkçe kitapları ne oranda kapsıyor? | FR-30'un önceliği ve yapılıp yapılmayacağı | Faz 2'ye ertelendi |
| 2 | Demo kitap verisi için lisansı uygun, Türkçe kitap içeren açık bir veri seti var mı? | FR-29'un veri kaynağı | Faz 2'ye ertelendi |
| 3 | E-posta hangi yolla gönderilecek (kurum SMTP hesabı ya da e-posta servisi)? | FR-18, FR-19; R-02 | Faz 3'e ertelendi (ADR) |
| 4 | LAN içinde HTTPS kullanılacak mı (kendinden imzalı sertifika ya da düz HTTP)? | NFR-08, parola güvenliği | Faz 3'e ertelendi (ADR) |
| 5 | Sunucunun donanımı ve işletim sistemi ne? | Faz 3 stack seçimi, FR-28 | Belli değil; çapraz platform kısıtı olarak bölüm 7'ye yazıldı |
| 6 | Varsayılan 2 yıllık saklama süresi kurumun KVKK politikasına uyuyor mu? | FR-25 | Açık (kurum teyidi) |
| 7 | Küçük kararlar listesi (varsayılan tutarlar, hesap kuralları, kodlar) | FR-05…FR-27 | Onaylandı (2026-10-31); görev planı bölüm 3 |
