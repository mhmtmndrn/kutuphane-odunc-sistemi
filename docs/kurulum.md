# Kurulum ve işletim

- **Kime:** Sunucuyu kuran ve bakımını yapan kütüphane yöneticisi ya da teknik destek.
- **Kapsam:** İlk kurulum, personel bilgisayarlarının hazırlanması, güncelleme, yedekler, bina dışı kopya ve yedekten geri yükleme.
- **Yapı:** Önce iki platformda ortak olan adımlar gelir. Platforma özgü komutlar [Windows](#windows) ve [Linux](#linux) bölümlerindedir; iki bölüm aynı alt başlıklara sahiptir ([ADR-0060](decisions/0060-install-doc-common-body-two-platforms.md)).
- **Günlük kullanım** için [kullanım kılavuzuna](kullanim-kilavuzu.md) bakın.

## Genel bakış

Sistem sunucuda iki servis olarak çalışır ([architecture §8](architecture.md)):

- **`library-app`:** waitress uygulama sunucusu. Yalnız `127.0.0.1:8000` adresini dinler; LAN'dan doğrudan erişilemez. Günlük yedek, haftalık dışa aktarma, hatırlatma ve saklama görevlerini çalıştıran zamanlayıcı da bu servistedir (`LIBRARY_SCHEDULER_ENABLED=1`).
- **`library-caddy`:** Caddy. Sunucunun LAN adresinde 80 ve 443 portlarını dinler, HTTPS'i kendi yerel sertifika otoritesiyle (CA) sağlar, `/static/` dosyalarını doğrudan sunar ve diğer istekleri `library-app`'e iletir. HTTP istekleri HTTPS'e yönlendirilir.

İki servis de ayrı bir yerel hesapla çalışır: Windows'ta `library-svc`, Linux'ta `library` ([ADR-0062](decisions/0062-service-account.md)). Çökünce kendiliğinden yeniden başlar. Caddy, uygulama servisine bağlıdır; önce uygulama başlar.

Personel uygulamaya sunucunun sabit IP adresiyle erişir, ör. `https://192.168.1.10/` ([ADR-0061](decisions/0061-access-by-static-ip.md)). Sistem yalnız LAN içindir; yönlendiricide dışarıya hiçbir port açılmaz (NFR-08).

Caddy'nin erişim logu bilerek kapalıdır: arama sorguları üye adı ve telefonu taşır ([ADR-0065](decisions/0065-caddy-no-access-log.md)). İşlemlerin izi uygulamadaki denetim kaydındadır.

## Ön koşullar

- **Sunucu:** Windows 10/11 ya da Windows Server; veya Debian 12 gibi systemd kullanan bir Linux. Kütüphanede sürekli açık kalan bir bilgisayar yeterlidir.
- **Python 3.11** (64 bit). Bağımlılıkların sürümleri `requirements.txt`'te sabittir.
- **Yerel disk:** Veritabanı (SQLite) sunucunun kendi diskinde durur. Ağ paylaşımına ya da USB belleğe konmaz; SQLite'ın WAL kipi ağ dosya sistemlerinde güvenli çalışmaz.
- **Harici yedek diski:** Günlük yedekler ve haftalık şifreli dışa aktarmalar için sunucuya sürekli takılı bir disk. Windows'ta NTFS, Linux'ta ext4 biçimli olmalıdır (klasör izinleri için).
- **En az iki USB bellek:** Bina dışı kopya rotasyonu için (bkz. [Yedekler ve bina dışı kopya](#yedekler-ve-bina-dışı-kopya)).
- **Kurum SMTP hesabı:** Hatırlatma e-postaları için sunucu adı, port (587, STARTTLS), kullanıcı adı, parola ve gönderen adresi (ADR-0004).
- **Yönlendiriciye yönetici erişimi:** Sunucunun IP adresini DHCP rezervasyonuyla sabitlemek için.
- **Sürüm arşivi:** `library-vX.Y.Z.zip` (bkz. [Sürüm arşivi](#sürüm-arşivi)). Sunucuda git ya da GitHub erişimi gerekmez ([ADR-0064](decisions/0064-release-zip-and-update-procedure.md)).
- **Araçlar:** Caddy 2.11.7 ve Windows'ta WinSW 2.12.0. Sürümler sabittir; bağlantılar platform bölümlerindedir ([ADR-0063](decisions/0063-tool-versions-winsw-caddy.md)). Caddy ve WinSW kendiliğinden güncellenmez; yeni sürüm önce bir test ortamında `caddy validate` ile denenir, sonra bu belge ve bağlantılar güncellenir.

## Klasör düzeni

| İçerik | Windows | Linux | Kim yazar |
|---|---|---|---|
| Uygulama kodu (sürüm arşivi) | `C:\Kutuphane\app` | `/opt/library/app` | Yalnız yönetici |
| Python sanal ortamı | `C:\Kutuphane\venv` | `/opt/library/venv` | Yalnız yönetici |
| Veritabanı | `C:\Kutuphane\data` | `/var/lib/library/data` | Servis hesabı |
| Statik dosyalar (`collectstatic`) | `C:\Kutuphane\static` | `/var/lib/library/static` | `collectstatic` |
| Gizli değerler | `C:\Kutuphane\secrets`, `C:\Kutuphane\winsw\*.xml` | `/etc/library` | Yalnız yönetici |
| Caddy ve yerel CA | `C:\Kutuphane\caddy` | `/usr/local/bin/caddy`, `/var/lib/library/caddy` | Servis hesabı |
| Servis tanımları ve loglar | `C:\Kutuphane\winsw` | `/etc/systemd/system`, journald | Yönetici; loglar servis |
| Günlük yedekler | Harici disk, ör. `E:\Kutuphane\backups` | `/mnt/library-backup/backups` | Servis hesabı |
| Şifreli dışa aktarmalar | Harici disk, ör. `E:\Kutuphane\exports` | `/mnt/library-backup/exports` | Servis hesabı |

Veri, gizli değer ve Caddy klasörleri yalnız yöneticilere ve servis hesabına açıktır. Caddy klasörü yerel CA'nın özel anahtarını taşır.

Yedek ve dışa aktarma klasörleri **elle açılır**. Uygulama bu klasörleri kendisi oluşturmaz: disk takılı değilken sistem diskine yedek yazılmasın diye klasör yoksa yedek komutu "… klasörü bulunamadı" hatasıyla durur ve yöneticinin ana sayfasında uyarı çıkar.

## Ortam değişkenleri

Uygulama bütün yapılandırmayı ortam değişkenlerinden okur (architecture §6.4). Eksik bir değişken, süreci "Eksik ortam değişkeni: <ad>" hatasıyla durdurur.

- **Windows'ta** değerler WinSW XML'lerindeki `<env>` öğelerindedir: `C:\Kutuphane\winsw\library-app.xml` ve `library-caddy.xml`. Depodaki örneklerde (`deploy/winsw/`) kuruma özgü ve gizli değerler `__DOLDUR__` olarak bırakılmıştır.
- **Linux'ta** iki servis de `/etc/library/library.env` dosyasını okur. Örneği `deploy/library.env.example`'dır; her değişkenin üstünde bir açıklama satırı vardır, gizli değerler boştur.

| Değişken | Anlamı | Örnek |
|---|---|---|
| `DJANGO_SETTINGS_MODULE` | Ayar modülü; üretimde her zaman bu değer | `library_site.settings.prod` |
| `LIBRARY_SECRET_KEY` | Django gizli anahtarı (aşağıda nasıl üretileceği) | — |
| `LIBRARY_DB_PATH` | SQLite veritabanı dosyası (yerel disk) | `C:\Kutuphane\data\library.sqlite3` |
| `LIBRARY_ALLOWED_HOSTS` | Sunucunun sabit IP adresi | `192.168.1.10` |
| `LIBRARY_BACKUP_DIR` | Günlük yedek klasörü (harici disk) | `E:\Kutuphane\backups` |
| `LIBRARY_EXPORT_DIR` | Haftalık şifreli dışa aktarma klasörü (harici disk) | `E:\Kutuphane\exports` |
| `LIBRARY_EXPORT_PASSPHRASE_FILE` | Dışa aktarma parolasının bulunduğu dosya | `C:\Kutuphane\secrets\export-passphrase.txt` |
| `LIBRARY_EMAIL_HOST` | Kurum SMTP sunucusu | `smtp.kurum.example` |
| `LIBRARY_EMAIL_PORT` | SMTP portu | `587` |
| `LIBRARY_EMAIL_USER` | SMTP kullanıcı adı | — |
| `LIBRARY_EMAIL_PASSWORD` | SMTP parolası | — |
| `LIBRARY_EMAIL_FROM` | Hatırlatma e-postalarının gönderen adresi | `kutuphane@kurum.example` |
| `LIBRARY_SCHEDULER_ENABLED` | Zamanlayıcı; yalnız uygulama servisinde `1` | `1` |
| `LIBRARY_STATIC_ROOT` | `collectstatic` çıktısı; Caddy buradan sunar | `C:\Kutuphane\static` |
| `LIBRARY_HOST` | Caddy site adresi: sunucunun sabit IP adresi | `192.168.1.10` |
| `LIBRARY_BIND` | Caddy'nin dinlediği LAN adresi; `LIBRARY_HOST` ile aynı | `192.168.1.10` |

`LIBRARY_HOST` ve `LIBRARY_BIND` yalnız Caddy servisinde, diğerleri uygulama servisinde kullanılır; `LIBRARY_STATIC_ROOT` ikisinde de aynı olmalıdır. `LIBRARY_HOST`, `LIBRARY_BIND` ve `LIBRARY_ALLOWED_HOSTS` aynı IP adresidir.

`LIBRARY_SECRET_KEY` için bir kez şu komutun çıktısını kullanın ve kimseyle paylaşmayın:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Dışa aktarma parolası, parola dosyasının ilk satırıdır. Uzun ve tahmin edilemez bir parola seçin; aynı parolayı ayrıca kâğıda yazıp sunucudan ve USB belleklerden ayrı bir yerde, kapalı zarfta saklayın. Parola kaybolursa şifreli dışa aktarmalar açılamaz.

## Sürüm arşivi

Kod sunucuya, depodaki bir sürüm etiketinden (`vX.Y.Z`) üretilen zip arşiviyle gelir ([ADR-0064](decisions/0064-release-zip-and-update-procedure.md)). Arşiv, geliştirici bilgisayarında depo klasöründe üretilir:

```bash
git archive --format=zip --prefix=library/ v1.0.0 -o library-v1.0.0.zip
```

Arşiv USB bellekle ya da ağ paylaşımıyla sunucuya taşınır. İçinde tek bir `library/` klasörü vardır; bu klasör sunucuda uygulama klasörünün (`C:\Kutuphane\app`, `/opt/library/app`) yerini alır. Arşivin adındaki etiketi, kurulacak sürümle karşılaştırın.

## İlk kurulum

Aşağıdaki sıra iki platformda aynıdır. Her adımın komutları platform bölümündedir ([Windows](#windows), [Linux](#linux)).

**Hazırlık:**

- **Sabit IP:** Yönlendiricinin yönetim sayfasında sunucunun ağ kartı için bir DHCP rezervasyonu açın (ör. `192.168.1.10`). Bu adres `LIBRARY_HOST`, `LIBRARY_BIND` ve `LIBRARY_ALLOWED_HOSTS` değeridir ([ADR-0061](decisions/0061-access-by-static-ip.md)).
- **Servis hesabı ve klasörler:** Platform bölümündeki "Hesap" ve "Klasörler ve izinler" adımları.
- **Kod:** Sürüm arşivini uygulama klasörüne açın (platform bölümünde "Sürüm arşivinin açılması").
- **Ortam değişkenleri:** WinSW XML'lerini ya da `library.env`'i doldurun; dışa aktarma parola dosyasını oluşturun.

**Kurulum adımları** (architecture §8):

1. **Python 3.11 ve sanal ortam:** Python 3.11'i kurun, sanal ortamı oluşturun ve bağımlılıkları sabit sürümleriyle yükleyin: `python -m pip install -r requirements.txt`.
2. **`migrate` ve `collectstatic`:** Platform bölümündeki "Komutların elle çalıştırılması" ile bir komut oturumu açın ve şunları çalıştırın:

   ```bash
   python manage.py migrate
   ```

   ```bash
   python manage.py collectstatic --noinput
   ```

3. **İlk yönetici hesabı:** Aynı oturumda ilk yöneticiyi oluşturun. Diğer personel hesaplarını bu hesapla uygulamadaki "Personel" ekranından açın.

   ```bash
   python manage.py createsuperuser
   ```

   `load_seed_data` (demo verisi) yalnız demo ve test ortamları içindir; gerçek veritabanında çalıştırmayın.
4. **Caddy ve kök sertifika:** Caddy 2.11.7'yi indirip özetini doğrulayın ve yerine koyun. Caddy ilk kez başladığında yerel CA'yı ve kök sertifikayı (`root.crt`) üretir; kök sertifika 5. adımdan sonra [personel bilgisayarlarına](#personel-bilgisayarları) yüklenir.
5. **Servisler:** `library-app` ve `library-caddy` servislerini kaydedin. Servisleri başlatmadan önce 6. adımı tamamlayın; zamanlayıcı ilk gece yedek klasörünü bulamazsa yedek başarısız olur.
6. **Yedek diski ve dışa aktarma klasörü:** Harici diski bağlayın, `LIBRARY_BACKUP_DIR` ve `LIBRARY_EXPORT_DIR` klasörlerini elle açın ve servis hesabına yazma izni verin. Ardından servisleri başlatın.
7. **NTP:** Sistem saatinin NTP ile eşitlendiğini doğrulayın. Son tarih, ceza, hatırlatma ve yedek zamanları sunucu saatine dayanır.

**Kontrol:** Kurulumdan sonra şunları deneyin:

- Bir personel bilgisayarında `https://<IP>/` giriş ekranını sertifika uyarısı olmadan açar; `http://<IP>/` HTTPS'e yönlendirilir.
- `curl -k https://<IP>/static/css/app.css` → 200.
- `https://<IP>/admin/` → 404 (yönetim paneli üretimde yoktur).
- Sunucuda waitress yalnız `127.0.0.1:8000`'i, Caddy yalnız `<IP>:80` ve `<IP>:443`'ü dinler (platform bölümünde "Kontrol").
- LAN dışından (ör. cep telefonunun mobil verisiyle) sunucuya ulaşılamaz.
- Ertesi sabah yöneticinin ana sayfasında yedek uyarısı yoktur ve yedek klasöründe `library-YYYYMMDD.sqlite3` dosyası vardır.

## Personel bilgisayarları

Personel bilgisayarlarının Windows olduğu varsayılmıştır. Her bilgisayarda bir kez:

1. **Kök sertifika:** Sunucudaki `root.crt` dosyasını (yeri platform bölümünde, "Caddy") USB bellekle bilgisayara kopyalayın. Yönetici olarak açılmış bir komut isteminde, dosyanın bulunduğu klasörde:

   ```bat
   certutil -addstore -f Root root.crt
   ```

   Kök sertifika gizli değildir; özel anahtar (`root.key`) sunucudan hiçbir zaman çıkarılmaz.
2. **Firefox:** Firefox Windows'un sertifika deposunu kullanmıyorsa `about:config` sayfasında `security.enterprise_roots.enabled` değerini `true` yapın ya da kök sertifikayı Firefox ayarlarındaki "Sertifikaları göster → Yetkililer → İçe aktar" ile ekleyin. Chrome ve Edge Windows deposunu kullanır.
3. **Kısayol:** Masaüstüne `https://<IP>/` adresini açan bir kısayol koyun (tarayıcıda adresi açıp adres çubuğundaki kilidi masaüstüne sürükleyin).

Yeni bir personel bilgisayarı eklendiğinde bu üç adım o bilgisayarda da yapılır. Caddy'nin veri klasörü kaybolursa yeni bir kök sertifika üretilir ve bütün bilgisayarlara yeniden yüklenmesi gerekir; bu yüzden klasör [yedeklenir](#yedekler-ve-bina-dışı-kopya).

## Güncelleme

Yeni bir sürüm arşivi geldiğinde ([ADR-0064](decisions/0064-release-zip-and-update-procedure.md)). Personele kısa bir kesinti olacağını haber verin; işlem genellikle 10–15 dakika sürer.

1. **Servisi durdurun:** Önce `library-caddy`, sonra `library-app` (platform bölümünde "Servisler").
2. **Yedek alın:** "Komutların elle çalıştırılması" ile komut oturumu açın ve migration'dan önce elle yedek alın. Çıktıdaki "Yedek alındı: …" satırını not edin; aynı günün gece yedeğinin üzerine yazar.

   ```bash
   python manage.py backup_db
   ```

3. **Zip'i açın:** Eski uygulama klasörünün adını `app-old` yapın ve yeni arşivi açın (platform bölümünde "Sürüm arşivinin açılması").
4. **Bağımlılıkları yükleyin:** Linux'ta bu adım root olarak çalıştırılır (platform bölümüne bakın).

   ```bash
   python -m pip install -r requirements.txt
   ```

5. **Veritabanını güncelleyin:**

   ```bash
   python manage.py migrate
   ```

6. **Statik dosyaları toplayın:**

   ```bash
   python manage.py collectstatic --noinput
   ```

7. **Yapılandırmayı karşılaştırın:** Yeni sürümün `deploy/` klasöründeki dosyaları (WinSW XML'leri, systemd unit'leri, `library.env.example`) kurulu olanlarla karşılaştırın. Yeni bir ortam değişkeni ya da ayar varsa kurulu dosyaya ekleyin. Caddyfile uygulama klasöründen okunduğu için ayrıca kopyalanmaz.
8. **Servisi başlatın:** Önce `library-app`, sonra `library-caddy`.
9. **Kontrol:** Giriş yapın, ana sayfayı ve bir üye aramasını açın; [İlk kurulum](#ilk-kurulum) bölümündeki "Kontrol" maddelerinden statik dosya ve `/admin/` denemelerini tekrarlayın.

Birkaç gün sorun çıkmazsa `app-old` klasörünü silin. **Geri dönüş:** Güncelleme başarısız olursa servisleri durdurun, yeni klasörü silip `app-old`'un adını `app` yapın, 2. adımdaki yedeği [geri yükleyin](#yedekten-geri-yükleme) ve servisleri başlatın.

## Yedekler ve bina dışı kopya

Uygulama servisindeki zamanlayıcı şunları kendisi yapar (sunucu kapalıysa açılışta ve saatlik telafiyle):

- **Her gece 02.00:** Günlük yedek, `LIBRARY_BACKUP_DIR` içinde `library-YYYYMMDD.sqlite3`. 30 günden eski yedekler silinir.
- **Her pazartesi 03.00:** Son günlük yedekten şifreli dışa aktarma, `LIBRARY_EXPORT_DIR` içinde `library-export-YYYYMMDD.libx`. 56 günden eskiler silinir.
- **Her gece 02.30:** Saklama süresi dolan üyelerin anonimleştirilmesi; **her sabah 09.00:** hatırlatma e-postaları.

Yöneticinin ana sayfası son günlük yedek başarısız olduysa ya da 26 saatten eskiyse, bina dışı yedek 7 günden eskiyse uyarı gösterir.

**USB rotasyonu (bina dışı kopya, ADR-0006):**

1. Her hafta pazartesiden sonra `LIBRARY_EXPORT_DIR`'deki en yeni `.libx` dosyasını USB belleklerden birine kopyalayın.
2. USB belleği bina dışında saklayın (ör. kurum yöneticisinin evi ya da başka bir şube). Önceki hafta dışarıda olan belleği geri getirin; bir sonraki hafta onu kullanın. En az iki bellek dönüşümlü kullanılır, biri her zaman bina dışındadır.
3. Dosya şifrelidir; parolası olmadan açılamaz. Parolayı USB belleğin yanında **taşımayın**; kâğıttaki kopyası ayrı bir yerde, kapalı zarfta durur ve çevrimdışı saklanır (bir bilgisayarda, e-postada ya da bulut belgesinde tutulmaz).

**Caddy veri klasörü:** Kurulumdan sonra bir kez, Caddy servisi durdurulmuşken Caddy veri klasörünün `pki` alt klasörünü (yerel CA) şifreli bir USB belleğe ya da güvenli bir dolaba kopyalayın. Bu klasör CA'nın özel anahtarını taşır; kaybolursa yeni bir kök sertifika gerekir, ele geçirilirse sahte sertifika üretilebilir.

## Yedekten geri yükleme

Veritabanı bozulduğunda ya da sunucu değiştiğinde (FR-28, NFR-04). Geri yükleme sırasında uygulama kapalı olmalıdır; açıkken komut reddedilir. AC-28 provasında bu yordamın süresi kronometreyle ölçülür ve 1 saatten kısa olmalıdır.

1. **Süreyi başlatın** (prova ise) ve personele sistemin kapalı olacağını haber verin.
2. **Servisleri durdurun:** Önce `library-caddy`, sonra `library-app`.
3. **Dosyayı seçin:** Genellikle `LIBRARY_BACKUP_DIR` içindeki en yeni `library-YYYYMMDD.sqlite3`. Harici disk de kayıpsa USB bellekteki en yeni `library-export-YYYYMMDD.libx` kullanılır.
4. **Komut oturumu açın** (platform bölümünde "Komutların elle çalıştırılması") ve geri yükleyin. Şifreli dosyada parola varsayılan olarak `LIBRARY_EXPORT_PASSPHRASE_FILE`'dan okunur; başka bir parola dosyası `--passphrase-file <yol>` ile verilir.

   ```bash
   python manage.py restore_backup <dosya yolu> --yes
   ```

5. **Çıktıyı okuyun:** "Geri yüklendi: üye=…, nüsha=…, ödünç=…" sayılarını not edin. "Önceki veritabanı korundu: …" satırı, değiştirilen veritabanının koruma kopyasının yolunu verir (`<db>.pre-restore-YYYYMMDD-HHMMSS`, varsa `-wal` ve `-shm` dosyalarıyla).
6. **Eski bir sürümün yedeğiyse** aynı oturumda `python manage.py migrate` çalıştırın.
7. **Servisleri başlatın:** Önce `library-app`, sonra `library-caddy`.
8. **Sayımları kontrol edin:** Giriş yapın; üye ve kitap aramasını, birkaç üyenin açık ödünçlerini ve geciken listesini açın. Sayılar 5. adımdakilerle ve yedeğin alındığı günün durumuyla uyumlu olmalıdır. Yedekten sonra yapılan işlemler (en çok bir günlük; USB'den dönüldüyse en çok bir haftalık) kâğıt kayıtlardan yeniden girilir.
9. **Koruma kopyasını silin (KVKK notu):** Koruma kopyası, saklama kuralının (FR-25) dışında kalan bir kişisel veri kopyasıdır; anonimleştirme görevi ona ulaşmaz ([ADR-0054](decisions/0054-restore-keeps-pre-restore-copy.md)). Geri yüklemenin doğru olduğunu kontrol ettikten sonra `pre-restore` dosyalarını (ve varsa `-wal`, `-shm` eşlerini) veri klasöründen elle silin. Yanlış dosya geri yüklendiyse silmeden önce servisleri durdurup koruma kopyasının adını eski adına çevirerek önceki duruma dönebilirsiniz.
10. **Süreyi durdurun** ve sonucu (tarih, kullanılan dosya, sayılar, süre) kaydedin.

**Başka bir sunucuya taşıma:** Yeni sunucuya [ilk kurulum](#ilk-kurulum) yapılır (`createsuperuser` hariç), ardından bu yordamla `.libx` dosyası geri yüklenir. Parola dosyası yeni sunucuda yoksa kâğıttaki paroladan oluşturulur.

## Windows

### Hesap

Yönetici olarak açılmış PowerShell'de `library-svc` yerel kullanıcısını oluşturun. Parolayı güçlü seçin ve kâğıtta, dışa aktarma parolasıyla aynı zarfta saklayın; WinSW XML'lerine de yazılacak.

```powershell
$parola = Read-Host -AsSecureString "library-svc parolası"
New-LocalUser -Name "library-svc" -Password $parola -PasswordNeverExpires -UserMayNotChangePassword -Description "Kütüphane servis hesabı"
```

Hesap Administrators grubuna eklenmez. "Hizmet olarak oturum açma" hakkını WinSW servis kurulumunda verir (`<allowservicelogon>true</allowservicelogon>`). Parolanın süresi dolmamalıdır; dolarsa servisler başlamaz.

### Klasörler ve izinler

```powershell
New-Item -ItemType Directory -Force C:\Kutuphane\app, C:\Kutuphane\venv, C:\Kutuphane\data, C:\Kutuphane\static, C:\Kutuphane\secrets, C:\Kutuphane\caddy, C:\Kutuphane\winsw\logs
```

`C:\Kutuphane`'nin devralınan izinlerini kaldırın; yalnız Administrators (`*S-1-5-32-544`), SYSTEM (`*S-1-5-18`) ve `library-svc` kalsın. Servis hesabı her şeyi okur, yalnız veri, Caddy ve log klasörlerine yazar:

```powershell
icacls C:\Kutuphane /inheritance:r /grant:r "*S-1-5-32-544:(OI)(CI)F" "*S-1-5-18:(OI)(CI)F" "library-svc:(OI)(CI)RX"
icacls C:\Kutuphane\data /grant "library-svc:(OI)(CI)M"
icacls C:\Kutuphane\caddy /grant "library-svc:(OI)(CI)M"
icacls C:\Kutuphane\winsw\logs /grant "library-svc:(OI)(CI)M"
```

Harici disk (örnekte `E:`) bağlıyken yedek ve dışa aktarma klasörlerini elle açın ve aynı izinleri verin:

```powershell
New-Item -ItemType Directory -Force E:\Kutuphane\backups, E:\Kutuphane\exports
icacls E:\Kutuphane /inheritance:r /grant:r "*S-1-5-32-544:(OI)(CI)F" "*S-1-5-18:(OI)(CI)F" "library-svc:(OI)(CI)M"
```

Dışa aktarma parola dosyasını oluşturun (ilk satır parola) ve UTF-8 olarak kaydedin:

```powershell
notepad C:\Kutuphane\secrets\export-passphrase.txt
```

### Sürüm arşivinin açılması

İlk kurulumda `C:\Kutuphane\app` boştur; klasörü silip arşivi açın. Güncellemede önce eski klasörün adını değiştirin. Arşivdeki `library` klasörü `app` olur:

```powershell
Rename-Item C:\Kutuphane\app app-old
Expand-Archive -Path .\library-v1.0.0.zip -DestinationPath C:\Kutuphane
Rename-Item C:\Kutuphane\library app
```

### Python ve sanal ortam

[python.org](https://www.python.org/downloads/windows/)'dan Python 3.11'in 64 bit Windows yükleyicisini indirin. Kurulumda "Install for all users" seçin (varsayılan yol `C:\Program Files\Python311`). Ardından:

```powershell
py -3.11 -m venv C:\Kutuphane\venv
C:\Kutuphane\venv\Scripts\python.exe -m pip install -r C:\Kutuphane\app\requirements.txt
```

`requirements.txt` Windows'ta saat dilimi verisi için gereken `tzdata`'yı da içerir.

### Caddy

Caddy 2.11.7'nin Windows arşivini indirin ve SHA-512 özetini yayımlanan `checksums.txt`'teki değerle karşılaştırın:

- Arşiv: <https://github.com/caddyserver/caddy/releases/download/v2.11.7/caddy_2.11.7_windows_amd64.zip>
- Özetler: <https://github.com/caddyserver/caddy/releases/download/v2.11.7/caddy_2.11.7_checksums.txt>
- Beklenen SHA-512: `c308154504e53755958ffc62d8a2657ab17eefd6dd25c45dbb2c3d93d29519971f77ca652f7d0f2bcb7f980b9ba3822478865e29969d0272d7613550a43152b1`

```powershell
(Get-FileHash -Algorithm SHA512 .\caddy_2.11.7_windows_amd64.zip).Hash.ToLower()
Expand-Archive -Path .\caddy_2.11.7_windows_amd64.zip -DestinationPath C:\Kutuphane\caddy
```

`caddy.exe` `C:\Kutuphane\caddy` içinde olmalıdır. Caddy yapılandırmayı uygulama klasöründen okur (`C:\Kutuphane\app\deploy\Caddyfile`). Veri klasörü `XDG_DATA_HOME` ile `C:\Kutuphane\caddy`'ye alınmıştır; ilk başlatmadan sonra kök sertifika şuradadır:

`C:\Kutuphane\caddy\caddy\pki\authorities\local\root.crt`

### Servisler

WinSW 2.12.0'ı indirin: <https://github.com/winsw/winsw/releases/download/v2.12.0/WinSW-x64.exe>. WinSW'de exe ile XML aynı adı taşır; exe'yi iki kez kopyalayın ve XML örneklerini yanlarına koyun:

```powershell
Copy-Item .\WinSW-x64.exe C:\Kutuphane\winsw\library-app.exe
Copy-Item .\WinSW-x64.exe C:\Kutuphane\winsw\library-caddy.exe
Copy-Item C:\Kutuphane\app\deploy\winsw\library-app.xml, C:\Kutuphane\app\deploy\winsw\library-caddy.xml C:\Kutuphane\winsw\
```

İki XML'i Not Defteri ile açın ve bütün `__DOLDUR__` değerlerini doldurun: `library-svc` parolası (`<password>`), `LIBRARY_SECRET_KEY`, IP adresi (`LIBRARY_ALLOWED_HOSTS`, `LIBRARY_HOST`, `LIBRARY_BIND`), yedek ve dışa aktarma klasörleri ve SMTP değerleri. XML'de `&`, `<` ve `"` karakterleri `&amp;`, `&lt;` ve `&quot;` olarak yazılır. Dosyaları UTF-8 olarak kaydedin.

[İlk kurulum](#ilk-kurulum) 6. adımı (yedek klasörleri) tamamsa servisleri kaydedip başlatın. Caddy servisi uygulama servisine bağlı olduğu için onu başlatmak önce uygulamayı başlatır:

```powershell
C:\Kutuphane\winsw\library-app.exe install
C:\Kutuphane\winsw\library-caddy.exe install
Start-Service library-caddy
Get-Service library-app, library-caddy
```

Durdurmak için `Stop-Service library-caddy` ve ardından `Stop-Service library-app`; başlatmak için `Start-Service library-caddy`. Servisler "Otomatik" başlar, çökünce 10 saniye sonra en çok üç kez yeniden başlatılır; sayaç bir gün sonra sıfırlanır.

**Loglar:** `C:\Kutuphane\winsw\logs` içindeki `library-app.*.log` ve `library-caddy.*.log` dosyaları. Her dosya 10 MB'a ulaşınca yenisine geçilir; en çok 8 dosya tutulur. Caddy erişim logu yoktur.

### Güvenlik duvarı

Sunucunun ağ bağlantısının profili "Özel" (Private) olmalıdır. 80 ve 443 portlarını yalnız yerel alt ağa açın:

```powershell
Get-NetConnectionProfile
New-NetFirewallRule -DisplayName "Kutuphane HTTPS" -Direction Inbound -Protocol TCP -LocalPort 80,443 -Profile Private -RemoteAddress LocalSubnet -Action Allow
```

Profil "Ortak" (Public) görünüyorsa `Set-NetConnectionProfile -InterfaceAlias "<bağlantı adı>" -NetworkCategory Private` ile değiştirin. 8000 portu için kural açılmaz. Yönlendiricide port yönlendirme yapılmaz.

### NTP

```powershell
w32tm /query /status
w32tm /resync
```

"Kaynak" (Source) satırı bir zaman sunucusu göstermelidir (ör. `time.windows.com`). "Local CMOS Clock" görünüyorsa Ayarlar → Saat ve dil → Tarih ve saat'te "Saati otomatik olarak ayarla"yı açın ve `w32tm /resync` çalıştırın. Saat dilimi (UTC+03:00) İstanbul olmalıdır.

### Komutların elle çalıştırılması

`manage.py` komutları servisin ortam değişkenleriyle çalışmalıdır. Yönetici olarak açılmış bir PowerShell'de ortamı WinSW XML'inden yükleyin; bu oturumdaki `python` sanal ortamın Python'udur:

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[xml]$xml = Get-Content -Encoding UTF8 C:\Kutuphane\winsw\library-app.xml
foreach ($e in $xml.service.env) { Set-Item -Path "env:$($e.name)" -Value $e.value }
$env:LIBRARY_SCHEDULER_ENABLED = "0"
$env:PYTHONIOENCODING = "utf-8"
$env:Path = "C:\Kutuphane\venv\Scripts;$env:Path"
Set-Location C:\Kutuphane\app
```

Ardından ör. `python manage.py backup_db`. Uygulama servisi açıkken geri yükleme reddedilir.

### Kontrol

```powershell
netstat -ano | findstr ":8000 :443 :80"
```

`127.0.0.1:8000` ve `<IP>:443`, `<IP>:80` dışında bir dinleme adresi olmamalıdır.

## Linux

Komutlar Debian 12 içindir; diğer dağıtımlarda paket adları değişebilir.

### Hesap

Oturum açamayan bir sistem kullanıcısı ve aynı adlı grup:

```bash
sudo useradd --system --user-group --home-dir /var/lib/library --shell /usr/sbin/nologin library
```

### Klasörler ve izinler

```bash
sudo install -d -o root -g root -m 0755 /opt/library
sudo install -d -o library -g library -m 0750 /var/lib/library /var/lib/library/data /var/lib/library/static
sudo install -d -o library -g library -m 0700 /var/lib/library/caddy
sudo install -d -o root -g library -m 0750 /etc/library
```

Harici diski `/etc/fstab`'a UUID'siyle ekleyip `/mnt/library-backup`'a bağlayın (`nofail` seçeneğiyle; disk yokken sunucu yine açılır). Disk bağlıyken klasörleri elle açın:

```bash
sudo blkid
sudo mkdir -p /mnt/library-backup
echo "UUID=<diskin UUID'si> /mnt/library-backup ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab
sudo mount /mnt/library-backup
sudo install -d -o library -g library -m 0750 /mnt/library-backup/backups /mnt/library-backup/exports
```

Ortam dosyasını ve dışa aktarma parola dosyasını oluşturup `sudoedit` ile doldurun:

```bash
sudo install -o root -g library -m 0640 /opt/library/app/deploy/library.env.example /etc/library/library.env
sudo install -o root -g library -m 0640 /dev/null /etc/library/export-passphrase.txt
sudoedit /etc/library/library.env
sudoedit /etc/library/export-passphrase.txt
```

`library.env`'de satırlar `AD=değer` biçimindedir; değerde boşluk kullanmayın.

### Sürüm arşivinin açılması

İlk kurulumda `/opt/library/app` yoktur. Güncellemede önce eski klasörün adını değiştirin. Arşivdeki `library` klasörü `app` olur:

```bash
sudo apt install unzip
sudo mv /opt/library/app /opt/library/app-old
sudo unzip -q library-v1.0.0.zip -d /opt/library
sudo mv /opt/library/library /opt/library/app
```

### Python ve sanal ortam

Sanal ortam root'a aittir; servis hesabı yalnız okur. Bağımlılıklar (ilk kurulumda ve [güncellemede](#güncelleme)) root olarak yüklenir:

```bash
sudo apt install python3.11 python3.11-venv
sudo python3.11 -m venv /opt/library/venv
sudo /opt/library/venv/bin/python -m pip install -r /opt/library/app/requirements.txt
```

### Caddy

Caddy 2.11.7'nin Linux arşivini indirin, SHA-512 özetini doğrulayın ve ikiliyi yerine koyun:

- Arşiv: <https://github.com/caddyserver/caddy/releases/download/v2.11.7/caddy_2.11.7_linux_amd64.tar.gz>
- Özetler: <https://github.com/caddyserver/caddy/releases/download/v2.11.7/caddy_2.11.7_checksums.txt>
- Beklenen SHA-512: `a7a433a1b133efc3c8d10eb0b99d52a24b5ef5c322dc77f5282182b1c0402139ab83f3a99f0c52409df77d20123fb0b523edad8a66d8f5e49136197bf61ef0e7`

```bash
sha512sum caddy_2.11.7_linux_amd64.tar.gz
tar -xzf caddy_2.11.7_linux_amd64.tar.gz caddy
sudo install -o root -g root -m 0755 caddy /usr/local/bin/caddy
```

Caddy yapılandırmayı uygulama klasöründen okur (`/opt/library/app/deploy/Caddyfile`). Veri klasörü `/var/lib/library/caddy`'dir; ilk başlatmadan sonra kök sertifika şuradadır (kopyalamak için `sudo cp`):

`/var/lib/library/caddy/caddy/pki/authorities/local/root.crt`

### Servisler

```bash
sudo cp /opt/library/app/deploy/systemd/library-app.service /opt/library/app/deploy/systemd/library-caddy.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now library-app library-caddy
systemctl status library-app library-caddy
```

Durdurmak için `sudo systemctl stop library-caddy library-app`, başlatmak için `sudo systemctl start library-app library-caddy`. Servisler çökünce 5 saniye sonra yeniden başlar. İkisi de `library` kullanıcısıyla çalışır; Caddy 80 ve 443 portlarını `CAP_NET_BIND_SERVICE` yeteneğiyle dinler. Unit'ler dosya sistemini salt okunur görür; uygulama yalnız veri, yedek ve dışa aktarma klasörlerine, Caddy yalnız kendi veri klasörüne yazar.

**Loglar:** `journalctl -u library-app` ve `journalctl -u library-caddy`. Caddy erişim logu yoktur.

### Güvenlik duvarı

`ufw` ile 80 ve 443 portlarını yalnız LAN alt ağına açın (örnekte `192.168.1.0/24`; SSH kullanılıyorsa onu da yalnız LAN'a açın):

```bash
sudo apt install ufw
sudo ufw default deny incoming
sudo ufw allow from 192.168.1.0/24 to any port 80,443 proto tcp
sudo ufw allow from 192.168.1.0/24 to any port 22 proto tcp
sudo ufw enable
```

8000 portu için kural açılmaz. Yönlendiricide port yönlendirme yapılmaz.

### NTP

```bash
timedatectl status
sudo timedatectl set-ntp true
```

"System clock synchronized: yes" ve "NTP service: active" görünmelidir.

### Komutların elle çalıştırılması

`manage.py` komutları `library` kullanıcısıyla ve servisin ortamıyla çalışır; böylece oluşan dosyalar da servis hesabına ait olur:

```bash
sudo -u library bash
set -a; . /etc/library/library.env; set +a
export LIBRARY_SCHEDULER_ENABLED=0
export PATH=/opt/library/venv/bin:$PATH
cd /opt/library/app
```

Ardından ör. `python manage.py backup_db`. Bu oturumda `pip install` çalışmaz; bağımlılıklar [Python ve sanal ortam](#python-ve-sanal-ortam-1) bölümündeki gibi root olarak yüklenir.

### Kontrol

```bash
sudo ss -ltnp | grep -E ':(80|443|8000)\b'
```

`127.0.0.1:8000` ve `<IP>:443`, `<IP>:80` dışında bir dinleme adresi olmamalıdır.

## Sorun giderme

- **Tarayıcı sunucuya bağlanamıyor:** Sunucunun IP adresi değişmiş olabilir (`ipconfig` ya da `ip addr`). DHCP rezervasyonunu kontrol edin. IP kalıcı olarak değiştiyse `LIBRARY_HOST`, `LIBRARY_BIND` ve `LIBRARY_ALLOWED_HOSTS`'u birlikte güncelleyin, servisleri yeniden başlatın ve personel kısayollarını düzeltin.
- **"Bad Request (400)":** Tarayıcıya yazılan adres `LIBRARY_ALLOWED_HOSTS` ile aynı değil.
- **Sertifika uyarısı:** Kök sertifika o bilgisayara yüklenmemiş ya da Caddy veri klasörü yeniden oluşmuş. [Personel bilgisayarları](#personel-bilgisayarları) adımlarını tekrarlayın.
- **Servis başlamıyor:** Logda "Eksik ortam değişkeni: <ad>" varsa değişkeni ekleyin. Windows'ta `library-svc` parolası değiştiyse iki XML'deki `<password>`'ü güncelleyip servisleri `uninstall` ve `install` ile yeniden kaydedin.
- **Yedek uyarısı:** Harici disk takılı mı, `LIBRARY_BACKUP_DIR` klasörü var mı ve servis hesabının yazma izni var mı kontrol edin; ardından komut oturumunda `python manage.py backup_db` çalıştırın.
- **Erişim logu gerekiyor:** Erişim logu bilerek kapalıdır ([ADR-0065](decisions/0065-caddy-no-access-log.md)). Bir sorunu incelemek için geçici olarak açılırsa iş bitince kapatılır ve oluşan log dosyası silinir; dosya üye adı ve telefonu içerebilir.
- **Yük testi (faz 6):** `scripts/loadtest.py` waitress'e Caddy'siz bağlanır; test süresince `LIBRARY_ALLOWED_HOSTS`'a `127.0.0.1` geçici olarak eklenir ve test bitince kaldırılır. Yük testi yalnız tohum verili bir test veritabanında yapılır.
