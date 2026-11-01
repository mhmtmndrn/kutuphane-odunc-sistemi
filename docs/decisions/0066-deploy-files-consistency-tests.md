# ADR-0066: Dağıtım dosyaları ve kullanıcı belgeleri otomatik tutarlılık testleriyle denetlenir

- **Durum:** Kabul edildi (2026-11-01)
- **Kaynak:** Kullanıcı, 2026-11-01 yerel oturumunda soru penceresinden seçti (G19 açılışı).

## Bağlam

- Plan G19'un testleri (TC-225…TC-234, TC-319) elle yapılır ve faz 6'ya kalır. Dağıtım dosyaları ise ortam değişkeni adlarını, yolları ve servis ayarlarını birbirinden ve ayarlardan (`library_site/settings/`) bağımsız olarak tekrar eder.
- Bir değişken adı yanlış yazılırsa ya da ayarlara yeni bir değişken eklenip dağıtım dosyalarına eklenmezse hata ancak kurulumda, süreç açılırken görülür.
- TC-352, README'nin metin koşullarını zaten otomatik denetliyor.

## Değerlendirilen seçenekler

1. **pytest tutarlılık testleri, elle TC'ler de kalır** (seçildi): Dosyalar ayrıştırılır ve birbirleriyle, ayarlarla ve architecture §6.4 ile karşılaştırılır. Kurulumun kendisi faz 6'da elle denenir.
2. **Yalnız elle TC'ler:** Reddedildi: tutarsızlık faz 6'ya kadar görünmez; dosyalar sonraki değişikliklerde kayabilir.

## Karar

- `tests/test_deploy_files.py` şunları denetler:
  - `deploy/library.env.example` ve iki WinSW XML'indeki `<env>` adları, ayarların okuduğu `LIBRARY_*` kümesi ve `DJANGO_SETTINGS_MODULE` ile (architecture §6.4 listesi) aynıdır. Caddy'ye özgü `LIBRARY_HOST` ve `LIBRARY_BIND` ayrıca denetlenir.
  - XML'ler ayrıştırılır ve zorunlu öğeleri (`id`, `executable`, `arguments`, `serviceaccount`, `onfailure`, `log`; Caddy servisinde `depend`) vardır.
  - systemd unit'lerinde ve Caddyfile'da zorunlu satırlar vardır (ör. `tls internal`, `handle_path /static/*`, `reverse_proxy 127.0.0.1:8000`, `bind {$LIBRARY_BIND}`, `Restart=on-failure`, `User=library`) ve Caddyfile'da `log` yönergesi yoktur (ADR-0065).
  - TC-319'un metin koşulları (kılavuz ve README) otomatik denetlenir; TC-319'un elle okunması da kalır.
- Testler ağa çıkmaz ve Caddy ya da WinSW ikilisi gerektirmez. `caddy validate` elle doğrulamada çalıştırılır.

## Sonuçlar

- **Olumlu:** Değişken adı, yol ve servis ayarı kaymaları her test koşusunda yakalanır.
- **Olumsuz / riskler:** Testler dosyaların sözdizimini değil içeriğini denetler; Caddyfile'ın gerçekten yüklendiği ancak `caddy validate` ile, servislerin çalıştığı ancak faz 6 kurulumunda görülür.

## İzlenebilirlik

- **Gereksinim:** NFR-04, NFR-05, NFR-06, NFR-08; FR-03, FR-11, FR-12, FR-29. Testler TC-359…TC-366.
- **Bağlantılı:** ADR-0010, ADR-0029, ADR-0065
