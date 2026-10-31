# ADR-0048: Uygulama, özel bir GitHub reposundan Claude Code bulut oturumlarıyla yapılır

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Kullanıcı, 2026-10-31 oturumunda soru penceresinden seçti.

## Bağlam

- Kullanıcının 100 $ tutarında Claude Code bulut oturumu kredisi var. Kredi yaklaşık 2026-11-05'te sıfırlanıyor. Yalnız bulut oturumlarını kapsıyor (web, masaüstü, CLI `--cloud`, mobil); sohbet, Routines ve remote control kapsam dışında.
- Depo yerel ve remote'u yok. Bulut oturumları repoyu GitHub'dan klonlar.
- Bulut oturumu kullanıcıya soru soramaz. Karar politikasına göre kritik kararları yalnız kullanıcı verir.
- SRS §7'deki "bulut yok" kısıtı ürünün çalışma ortamı içindir; geliştirme ortamını kapsamaz.

## Değerlendirilen seçenekler

- GitHub:
  1. **Özel (private) repo açmak** (seçildi).
  2. Var olan bir repoya push etmek.
  3. GitHub'a koymamak: bu durumda kredi kullanılamaz.
- Kapsam:
  1. **Onay kapısından sonra uygulama** (seçildi).
  2. Doküman işlerini de şimdiden bulutta yapmak.
  3. Yalnız `/code-review ultra`.
- Bulut oturumunda commit (ikinci soru):
  1. **Dala serbest commit ve push, `main`'e onayla birleştirme** (seçildi).
  2. Her görevin sonunda durup onay beklemek: paralellik ve kredi verimi düşer.
  3. Grup sonunda tek commit: geçmiş kabalaşır.
- Commit zamanı:
  1. **Plana uymak, kapıdan sonra commit'lemek** (seçildi).
  2. Hemen bir ara commit atmak.

## Karar

- Faz 4 sürecinin kalanı yerelde yürür.
- Onay kapısından sonra plan §9'daki commit atılır. Ardından `gh repo create --private` ile repo açılır ve push edilir. Bu adım için kullanıcıdan son bir onay alınır.
- G01–G19, plan §4.0'daki görev gruplarına ve bağımlılık sırasına göre bulut oturumlarında TDD ile uygulanır.
  - Her oturuma tam tanımlı bir görev verilir: plan bölümü, TC'ler, doğrulama komutu ve dal adı.
  - Oturum yeni bir kritik kararla karşılaşırsa karar vermez; durur ve soruyu raporlar.
- **Commit kuralı (küçük karar 16'ya bulut istisnası):** Bulut oturumu kendi `feature/<grup>` dalına Conventional Commits ile, görev başına commit atar ve push eder. Kullanıcının onayı `main`'e birleştirmede (PR incelemesi) alınır. `main`'e doğrudan commit atılmaz. Yerel oturumlarda küçük karar 16 aynen geçerlidir.
- Sonunda `/code-review ultra` çalıştırılır. Bu komutu kullanıcı başlatır.
- Depoya gerçek kişisel veri ve gizli değer girmez. Tohum veri sentetiktir, `.env` dosyası yoktur.

## Sonuçlar

- **Olumlu:** Bağımsız görev grupları paralel uygulanır ve kredi boşa gitmez.
- **Olumsuz / riskler:**
  - Kod GitHub'a çıkar (özel repo).
  - Bulut ortamı Linux'tur. Windows'a özgü parçalar (`msvcrt` kilidi, WinSW, `tzdata`) yerelde doğrulanmalıdır.
  - Bulut ortamındaki Python sürümü 3.11'den farklı olabilir (ADR-0013); oturum başında kontrol edilir.
  - Paralel dallar birleştirmede çakışabilir.
  - Kredinin ne kadarının harcanacağı önceden bilinemez. Bu riskler R-15'te izlenir.

## İzlenebilirlik

- **Gereksinim:** Süreç kararı; doğrudan bir FR'ye bağlı değil. Plan §4.0, §9.
- **Bağlantılı:** ADR-0013, ADR-0034
