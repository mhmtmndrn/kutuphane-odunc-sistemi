# Kullanım kılavuzu

- **Kime:** Kütüphane personeli (görevli ve yönetici).
- **Kapsam:** Ödünç masasındaki günlük işler ve yöneticinin işleri. Kurulum, güncelleme ve yedekten geri yükleme [kurulum belgesindedir](kurulum.md).
- **Not:** Ekran adları ve düğmeler tırnak içinde, uygulamada göründüğü gibi yazılmıştır.

## Genel

- Uygulama yalnız kütüphanenin ağında çalışır. Masaüstündeki kısayolu açın; adres `https://` ile başlar ve sunucunun IP adresidir (ör. `https://192.168.1.10/`). Tarayıcı sertifika uyarısı gösterirse devam etmeyin, yöneticiye haber verin.
- Üyeler sisteme giriş yapmaz; bütün işlemleri personel yapar.
- Barkod okuyucu klavye gibi çalışır: okutulan kod imlecin bulunduğu alana yazılır ve Enter'a basılmış sayılır. Okuyucu yoksa aynı alanlara kodu elle yazıp Enter'a basabilirsiniz.
- Üst menü: "Ana sayfa", "Ödünç", "İade", "Gecikenler", "Üyeler", "Kitaplar"; yönetici ayrıca "Saklama" ve "Personel"i görür. Sağ üstte "Parola" ve "Çıkış" vardır.
- Tutarlar TL olarak, virgülle yazılır (ör. `12,50`).

## Giriş ve çıkış

1. Kısayolu açın; "Personel girişi" ekranı gelir.
2. Kullanıcı adınızı ve parolanızı yazıp "Giriş yap"a basın.
3. Hesabınızı yönetici yeni açtıysa ya da parolanızı sıfırladıysa, girişten sonra önce yeni parola belirlemeniz istenir. Parola en az 10 karakterdir.
4. İşiniz bitince sağ üstteki "Çıkış"a basın. 30 dakika işlem yapılmazsa oturum kendiliğinden kapanır.

Arka arkaya 5 yanlış parola girilirse hesap 15 dakika kilitlenir ("Hesap geçici olarak kilitlendi. 15 dakika sonra yeniden deneyin."). Beklemek istemezseniz yönetici "Personel" ekranından kilidi kaldırabilir. Parolanızı değiştirmek için sağ üstteki "Parola"yı kullanın.

## Ödünç verme

1. "Ödünç"e basın. İmleç "Üye kartı, üye no, telefon ya da ad" alanındadır.
2. Üye kartını okutun. Kart yoksa üye no'yu, telefonu ya da adı yazıp Enter'a basın. Birden çok üye çıkarsa listeden doğru üyeyi seçin.
3. Üye paneli açılır: üye no, ad soyad, borç ve açık ödünçler. Ödünce engel bir durum varsa (ör. "Ödünç limiti dolu", "Gecikmiş ödünç var", "Borç eşiği aşıldı", "Üye pasif") panelde yazar; engel kalkmadan ödünç verilemez.
4. **Üyeye adını sorun.** Kartta ad yazmaz; kaybolan bir kart başkası tarafından kullanılabilir. Üyeye adını sor, ekrandaki adla karşılaştır; tutmuyorsa ödünç vermeyin ve kimliğini doğrulayın.
5. İmleç "Nüsha barkodu ya da kitap" alanına geçer. Kitabın etiketindeki barkodu okutun. Etiket okunmuyorsa başlığı yazıp Enter'a basın ve "Raftaki nüshalar" listesinden nüshayı seçin.
6. Önizlemede başlık, nüsha ve son tarih görünür. "Onayla"ya basın (okuyucuyla çalışırken Enter yeterlidir).
7. "Son tarih …" mesajı görünür. Son tarihi üyeye söyleyin. Son tarih kütüphanenin kapalı olduğu bir güne denk gelirse kendiliğinden sonraki açık güne kayar.

Aynı üyeye başka kitap vermek için 5. adımdan devam edin; yeni üye için "Ödünç"e yeniden basın.

## İade

1. "İade"ye basın. İmleç "Nüsha barkodu ya da kitap" alanındadır.
2. Kitabın barkodunu okutun. Etiket okunmuyorsa başlığı yazın ve "Ödünçteki nüshalar" listesinde doğru satırdaki "İade al"a basın.
3. Gecikme yoksa "İade alındı" görünür. Gecikme varsa ceza kendiliğinden yazılır ve mesajda tutarı görünür ("İade alındı; … ceza yazıldı"). Cezayı hemen ödemek isteyen üye için [Ödeme](#ödeme) bölümüne geçin.

Gecikme günü, son tarihten sonraki takvim günleridir; yönetici tarafından eklenmiş kapalı tarihler (tatil, beklenmedik kapanış) sayılmaz. Ödünç başına ceza, ayarlardaki üst sınırı geçmez.

## Uzatma

1. Üyenin sayfasını açın ("Üyeler"de arayın) ya da "Ödünç" ekranında üyeyi getirin; açık ödünçler listelenir.
2. Uzatılacak kitabın satırındaki "Uzat"a basın.
3. "Uzatıldı; yeni son tarih …" mesajını üyeye söyleyin.

Her ödünç bir kez uzatılabilir. Gecikmiş bir ödünç ya da borcu olan üyenin ödüncü uzatılamaz; ekranda nedeni yazar ("Uzatma hakkı kullanıldı", "Ödünç gecikmiş", "Ödenmemiş borç var").

## Üye kaydı ve e-posta rızası

**Yeni üye:**

1. "Üyeler" → "Yeni üye".
2. "Ad soyad" ve "Telefon" zorunludur; "E-posta" isteğe bağlıdır. Yalnız bu bilgiler alınır; kimlik numarası ya da adres sorulmaz.
3. "Kaydet"e basın; üye no kendiliğinden verilir.
4. Üyenin kartını basın (bkz. [Etiket ve kart basımı](#etiket-ve-kart-basımı)).

**Üye bilgilerini değiştirme:** Üyenin sayfasında "Düzenle". E-posta silinirse üyenin e-posta rızası da o gün geri alınmış sayılır.

**E-posta rızası:** Hatırlatma e-postası yalnız e-posta adresi olan ve rıza veren üyeye gider.

1. Üyenin sayfasında "E-posta rızası" bölümüne gidin. Rıza için e-posta adresi gereklidir.
2. "Tarih" alanına üyenin rızasını verdiği (ya da geri aldığı) günü yazın; bugün varsayılandır.
3. "Rıza ver" ya da "Rızayı geri al"a basın.

Gelecek bir tarih kabul edilmez. **Geçmiş tarihli rıza** kaydı kabul edilir ve geçmişe yazılır, ama üyenin bugünkü rıza durumunu yalnız **en yeni tarihli** kayıt belirler. Bu yüzden mevcut kayıttan daha eski bir tarihle girilen rıza ya da geri alma, geçerli durumu değiştirmez. Örnek: üye 10 Mart'ta rızasını geri almışsa, sonradan 1 Mart tarihli "Rıza ver" girmek rızayı açmaz; rıza ancak 10 Mart'tan sonraki bir tarihle verilirse açılır.

**Pasifleştirme ve aktifleştirme:** Kütüphaneden ayrılan üyeyi sayfasındaki "Pasifleştir" ile pasifleştirin. Açık ödüncü olan üye pasifleştirilemez; borcu olan üye için "Borç olduğunu biliyorum; üyeyi yine de pasifleştir" kutusu işaretlenir. Pasif üye geri gelirse "Aktifleştir". Saklama süresi dolan pasif üyelerin kişisel bilgileri sistem tarafından kendiliğinden silinir (anonimleştirme).

## Ödeme

1. Üyenin sayfasında "Borç dökümü"ne basın. "Güncel borç" ve bütün hareketler görünür.
2. "Ödeme al" bölümüne alınan tutarı yazın ve "Ödemeyi kaydet"e basın.
3. "Ödeme alındı: …" mesajı görünür. Ödeme en eski borçtan başlayarak kapatılır.

Borçtan fazla ödeme kabul edilmez. Borcun bir kısmı ödenebilir. **Af** (borcun silinmesi), **para iadesi** ve **bedel iptali** yalnız yöneticinin ekranında görünür; gerekçe yazılır ve denetim kaydına düşer.

## Kayıp ve hasar

Kayıp ve hasar işaretlemesini yalnız yönetici yapar; görevli yöneticiye haber verir.

1. Nüshanın sayfasını açın: "Kitaplar"da barkodu arayıp nüshanın barkoduna basın.
2. **Kayıp:** "Bedel (TL)" alanına üyeden istenecek bedeli, istenirse "Not"u yazın ve "Kayıp"a basın. Nüsha ödünçteyse ödünç kapanır; o güne kadar birikmiş gecikme cezası ve bedel üyenin borcuna yazılır.
3. **Hasar:** Aynı biçimde "Hasarlı"ya basın. Hasarlı nüsha daha sonra "Onarıldı" ile rafa döner ya da "Kayıttan düş" ile kayıttan düşer.
4. **Bulundu:** Kayıp sayılan kitap bulunursa herhangi bir personel nüsha sayfasında "Bulundu"ya basar; nüsha rafa döner. Bedel ödenmişse para iadesi yöneticinin kararıdır.

## Etiket ve kart basımı

Etiketler ve kartlar PDF olarak açılır; A4 etiket kâğıdına (sayfa başına 24 etiket) tarayıcının yazdır komutuyla, ölçek "Gerçek boyut" (%100) seçilerek basılır.

**Nüsha etiketleri:**

- Bir kitabın nüshaları: Kitabın sayfasında "Nüsha ekle" ile nüsha ekleyin, "Nüshalar" listesinde basılacakları işaretleyip "Etiket bas"a basın.
- Toplu: "Kitaplar" → "Nüsha etiketleri"; "Başlangıç barkodu" ve "Bitiş barkodu"nu yazıp "Etiket bas". Kayıttan düşmüş nüshalar atlanır; bir seferde en çok 240 etiket basılır.

**Üye kartları:**

- "Üyeler" → "Üye kartları"; "Başlangıç üye no" ve "Bitiş üye no" ile "Kart bas". Arama sonuçlarında işaretlenen üyeler için de "Kart bas" kullanılabilir. Pasif üyeler atlanır.
- Kartta yalnız kütüphane adı, üye no ve barkod vardır; ad yazmaz. **Kayıp kart** aynı üye no ile yeniden basılır; eski kart da geçerli kalır. Bu yüzden ödünçte üyeye adını sormak önemlidir.

## Gecikenler ve hatırlatma

- "Gecikenler" listesi son tarihi geçmiş ödünçleri, gecikme gününü ve birikmiş cezayı gösterir.
- Sistem her sabah son tarihe 2 gün kalan ve gecikmenin ilk gününe giren ödünçler için rızası olan üyelere kendiliğinden e-posta gönderir.
- Elle hatırlatma için satırları işaretleyip "Hatırlatma gönder"e basın. "e-posta yok" ya da "rıza yok" etiketli üyelere e-posta gitmez; onları telefonla arayın.

## Yönetici işleri

Bu bölümdeki ekranları yalnız yönetici rolündeki personel görür.

### Ana sayfa uyarıları

Yöneticinin ana sayfası son bina dışı yedeğin (şifreli dışa aktarma) tarihini ve yedek uyarılarını gösterir:

- **"Günlük yedek henüz alınmadı", "Son günlük yedek başarısız oldu", "Günlük yedek 26 saatten eski":** Harici yedek diskinin takılı ve açık olduğunu kontrol edin. Sorun sürerse kurulumu yapan kişiye haber verin ([kurulum belgesi](kurulum.md), "Sorun giderme").
- **"Bina dışı yedek henüz alınmadı", "Bina dışı yedek 7 günden eski":** Sistem her pazartesi gecesi şifreli bir dışa aktarma dosyası üretir. Haftada bir en yeni dosyayı USB belleğe kopyalayıp bina dışına götürün ve öbür belleği geri getirin. Dışa aktarma dosyası yoksa yedek diski kontrol edin.

Dışa aktarma parolasını USB bellekle birlikte taşımayın; kâğıttaki kopyası ayrı ve güvenli bir yerdedir. Parola kaybolursa bina dışı yedek açılamaz.

### Kapalı günler

"Ana sayfa" → "Kapalı günler":

- **Haftalık kapalı günler:** Kütüphanenin her hafta kapalı olduğu günleri işaretleyip "Kaydet". En az bir gün açık kalmalıdır. Son tarihler bu günlere denk gelmez.
- **Kapalı tarihler:** Tatil ya da beklenmedik kapanış için "Tarih" ve isteğe bağlı "Not" yazıp "Ekle". Bu tarihler hem son tarih hesabında atlanır hem de gecikme cezasından düşülür: kütüphane kapalıyken üyeye ceza yazılmaz.
- **Geçmiş kapalı tarihleri silmeyin.** Açık ödünçlerin cezası kapalı tarih kayıtlarına göre hesaplanır; geçmiş bir kapalı tarih silinirse o günü kapsayan açık ödünçlerin cezası artar. Yanlış girilmiş **gelecek** bir tarihi "Sil" ile kaldırabilirsiniz. Daha önce yazılmış (iadesi alınmış) cezalar değişmez.

### Ayarlar

"Ana sayfa" → "Ayarlar": ödünç süresi, aynı anda ödünç limiti, günlük ceza, ödünç başına ceza üst sınırı, borç eşiği, saklama süresi ve kartlara basılan kütüphane adı. "Kaydet"ten sonra değişiklikler yalnız **sonraki** ödünçlere uygulanır; mevcut ödünçlerin son tarihi ve ceza oranı değişmez. Saklama süresini değiştirmeden önce kurumun KVKK politikasına bakın.

### Personel

"Personel" ekranında hesap açma, rol değiştirme, pasifleştirme, parola sıfırlama ve kilit kaldırma yapılır. Sıfırlanan parolayla giren personelden yeni parola istenir. Son aktif yönetici pasifleştirilemez.

### Saklama ve denetim kaydı

- **"Saklama":** Saklama süresi dolduğu hâlde borcu olduğu için anonimleştirilmesi ertelenen üyeler. Borç ödenir ya da affedilirse üye sonraki gece anonimleştirilir.
- **"Denetim kaydı":** Ayar, kapalı gün, personel, af, para iadesi, kayıp ve hasar gibi işlemlerin kim tarafından ne zaman yapıldığı.
