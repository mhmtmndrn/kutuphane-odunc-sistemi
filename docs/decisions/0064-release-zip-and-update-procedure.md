# ADR-0064: Kod sunucuya bir etiketten üretilen zip arşiviyle gelir; belge güncelleme yordamını da verir

- **Durum:** Kabul edildi (2026-11-01)
- **Kaynak:** Kullanıcı, 2026-11-01 yerel oturumunda soru penceresinden seçti (G19 açılışı).

## Bağlam

- Depo özeldir (GitHub). Sunucunun depoya erişmesi için bir erişim anahtarı gerekir; anahtar sunucuda kalır ve kod geçmişinin tamamını açar.
- Kütüphane sunucusunda git kurulu olmayabilir. Kod, kurulumdan sonra da güncellenecektir (hata düzeltmeleri, faz 6 bulguları).
- Güncelleme sırasında migration çalışır; plan G19 migration öncesinde elle `backup_db` ister. Uygulama açıkken geri yükleme ve ikinci süreç kilitle engellenir (KL-4).

## Değerlendirilen seçenekler

1. **Etiketten `git archive` zip'i, ilk kurulum ve güncelleme yordamı** (seçildi): Geliştirici makinesinde `git archive` ile bir sürüm arşivi üretilir; arşiv USB bellek ya da ağ paylaşımıyla sunucuya taşınır. Sunucuda git ve GitHub erişimi gerekmez.
2. **`git clone`:** Güncelleme `git pull` ile yapılır. Reddedildi: özel depo için sunucuya bir erişim anahtarı konması gerekir.
3. **Yalnız ilk kurulumu belgelemek:** Reddedildi: güncelleme sırasındaki yedek, migration ve `collectstatic` adımları unutulursa veri kaybı ya da bozuk statik dosyalar oluşur.

## Karar

- Sürüm etiketi `vX.Y.Z` biçimindedir. Arşiv şu komutla üretilir: `git archive --format=zip --prefix=library/ <etiket> -o library-<etiket>.zip`.
- Arşiv sunucuda açılır; `library/` klasörü uygulama klasörünün (`C:\Kutuphane\app`, `/opt/library/app`) yerini alır.
- `docs/kurulum.md` ilk kurulumu ve güncellemeyi ayrı yordamlar olarak verir. Güncelleme sırası: servisi durdur → `backup_db` → zip'i aç → `pip install -r requirements.txt` → `migrate` → `collectstatic` → servisi başlat → kontrol.
- G19 bu yolu yalnız belgeler; ilk etiket faz 6'da kullanıcı onayıyla atılır.

## Sonuçlar

- **Olumlu:** Sunucuda kimlik bilgisi ve git gerekmez; arşiv yalnız o sürümün dosyalarını taşır (geçmiş yoktur). Güncelleme her zaman bir yedekle başlar.
- **Olumsuz / riskler:**
  - Arşiv elle taşınır; yanlış sürümün açılması mümkündür. Belge, arşiv adındaki etiketin kontrolünü ister.
  - Eski uygulama klasörü güncellemeden sonra elle silinir.

## İzlenebilirlik

- **Gereksinim:** FR-28, NFR-04. Plan G19.
- **Bağlantılı:** ADR-0002, ADR-0060
